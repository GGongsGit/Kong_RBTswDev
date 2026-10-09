# 2-1 예상문제 2 : 2링크 관절 위치 + 원점 거리
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q21_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q21_2_output.txt"
L1, L2 = 0.85, 0.65

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    fout.write("x1 y1 x2 y2 r\n")
    for line in fin:
        if not line.strip():
            continue
        t1, t2 = np.deg2rad([float(v) for v in line.split()])
        x1, y1 = L1*np.cos(t1), L1*np.sin(t1)
        x2, y2 = x1 + L2*np.cos(t1 + t2), y1 + L2*np.sin(t1 + t2)
        fout.write(f"{x1:.4f} {y1:.4f} {x2:.4f} {y2:.4f} {np.hypot(x2, y2):.4f}\n")
