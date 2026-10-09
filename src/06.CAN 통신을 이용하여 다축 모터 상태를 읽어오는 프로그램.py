# -*- coding: utf-8 -*-
"""
Multi-axis motor status monitor over CAN using raw CANopen SDO upload (no EDS needed).
- Polls CiA 402 objects via SDO Upload:
    0x6041:00 Statusword           (uint16)
    0x6061:00 Modes of operation display (int8)
    0x6064:00 Position actual value (int32)
    0x606C:00 Velocity actual value (int32)
    0x6078:00 Current actual value  (int16)
- CSV logging & console summary
- Interfaces: python-can (socketcan/pcan/kvaser/vector/ixxat/zlgcan ...)

Usage examples:
  python multi_axis_can_monitor.py --interface pcan --channel PCAN_USBBUS1 --bitrate 500000 --nodes 1,2,3 --csv motors.csv
  python multi_axis_can_monitor.py --interface kvaser --channel 0 --bitrate 500000 --nodes 1-6
  python multi_axis_can_monitor.py --interface socketcan --channel can0 --nodes 1,2 --rate 10
"""

import csv
import time
import argparse
import sys
from typing import List, Tuple, Optional, Dict

import can  # python-can

SDO_RX_BASE = 0x600  # client->server (upload request)
SDO_TX_BASE = 0x580  # server->client (upload response)


# ---------------------------- CAN helpers ----------------------------

def open_bus(interface: str, channel: str, bitrate: int) -> can.Bus:
    """
    Create python-can Bus with common backends.
    - socketcan: channel 'can0', bitrate ignored (set at OS level)
    - pcan: channel 'PCAN_USBBUS1', bitrate integer (e.g., 500000)
    - kvaser: channel '0', bitrate integer
    - vector: channel '0', app_name optional (not used here)
    """
    kwargs = {"interface": interface, "channel": channel}
    # Some backends need 'bitrate'; socketcan typically ignores this
    if bitrate:
        kwargs["bitrate"] = bitrate
    try:
        bus = can.Bus(**kwargs)
        return bus
    except Exception as e:
        print(f"[ERR] CAN open failed: {e}")
        raise


def sdo_upload(bus: can.Bus, node_id: int, index: int, subindex: int,
               timeout: float = 0.2, retries: int = 2) -> bytes:
    """
    Perform a CANopen SDO expedited upload (read) for given (index, subindex).
    Returns raw data bytes (little-endian, 0..4 bytes).
    Raises RuntimeError on abort/timeout.
    """
    rx_cobid = SDO_TX_BASE + node_id
    tx_cobid = SDO_RX_BASE + node_id

    # CANopen SDO upload request frame (expedited):
    # Byte0: 0x40 (cs=2, expedited upload request)
    # Byte1: index low, Byte2: index high, Byte3: subindex
    # Byte4..7: 0
    req = can.Message(arbitration_id=tx_cobid,
                      data=bytes([0x40, index & 0xFF, (index >> 8) & 0xFF, subindex, 0, 0, 0, 0]),
                      is_extended_id=False)

    for attempt in range(retries + 1):
        bus.send(req)

        t0 = time.time()
        while (time.time() - t0) < timeout:
            msg = bus.recv(timeout=timeout)
            if msg is None:
                break
            if msg.arbitration_id != rx_cobid or len(msg.data) != 8:
                continue

            b0 = msg.data[0]
            # Abort?
            if b0 == 0x80:
                abort_code = int.from_bytes(msg.data[4:8], "little")
                raise RuntimeError(f"SDO abort (node {node_id:02X}, idx 0x{index:04X}:{subindex:02X}, code 0x{abort_code:08X})")

            # Upload response should have cs=2 (0b010), expedited bit set
            expedited = (b0 & 0x02) != 0
            if (b0 >> 5) & 0x07 != 0x2 or not expedited:
                # Not an expedited upload response; ignore
                continue

            # n bytes not used count in bytes 0 bits 2..3
            n = (b0 >> 2) & 0x03  # number of empty bytes at end
            size = 4 - n
            raw = bytes(msg.data[4:4 + size])
            return raw

        # retry if not received
    raise RuntimeError(f"SDO timeout (node {node_id:02X}, idx 0x{index:04X}:{subindex:02X})")


def to_int_le(data: bytes, signed: bool) -> int:
    if len(data) == 0:
        return 0
    return int.from_bytes(data, byteorder="little", signed=signed)


# ---------------------------- CiA 402 parsing ----------------------------

