# planar_2R_kinematics.py
# 2R관절의 개수(DoF: Degree of Freedom)가 2개, R → Revolute Joint (회전 관절, Rotary),따라서 2R 매니퓰레이터는 회전 관절 2개로 이루어진 로봇 팔을 뜻합니다.
# 단일 파일 버전: 모듈(twoR_kinematics) 의존성 없음


from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple
import numpy as np

Array = np.ndarray

@dataclass
class TwoRConfig:
    L1: float
    L2: float

def fk_2r(L1: float, L2: float, q: Array) -> Array:
    """순운동학: [x, y, theta_z] 반환"""
    q1, q2 = float(q[0]), float(q[1])
    c1, s1 = math.cos(q1), math.sin(q1)
    c12, s12 = math.cos(q1 + q2), math.sin(q1 + q2)
    x = L1 * c1 + L2 * c12
    y = L1 * s1 + L2 * s12
    theta = q1 + q2  # planar에서 z-축 yaw
    return np.array([x, y, theta], dtype=float)

def jacobian_2r(L1: float, L2: float, q: Array) -> Array:
    """자코비안 J(q): 3x2, [xdot, ydot, thetadot] = J @ [q1d, q2d]"""
    q1, q2 = float(q[0]), float(q[1])
    s1, c1 = math.sin(q1), math.cos(q1)
    s12, c12 = math.sin(q1 + q2), math.cos(q1 + q2)
    J = np.array([
        [-L1 * s1 - L2 * s12,   -L2 * s12],
        [ L1 * c1 + L2 * c12,    L2 * c12],
        [ 1.0,                   1.0     ]
    ], dtype=float)
    return J

def jdot_2r(L1: float, L2: float, q: Array, qdot: Array) -> Array:
    """자코비안 시간미분 Jdot(q, qdot): 3x2"""
    q1, q2 = float(q[0]), float(q[1])
    q1d, q2d = float(qdot[0]), float(qdot[1])
    c1, s1 = math.cos(q1), math.sin(q1)
    c12, s12 = math.cos(q1 + q2), math.sin(q1 + q2)
    q12d = q1d + q2d
    Jdot = np.array([
        [-L1 * c1 * q1d - L2 * c12 * q12d,   -L2 * c12 * q12d],
        [-L1 * s1 * q1d - L2 * s12 * q12d,   -L2 * s12 * q12d],
        [ 0.0,                                 0.0           ]
    ], dtype=float)
    return Jdot

def twist_2r(L1: float, L2: float, q: Array, qdot: Array) -> Array:
    """트위스트(작업공간 속도) [xdot, ydot, thetadot]"""
    J = jacobian_2r(L1, L2, q)
    return J @ np.asarray(qdot, dtype=float)

def task_accel_2r(L1: float, L2: float, q: Array, qdot: Array, qddot: Array) -> Array:
    """작업공간 가속도 [xddot, yddot, thetaddot] = J@qddot + Jdot@qdot"""
    J  = jacobian_2r(L1, L2, q)
    Jd = jdot_2r(L1, L2, q, qdot)
    qdot  = np.asarray(qdot, dtype=float)
    qddot = np.asarray(qddot, dtype=float)
    return J @ qddot + Jd @ qdot

def demo() -> None:
    # 예시 파라미터
    L1, L2 = 1.0, 1.0
    q     = np.deg2rad(np.array([30.0, 45.0]))  # [q1, q2] (rad)
    qdot  = np.array([0.5, -0.2])               # (rad/s)
    qddot = np.array([0.3, -0.1])               # (rad/s^2)

    # 계산
    x     = fk_2r(L1, L2, q)
    J     = jacobian_2r(L1, L2, q)
    Jd    = jdot_2r(L1, L2, q, qdot)
    V     = twist_2r(L1, L2, q, qdot)
    A     = task_accel_2r(L1, L2, q, qdot, qddot)

    # 출력
    np.set_printoptions(precision=6, suppress=True)
    print("=== Planar 2R Kinematics Demo ===")
    print(f"L1={L1:.3f}, L2={L2:.3f}")
    print(f"q (rad):     {q}")
    print(f"qdot (rad/s): {qdot}")
    print(f"qddot(rad/s^2): {qddot}\n")
    print("FK [x, y, theta_z]:\n", x, "\n")
    print("J(q):\n", J, "\n")
    print("Jdot(q,qdot):\n", Jd, "\n")
    print("Twist [xdot, ydot, thetadot]:\n", V, "\n")
    print("Task Accel [xddot, yddot, thetaddot]:\n", A, "\n")

if __name__ == "__main__":
    demo()
