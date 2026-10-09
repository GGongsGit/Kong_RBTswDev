import numpy as np
import matplotlib.pyplot as plt

class PID_Dfiltered:
    def __init__(self, Kp, Ki, Kd, Td=0.02, Ts=0.002, umin=-np.inf, umax=np.inf):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.Td, self.Ts = Td, Ts
        self.umin, self.umax = umin, umax
        self.I = 0.0
        self.e_prev = 0.0
        self.d_state = 0.0  # derivative filter state (first-order LPF)

    def step(self, e):
        # derivative with LPF: y_d[k] = alpha*y_d[k-1] + (1-alpha)*(e[k]-e[k-1])/Ts
        alpha = self.Td / (self.Td + self.Ts)
        de = (e - self.e_prev)/self.Ts
        self.d_state = alpha*self.d_state + (1-alpha)*de

        u_unsat = self.Kp*e + self.I + self.Kd*self.d_state
        u = np.clip(u_unsat, self.umin, self.umax)
        # anti-windup
        aw = (u - u_unsat)
        self.I += self.Ki*self.Ts*e + aw
        self.e_prev = e
        return u

# Plant params
m, c, k, Ku = 1.0, 0.6, 4.0, 1.0
Ts = 0.002
T_end = 6.0
N = int(T_end/Ts)

pid = PID_Dfiltered(Kp=60, Ki=40, Kd=4, Td=0.02, Ts=Ts, umin=-10, umax=10)

y = 0.0; ydot = 0.0
ts, ys, rs, us = [], [], [], []
for k in range(N):
    t = k*Ts
    r = 1.0 if t >= 0.2 else 0.0
    e = r - y
    u = pid.step(e)

    # m ydd + c ydot + k y = Ku u  -> ydd = (Ku u - c ydot - k y)/m
    ydd = (Ku*u - c*ydot - k*y)/m
    ydot += Ts*ydd
    y += Ts*ydot

    ts.append(t); rs.append(r); ys.append(y); us.append(u)

plt.figure(figsize=(8,4))
plt.subplot(2,1,1); plt.plot(ts, rs, label='ref'); plt.plot(ts, ys, label='y'); plt.legend(); plt.ylabel('Position')
plt.subplot(2,1,2); plt.plot(ts, us, label='u'); plt.legend(); plt.ylabel('Control'); plt.xlabel('Time [s]')
plt.suptitle('Mass-Spring-Damper with PID (LPF-D, anti-windup)')
plt.tight_layout(); plt.show()
