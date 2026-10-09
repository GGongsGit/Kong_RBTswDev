# forward_kinematics.py
# 순기구학 (Standard DH) - Numpy만 사용
import numpy as np

# --------- 기본 유틸 ---------
def rotmat_to_rpy_zyx(R):
    """
    ZYX 순서의 Roll-Pitch-Yaw(= yaw, pitch, roll) [rad]
    R: 3x3 rotation matrix
    반환: (roll, pitch, yaw)
    """
    sy = -R[2,0]
    cy = np.sqrt(R[0,0]**2 + R[1,0]**2)
    pitch = np.arctan2(sy, cy)

    if np.isclose(cy, 0.0):
        # 특이 (gimbal lock): roll=0으로 두고 yaw에 흡수
        roll = 0.0
        yaw = np.arctan2(-R[0,1], R[1,1])
    else:
        roll = np.arctan2(R[2,1], R[2,2])
        yaw  = np.arctan2(R[1,0], R[0,0])
    return roll, pitch, yaw


def dh_transform(a, alpha, d, theta):
    """
    표준 DH로부터 단일 링크 동차변환 A_i 구성
    모든 각도 단위: rad
    """
    ca, sa = np.cos(alpha), np.sin(alpha)
    ct, st = np.cos(theta), np.sin(theta)
    return np.array([
        [ ct, -st*ca,  st*sa, a*ct],
        [ st,  ct*ca, -ct*sa, a*st],
        [  0,     sa,     ca,    d],
        [  0,      0,      0,    1]
    ], dtype=float)


# --------- 순기구학 메인 ---------
def fk_dh(dh_params, q=None, joint_types=None, degrees=True, return_all=False):
    """
    DH 파라미터 기반 순기구학.
    dh_params: list of dicts([{a, alpha, d, theta}, ...])  # 표준 DH
    q:          조인트 값 리스트(선택). 제공 시 R은 theta+=q, P는 d+=q
    joint_types: 조인트 유형 리스트(['R'|'P', ...])  q 해석용
    degrees:    입력 각도(deg) 여부. True면 deg→rad 변환
    return_all: 각 단계의 T_0_i 리스트도 반환할지 여부

    반환:
      T_0_n  (4x4)
      (옵션) Ts = [T_0_1, T_0_2, ..., T_0_n]
    """
    # 파라미터 복사 및 단위 정리
    params = []
    for p in dh_params:
        a = float(p["a"])
        alpha = float(p["alpha"])
        d = float(p["d"])
        theta = float(p["theta"])
        if degrees:
            alpha = np.deg2rad(alpha)
            theta = np.deg2rad(theta)
        params.append({"a":a, "alpha":alpha, "d":d, "theta":theta})

    # q 적용 (R은 theta, P는 d)
    if q is not None:
        assert joint_types is not None and len(joint_types) == len(params) == len(q)
        for i, typ in enumerate(joint_types):
            if typ.upper() == 'R':
                theta_offset = np.deg2rad(q[i]) if degrees else q[i]
                params[i]["theta"] += theta_offset
            elif typ.upper() == 'P':
                params[i]["d"] += q[i]
            else:
                raise ValueError("joint_types는 'R' 또는 'P'만 허용합니다.")

    T = np.eye(4)
    Ts = []
    for p in params:
        A = dh_transform(p["a"], p["alpha"], p["d"], p["theta"])
        T = T @ A
        if return_all:
            Ts.append(T.copy())

    return (T, Ts) if return_all else T


# --------- 2링크 평면(2R) 예제 ---------
def fk_2r_planar(L1, L2, theta1, theta2, degrees=True):
    """
    2R 평면 매니퓰레이터의 말단 좌표 (x, y) 및 전체 T 반환.
    Link는 XY평면에서 회전(Z축 회전), 표준 DH 표기 사용.
    """
    # 2R 평면표준 DH (z축 회전, x축에 링크 길이)
    dh = [
        {"a": L1, "alpha": 0.0, "d": 0.0, "theta": theta1},
        {"a": L2, "alpha": 0.0, "d": 0.0, "theta": theta2},
    ]
    T = fk_dh(dh, degrees=degrees)
    x, y = T[0,3], T[1,3]
    return (x, y, T)

# --------- 사용 예시 ---------
if __name__ == "__main__":
    # (1) 일반 DH 예시: 3-자유도 (R-R-P)
    dh_table = [
        {"a": 0.3, "alpha":  90.0, "d": 0.2, "theta":  30.0},  # i=1
        {"a": 0.2, "alpha":   0.0, "d": 0.0, "theta": -45.0},  # i=2
        {"a": 0.0, "alpha":   0.0, "d": 0.1, "theta":   0.0},  # i=3 (기본 오프셋)
    ]
    joint_types = ['R', 'R', 'P']
    q = [10.0, -20.0, 0.05]  # deg, deg, meters
    T_0_n, Ts = fk_dh(dh_table, q=q, joint_types=joint_types, degrees=True, return_all=True)
    print("=== 일반 DH 순기구학 결과 (R-R-P) ===")
    print("T_0_n =\n", np.array_str(T_0_n, precision=4, suppress_small=True))
    R = T_0_n[:3,:3]
    roll, pitch, yaw = rotmat_to_rpy_zyx(R)
    print(f"rpy[rad] = ({roll:.4f}, {pitch:.4f}, {yaw:.4f})")
    print(f"position [m] = {T_0_n[:3,3]}")

    # (2) 2R 평면 예시
    L1, L2 = 1.0, 0.8
    theta1, theta2 = 45.0, 30.0  # deg
    x, y, T = fk_2r_planar(L1, L2, theta1, theta2, degrees=True)
    print("\n=== 2R 평면 순기구학 ===")
    print(f"end-effector (x, y) = ({x:.4f}, {y:.4f}) [m]")
    print("T_0_2 =\n", np.array_str(T, precision=4, suppress_small=True))
