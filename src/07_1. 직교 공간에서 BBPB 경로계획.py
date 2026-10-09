import numpy as np
import matplotlib.pyplot as plt
plt.rc("font", family="Gulim")

def bbpb_scalar_profile(L, a_max, j_max, dt=0.001):
    t_j = a_max / j_max
    d_j = (1/6) * a_max**3 / j_max**2
    v_j = 0.5 * a_max**2 / j_max

    D_ = L - 2 * d_j
    discriminant = v_j**2 + a_max * D_
    if discriminant < 0:
        raise ValueError("거리가 너무 짧습니다!")
    t_a = (-v_j + np.sqrt(discriminant)) / a_max
    T = 2*t_j + 2*t_a
    t = np.arange(0, T, dt)

    s = np.zeros_like(t)  # 위치(경로비율)
    v_s = np.zeros_like(t)
    a_s = np.zeros_like(t)
    
    t0 = t_j
    t1 = t_j + t_a
    t2 = T - t_j - t_a
    t3 = T - t_j
    t4 = T

    for i, ti in enumerate(t):
        if ti <= t0:
            a_s[i] = j_max * ti
            v_s[i] = 0.5 * j_max * ti**2
            s[i] = (1/6)* j_max * ti**3 / L
        elif ti <= t1:
            a_s[i] = a_max
            v_s[i] = v_j + a_max * (ti-t0)
            s[i] = (d_j + v_j*(ti-t0) + 0.5*a_max*(ti-t0)**2) / L
        elif ti <= t3:
            ta_ = ti - t2
            a_s[i] = a_max - j_max * ta_
            v_s[i] = v_j + a_max * t_a - 0.5 * j_max * ta_**2
            s[i] = (L - d_j - v_j*(t4-ti) - 0.5*a_max*(t4-ti)**2) / L
        else:
            ta_ = t4 - ti
            a_s[i] = j_max * ta_
            v_s[i] = 0.5 * j_max * ta_**2
            s[i] = (L - (1/6)*j_max*ta_**3) / L
    return t, s, v_s, a_s, T

# 2D 경로 정보
P0 = np.array([0.0, 0.0])
P1 = np.array([0.7, 0.3])
delta = P1 - P0
L = np.linalg.norm(delta)

a_max = 2.0
j_max = 8.0

t, s, v_s, a_s, T = bbpb_scalar_profile(L, a_max, j_max)

x = P0[0] + s * delta[0]
y = P0[1] + s * delta[1]
vx = v_s * (delta[0]/L)
vy = v_s * (delta[1]/L)

plt.figure(figsize=(10,6))
plt.subplot(221)
plt.plot(x, y)
plt.xlabel('x')
plt.ylabel('y')
plt.title('2D BBPB 경로')

plt.subplot(222)
plt.plot(t, x, label='x')
plt.plot(t, y, label='y')
plt.xlabel('Time (s)')
plt.ylabel('Position')
plt.legend()

plt.subplot(223)
plt.plot(t, vx, label='vx')
plt.plot(t, vy, label='vy')
plt.xlabel('Time (s)')
plt.ylabel('Velocity')
plt.legend()

plt.subplot(224)
plt.plot(t, a_s*(delta[0]/L), label='ax')
plt.plot(t, a_s*(delta[1]/L), label='ay')
plt.xlabel('Time (s)')
plt.ylabel('Acceleration')
plt.legend()

plt.tight_layout()
plt.show()
