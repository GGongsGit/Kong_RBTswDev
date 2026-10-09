# joint_position_hold_pid.py
# - 단일 회전 관절을 PID로 목표 각도에 고정(위치 유지)
# - 중력/마찰/출력포화/anti-windup/미분LPF 포함
# - 그래프 및 간단 지표(정착시간, 오버슈트, IAE) 출력

import math
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# ---------------- PID Controller (D on measurement) ----------------
class PIDPosHold:
    """
    u = Kp*e + I - Kd * (y_dot_f)  (D on measurement, to avoid derivative kick)
    I_dot = Ki * e + Kw * (u_sat - u_unsat)  # anti-windup back-calculation
    y_dot_f: 1st-order LPF of measured derivative
    """
    def __init__(self, Kp, Ki, Kd, Ts, umin=-np.inf, umax=np.inf, D_tau=0.01, Kw=10.0):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.Ts = Ts
        self.umin, self.umax = umin, umax
        self.D_tau = D_tau  # derivative low-pass time constant
        self.Kw = Kw        # anti-windup back-calculation gain

        self.I = 0.0
        self.y_prev = 0.0
        self.y_dot_f = 0.0  # filtered derivative of measurement

    def step(self, r, y):
        e = r - y

        # derivative (on measurement): y_dot ≈ (y - y_prev)/Ts, then LPF
        y_dot = (y - self.y_prev)/self.Ts
        alpha = self.D_tau / (self.D_tau + self.Ts)  # 0~1, closer to 1 = heavier smoothing
        self.y_dot_f = alpha*self.y_dot_f + (1-alpha)*y_dot

        u_unsat = self.Kp*e + self.I - self.Kd*self.y_dot_f
        u = np.clip(u_unsat, self.umin, self.umax)

        # anti-windup back-calculation
        self.I += self.Ts*( self.Ki*e + self.Kw*(u - u_unsat) )

        self.y_prev = y
        return u, e

# ---------------- Metrics ----------------
@dataclass
class Metrics:
    settling_time: float
    overshoot_percent: float
    IAE: float

def compute_metrics(ts, r, y, e, band_ratio=0.02):
    ts = np.asarray(ts); r = np.asarray(r); y = np.asarray(y); e = np.asarray(e)
    Ts = ts[1] - ts[0] if len(ts) > 1 else 0.0
    r_final = r[-1]
    # 정착시간: 최종 기준 대비 ±2% 밴드를 이후 내내 유지하는 마지막 진입 시각
    if r_final == 0:
        band_abs = band_ratio
    else:
        band_abs = abs(r_final)*band_ratio
    cond = np.abs(y - r_final) <= band_abs
    st = math.nan
    for k in range(len(y)):
        if np.all(cond[k:]):
            st = ts[k]
            break
    # 오버슈트
    os_percent = 0.0
    if r_final != 0.0:
        y_max = float(np.max(y))
        os_percent = max(0.0, (y_max - r_final)/abs(r_final)*100.0)
    # IAE
    IAE = float(np.sum(np.abs(e)) * (Ts if Ts > 0 else 1.0))
    return Metrics(st, os_percent, IAE)

# ---------------- Plant (Single-Joint Pendulum-like) ----------------
class SingleJoint:
    """
    J*wdot + B*w + m*g*l*sin(theta) = Kt*u - tau_dist
    state: [theta, w]
    """
    def __init__(self, J=0.02, B=0.05, m=2.0, l=0.25, g=9.81, Kt=0.5):
        self.J, self.B, self.m, self.l, self.g, self.Kt = J, B, m, l, g, Kt
        self.theta = 0.0
        self.omega = 0.0

    def step(self, u, tau_dist, Ts):
        # dynamics
        tau_g = self.m*self.g*self.l*math.sin(self.theta)
        wdot = (self.Kt*u - tau_dist - self.B*self.omega - tau_g)/self.J
        self.omega += Ts*wdot
        self.theta += Ts*self.omega
        return self.theta, self.omega, tau_g

# ---------------- (Optional) Gravity Feedforward ----------------
def gravity_ff(m, g, l, theta):
    return m*g*l*math.sin(theta)

