# 8-2 예상문제 2 : 월드 좌표(m) → 지도 셀 (열, 행)
import math

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q72_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q72_2_output.txt"
RES, OX, OY, W, H = 0.05, -1.00, -2.00, 100, 80

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    fout.write("x y col row inside\n")
    for line in fin:
        if not line.strip() or line.startswith("#"):
            continue
        x, y = map(float, line.split())
        col = math.floor((x - OX) / RES + 1e-9)          # 내림 (음수도 올바르게)
        row = math.floor((y - OY) / RES + 1e-9)
        inside = 0 <= col < W and 0 <= row < H
        fout.write(f"{x} {y} {col} {row} {'YES' if inside else 'NO'}\n")
