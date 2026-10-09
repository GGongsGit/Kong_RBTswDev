# 2-2 예상문제 2 : IK 결과를 FK로 검산
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q22_2_input.txt"
L1, L2 = 1.0, 1.0

def ik(x, y, s):
    c2 = np.clip((x*x + y*y - L1*L1 - L2*L2) / (2*L1*L2), -1, 1)
    t2 = s*np.arccos(c2)
    t1 = np.arctan2(y, x) - np.arctan2(L2*np.sin(t2), L1 + L2*np.cos(t2))
    return t1, t2

def fk(t1, t2):
    return (L1*np.cos(t1) + L2*np.cos(t1 + t2),
            L1*np.sin(t1) + L2*np.sin(t1 + t2))

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        if not line.strip():
            continue
        x, y = map(float, line.split())
        errs = []
        for s in (+1, -1):
            xe, ye = fk(*ik(x, y, s))
            errs.append(np.hypot(xe - x, ye - y))
        status = "OK" if max(errs) < 1e-9 else "NG"
        print(f"({x}, {y})  max error = {max(errs):.1e}  {status}")
