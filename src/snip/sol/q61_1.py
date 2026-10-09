# 7-1 예상문제 1 : CAN 로그에서 ID 0x200만 골라 디코딩 → CSV
import csv

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q61_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q61_1_output.csv"

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, \
     open(OUT_FILE, "w", newline="", encoding="utf-8-sig") as fout:
    w = csv.writer(fout)
    w.writerow(["time", "rpm", "current(A)", "temp(C)", "fault"])
    for line in fin:
        p = line.split()
        if len(p) != 10 or int(p[1], 16) != 0x200:
            continue
        b = bytes(int(x, 16) for x in p[2:])
        rpm  = int.from_bytes(b[0:2], "little")
        cur  = int.from_bytes(b[2:4], "little", signed=True) * 0.01
        w.writerow([p[0], rpm, f"{cur:.2f}", b[4], b[5]])
