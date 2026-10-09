# 2-3 예상문제 2 : 원하는 말단 속도 → 관절 속도 (특이점 검사)
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q23_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q23_2_output.txt"
L1, L2 = 1.0, 1.0
EPS = 1e-3

def J(t1, t2):
    return np.array([[-L1*np.sin(t1) - L2*np.sin(t1+t2), -L2*np.sin(t1+t2)],
                     [ L1*np.cos(t1) + L2*np.cos(t1+t2),  L2*np.cos(t1+t2)]])

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    fout.write("dth1 dth2\n")
    for line in fin:
        if not line.strip():
            continue
        d1, d2, vx, vy = map(float, line.split())
        Jm = J(np.deg2rad(d1), np.deg2rad(d2))
        if abs(np.linalg.det(Jm)) < EPS:
            fout.write("SINGULAR\n")
            continue
        w = np.linalg.solve(Jm, [vx, vy])
        fout.write(f"{w[0]:.4f} {w[1]:.4f}\n")
