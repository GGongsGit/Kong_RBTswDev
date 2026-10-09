# -*- coding: utf-8 -*-
"""
Particle Filter (PF) 2D Localization Demo on Occupancy Grid
- Pure Python + NumPy + Matplotlib (no ROS)
- Raycasting-based range sensor model (12 beams)
- Saves a result image 'pf_localization_result.png' (Agg backend)

이 스크립트는 2D 격자 지도에서 파티클 필터로 로봇 위치를 추정하는 예제입니다.
- N개의 파티클을 유지하며, 속도/각속도 명령(v, w)으로 예측 → 측정(빔 거리)으로 갱신 → 재샘플링.
- 최종 결과 이미지는 지도 + 진궤적 + 데드레커닝 + PF 추정 궤적을 포함합니다.
"""

import math
import numpy as np

# ---- Matplotlib: GUI 백엔드 없이 파일 저장 위주로 동작 ----
import matplotlib
try:
    if matplotlib.get_backend().lower() not in ["agg", "module://matplotlib_inline.backend_inline"]:
        matplotlib.use("Agg")
except Exception:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt


# -------------------- 유틸 --------------------
def wrap_to_pi(a):
    """각도를 [-pi, pi] 범위로 정규화합니다."""
    return (a + np.pi) % (2 * np.pi) - np.pi


def motion_model_velocity(pose, v, w, dt, alphas, rng):
    """
    시속도-각속도 모델(Thrun et al.)에 따른 샘플링 모션 모델.
    pose: (x, y, theta)
    v, w: 제어 입력(선속, 각속) [m/s, rad/s]
    dt:  시간 간격
    alphas: 잡음 파라미터 (α1..α4) tuple
    rng: np.random.Generator
    """
    x, y, th = pose
    a1, a2, a3, a4 = alphas

    v_hat = v + rng.normal(0.0, np.sqrt(a1 * v**2 + a2 * w**2))
    w_hat = w + rng.normal(0.0, np.sqrt(a3 * v**2 + a4 * w**2))
    gamma = rng.normal(0.0, np.sqrt(a1 * v**2 + a2 * w**2))  # 작은 각속도 드리프트

    if abs(w_hat) < 1e-6:
        # 거의 직선
        x_new = x + v_hat * dt * np.cos(th)
        y_new = y + v_hat * dt * np.sin(th)
        th_new = th + gamma * dt
    else:
        x_new = x - (v_hat / w_hat) * np.sin(th) + (v_hat / w_hat) * np.sin(th + w_hat * dt)
        y_new = y + (v_hat / w_hat) * np.cos(th) - (v_hat / w_hat) * np.cos(th + w_hat * dt)
        th_new = th + w_hat * dt + gamma * dt

    return (x_new, y_new, wrap_to_pi(th_new))


def build_demo_map(cell_size=0.1):
    """
    시뮬레이션용 데모 맵을 생성합니다.
    - 공간: 약 10m x 10m (100 x 100 cell)
    - 외곽 벽 + 내부 장애물 몇 개
    반환: (occ_grid, cell_size)
      * occ_grid: 0=free, 1=obstacle (np.ndarray[h, w])
    """
    H, W = 100, 100
    m = np.zeros((H, W), dtype=np.uint8)

    # 외곽 벽
    m[0, :] = 1
    m[-1, :] = 1
    m[:, 0] = 1
    m[:, -1] = 1

    # 내부 장애물 (직사각형 블록들)
    m[20:25, 20:80] = 1
    m[40:70, 50:55] = 1
    m[70:75, 15:45] = 1
    m[55:85, 75:80] = 1

    return m, cell_size


def is_free(occ, x, y, cell_size):
    """연속좌표(x,y)가 free 셀인지 검사합니다."""
    H, W = occ.shape
    c = int(round(x / cell_size))
    r = int(round(y / cell_size))
    if r < 0 or r >= H or c < 0 or c >= W:
        return False
    return occ[r, c] == 0


def raycast(occ, x, y, theta, max_range, cell_size, step=None):
    """
    단순 레이캐스트로 빔 거리 예측을 계산합니다.
    - occ: occupancy grid (0/1)
    - (x, y, theta): 로봇 위치/자세 [m, m, rad]
    - max_range: 최대 감지 거리 [m]
    - step: 보폭 [m], 기본은 cell_size * 0.5
    반환: 충돌 지점까지 거리(또는 max_range)
    """
    if step is None:
        step = cell_size * 0.5
    dist = 0.0
    H, W = occ.shape
    for _ in range(int(max_range / step)):
        xx = x + dist * np.cos(theta)
        yy = y + dist * np.sin(theta)
        # 지도 밖이면 최대거리로 처리
        c = int(round(xx / cell_size))
        r = int(round(yy / cell_size))
        if r < 0 or r >= H or c < 0 or c >= W:
            return max_range
        if occ[r, c] == 1:
            return dist
        dist += step
    return max_range


