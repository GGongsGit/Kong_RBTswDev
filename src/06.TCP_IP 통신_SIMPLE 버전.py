# TCP/IP 소켓만 사용해 모터(게이트웨이)에 접속 
# → CANopen SDO 업로드로 핵심 상태(상태워드/모드/위치/속도/전류)를 읽어오는 
# 아주 심플한 예제입니다.
# 게이트웨이는 SLCAN ASCII over TCP(Lawicel 스타일: t<ID><DLC><DATA>\r)을 
# 쓴다고 가정

# -*- coding: utf-8 -*-
# motor_status_tcp_min.py
# TCP/IP(SLCAN ASCII)로 CANopen SDO Upload로 상태 읽기 - 초간단 버전
import socket, select, time

HOST = "192.168.0.10"   # 게이트웨이 IP
PORT = 29536            # 게이트웨이 TCP 포트
NODE_ID = 1             # 대상 노드 ID (1..127)
RATE_HZ = 5             # 폴링 주기(Hz)

SDO_RX_BASE = 0x600     # 클라이언트->서버 (요청)
SDO_TX_BASE = 0x580     # 서버->클라이언트 (응답)

# --- SLCAN helpers (11-bit 표준 ID 전용) ---
def slcan_send(sock, arbid, data: bytes):
    dlc = min(len(data), 8)
    line = "t{:03X}{:1X}{}\r".format(arbid & 0x7FF, dlc, data[:dlc].hex().upper())
    sock.sendall(line.encode("ascii"))

_rxbuf = bytearray()
def slcan_recv(sock, timeout=0.2):
    # '\r' 끝나는 한 줄을 받아 1개 프레임으로 디코드
    # 형식: tIII D DATA...\r  (I:3hex, D:1hex)
    end = _rxbuf.find(b"\r")
    if end < 0:
        r, _, _ = select.select([sock], [], [], timeout)
        if not r:
            return None
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError("TCP closed")
        _rxbuf.extend(chunk)
        end = _rxbuf.find(b"\r")
        if end < 0:
            return None
    line = bytes(_rxbuf[:end])
    del _rxbuf[:end+1]
    if not line or line[:1] != b"t":  # 29-bit 'T'는 미지원
        return None
    txt = line.decode("ascii")
    arbid = int(txt[1:4], 16)
    dlc = int(txt[4], 16)
    data_hex = txt[5:]
    if len(data_hex) != 2*dlc:
        return None
    data = bytes.fromhex(data_hex)
    data = (data + b"\x00"*8)[:8]
    return arbid, dlc, data

# --- 유틸 ---
def to_int_le(b: bytes, signed=False):
    return int.from_bytes(b, "little", signed=signed) if b else 0

# --- SDO upload(익스피디티드) 한 번 읽기 ---
def sdo_upload(sock, node_id: int, index: int, subidx: int, timeout=0.25):
    rx_id = SDO_TX_BASE + node_id
    tx_id = SDO_RX_BASE + node_id
    # 요청: 0x40, idx(lo,hi), sub, pad
    req = bytes([0x40, index & 0xFF, (index >> 8) & 0xFF, subidx, 0,0,0,0])
    slcan_send(sock, tx_id, req)

    t0 = time.time()
    while time.time() - t0 < timeout:
        frame = slcan_recv(sock, timeout=timeout)
        if not frame:
            continue
        arbid, dlc, data = frame
        if arbid != rx_id or dlc < 8:
            continue
        b0 = data[0]
        if b0 == 0x80:  # abort
            abort = int.from_bytes(data[4:8], "little")
            raise RuntimeError(f"SDO abort 0x{index:04X}:{subidx:02X} code=0x{abort:08X}")
        # 응답: cs=2(업로드 응답), expedited=1
        if ((b0 >> 5) & 0x7) != 0x2 or (b0 & 0x02) == 0:
            continue
        n = (b0 >> 2) & 0x3        # 뒤쪽 비어있는 바이트 수
        size = 4 - n               # 실제 유효 바이트
        return bytes(data[4:4+size])
    raise RuntimeError(f"SDO timeout 0x{index:04X}:{subidx:02X}")

def main():
    # 접속
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3.0)
    s.connect((HOST, PORT))
    s.setblocking(False)

    # 일부 게이트웨이는 CAN 오픈 명령이 필요할 수 있음 (예: b'O\\r')
    # s.sendall(b'O\r')  # 필요 시 주석 해제

    period = 1.0 / max(0.1, RATE_HZ)
    print(f"[INFO] TCP {HOST}:{PORT}, node={NODE_ID}, {RATE_HZ} Hz")

    try:
        while True:
            t0 = time.time()
            try:
                sw  = to_int_le(sdo_upload(s, NODE_ID, 0x6041, 0x00), signed=False)
                md  = int.from_bytes(sdo_upload(s, NODE_ID, 0x6061, 0x00), "little", signed=True)
                pos = to_int_le(sdo_upload(s, NODE_ID, 0x6064, 0x00), signed=True)
                vel = to_int_le(sdo_upload(s, NODE_ID, 0x606C, 0x00), signed=True)
                cur = to_int_le(sdo_upload(s, NODE_ID, 0x6078, 0x00), signed=True)
                print(f"SW=0x{sw:04X}  MODE={md:>3}  POS={pos:>10}  VEL={vel:>8}  CUR={cur:>6}")
            except RuntimeError as e:
                print("[WARN]", e)

            # 간단한 주기 제어
            dt = time.time() - t0
            slp = period - dt
            if slp > 0:
                time.sleep(slp)
    except KeyboardInterrupt:
        print("\n[INFO] Stop")
    finally:
        try:
            s.close()
        except:
            pass

if __name__ == "__main__":
    main()
