import numpy as np

def lspb(q0, qf, tf, a, n=1000):
    # Δq = a·tb·(tf - tb)  →  tb² - tf·tb + Δq/a = 0
    dq = qf - q0
    disc = tf**2 - 4*abs(dq)/a
    if disc < 0:
        raise ValueError(f"가속도 부족: a ≥ {4*abs(dq)/tf**2:.4f} 필요")
    tb = (tf - np.sqrt(disc)) / 2          # 작은 근
    s  = np.sign(dq)
    v  = s*a*tb                             # 등속 구간 속도

    t = np.linspace(0, tf, n)
    q = np.empty_like(t); qd = np.empty_like(t); qdd = np.empty_like(t)
    m1 = t <= tb
    m3 = t >= tf - tb
    m2 = ~(m1 | m3)
    q[m1] = q0 + 0.5*s*a*t[m1]**2;          qd[m1] = s*a*t[m1];        qdd[m1] = s*a
    q[m2] = q0 + v*(t[m2] - tb/2);          qd[m2] = v;                qdd[m2] = 0
    q[m3] = qf - 0.5*s*a*(tf - t[m3])**2;   qd[m3] = s*a*(tf - t[m3]); qdd[m3] = -s*a
    return t, q, qd, qdd, tb

t, q, qd, qdd, tb = lspb(np.pi/6, np.pi/2, 2.0, 2.0)
print(f"tb = {tb:.4f} s, q(tf) = {q[-1]:.4f}")   # tb = 0.3098 s, q(tf) = 1.5708
