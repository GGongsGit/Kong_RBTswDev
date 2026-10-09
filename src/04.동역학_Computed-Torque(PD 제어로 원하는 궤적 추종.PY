import numpy as np
from dataclasses import dataclass

# -------------------------
# 1) 로봇 파라미터
# -------------------------
@dataclass
class TwoLinkParams:
    m1: float = 2.0     # kg
    m2: float = 1.5     # kg
    l1: float = 1.0     # m
    l2: float = 0.8     # m
    lc1: float = 0.5    # m (COM from joint1)
    lc2: float = 0.4    # m (COM from joint2)
    I1: float = 0.05    # kg*m^2
    I2: float = 0.02    # kg*m^2
    g:  float = 9.81    # m/s^2

P = TwoLinkParams()

# -------------------------
# 2) 동역학 모델: M, C, G
# -------------------------
def M_mat(q, P=P):
    q1, q2 = q
    c2 = np.cos(q2)
    M11 = P.I1 + P.I2 + P.m1*P.lc1**2 + P.m2*(P.l1**2 + P.lc2**2 + 2*P.l1*P.lc2*c2)
    M12 = P.I2 + P.m2*(P.lc2**2 + P.l1*P.lc2*c2)
    M22 = P.I2 + P.m2*P.lc2**2
    return np.array([[M11, M12],
                     [M12, M22]])

def C_vec(q, dq, P=P):
    q1, q2 = q
    dq1, dq2 = dq
    h = P.m2*P.l1*P.lc2*np.sin(q2)
    C1 = -2*h*dq1*dq2 - h*dq2**2
    C2 =  h*dq1**2
    return np.array([C1, C2])

def G_vec(q, P=P):
    q1, q2 = q
    g1 = (P.m1*P.lc1 + P.m2*P.l1)*P.g*np.cos(q1) + P.m2*P.lc2*P.g*np.cos(q1+q2)
    g2 = P.m2*P.lc2*P.g*np.cos(q1+q2)
    return np.array([g1, g2])

# -------------------------
# 3) 역동역학: 토크 계산
# -------------------------
def inverse_dynamics(q, dq, ddq, P=P):
    """ tau = M(q) ddq + C(q,dq) + G(q) """
    return M_mat(q, P) @ ddq + C_vec(q, dq, P) + G_vec(q, P)

# -------------------------
# 4) 순동역학: ddq 계산
# -------------------------
def forward_dynamics(q, dq, tau, P=P):
    """ ddq = M^{-1} (tau - C - G) """
    M = M_mat(q, P)
    rhs = tau - C_vec(q, dq, P) - G_vec(q, P)
    return np.linalg.solve(M, rhs)

# -------------------------
# 5) RK4 적분기
# -------------------------
def rk4_step(state, u, dt, dyn_fun):
    """
    state = (q, dq)
    u = tau (2,)
    dyn_fun(q, dq, tau) -> ddq
    """
    q, dq = state

    def f(q_, dq_):
        ddq_ = dyn_fun(q_, dq_, u)
        return dq_, ddq_

    # k1
    k1_q, k1_dq = f(q, dq)

    # k2
    k2_q, k2_dq = f(q + 0.5*dt*k1_q, dq + 0.5*dt*k1_dq)

    # k3
    k3_q, k3_dq = f(q + 0.5*dt*k2_q, dq + 0.5*dt*k2_dq)

    # k4
    k4_q, k4_dq = f(q + dt*k3_q, dq + dt*k3_dq)

    q_next  = q  + (dt/6.0)*(k1_q  + 2*k2_q  + 2*k3_q  + k4_q)
    dq_next = dq + (dt/6.0)*(k1_dq + 2*k2_dq + 2*k3_dq + k4_dq)

    return q_next, dq_next

# -------------------------
# 6) Computed-Torque + PD (역동역학 기반 제어)
#    원하는 궤적(qd, dqd, ddqd)에 맞춰 토크 생성
# -------------------------
def computed_torque(q, dq, t, P=P):
    # 원하는 기준 궤적(예: 부드러운 사인 궤적)
    # qd(t) = [0.6*sin(0.5 t), 0.8*sin(0.5 t + pi/4)]
    qd   = np.array([0.6*np.sin(0.5*t), 0.8*np.sin(0.5*t + np.pi/4)])
    dqd  = np.array([0.6*0.5*np.cos(0.5*t), 0.8*0.5*np.cos(0.5*t + np.pi/4)])
    ddqd = np.array([-0.6*(0.5**2)*np.sin(0.5*t),
                     -0.8*(0.5**2)*np.sin(0.5*t + np.pi/4)])

    # PD 게인 (대칭양의정)
    Kp = np.diag([60.0, 60.0])
    Kd = np.diag([12.0, 12.0])

    e   = qd - q
    de  = dqd - dq
    v   = ddqd + Kd @ de + Kp @ e         # 가상가속도
    tau = M_mat(q,P) @ v + C_vec(q,dq,P) + G_vec(q,P)  # 역동역학 기반
    return tau, qd, dqd

# -------------------------
# 7) 시뮬레이션 (순동역학)
# -------------------------
def simulate(T=6.0, dt=0.002, P=P):
    steps = int(T/dt)
    q  = np.array([0.0, 0.0])     # 초기자세 [rad]
    dq = np.array([0.0, 0.0])     # 초기각속도 [rad/s]

    qs, dqs, qds, dqds, taus, ts = [], [], [], [], [], []

    for k in range(steps):
        t = k*dt
        tau, qd, dqd = computed_torque(q, dq, t, P)
        # 순동역학 적분
        q, dq = rk4_step((q, dq), tau, dt, lambda qq,ddqq,uu: forward_dynamics(qq, ddqq, uu, P))
        qs.append(q.copy()); dqs.append(dq.copy())
        qds.append(qd.copy()); dqds.append(dqd.copy()); taus.append(tau.copy())
        ts.append(t)

    return np.array(ts), np.array(qs), np.array(dqs), np.array(qds), np.array(dqds), np.array(taus)

if __name__ == "__main__":
    ts, qs, dqs, qds, dqds, taus = simulate()

    # --- (선택) 간단한 시각화 ---
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(3,1, figsize=(8,8), sharex=True)
        ax[0].plot(ts, qs[:,0], label='q1')
        ax[0].plot(ts, qds[:,0], '--', label='q1_d', alpha=0.7)
        ax[0].set_ylabel('rad'); ax[0].set_title('Joint 1')

        ax[1].plot(ts, qs[:,1], label='q2')
        ax[1].plot(ts, qds[:,1], '--', label='q2_d', alpha=0.7)
        ax[1].set_ylabel('rad'); ax[1].set_title('Joint 2')

        ax[2].plot(ts, taus[:,0], label='tau1')
        ax[2].plot(ts, taus[:,1], label='tau2')
        ax[2].set_ylabel('Nm'); ax[2].set_xlabel('time [s]')
        ax[2].set_title('Torques')
        for a in ax: a.grid(True); a.legend()
        plt.tight_layout(); plt.show()
    except Exception as e:
        print("Plot skipped:", e)
