import numpy as np
import matplotlib.pyplot as plt

def cubic_joint(t0, t1, theta0, theta1, v0, v1, dt=0.01):
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

# 예시: 3 Joint, 속도 0에서 시작/종료 (보통 모션 플래닝)
theta0 = [0.0, 1.0, -0.7]
theta1 = [1.0, 0.2, 0.8]
v0 = [0.0, 0.0, 0.0]
v1 = [0.0, 0.0, 0.0]
T_sync = 3.0    # 모든 관절 동기화 시간

theta_arrs = []
v_arrs = []
a_arrs = []
for i in range(3):
    t, theta, vel, acc = cubic_joint(0, T_sync, theta0[i], theta1[i], v0[i], v1[i])
    theta_arrs.append(theta)
    v_arrs.append(vel)
    a_arrs.append(acc)

t = np.arange(0, T_sync+0.01, 0.01)

fig, axs = plt.subplots(3, 1, figsize=(10, 10))

# 위치 그래프
axs[0].plot(t, theta_arrs[0], label='θ₁')
axs[0].plot(t, theta_arrs[1], label='θ₂')
axs[0].plot(t, theta_arrs[2], label='θ₃')
axs[0].set_xlabel("Time (s)")
axs[0].set_ylabel("Position (rad)")
axs[0].set_title("Joint Cubic Path")
axs[0].legend()

# 속도 그래프
axs[1].plot(t, v_arrs[0], label='v₁')
axs[1].plot(t, v_arrs[1], label='v₂')
axs[1].plot(t, v_arrs[2], label='v₃')
axs[1].set_xlabel("Time (s)")
axs[1].set_ylabel("Velocity (rad/s)")
axs[1].set_title("Joint Cubic Velocity")
axs[1].legend()

# 가속도 그래프
axs[2].plot(t, a_arrs[0], label='a₁')
axs[2].plot(t, a_arrs[1], label='a₂')
axs[2].plot(t, a_arrs[2], label='a₃')
axs[2].set_xlabel("Time (s)")
axs[2].set_ylabel("Acceleration (rad/s^2)")
axs[2].set_title("Joint Cubic Acceleration")
axs[2].legend()

plt.tight_layout()
plt.show()
