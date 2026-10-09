import numpy as np

def cubic(q0, qf, v0, vf, t0, tf, dt):
    # θ(t) = a0 + a1·t + a2·t² + a3·t³  →  경계조건 4개로 AX = B
    A = np.array([[1, t0, t0**2,   t0**3],
                  [0, 1,  2*t0,  3*t0**2],
                  [1, tf, tf**2,   tf**3],
                  [0, 1,  2*tf,  3*tf**2]])
    B = np.array([q0, v0, qf, vf])
    a0, a1, a2, a3 = np.linalg.solve(A, B)

    t = np.arange(t0, tf + dt/2, dt)     # tf까지 포함 (dt/2로 부동소수 오차 방지)
    q   = a0 + a1*t + a2*t**2 + a3*t**3
    qd  = a1 + 2*a2*t + 3*a3*t**2
    qdd = 2*a2 + 6*a3*t
    return t, q, qd, qdd, (a0, a1, a2, a3)

t, q, qd, qdd, coef = cubic(np.pi/6, np.pi/2, 0, 0, 0, 0.5, 0.05)
print(np.round(coef, 4))      # [ 0.5236  0.  12.5664 -16.7552]
