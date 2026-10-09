import numpy as np
import matplotlib.pyplot as plt

P0 = np.array([0.0, 0.0])   # 시작점 (x0, y0)
P1 = np.array([0.7, 0.3])   # 도착점 (x1, y1)
delta = P1 - P0
L = np.linalg.norm(delta)
V = 0.2 # m/s

T = L / V

dt = 0.01
t_arr = np.arange(0, T+dt, dt)
s_arr = V * t_arr

x = P0[0] + (delta[0]/L) * s_arr
y = P0[1] + (delta[1]/L) * s_arr

vx = np.full_like(t_arr, V * delta[0]/L)
vy = np.full_like(t_arr, V * delta[1]/L)

fig, axs = plt.subplots(2, 2, figsize=(10, 7))

# 2D 경로
axs[0, 0].plot(x, y, label='2D Linear Path')
axs[0, 0].set_xlabel('x')
axs[0, 0].set_ylabel('y')
axs[0, 0].set_title('2D Path')
axs[0, 0].legend()
axs[0, 0].axis('equal')

# 위치
axs[0, 1].plot(t_arr, x, label='x(t)')
axs[0, 1].plot(t_arr, y, label='y(t)')
axs[0, 1].set_xlabel('Time (s)')
axs[0, 1].set_ylabel('Position')
axs[0, 1].set_title('Position vs Time')
axs[0, 1].legend()

# 속도
axs[1, 0].plot(t_arr, vx, label='vx')
axs[1, 0].plot(t_arr, vy, label='vy')
axs[1, 0].set_xlabel('Time (s)')
axs[1, 0].set_ylabel('Velocity')
axs[1, 0].set_title('Velocity vs Time')
axs[1, 0].legend()

# 가속도(항상 0)
axs[1, 1].plot(t_arr, np.zeros_like(t_arr), label='ax=0')
axs[1, 1].plot(t_arr, np.zeros_like(t_arr), label='ay=0')
axs[1, 1].set_xlabel('Time (s)')
axs[1, 1].set_ylabel('Acceleration')
axs[1, 1].set_title('Acceleration vs Time')
axs[1, 1].legend()

plt.tight_layout()
plt.show()
