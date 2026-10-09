# -*- coding: utf-8 -*-
"""
TCP/IP Robot Status Monitoring Client (NDJSON protocol)
- Connects to host:port, optional API key auth, subscribes to robot status stream
- Heartbeat (PING/PONG), auto-reconnect with exponential backoff
- CSV logging, threshold alerts (battery/temp/e-stop), concise console view
- Optional TLS (server certificate verification)

Usage examples:
  python robot_monitor_client.py --host 127.0.0.1 --port 9000 --csv robot_log.csv
  python robot_monitor_client.py --host robot.example.com --port 443 --tls --ca cert.pem --api-key YOUR_TOKEN
"""

import asyncio
import json
import sys
import time
import csv
import signal
import argparse
import ssl
from pathlib import Path
from typing import Optional, Dict, Any


class RobotMonitorClient:
    def __init__(
        self,
        host: str,
        port: int,
        api_key: Optional[str] = None,
        subscribe_payload: Optional[Dict[str, Any]] = None,
        csv_path: Optional[str] = None,
        min_backoff: float = 1.0,
        max_backoff: float = 30.0,
        keepalive_interval: float = 10.0,
        idle_timeout: float = 30.0,
        battery_low_thresh: float = 20.0,
        joint_temp_crit_thresh: float = 80.0,
        use_tls: bool = False,
        ca_cert: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.api_key = api_key
        self.subscribe_payload = subscribe_payload or {"type": "subscribe", "stream": "robot_status"}
        self.csv_path = csv_path
        self.min_backoff = min_backoff
        self.max_backoff = max_backoff
        self.keepalive_interval = keepalive_interval
        self.idle_timeout = idle_timeout
        self.battery_low_thresh = battery_low_thresh
        self.joint_temp_crit_thresh = joint_temp_crit_thresh
        self.use_tls = use_tls
        self.ca_cert = ca_cert

        self._stop = False
        self._writer: Optional[asyncio.StreamWriter] = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._last_rx = 0.0
        self._last_ping = 0.0
        self._csv_writer = None
        self._csv_file = None

    # ----------------- connection helpers -----------------
    def _build_ssl_context(self) -> Optional[ssl.SSLContext]:
        if not self.use_tls:
            return None
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        if self.ca_cert:
            ctx.load_verify_locations(self.ca_cert)
        # Strong defaults already set by create_default_context
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx

    async def connect_once(self):
        ssl_ctx = self._build_ssl_context()
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port, ssl=ssl_ctx)
        self._last_rx = time.time()
        self._last_ping = 0.0

        # optional auth
        if self.api_key:
            await self._send_json({"type": "auth", "api_key": self.api_key})

        # subscribe
        await self._send_json(self.subscribe_payload)

    async def _send_json(self, obj: Dict[str, Any]):
        if not self._writer:
            return
        data = json.dumps(obj, separators=(",", ":")) + "\n"
        self._writer.write(data.encode("utf-8"))
        await self._writer.drain()

    # ----------------- CSV logging -----------------
    def _csv_init(self):
        if not self.csv_path or self._csv_writer:
            return
        Path(self.csv_path).parent.mkdir(parents=True, exist_ok=True)
        self._csv_file = open(self.csv_path, "a", newline="", encoding="utf-8")
        self._csv_writer = csv.writer(self._csv_file)
        # header (idempotent; write unconditionally is fine for quick use)
        self._csv_writer.writerow([
            "ts","robot_id","mode","estop","battery",
            "pose_x","pose_y","pose_theta",
            "vel_vx","vel_vy","vel_omega",
            "joint_temps"
        ])
        self._csv_file.flush()

    def _csv_write_status(self, msg: Dict[str, Any]):
        if not self._csv_writer:
            return
        pose = msg.get("pose", {})
        vel  = msg.get("vel", {})
        temps = msg.get("joint_temp")
        row = [
            msg.get("ts"),
            msg.get("robot_id"),
            msg.get("mode"),
            msg.get("estop"),
            msg.get("battery"),
            pose.get("x"), pose.get("y"), pose.get("theta"),
            vel.get("vx"), vel.get("vy"), vel.get("omega"),
            ";".join(map(lambda x: f"{x:.1f}", temps)) if isinstance(temps, list) else ""
        ]
        self._csv_writer.writerow(row)
        self._csv_file.flush()

    # ----------------- processing -----------------
    def _alert_check(self, msg: Dict[str, Any]):
        if msg.get("type") != "status":
            return
        estop = bool(msg.get("estop", False))
        batt = msg.get("battery")
        temps = msg.get("joint_temp") or []
        if estop:
            print("⚠️  [E-STOP] 비상정지 신호 감지됨!")
        if isinstance(batt, (int, float)) and batt <= self.battery_low_thresh:
            print(f"⚠️  [BATTERY] 배터리 낮음: {batt:.1f}% ≤ {self.battery_low_thresh}%")
        if temps:
            tmax = max(temps)
            if tmax >= self.joint_temp_crit_thresh:
                print(f"🔥  [TEMP] 관절 최고온도 과열: {tmax:.1f}°C ≥ {self.joint_temp_crit_thresh:.1f}°C")

    def _pretty_status_line(self, msg: Dict[str, Any]) -> str:
        rid = msg.get("robot_id","?")
        mode = msg.get("mode","?")
        batt = msg.get("battery","?")
        estop = "YES" if msg.get("estop", False) else "no"
        pose = msg.get("pose") or {}
        temps = msg.get("joint_temp") or []
        tmax = f"{max(temps):.1f}°C" if temps else "n/a"
        return (f"[{msg.get('ts','?')}] {rid} mode={mode} estop={estop} "
                f"batt={batt}% pose=({pose.get('x','?'):.2f},{pose.get('y','?'):.2f},{pose.get('theta','?'):.2f}) "
                f"tmax={tmax}")

    async def _session_loop(self):
        assert self._reader and self._writer
        self._csv_init()

        while not self._stop:
            # keepalive & idle detection
            now = time.time()
            if now - self._last_rx > self.idle_timeout:
                raise asyncio.TimeoutError("idle timeout")

            if now - self._last_ping > self.keepalive_interval:
                await self._send_json({"type": "ping", "ts": int(now)})
                self._last_ping = now

            try:
                line = await asyncio.wait_for(self._reader.readline(), timeout=1.0)
            except asyncio.TimeoutError:
                continue  # allow keepalive/idle checks

            if not line:
                # EOF from server
                raise ConnectionError("server closed connection")

            self._last_rx = time.time()
            s = line.decode("utf-8", errors="ignore").strip()
            if not s:
                continue

            try:
                msg = json.loads(s)
            except json.JSONDecodeError:
                print("[WARN] invalid JSON frame ignored")
                continue

            mtype = msg.get("type")
            if mtype == "ping":
                await self._send_json({"type":"pong","ts":int(time.time())})
                continue
            if mtype == "pong":
                continue

            if mtype == "status":
                # optional filtering/validation can be added here
                self._csv_write_status(msg)
                self._alert_check(msg)
                # concise console line
                try:
                    print(self._pretty_status_line(msg))
                except Exception:
                    # be robust to missing fields
                    print(f"[STATUS] {msg}")
                continue

            # generic message
            print(f"[INFO] {msg}")

    async def run(self):
        backoff = self.min_backoff
        while not self._stop:
            try:
                print(f"[INFO] connecting to {self.host}:{self.port} ...")
                await self.connect_once()
                print("[INFO] connected. waiting for status stream...")
                backoff = self.min_backoff  # reset on success
                await self._session_loop()
            except (asyncio.CancelledError, KeyboardInterrupt):
                break
            except Exception as e:
                print(f"[WARN] connection error: {e}. reconnect in {backoff:.1f}s")
                await asyncio.sleep(backoff)
                backoff = min(self.max_backoff, backoff * 2)
            finally:
                try:
                    if self._writer:
                        self._writer.close()
                        await self._writer.wait_closed()
                except Exception:
                    pass
                self._reader = None
                self._writer = None

    def stop(self):
        self._stop = True
        try:
            if self._csv_file:
                self._csv_file.close()
        except Exception:
            pass


