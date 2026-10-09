# pid_metrics_logger.py
# - 3가지 케이스(1차 PI / 2차 PID / DC모터 속도 PID) 시뮬레이션
# - CSV 로깅: t,r,y,u,e,(disturbance)
# - 성능지표 자동 계산: Settling time(±2%), Overshoot(%), IAE

import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# ---------- 공통 유틸 ----------
def write_csv(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def step_change_index(ref):
    # 첫 단계 변화 시점을 찾는다(초기값과 다른 값이 등장하는 첫 샘플)
    r0 = ref[0]
    for i, r in enumerate(ref):
        if r != r0:
            return i
    return 0

@dataclass
class Metrics:
    settling_time: float
    overshoot_percent: float
    IAE: float

def compute_metrics(ts, r, y, e, band_ratio=0.02):
    """표준 정의 기반 지표 계산.
    - Settling time: 최종 기준값 r_f 대비 ±band_ratio 안에 들어가 '그 이후 내내' 유지되는 첫 시각
    - Overshoot: (max(y)-r_f)/|r_f| * 100 [%], 단 r_f != 0일 때만
    - IAE: sum(|e|)*Ts
    """
    ts = np.asarray(ts); r = np.asarray(r); y = np.asarray(y); e = np.asarray(e)
    Ts = ts[1] - ts[0] if len(ts) > 1 else 0.0

    # 분석은 최종 기준값 기준
    r_f = r[-1]
    # 단계가 있는 경우, 단계 이후 구간만 분석(오버슈트 계산에 과도기만 반영되도록)
    k_step = step_change_index(r)
    y_post = y[k_step:]
    ts_post = ts[k_step:]

    # Settling time (±2% band)
    st = math.nan
    if r_f == 0:
        # r_f == 0인 특수 상황: 절대 밴드 |y| <= band_ratio*1 (==0.02)로 판단
        band_abs = band_ratio
        cond = np.abs(y - r_f) <= band_abs
    else:
        band_abs = abs(r_f) * band_ratio
        cond = np.abs(y - r_f) <= band_abs

    # "그 이후 내내" 만족하는 마지막 진입 시각
    idx = None
    for k in range(len(y)):
        if np.all(cond[k:]):
            idx = k
            break
    if idx is not None:
        st = ts[idx] - ts[k_step]  # 단계 이후 경과시간으로 표현(원하시면 절대시간으로 바꿔도 됨)

    # Overshoot
    os_percent = 0.0
    if r_f != 0 and len(y_post) > 0:
        y_max = np.max(y_post)
        os_percent = max(0.0, (y_max - r_f) / abs(r_f) * 100.0)

    # IAE
    IAE = float(np.sum(np.abs(e)) * (Ts if Ts > 0 else 1.0))

    return Metrics(settling_time=float(st), overshoot_percent=float(os_percent), IAE=float(IAE))

def print_metrics_table(title, m: Metrics):
    print(f"\n[{title}] 성능지표")
    print("-" * 44)
    print(f"{'정착시간 (s)':<18}: {m.settling_time:>10.4f}")
    print(f"{'오버슈트 (%)':<18}: {m.overshoot_percent:>10.2f}")
    print(f"{'IAE':<18}: {m.IAE:>10.6f}")

# ---------- 제어기 ----------
class PI:
    def __init__(self, Kp, Ki, Ts, umin=-np.inf, umax=np.inf):
        self.Kp, self.Ki, self.Ts = Kp, Ki, Ts
        self.umin, self.umax = umin, umax
        self.I = 0.0

    def step(self, e):
        u_unsat = self.Kp * e + self.I
        u = np.clip(u_unsat, self.umin, self.umax)
        # anti-windup: 클램핑(백-계산 대신 간단 방식)
        self.I += self.Ki * self.Ts * e + (u - u_unsat)
        return u

class PID_Dfiltered:
    def __init__(self, Kp, Ki, Kd, Ts, Td=0.02, umin=-np.inf, umax=np.inf):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.Ts, self.Td = Ts, Td
        self.umin, self.umax = umin, umax
        self.I = 0.0
        self.e_prev = 0.0
        self.d_state = 0.0  # 1차 LPF 상태

    def step(self, e):
        alpha = self.Td / (self.Td + self.Ts)
        de = (e - self.e_prev) / self.Ts
        self.d_state = alpha * self.d_state + (1 - alpha) * de

        u_unsat = self.Kp * e + self.I + self.Kd * self.d_state
        u = np.clip(u_unsat, self.umin, self.umax)
        self.I += self.Ki * self.Ts * e + (u - u_unsat)  # anti-windup
        self.e_prev = e
        return u

# ---------- 케이스 1: 1차 시스템 PI ----------
def run_first_order_PI():
    K, tau = 1.0, 2.0
    Ts, T_end = 0.01, 10.0
    N = int(T_end / Ts)
    ctrl = PI(Kp=1.2, Ki=0.8, Ts=Ts, umin=-3.0, umax=3.0)

    y = 0.0
    ts, rs, ys, us, es = [], [], [], [], []
    for k in range(N):
        t = k * Ts
        r = 1.0 if t >= 0.5 else 0.0
        e = r - y
        u = ctrl.step(e)

        # y_dot = (-1/tau)*y + (K/tau)*u
        ydot = (-1.0 / tau) * y + (K / tau) * u
        y += Ts * ydot

        ts.append(t); rs.append(r); ys.append(y); us.append(u); es.append(e)

    # CSV 저장
    rows = list(zip(ts, rs, ys, us, es))
    write_csv("run1_first_order.csv", rows, header=["t", "r", "y", "u", "e"])

    # 지표 계산
    m = compute_metrics(ts, rs, ys, es, band_ratio=0.02)
    print_metrics_table("Run1 - 1차 시스템 PI", m)

    # 플롯
    fig, ax = plt.subplots(2, 1, figsize=(8, 4), sharex=True)
    ax[0].plot(ts, rs, label="ref"); ax[0].plot(ts, ys, label="y"); ax[0].legend(); ax[0].set_ylabel("Output")
    ax[1].plot(ts, us, label="u"); ax[1].legend(); ax[1].set_ylabel("Control"); ax[1].set_xlabel("Time [s]")
    fig.suptitle("Run1: First-Order + PI (anti-windup)")
    plt.tight_layout()
    return ts, rs, ys, us, es

# ---------- 케이스 2: 2차 시스템 PID ----------
def run_second_order_PID():
    m, c, k, Ku = 1.0, 0.6, 4.0, 1.0
    Ts, T_end = 0.002, 6.0
    N = int(T_end / Ts)
    pid = PID_Dfiltered(Kp=60, Ki=40, Kd=4, Ts=Ts, Td=0.02, umin=-10.0, umax=10.0)

    y, ydot = 0.0, 0.0
    ts, rs, ys, us, es = [], [], [], [], []
    for k in range(N):
        t = k * Ts
        r = 1.0 if t >= 0.2 else 0.0
        e = r - y
        u = pid.step(e)

        # ydd = (Ku*u - c*ydot - k*y)/m
        ydd = (Ku * u - c * ydot - k * y) / m
        ydot += Ts * ydd
        y += Ts * ydot

        ts.append(t); rs.append(r); ys.append(y); us.append(u); es.append(e)

    write_csv("run2_second_order.csv", list(zip(ts, rs, ys, us, es)), header=["t", "r", "y", "u", "e"])
    mtr = compute_metrics(ts, rs, ys, es, band_ratio=0.02)
    print_metrics_table("Run2 - 2차(MSD) PID", mtr)

    fig, ax = plt.subplots(2, 1, figsize=(8, 4), sharex=True)
    ax[0].plot(ts, rs, label="ref"); ax[0].plot(ts, ys, label="y"); ax[0].legend(); ax[0].set_ylabel("Position")
    ax[1].plot(ts, us, label="u"); ax[1].legend(); ax[1].set_ylabel("Control"); ax[1].set_xlabel("Time [s]")
    fig.suptitle("Run2: Mass-Spring-Damper + PID (LPF-D, anti-windup)")
    plt.tight_layout()
    return ts, rs, ys, us, es

# ---------- 케이스 3: DC 모터 속도 PID + 외란 ----------
def run_dc_motor_PID():
    J, B, Kt = 0.02, 0.02, 0.1
    Ts, T_end = 0.001, 3.0
    N = int(T_end / Ts)
    pid = PID_Dfiltered(Kp=2.5, Ki=150.0, Kd=0.01, Ts=Ts, Td=0.002, umin=-12.0, umax=12.0)

    w = 0.0
    ts, rs, ys, us, es, taus = [], [], [], [], [], []
    for k in range(N):
        t = k * Ts
        r = 50.0 if t >= 0.1 else 0.0  # [rad/s]
        tau_L = 0.15 if (1.5 <= t < 1.8) else 0.0

        e = r - w
        u = pid.step(e)

        # wdot = (Kt*u - tau_L - B*w)/J
        wdot = (Kt * u - tau_L - B * w) / J
        w += Ts * wdot

        ts.append(t); rs.append(r); ys.append(w); us.append(u); es.append(e); taus.append(tau_L)

    write_csv(r"C:\MyProgram\run3_dc_motor.csv",
              list(zip(ts, rs, ys, us, es, taus)),
              header=["t", "r(rad/s)", "w(rad/s)", "u(V)", "e", "tau_L(Nm)"])

    # 지표는 전체 구간 기준(외란 포함)으로 계산.
    mtr = compute_metrics(ts, rs, ys, es, band_ratio=0.02)
    print_metrics_table("Run3 - DC Motor Speed PID (+disturbance)", mtr)

    fig, ax = plt.subplots(3, 1, figsize=(8, 5), sharex=True)
    ax[0].plot(ts, rs, label="ref"); ax[0].plot(ts, ys, label="omega"); ax[0].legend(); ax[0].set_ylabel("rad/s")
    ax[1].plot(ts, us, label="u[V]"); ax[1].legend(); ax[1].set_ylabel("V")
    ax[2].plot(ts, taus, label="load torque"); ax[2].legend(); ax[2].set_ylabel("N·m"); ax[2].set_xlabel("Time [s]")
    fig.suptitle("Run3: DC Motor Speed PID with Load Disturbance")
    plt.tight_layout()
    return ts, rs, ys, us, es, taus

# ---------- 메인 ----------
if __name__ == "__main__":
    print("=== PID 성능지표 & CSV 로깅 실행 ===")
    run1 = run_first_order_PI()
    run2 = run_second_order_PID()
    run3 = run_dc_motor_PID()
    plt.show()
