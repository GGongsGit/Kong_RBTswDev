import numpy as np

def bbpb(q0, qf, tf, n=1000):
    # 등속 구간 없음: tb = tf/2, 가속도는 a = 4·Δq / tf² 로 '정해진다'
    tb = tf/2
    a  = 4*(qf - q0)/tf**2
    t  = np.linspace(0, tf, n)
    up = t <= tb
    q  = np.where(up, q0 + 0.5*a*t**2, qf - 0.5*a*(tf - t)**2)
    qd = np.where(up, a*t, a*(tf - t))
    qdd = np.where(up, a, -a)
    return t, q, qd, qdd, a

t, q, qd, qdd, a = bbpb(np.pi/6, np.pi/2, 2.0)
print(f"a = {a:.4f}, q(tf) = {q[-1]:.4f}")       # a = 1.0472, q(tf) = 1.5708