def parse_statusword(sw: int) -> str:
    """
    Decode CiA 402 statusword (0x6041) into a brief state string.
    """
    # bits based on DS402; this is a compact summary for quick view
    b = lambda i: (sw >> i) & 1
    if b(3):  # Fault
        return "FAULT"
    if b(0) and not b(1) and not b(2):
        return "NOT READY"
    if b(0) and b(1) and not b(2):
        return "SWITCHED_ON"
    if b(0) and b(1) and b(2):
        return "OP_ENABLED"
    if b(6):
        return "SWITCH_ON_DISABLED"
    if b(5):
        return "QUICK_STOP"
    return f"0x{sw:04X}"


def mode_name(mode_disp: int) -> str:
    names = {
        -1: "JOG",
         0: "NO_MODE",
         1: "PROFILE_POSITION",
         3: "PROFILE_VELOCITY",
         4: "PROFILE_TORQUE",
         6: "HOMING",
         7: "INTERPOLATED_POSITION",
         8: "CYCLIC_SYNC_POSITION",
         9: "CYCLIC_SYNC_VELOCITY",
        10: "CYCLIC_SYNC_TORQUE",
    }
    return names.get(mode_disp, str(mode_disp))


def read_motor_status(bus: can.Bus, node_id: int) -> Dict[str, int]:
    """
    Read key CiA-402 objects via SDO Upload.
    Returns a dict with parsed values.
    """
    sw = to_int_le(sdo_upload(bus, node_id, 0x6041, 0x00), signed=False)
    md = int.from_bytes(sdo_upload(bus, node_id, 0x6061, 0x00), "little", signed=True)
    pos = to_int_le(sdo_upload(bus, node_id, 0x6064, 0x00), signed=True)
    vel = to_int_le(sdo_upload(bus, node_id, 0x606C, 0x00), signed=True)
    cur = to_int_le(sdo_upload(bus, node_id, 0x6078, 0x00), signed=True)

    return {
        "statusword": sw,
        "state": parse_statusword(sw),
        "mode_disp": md,
        "mode_name": mode_name(md),
        "position": pos,
        "velocity": vel,
        "current": cur,
    }


# ---------------------------- Main loop ----------------------------

def parse_nodes(arg: str) -> List[int]:
    """
    Parse node list spec like '1,2,5-7' -> [1,2,5,6,7]
    """
    nodes: List[int] = []
    for part in arg.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a, b = int(a), int(b)
            nodes.extend(list(range(min(a, b), max(a, b) + 1)))
        else:
            nodes.append(int(part))
    # unique & sorted
    return sorted(set(nodes))


def main():
    ap = argparse.ArgumentParser(description="Multi-axis motor monitor via CAN (raw CANopen SDO)")
    ap.add_argument("--interface", required=True, help="python-can interface (pcan, kvaser, socketcan, vector, ixxat, zlgcan, ...)")
    ap.add_argument("--channel",   required=True, help="channel (e.g., PCAN_USBBUS1 | 0 | can0)")
    ap.add_argument("--bitrate",   type=int, default=500000, help="bitrate (e.g., 500000)")
    ap.add_argument("--nodes",     required=True, help="node list like '1,2,5-7'")
    ap.add_argument("--rate",      type=float, default=10.0, help="polling rate Hz")
    ap.add_argument("--csv",       default=None, help="CSV log path")
    ap.add_argument("--timeout",   type=float, default=0.25, help="SDO timeout seconds")
    ap.add_argument("--retries",   type=int,   default=1, help="SDO retries per object")
    args = ap.parse_args()

    nodes = parse_nodes(args.nodes)
    period = 1.0 / max(0.1, args.rate)

    try:
        bus = open_bus(args.interface, args.channel, args.bitrate)
    except Exception:
        sys.exit(2)

    writer = None
    f = None
    if args.csv:
        f = open(args.csv, "a", newline="", encoding="utf-8")
        writer = csv.writer(f)
        writer.writerow(["ts","node","state","mode","statusword",
                         "position","velocity","current"])

    print("[INFO] Start polling:", nodes, f"@ {args.rate} Hz")
    try:
        while True:
            t0 = time.time()
            for nid in nodes:
                try:
                    # Use per-call timeout/retry by temporarily adjusting function defaults
                    status = read_motor_status(bus, nid)
                except RuntimeError as e:
                    print(f"[WARN] node {nid}: {e}")
                    continue
                line = (f"node={nid:02d} state={status['state']:<14} "
                        f"mode={status['mode_name']:<22} "
                        f"sw=0x{status['statusword']:04X} "
                        f"pos={status['position']} vel={status['velocity']} cur={status['current']}")
                print(line)

                if writer:
                    writer.writerow([int(t0), nid, status["state"], status["mode_name"],
                                     f"0x{status['statusword']:04X}",
                                     status["position"], status["velocity"], status["current"]])
                    f.flush()

            # simple rate control
            dt = time.time() - t0
            sleep = period - dt
            if sleep > 0:
                time.sleep(sleep)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")
    finally:
        try:
            if f: f.close()
            bus.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
