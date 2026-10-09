# 7-1 예상문제 2 : 물리값 → CAN 8바이트 인코딩 (MotorStatus)
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q61_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q61_2_output.txt"

def encode(rpm, cur, temp, fault):
    raw_cur = round(cur / 0.01)                         # 물리값 → raw (factor 0.01)
    data = (rpm.to_bytes(2, "little") +
            raw_cur.to_bytes(2, "little", signed=True) +
            bytes([temp, fault, 0, 0]))
    return " ".join(f"{x:02X}" for x in data)

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    for line in fin:
        if not line.strip() or line.startswith("#"):
            continue
        rpm, cur, temp, fault = line.split()
        fout.write(encode(int(rpm), float(cur), int(temp), int(fault)) + "\n")
