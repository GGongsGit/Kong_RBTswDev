# 3-1 예상문제 1 : CUBIC 궤적 (v0 = vf = 0) → CSV
import csv
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q31_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q31_1_output.csv"

prm = {}
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        if line.strip():
            k, v = line.split()
            prm[k] = float(v)

q0, qf = np.deg2rad(prm["q0_deg"]), np.deg2rad(prm["qf_deg"])
tf, dt = prm["tf"], prm["dt"]
A = np.array([[1, 0, 0, 0], [0, 1, 0, 0],
              [1, tf, tf**2, tf**3], [0, 1, 2*tf, 3*tf**2]])
a0, a1, a2, a3 = np.linalg.solve(A, [q0, 0, qf, 0])

t = np.arange(0, tf + dt/2, dt)
q   = a0 + a1*t + a2*t**2 + a3*t**3
qd  = a1 + 2*a2*t + 3*a3*t**2
qdd = 2*a2 + 6*a3*t

with open(OUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["time(s)", "pos(deg)", "vel(deg/s)", "acc(deg/s^2)"])
    for i in range(len(t)):
        w.writerow([f"{t[i]:.1f}"] + [f"{round(np.degrees(v), 3) + 0.0:.3f}"     # -0.000 방지
                                      for v in (q[i], qd[i], qdd[i])])
print(f"a2 = {a2:.5f}, a3 = {a3:.5f} (rad)")
