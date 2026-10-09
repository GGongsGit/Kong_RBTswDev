import numpy as np
import matplotlib.pyplot as plt

def bbpb_joint(theta0, theta1, amax, jmax, dt=0.001):
    D = abs(theta1 - theta0)
    sgn = np.sign(theta1 - theta0)
    t_j = amax / jmax
    d_j = (1/6)*amax**3/jmax**2
    v_j = 0.5*amax**2/jmax

    D_ = D - 2*d_j
    discriminant = v_j**2 + amax*D_
    if discriminant < 0:
        raise ValueError("거리가 너무 짧습니다.")
    t_a = (-v_j + np.sqrt(discriminant))/amax
    T = 2*t_j + 2*t_a
    t_arr = np.arange(0, T+dt, dt)
    theta = np.zeros_like(t_arr)
    v = np.zeros_like(t_arr)
    a = np.zeros_like(t_arr)

    # 구간 경계
    t0 = t_j
    t1 = t_j + t_a
    t2 = T - t_j - t_a
    t3 = T - t_j
    t4 = T

    for i, ti in enumerate(t_arr):
        if ti <= t0:
            a[i] = jmax * ti * sgn
            v[i] = 0.5 * jmax * ti**2 * sgn
            theta[i] = theta0 + (1/6)*jmax*ti**3*sgn
        elif ti <= t1:
            a[i] = amax * sgn
            v[i] = v_j*sgn + amax*(ti-t0)*sgn
            theta[i] = theta0 + d_j*sgn + v_j*(ti-t0)*sgn + 0.5*amax*(ti-t0)**2*sgn
        elif ti <= t3:
            ta_ = ti - t2
            a[i] = amax*sgn - jmax*ta_*sgn
            v[i] = v_j*sgn + amax*t_a*sgn - 0.5*jmax*ta_**2*sgn
            theta[i] = theta1 - d_j*sgn - v_j*(t4-ti)*sgn - 0.5*amax*(t4-ti)**2*sgn
        else:
            ta_ = t4 - ti
            a[i] = jmax*ta_*sgn
            v[i] = 0.5*jmax*ta_**2*sgn
            theta[i] = theta1 - (1/6)*jmax*ta_**3*sgn
    return t_arr, theta, v, a

# 예제 사용
theta0, theta1 = 0.0, 1.2             # rad
amax, jmax = 1.8, 7.0                 # rad/s^2, rad/s^3

t, th, vel, acc = bbpb_joint(theta0, theta1, amax, jmax)

plt.figure(figsize=(10,8))
plt.subplot(311)
plt.plot(t, th)
plt.xlabel('time (s)')
plt.ylabel('theta (rad)')
plt.title('Joint Position (S-Curve BBPB)')

plt.subplot(312)
plt.plot(t, vel)
plt.xlabel('time (s)')
plt.ylabel('velocity (rad/s)')
plt.title('Joint Velocity')

plt.subplot(313)
plt.plot(t, acc)
plt.xlabel('time (s)')
plt.ylabel('acceleration (rad/s^2)')
plt.title('Joint Acceleration')

plt.tight_layout()
plt.show()