# ---------------- Main Simulation ----------------
def simulate_position_hold(
    # sim
    T_end=6.0, Ts=0.002,
    # target
    theta_ref_deg=30.0, ref_apply_time=0.2,
    # plant
    J=0.02, B=0.05, m=2.0, l=0.25, g=9.81, Kt=0.5,
    # controller
    Kp=18.0, Ki=60.0, Kd=1.2, D_tau=0.01, Kw=25.0,
    Umax=12.0,
    # options
    use_gravity_ff=True,
    disturbance_profile=lambda t: 0.0
):
    N = int(T_end/Ts)
    plant = SingleJoint(J=J, B=B, m=m, l=l, g=g, Kt=Kt)
    pid = PIDPosHold(Kp=Kp, Ki=Ki, Kd=Kd, Ts=Ts, D_tau=D_tau, Kw=Kw, umin=-Umax, umax=Umax)

    ts, rs, ys, ws, us, es, taus_g, taus_d = [], [], [], [], [], [], [], []

    for k in range(N):
        t = k*Ts
        r = math.radians(theta_ref_deg) if t >= ref_apply_time else 0.0
        y = plant.theta

        # 외란 토크(예: 부하 충격)
        tau_dist = disturbance_profile(t)

        # 중력 보상 feedforward(선택)
        u_ff = 0.0
        if use_gravity_ff:
            # FF는 제어입력 공간(u)로 환산: tau_g_ff / Kt
            tau_ff = gravity_ff(m, g, l, r)  # 기준각 기준 보상
            u_ff = tau_ff / Kt

        # PID (feedback)
        u_pid, e = pid.step(r, y)
        u = u_pid + u_ff
        u = np.clip(u, -Umax, Umax)  # 안전 차원에서 다시 한 번 클립

        theta, omega, tau_g = plant.step(u, tau_dist, Ts)

        ts.append(t); rs.append(r); ys.append(theta); ws.append(omega)
        us.append(u); es.append(e); taus_g.append(tau_g); taus_d.append(tau_dist)

    # 지표 계산(라디안→디그리 변환 후 오버슈트 해석이 직관적이지만, 표준 정의는 라디안 그대로도 무방)
    mtr = compute_metrics(np.array(ts), np.array(rs), np.array(ys), np.array(es), band_ratio=0.02)

    # 플롯
    fig, ax = plt.subplots(3, 1, figsize=(9, 6), sharex=True)
    ax[0].plot(ts, np.degrees(rs), label='ref [deg]')
    ax[0].plot(ts, np.degrees(ys), label='theta [deg]')
    ax[0].set_ylabel('Angle [deg]'); ax[0].legend(); ax[0].grid(True)

    ax[1].plot(ts, us, label='u (cmd)')
    ax[1].set_ylabel('Control'); ax[1].legend(); ax[1].grid(True)

    ax[2].plot(ts, taus_d, label='disturbance τd')
    ax[2].plot(ts, taus_g, label='gravity τg', alpha=0.7)
    ax[2].set_ylabel('Torque [N·m]'); ax[2].set_xlabel('Time [s]')
    ax[2].legend(); ax[2].grid(True)

    fig.suptitle('Single-Joint Position Hold with PID (anti-windup, D-filter, gravity FF)')
    plt.tight_layout()
    plt.show()

    print("\n=== 성능 지표 ===")
    print(f"정착시간 (s) : {mtr.settling_time:.4f}")
    print(f"오버슈트 (%) : {mtr.overshoot_percent:.2f}")
    print(f"IAE          : {mtr.IAE:.6f}")

# ---------------- Example Disturbance ----------------
def example_disturbance(t):
    # 2.5s ~ 2.8s 동안 0.6 N·m 외란
    if 2.5 <= t < 2.8:
        return 0.6
    return 0.0

if __name__ == "__main__":
    simulate_position_hold(
        # 시뮬레이션/목표
        T_end=6.0, Ts=0.002,
        theta_ref_deg=30.0, ref_apply_time=0.2,
        # 플랜트
        J=0.02, B=0.05, m=2.0, l=0.25, g=9.81, Kt=0.5,
        # PID 게인 (초기값, 필요시 조정)
        Kp=18.0, Ki=60.0, Kd=1.2, D_tau=0.01, Kw=25.0,
        Umax=12.0,
        use_gravity_ff=True,
        disturbance_profile=example_disturbance
    )
