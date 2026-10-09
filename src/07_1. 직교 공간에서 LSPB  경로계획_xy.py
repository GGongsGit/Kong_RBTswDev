import numpy as np
import matplotlib.pyplot as plt

def lspb_profile(L, Vmax, amax, dt=0.001):
    # 1. 가감속 구간 시간
    t_a = Vmax / amax
    d_a = 0.5 * amax * t_a**2

    # 2. 등속구간 거리
    d_c = L - 2 * d_a

    if d_c >= 0: # 등속구간 존재
        t_c = d_c / Vmax
        T = 2 * t_a + t_c
        t_arr = np.arange(0, T+dt, dt)
        s = np.zeros_like(t_arr)
        v = np.zeros_like(t_arr)
        a = np.zeros_like(t_arr)
        for i, t in enumerate(t_arr):
            if t < t_a:
                s[i] = 0.5 * amax * t**2
                v[i] = amax * t
                a[i] = amax
            elif t < t_a + t_c:
                s[i] = d_a + Vmax * (t - t_a)
                v[i] = Vmax
                a[i] = 0
            else:
                tau = t - t_a - t_c
                s[i] = d_a + d_c + Vmax * tau - 0.5 * amax * tau**2
                v[i] = Vmax - amax * tau
                a[i] = -amax
    else: # 등속구간 없음 (피크속도만 오르고 바로 감속)
        Vpeak = np.sqrt(L * amax)
        t_a = Vpeak / amax
        T = 2 * t_a
        t_arr = np.arange(0, T+dt, dt)
        s = np.zeros_like(t_arr)
        v = np.zeros_like(t_arr)
        a = np.zeros_like(t_arr)
        for i, t in enumerate(t_arr):
            if t < t_a:
                s[i] = 0.5 * amax * t**2
                v[i] = amax * t
                a[i] = amax
            else:
                tau = t - t_a
                s[i] = 0.5 * Vpeak**2 / amax + Vpeak * tau - 0.5 * amax * tau**2
                v[i] = Vpeak - amax * tau
                a[i] = -amax
    return t_arr, s, v, a

# 2D 직선 경로 예시
P0 = np.array([0.0, 0.0])
P1 = np.array([0.0, 10.0])
delta = P1 - P0
L = np.linalg.norm(delta)

Vmax = 2
amax = 1.0

t, s, v, a = lspb_profile(L, Vmax, amax)

# 비율에 따른 실제 2D 궤적/속도/가속도
lambda_ = s / L  # 진행비율
x = P0[0] + lambda_ * delta[0]
y = P0[1] + lambda_ * delta[1]
vx = v * (delta[0]/L)
vy = v * (delta[1]/L)
ax = a * (delta[0]/L)
ay = a * (delta[1]/L)

fig, axs = plt.subplots(2,2,figsize=(10,7))
# 2D 경로
axs[0,0].plot(x,y, label='LSPB 2D path')
axs[0,0].set_xlabel('x')
axs[0,0].set_ylabel('y')
axs[0,0].set_title('LSPB 2D Path')
axs[0,0].legend()
axs[0,0].axis('equal')

# 위치
axs[0,1].plot(t, x, label='x(t)')
axs[0,1].plot(t, y, label='y(t)')
axs[0,1].set_xlabel('Time (s)')
axs[0,1].set_ylabel('Position')
axs[0,1].set_title('Position vs Time')
axs[0,1].legend()

# 속도
axs[1,0].plot(t, vx, label='vx(t)')
axs[1,0].plot(t, vy, label='vy(t)')
axs[1,0].set_xlabel('Time (s)')
axs[1,0].set_ylabel('Velocity')
axs[1,0].set_title('Velocity vs Time')
axs[1,0].legend()

# 가속도
axs[1,1].plot(t, ax, label='ax(t)')
axs[1,1].plot(t, ay, label='ay(t)')
axs[1,1].set_xlabel('Time (s)')
axs[1,1].set_ylabel('Acceleration')
axs[1,1].set_title('Acceleration vs Time')
axs[1,1].legend()

plt.tight_layout()
plt.show()
