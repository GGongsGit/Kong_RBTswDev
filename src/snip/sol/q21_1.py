# 2-1 예상문제 1 : 3링크 FK
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q21_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q21_1_output.txt"
L = [0.5, 0.4, 0.3]

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    for line in fin:
        if not line.strip():
            continue
        th = np.deg2rad([float(v) for v in line.split()])
        cum = np.cumsum(th)                       # θ1, θ1+θ2, θ1+θ2+θ3
        x = np.sum(np.array(L) * np.cos(cum))
        y = np.sum(np.array(L) * np.sin(cum))
        fout.write(f"{x:.2f} {y:.2f}\n")
