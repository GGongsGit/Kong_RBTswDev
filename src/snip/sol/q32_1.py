# 3-2 예상문제 1 : LSPB 궤적 값
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q32_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q32_1_output.txt"

prm = {}
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        if line.strip():
            k, v = line.split()
            prm[k] = float(v)
q0, qf = np.deg2rad(prm["q0_deg"]), np.deg2rad(prm["qf_deg"])
tf, a = prm["tf"], prm["a_max"]

dq = qf - q0
tb = (tf - np.sqrt(tf**2 - 4*dq/a)) / 2          # tb² - tf·tb + Δq/a = 0 의 작은 근
v = a*tb

def q_at(t):
    if t <= tb:
        return q0 + 0.5*a*t**2
    if t >= tf - tb:
        return qf - 0.5*a*(tf - t)**2
    return q0 + v*(t - tb/2)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(f"tb {tb:.4f}\nv_max {v:.4f}\n")
    f.write("t q(deg)\n")
    for t in np.arange(0, tf + 0.25, 0.5):
        f.write(f"{t:.1f} {np.degrees(q_at(t)):.3f}\n")
