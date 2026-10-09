import numpy as np
import matplotlib.pyplot as plt

class PI:
    def __init__(self, Kp, Ki, umin=-np.inf, umax=np.inf, Ts=0.01):
        self.Kp, self.Ki, self.Ts = Kp, Ki, Ts
        self.umin, self.umax = umin, umax
        self.I = 0.0  # integrator state

    def step(self, e, y_dot_like=None):
        # 기본 PI
        u_unsat = self.Kp*e + self.I
        # 포화
        u = np.clip(u_unsat, self.umin, self.umax)
        # Anti-windup (clamping)
        aw = (u - u_unsat)
        self.I += (self.Ki*self.Ts)*e + aw  # aw로 적분 폭주 방지
        return u

# 1차 시스템: y_dot = (-1/τ)*y + (K/τ)*u
K, tau = 1.0, 2.0
Ts = 0.01
T_end = 10.0
N = int(T_end/Ts)

ctrl = PI(Kp=1.2, Ki=0.8, umin=-3.0, umax=3.0, Ts=Ts)

y = 0.0
ys, us, rs, ts = [], [], [], []
for k in range(N):
    t = k*Ts
    r = 1.0 if t >= 0.5 else 0.0  # step at 0.5s
    e = r - y
    u = ctrl.step(e)

    # plant integration (Euler)
    y_dot = (-1.0/tau)*y + (K/tau)*u
    y += Ts*y_dot

    ts.append(t); rs.append(r); ys.append(y); us.append(u)

plt.figure(figsize=(8,4))
plt.subplot(2,1,1); plt.plot(ts, rs, label='ref'); plt.plot(ts, ys, label='y'); plt.legend(); plt.ylabel('Output')
plt.subplot(2,1,2); plt.plot(ts, us, label='u'); plt.legend(); plt.ylabel('Control'); plt.xlabel('Time [s]')
plt.suptitle('First-Order Plant with PI (anti-windup)')
plt.tight_layout(); plt.show()
