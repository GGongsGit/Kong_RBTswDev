import numpy as np
import matplotlib.pyplot as plt

def cubic_poly(t0, t1, q0, q1, v0, v1, dt=0.01):
    T = t1 - t0
    a0 = q0
    a1 = v0
    a2 = (3*(q1-q0)/T**2) - (2*v0+v1)/T
    a3 = (-2*(q1-q0)/T**3) + (v0+v1)/T**2
    t = np.arange(t0, t1+dt, dt)
    q = a0 + a1*(t-t0) + a2*(t-t0)**2 + a3*(t-t0)**3
    v = a1 + 2*a2*(t-t0) + 3*a3*(t-t0)**2
    a = 2*a2 + 6*a3*(t-t0)
    return t, q, v, a

# 초기 위치/속도 (예시: 드론, 로봇 등)

x0 = 0.0
x1 = 1.2
vx0 = 0.0
vx1 = 0.0
t0, t1 = 0, 2.5

t, x, vx, ax = cubic_poly(t0, t1, x0, x1, vx0, vx1)


fig, axs = plt.subplots(2,2,figsize=(10,7))
# 2D 궤적 (xy평면)
axs[0,0].plot(x)
axs[0,0].set_xlabel("x")
axs[0,0].set_title("Cubic 2D trajectory")
axs[0,0].grid()

# 시간-위치
axs[0,1].plot(t, x, label='x')
axs[0,1].set_xlabel("time (s)")
axs[0,1].set_ylabel("Position")
axs[0,1].legend()
axs[0,1].set_title("Position vs time")

# 시간-속도
axs[1,0].plot(t, vx, label='vx')
axs[1,0].set_xlabel("time (s)")
axs[1,0].set_ylabel("Velocity")
axs[1,0].legend()
axs[1,0].set_title("Velocity vs time")

# 시간-가속도
axs[1,1].plot(t, ax, label='ax')
axs[1,1].set_xlabel("time (s)")
axs[1,1].set_ylabel("Acceleration")
axs[1,1].legend()
axs[1,1].set_title("Acceleration vs time")

plt.tight_layout()
plt.show()
