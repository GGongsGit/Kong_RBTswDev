# 2-2 예상문제 1 : 2링크 IK 두 해 (도달 불가 처리)
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q22_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q22_1_output.txt"
L1, L2 = 1.0, 0.8

def ik(x, y):
    r = np.hypot(x, y)
    if r > L1 + L2 or r < abs(L1 - L2):
        return None
    c2 = np.clip((x*x + y*y - L1*L1 - L2*L2) / (2*L1*L2), -1, 1)
    out = []
    for s in (+1, -1):
        t2 = s*np.arccos(c2)
        t1 = np.arctan2(y, x) - np.arctan2(L2*np.sin(t2), L1 + L2*np.cos(t2))
        out.append((round(np.degrees(t1), 2) + 0.0, round(np.degrees(t2), 2) + 0.0))   # -0.00 방지
    return out

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    fout.write("x y t1_a t2_a t1_b t2_b\n")
    for line in fin:
        if not line.strip():
            continue
        x, y = map(float, line.split())
        sol = ik(x, y)
        if sol is None:
            fout.write(f"{x} {y} UNREACHABLE\n")
        else:
            (a1, a2), (b1, b2) = sol
            fout.write(f"{x} {y} {a1:.2f} {a2:.2f} {b1:.2f} {b2:.2f}\n")
