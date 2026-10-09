import numpy as np
import matplotlib.pyplot as plt

theta0 = [0.0, 1.2, -0.7]    # 시작 각도 (rad)
theta1 = [1.0, 0.8,  0.9]    # 목표 각도 (rad)
V_limit = [0.6, 0.4, 0.5]    # 각 관절 최대속도 (rad/s)

D = [t1-t0 for t0, t1 in zip(theta0, theta1)]
T_list = [abs(d)/V for d, V in zip(D, V_limit)]
T_sync = max(T_list)         # 가장 오래 걸리는 시간

dt = 0.01
t = np.arange(0, T_sync+dt, dt)

theta_profiles = []
v_profiles = []
for i in range(3):
    theta_traj = theta0[i] + (t/T_sync)*(theta1[i] - theta0[i])
    v_traj = (theta1[i] - theta0[i])/T_sync * np.ones_like(t)
    theta_profiles.append(theta_traj)
    v_profiles.append(v_traj)

fig, axs = plt.subplots(2,1, figsize=(10,6))
axs[0].plot(t, theta_profiles[0], label='θ₁')
axs[0].plot(t, theta_profiles[1], label='θ₂')
axs[0].plot(t, theta_profiles[2], label='θ₃')
axs[0].set_ylabel("Joint Position (rad)")
axs[0].set_xlabel("Time (s)")
axs[0].legend()
axs[0].set_title("JOINT-space Linear (Uniform) Path")

axs[1].plot(t, v_profiles[0], label='v₁')
axs[1].plot(t, v_profiles[1], label='v₂')
axs[1].plot(t, v_profiles[2], label='v₃')
axs[1].set_ylabel("Velocity (rad/s)")
axs[1].set_xlabel("Time (s)")
axs[1].legend()
axs[1].set_title("JOINT velocity")

plt.tight_layout()
plt.show()
