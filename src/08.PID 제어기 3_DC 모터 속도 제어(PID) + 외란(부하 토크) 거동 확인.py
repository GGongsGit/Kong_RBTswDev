import numpy as np
import matplotlib.pyplot as plt

class PID:
    def __init__(self, Kp, Ki, Kd, Ts, umin=-np.inf, umax=np.inf, Td=0.005):
        self.Kp, self.Ki, self.Kd, self.Ts = Kp, Ki, Kd, Ts
        self.umin, self.umax = umin, umax
        self.I = 0.0
        self.e_prev = 0.0
        # small LPF on D
        self.Td = Td
        self.d_state = 0.0

    def step(self, e):
        alpha = self.Td / (self.Td + self.Ts)
        de = (e - self.e_prev)/self.Ts
        self.d_state = alpha*self.d_state + (1-alpha)*de

        u_unsat = self.Kp*e + self.I + self.Kd*self.d_state
        u = np.clip(u_unsat, self.umin, self.umax)
        # anti-windup
        self.I += self.Ki*self.Ts*e + (u - u_unsat)
        self.e_prev = e
        return u

J, B, Kt = 0.02, 0.02, 0.1
Ts = 0.001
N = int(3.0/Ts)

pid = PID(Kp=2.5, Ki=150.0, Kd=0.01, Ts=Ts, umin=-12.0, umax=12.0, Td=0.002)

w = 0.0
ts, wrs, ws, us, taus = [], [], [], [], []
for k in range(N):
    t = k*Ts
    wr = 50.0 if t >= 0.1 else 0.0  # target speed [rad/s]
    tau_L = 0.15 if (1.5 <= t < 1.8) else 0.0

    e = wr - w
    u = pid.step(e)

    # J wdot + B w = Kt u - tau_L  ->  wdot = (Kt u - tau_L - B w)/J
    wdot = (Kt*u - tau_L - B*w)/J
    w += Ts*wdot

    ts.append(t); wrs.append(wr); ws.append(w); us.append(u); taus.append(tau_L)

fig, ax = plt.subplots(3,1, figsize=(8,5), sharex=True)
ax[0].plot(ts, wrs, label='ref'); ax[0].plot(ts, ws, label='omega'); ax[0].legend(); ax[0].set_ylabel('rad/s')
ax[1].plot(ts, us, label='u[V]'); ax[1].legend(); ax[1].set_ylabel('V')
ax[2].plot(ts, taus, label='load torque'); ax[2].legend(); ax[2].set_ylabel('N·m'); ax[2].set_xlabel('Time [s]')
fig.suptitle('DC Motor Speed PID with Load Disturbance')
plt.tight_layout(); plt.show()
