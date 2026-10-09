# 2-3 예상문제 1 : 관절 속도 → 말단 선속도
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q23_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q23_1_output.txt"
L1, L2 = 1.0, 1.0

def J(t1, t2):
    return np.array([[-L1*np.sin(t1) - L2*np.sin(t1+t2), -L2*np.sin(t1+t2)],
                     [ L1*np.cos(t1) + L2*np.cos(t1+t2),  L2*np.cos(t1+t2)]])

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    fout.write("vx vy |v|\n")
    for line in fin:
        if not line.strip():
            continue
        d1, d2, w1, w2 = map(float, line.split())   # θ1, θ2 (deg), θ̇1, θ̇2 (rad/s)
        v = J(np.deg2rad(d1), np.deg2rad(d2)) @ np.array([w1, w2])
        fout.write(f"{v[0]:.4f} {v[1]:.4f} {np.linalg.norm(v):.4f}\n")