def simulate_measurement(occ, pose, beam_angles, zmax, cell_size, noise_std, rng):
    """
    빔 각도 집합에 대해 레이캐스트로 이상측정치를 만들고, 가우시안 노이즈를 추가합니다.
    pose: (x, y, th)
    반환: z (np.array, shape=[len(beam_angles)])
    """
    x, y, th = pose
    ideal = np.array([raycast(occ, x, y, th + a, zmax, cell_size) for a in beam_angles])
    noisy = ideal + rng.normal(0.0, noise_std, size=ideal.shape)
    noisy = np.clip(noisy, 0.0, zmax)
    return noisy


def predict_ranges_from_particle(occ, particle_pose, beam_angles, zmax, cell_size):
    x, y, th = particle_pose
    return np.array([raycast(occ, x, y, th + a, zmax, cell_size) for a in beam_angles])


def systematic_resample(particles, weights, rng):
    """
    시스템 재샘플링(Systematic Resampling)
    particles: (N, 3) [x,y,theta]
    weights: (N,)
    """
    N = len(weights)
    positions = (rng.random() + np.arange(N)) / N
    cumsum = np.cumsum(weights)
    cumsum[-1] = 1.0  # 수치오차 보호
    idx = np.searchsorted(cumsum, positions)
    return particles[idx]