# ----------------- CLI -----------------
import os
import argparse

def parse_args():
    ap = argparse.ArgumentParser(description="TCP Robot Status Monitoring Client (NDJSON)")
    ap.add_argument("--host",
                    default=os.environ.get("ROBOT_HOST", "192.168.21.10"),
                    help="server host (default: env ROBOT_HOST or 192.168.21.10)")
    ap.add_argument("--port",
                    type=int,
                    default=int(os.environ.get("ROBOT_PORT", "9000")),
                    help="server port (default: env ROBOT_PORT or 9000)")
    ap.add_argument("--api-key",
                    default=os.environ.get("ROBOT_API_KEY"),
                    help="optional API key (default: env ROBOT_API_KEY)")
    ap.add_argument("--csv", dest="csv_path", default=None, help="CSV log file path")
    ap.add_argument("--keepalive", type=float, default=10.0, help="PING interval seconds")
    ap.add_argument("--idle-timeout", type=float, default=30.0, help="disconnect if no data for N seconds")
    ap.add_argument("--batt-low", type=float, default=20.0, help="battery low threshold percent")
    ap.add_argument("--temp-crit", type=float, default=80.0, help="critical joint temperature threshold °C")
    ap.add_argument("--tls", action="store_true", help="use TLS")
    ap.add_argument("--ca", dest="ca_cert", default=None, help="CA certificate path for TLS verification")

    args = ap.parse_args()

    # 간단한 유효성 검사
    if not (0 < args.port < 65536):
        ap.error("--port must be 1..65535")

    return args



async def main_async():
    args = parse_args()
    client = RobotMonitorClient(
        host=args.host,
        port=args.port,
        api_key=args.api_key,
        csv_path=args.csv_path,
        keepalive_interval=args.keepalive,
        idle_timeout=args.idle_timeout,
        battery_low_thresh=args.batt_low,
        joint_temp_crit_thresh=args.temp_crit,
        use_tls=args.tls,
        ca_cert=args.ca_cert,
    )

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, client.stop)
        except NotImplementedError:
            # Windows may not support add_signal_handler for SIGTERM
            pass

    try:
        await client.run()
    finally:
        client.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass
