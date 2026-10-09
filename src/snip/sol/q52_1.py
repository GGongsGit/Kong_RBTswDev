# 6-1 예상문제 1 : 2링크 역동역학 τ = M·q̈ + C + G
import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q52_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q52_1_output.txt"
m1, m2, l1, lc1, lc2, I1, I2, g = 2.0, 1.5, 1.0, 0.5, 0.4, 0.05, 0.02, 9.81

def tau(q, dq, ddq):
    q1, q2 = q; dq1, dq2 = dq
    c2, s2 = np.cos(q2), np.sin(q2)
    M = np.array([[I1 + I2 + m1*lc1**2 + m2*(l1**2 + lc2**2 + 2*l1*lc2*c2), I2 + m2*(lc2**2 + l1*lc2*c2)],
                  [I2 + m2*(lc2**2 + l1*lc2*c2),                             I2 + m2*lc2**2]])
    h = m2*l1*lc2*s2
    C = np.array([-2*h*dq1*dq2 - h*dq2**2, h*dq1**2])
    G = np.array([(m1*lc1 + m2*l1)*g*np.cos(q1) + m2*lc2*g*np.cos(q1 + q2),
                  m2*lc2*g*np.cos(q1 + q2)])
    return M @ ddq + C + G

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    fout.write("tau1(Nm) tau2(Nm)\n")
    for line in fin:
        if not line.strip() or line.startswith("#"):
            continue
        v = [float(s) for s in line.split()]
        t = tau(np.deg2rad(v[0:2]), np.array(v[2:4]), np.array(v[4:6]))
        fout.write(f"{t[0] + 0.0:.3f} {t[1] + 0.0:.3f}\n")