# -------------------- 메인 시뮬레이션 --------------------
def run_pf_demo(
    N=500, T=300, dt=0.1,
    v_cmd=0.25, w_cmd_schedule=(0.0, 0.2, -0.2, 0.0),  # 단순한 회전 스케줄
    alphas=(1e-3, 1e-3, 1e-3, 1e-3),
    beam_count=12, zmax=6.0, z_noise=0.05,  # 센서
    resample_thresh_ratio=0.5,
    seed=0
):
    """
    파티클 필터 데모를 수행하고 결과 이미지를 저장합니다.
    반환: 저장 경로, (최종오차_m, 최종자세오차_rad)
    """
    rng = np.random.default_rng(seed)
    occ, cell_size = build_demo_map(cell_size=0.1)

    # 초기 상태(진실/데드레커닝/PF 초기화)
    x0, y0, th0 = 1.0, 1.0, 0.0
    true_pose = np.array([x0, y0, th0], dtype=float)
    odom_pose = np.array([x0, y0, th0], dtype=float)

    # 파티클 초기화 (초기 주변 가우시안)
    particles = np.column_stack([
        rng.normal(x0, 0.2, size=N),
        rng.normal(y0, 0.2, size=N),
        rng.normal(th0, 0.1, size=N),
    ])
    # 지도 밖/장애물 위 파티클은 근처 프리셀로 약간 이동
    for i in range(N):
        for _ in range(50):
            if is_free(occ, particles[i,0], particles[i,1], cell_size):
                break
            particles[i,0] = rng.normal(x0, 0.5)
            particles[i,1] = rng.normal(y0, 0.5)

    weights = np.ones(N) / N

    # 빔 각도 설정 (로봇 전방 기준 균일 분포)
    beam_angles = np.linspace(-np.pi*3/4, np.pi*3/4, beam_count)

    # 기록용
    true_traj = [true_pose.copy()]
    odom_traj = [odom_pose.copy()]
    pf_traj = [np.average(particles, axis=0, weights=weights)]

    # 시뮬레이션 루프
    w_sched = list(w_cmd_schedule)
    sched_len = len(w_sched)
    sched_period = max(1, T // sched_len)

    for t in range(T):
        # 간단한 각속도 스케줄 (T를 구간으로 나눠 w_cmd 변경)
        w_cmd = w_sched[min(t // sched_period, sched_len - 1)]

        # --- Ground truth update (약간의 실제 잡음을 줄 수도 있음) ---
        true_pose = np.array(motion_model_velocity(true_pose, v_cmd, w_cmd, dt, alphas, rng))

        # 지도가 막고 있으면 간단히 방향을 틀어줌(데모용)
        if not is_free(occ, true_pose[0], true_pose[1], cell_size):
            true_pose[2] = wrap_to_pi(true_pose[2] + np.pi/2)
            true_pose[0] = np.clip(true_pose[0], 0.2, occ.shape[1]*cell_size-0.2)
            true_pose[1] = np.clip(true_pose[1], 0.2, occ.shape[0]*cell_size-0.2)

        # --- Odometry dead-reckoning (이상적으로 적분: 노이즈 X) ---
        odom_pose = np.array(motion_model_velocity(odom_pose, v_cmd, w_cmd, dt, (0,0,0,0), rng))

        # --- Simulated LIDAR measurement from true pose ---
        z = simulate_measurement(occ, true_pose, beam_angles, zmax, cell_size, z_noise, rng)

        # --- PF: Prediction ---
        for i in range(N):
            particles[i] = motion_model_velocity(particles[i], v_cmd, w_cmd, dt, alphas, rng)

        # --- PF: Update (Range-only likelihood, independent beams) ---
        # log-likelihood을 사용해 언더플로 방지
        sigma2 = (z_noise**2)
        log_w = np.zeros(N)
        for i in range(N):
            # 파티클이 맵 밖/장애물 안에 있으면 가중치 불이익
            if not is_free(occ, particles[i,0], particles[i,1], cell_size):
                log_w[i] = -1e6
                continue
            zhat = predict_ranges_from_particle(occ, particles[i], beam_angles, zmax, cell_size)
            # L(z | x_i) ∝ exp(-||z - zhat||^2 / (2*sigma^2))  (빔 독립 가정)
            err = z - zhat
            log_w[i] = -0.5 * np.sum((err * err) / sigma2)

        # 정규화
        log_w -= np.max(log_w)  # 수치 안정화
        w = np.exp(log_w)
        w_sum = np.sum(w) + 1e-12
        weights = w / w_sum

        # 유효 샘플 수
        neff = 1.0 / np.sum(weights**2)
        if neff < resample_thresh_ratio * N:
            particles = systematic_resample(particles, weights, rng)
            weights = np.ones(N) / N

        # 추정치(가중 평균, 각도는 circular mean)
        x_est = np.average(particles[:,0], weights=weights)
        y_est = np.average(particles[:,1], weights=weights)
        s = np.average(np.sin(particles[:,2]), weights=weights)
        c = np.average(np.cos(particles[:,2]), weights=weights)
        th_est = math.atan2(s, c)
        pf_est = np.array([x_est, y_est, th_est])

        true_traj.append(true_pose.copy())
        odom_traj.append(odom_pose.copy())
        pf_traj.append(pf_est)

    # -------------------- 결과 시각화 --------------------
    fig, ax = plt.subplots(figsize=(7,7))
    ax.imshow(occ, origin="lower")  # 지도 (0/1)
    ax.set_title("Particle Filter 2D Localization (demo)")
    ax.set_xlabel("x (cells)")
    ax.set_ylabel("y (cells)")

    # 좌표를 셀 단위로 변환하여 그립니다(색상 지정은 하지 않음: 기본값 사용).
    tt = np.array(true_traj)
    od = np.array(odom_traj)
    pf = np.array(pf_traj)

    # 미터 -> 셀 인덱스 변환
    tt_x = tt[:,0] / cell_size; tt_y = tt[:,1] / cell_size
    od_x = od[:,0] / cell_size; od_y = od[:,1] / cell_size
    pf_x = pf[:,0] / cell_size; pf_y = pf[:,1] / cell_size

    ax.plot(tt_x, tt_y, linewidth=2)     # true
    ax.plot(od_x, od_y, linewidth=1)     # odom
    ax.plot(pf_x, pf_y, linewidth=2)     # PF est

    # 시작/끝점 마커
    ax.scatter([tt_x[0]], [tt_y[0]], s=60, marker='o')
    ax.scatter([tt_x[-1]], [tt_y[-1]], s=120, marker='*')

    ax.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    out = "pf_localization_result.png"
    plt.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)

    # 최종 오차 출력 (미터, 라디안)
    pos_err = math.hypot(tt[-1,0] - pf[-1,0], tt[-1,1] - pf[-1,1])
    yaw_err = abs(wrap_to_pi(tt[-1,2] - pf[-1,2]))
    return out, (pos_err, yaw_err)


if __name__ == "__main__":
    out, (pe, ye) = run_pf_demo()
    print("[완료] 결과 이미지 저장:", out)
    print(f"최종 위치 오차 ≈ {pe:.3f} m, 최종 자세 오차 ≈ {ye:.3f} rad")
