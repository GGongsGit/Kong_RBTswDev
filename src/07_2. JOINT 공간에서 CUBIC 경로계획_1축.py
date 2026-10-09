import numpy as np
import matplotlib.pyplot as plt

def cubic_joint(t0, t1, theta0, theta1, v0, v1, dt):
    T = t1 - t0
    a0 = theta0
    a1 = v0
    a2 = (3*(theta1-theta0)/T**2) - (2*v0+v1)/T
    a3 = (-2*(theta1-theta0)/T**3) + (v0+v1)/T**2
    t = np.arange(t0, t1+dt, dt)
    theta = a0 + a1*(t-t0) + a2*(t-t0)**2 + a3*(t-t0)**3
    vel = a1 + 2*a2*(t-t0) + 3*a3*(t-t0)**2
    acc = 2*a2 + 6*a3*(t-t0)
    return t, theta, vel, acc

# 단일 Joint 예시: 시작/끝 위치와 속도
theta0 = 0.0     # 시작 위치 (rad)
theta1 = 1.0     # 목표 위치 (rad)
v0 = 0.0         # 시작 속도 (rad/s)
v1 = 0.0         # 종료 속도 (rad/s)
T_sync = 3.0     # 경로 총 시간 (초)

t, theta, vel, acc = cubic_joint(0, T_sync, theta0, theta1, v0, v1, 0.01)







fig, axs = plt.subplots(3, 1, figsize=(10, 10))

# 위치 그래프
axs[0].plot(t, theta, label='θ')
axs[0].set_xlabel("Time (s)")
axs[0].set_ylabel("Position (rad)")
axs[0].set_title("Joint Cubic Path")
axs[0].legend()

# 속도 그래프
axs[1].plot(t, vel, label='v')
axs[1].set_xlabel("Time (s)")
axs[1].set_ylabel("Velocity (rad/s)")
axs[1].set_title("Joint Cubic Velocity")
axs[1].legend()

# 가속도 그래프
axs[2].plot(t, acc, label='a')
axs[2].set_xlabel("Time (s)")
axs[2].set_ylabel("Acceleration (rad/s^2)")
axs[2].set_title("Joint Cubic Acceleration")
axs[2].legend()

plt.tight_layout()
plt.show()
