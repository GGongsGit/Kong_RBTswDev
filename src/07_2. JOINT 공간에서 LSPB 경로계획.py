import numpy as np
import matplotlib.pyplot as plt

def lspb_joint(theta0, theta1, vmax, amax, dt=0.001):
    d_theta = theta1 - theta0
    sgn = np.sign(d_theta)
    d_theta = abs(d_theta)
    t_a = vmax / amax
    d_a = 0.5 * amax * t_a**2
    d_c = d_theta - 2 * d_a
    if d_c >= 0:
        t_c = d_c / vmax
        T = 2 * t_a + t_c
        t_arr = np.arange(0, T+dt, dt)
        theta = np.zeros_like(t_arr)
        v = np.zeros_like(t_arr)
        a = np.zeros_like(t_arr)
        for i, t in enumerate(t_arr):
            if t < t_a:
                theta[i] = theta0 + 0.5 * amax * t**2 * sgn
                v[i] = amax * t * sgn
                a[i] = amax * sgn
            elif t < t_a + t_c:
                theta[i] = theta0 + d_a * sgn + vmax * (t-t_a) * sgn
                v[i] = vmax * sgn
                a[i] = 0
            else:
                tau = t - t_a - t_c
                theta[i] = theta1 - 0.5 * amax * (T-t)**2 * sgn
                v[i] = vmax * sgn - amax * tau * sgn
                a[i] = -amax * sgn
    else:
        vmax_peak = np.sqrt(d_theta * amax)
        t_a = vmax_peak / amax
        T = 2 * t_a
        t_arr = np.arange(0, T+dt, dt)
        theta = np.zeros_like(t_arr)
        v = np.zeros_like(t_arr)
        a = np.zeros_like(t_arr)
        for i, t in enumerate(t_arr):
            if t < t_a:
                theta[i] = theta0 + 0.5 * amax * t**2 * sgn
                v[i] = amax * t * sgn
                a[i] = amax * sgn
            else:
                tau = t - t_a
                theta[i] = theta0 + 0.5 * vmax_peak**2 / amax * sgn + vmax_peak * tau * sgn - 0.5 * amax * tau**2 * sgn
                v[i] = vmax_peak * sgn - amax * tau * sgn
                a[i] = -amax * sgn
    return t_arr, theta, v, a, T

# ---------- 수정된 리스트 초기화 부분 ----------
theta0_list = [0, 1, -0.5]
theta1_list = [1, 0.2, 1.3]
vmax_list  = [0.7, 0.5, 0.4]
amax_list  = [1.2, 0.9, 0.6]

T_list = []
t_arrs = []
theta_arrs = []
v_arrs = []
a_arrs = []
for i in range(3):
    t, theta, v, a, T = lspb_joint(theta0_list[i], theta1_list[i], vmax_list[i], amax_list[i])
    T_list.append(T)
    t_arrs.append(t)
    theta_arrs.append(theta)
    v_arrs.append(v)
    a_arrs.append(a)

# 동기화하기
T_sync = max(T_list)
t_sync = np.arange(0, T_sync, 0.001)
theta_sync = []
v_sync = []
a_sync = []
for i in range(3):
    s = np.linspace(0, 1, len(t_arrs[i]))
    s_sync = np.linspace(0, 1, len(t_sync))
    th = np.interp(s_sync, s, theta_arrs[i])
    vv = np.interp(s_sync, s, v_arrs[i])
    aa = np.interp(s_sync, s, a_arrs[i])
    theta_sync.append(th)
    v_sync.append(vv)
    a_sync.append(aa)

fig, axs = plt.subplots(2,2,figsize=(12,8))

axs[0,0].plot(t_sync, theta_sync[0], label='θ₁')
axs[0,0].plot(t_sync, theta_sync[1], label='θ₂')
axs[0,0].plot(t_sync, theta_sync[2], label='θ₃')
axs[0,0].set_xlabel('Time (s)')
axs[0,0].set_ylabel('Position (rad)')
axs[0,0].set_title('Joint Position')
axs[0,0].legend()

axs[0,1].plot(t_sync, v_sync[0], label='v₁')
axs[0,1].plot(t_sync, v_sync[1], label='v₂')
axs[0,1].plot(t_sync, v_sync[2], label='v₃')
axs[0,1].set_xlabel('Time (s)')
axs[0,1].set_ylabel('Velocity (rad/s)')
axs[0,1].set_title('Joint Velocity')
axs[0,1].legend()

axs[1,0].plot(t_sync, a_sync[0], label='a₁')
axs[1,0].plot(t_sync, a_sync[1], label='a₂')
axs[1,0].plot(t_sync, a_sync[2], label='a₃')
axs[1,0].set_xlabel('Time (s)')
axs[1,0].set_ylabel('Acceleration (rad/s²)')
axs[1,0].set_title('Joint Acceleration')
axs[1,0].legend()

axs[1,1].axis('off')
plt.tight_layout()
plt.show()
