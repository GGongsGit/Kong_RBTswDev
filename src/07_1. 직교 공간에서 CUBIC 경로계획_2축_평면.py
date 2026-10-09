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
x0, y0 = 0.0, 0.0
x1, y1 = 1.2, 0.8
vx0, vy0 = 0.0, 0.0
vx1, vy1 = 0.0, 0.0
t0, t1 = 0, 2.5
_, x, vx, ax = cubic_poly(t0, t1, x0, x1, vx0, vx1)
t, y, vy, ay = cubic_poly(t0, t1, y0, y1, vy0, vy1)

fig, axs = plt.subplots(2,2,figsize=(10,7))

# (1) 2D Trajectory
axs[0,0].plot(x, y)
axs[0,0].set_xlabel("x")
axs[0,0].set_ylabel("y")
axs[0,0].set_title("Cubic 2D trajectory")
axs[0,0].grid()

# (2) Position vs Time
axs[0,1].plot(t, x, label='x')
axs[0,1].plot(t, y, label='y')
axs[0,1].set_xlabel("Time (s)")
axs[0,1].set_ylabel("Position")
axs[0,1].legend()
axs[0,1].set_title("Position vs Time")
axs[0,1].grid()

# (3) Velocity vs Time
axs[1,0].plot(t, vx, label='vx')
axs[1,0].plot(t, vy, label='vy')
axs[1,0].set_xlabel("Time (s)")
axs[1,0].set_ylabel("Velocity")
axs[1,0].legend()
axs[1,0].set_title("Velocity vs Time")
axs[1,0].grid()

# (4) Acceleration vs Time
axs[1,1].plot(t, ax, label='ax')
axs[1,1].plot(t, ay, label='ay')
axs[1,1].set_xlabel("Time (s)")
axs[1,1].set_ylabel("Acceleration")
axs[1,1].legend()
axs[1,1].set_title("Acceleration vs Time")
axs[1,1].grid()

plt.tight_layout()
plt.show()