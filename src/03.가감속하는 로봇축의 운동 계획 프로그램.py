import numpy as np
import matplotlib.pyplot as plt

# 목표 파라미터
q0 = 0.0       # 초기 위치 [rad]
qf = 1.0       # 목표 위치 [rad]
v_max = 1.0    # 최대 속도 [rad/s]
a_max = 2.0    # 최대 가속도 [rad/s^2]
dt = 0.01      # 샘플링 주기 [s]

# 1. 가속 시간 및 변위
t_a = v_max / a_max
d_a = 0.5 * a_max * t_a**2

# 2. 등속 구간 확인
d_total = qf - q0
d_c = d_total - 2*d_a

if d_c < 0:
    # 삼각형 프로파일로 수정
    t_a = np.sqrt(d_total / a_max)
    t_c = 0
    T = 2 * t_a
else:
    t_c = d_c / v_max
    T = 2 * t_a + t_c

# 3. 시뮬레이션 시간 벡터
time = np.arange(0, T, dt)
q, v, a = [], [], []

for t in time:
    if t < t_a:  # 가속 구간
        a_t = a_max
        v_t = a_max * t
        q_t = q0 + 0.5 * a_max * t**2
    elif t < t_a + t_c:  # 등속 구간
        a_t = 0
        v_t = v_max
        q_t = q0 + d_a + v_max * (t - t_a)
    elif t <= T:  # 감속 구간
        t_d = t - (t_a + t_c)
        a_t = -a_max
        v_t = v_max - a_max * t_d
        q_t = qf - 0.5 * a_max * (T - t)**2
    else:
        a_t, v_t, q_t = 0, 0, qf

    q.append(q_t)
    v.append(v_t)
    a.append(a_t)

# 4. 시각화
plt.figure(figsize=(10,6))
plt.subplot(3,1,1)
plt.plot(time, q, label="Position q(t)")
plt.ylabel("q [rad]")
plt.legend()

plt.subplot(3,1,2)
plt.plot(time, v, label="Velocity v(t)")
plt.ylabel("v [rad/s]")
plt.legend()

plt.subplot(3,1,3)
plt.plot(time, a, label="Acceleration a(t)")
plt.ylabel("a [rad/s^2]")
plt.xlabel("Time [s]")
plt.legend()

plt.tight_layout()
plt.show()
