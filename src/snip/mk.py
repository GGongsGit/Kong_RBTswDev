import numpy as np

def jacobian_2link(l1, l2, th1, th2):
    """2링크 평면 로봇의 자코비안 J(θ) (2x2, θ는 rad)"""
    s1, c1 = np.sin(th1), np.cos(th1)
    s12, c12 = np.sin(th1 + th2), np.cos(th1 + th2)
    return np.array([[-l1*s1 - l2*s12, -l2*s12],
                     [ l1*c1 + l2*c12,  l2*c12]])

def jdot_2link(l1, l2, th1, th2, dth1, dth2):
    """J의 시간 미분 J̇(θ, θ̇)"""
    c1, s1 = np.cos(th1), np.sin(th1)
    c12, s12 = np.cos(th1 + th2), np.sin(th1 + th2)
    d12 = dth1 + dth2
    return np.array([[-l1*c1*dth1 - l2*c12*d12, -l2*c12*d12],
                     [-l1*s1*dth1 - l2*s12*d12, -l2*s12*d12]])

l1, l2 = 1.0, 1.0
th   = np.deg2rad([30.0, 45.0])      # 관절 각도 (rad)
dth  = np.array([0.5, -0.2])         # 관절 속도 (rad/s)
ddth = np.array([0.3, -0.1])         # 관절 가속도 (rad/s²)

J = jacobian_2link(l1, l2, *th)
print("det J =", round(np.linalg.det(J), 4))          # = l1*l2*sin(θ2) = 0.7071

# 1) 순방향 속도:  선속도 v = J(θ) · θ̇
v = J @ dth
print("v =", np.round(v, 4))                          # [-0.5398  0.5107]

# 2) 역방향 속도:  θ̇ = J⁻¹ · v   (inv 대신 solve 사용)
dth_back = np.linalg.solve(J, v)
print("θ̇ =", np.round(dth_back, 4))                   # [ 0.5 -0.2]  ← 원래 값 복원

# 3) 말단 가속도:  a = J · θ̈ + J̇ · θ̇
Jd = jdot_2link(l1, l2, *th, *dth)
a = J @ ddth + Jd @ dth
print("a =", np.round(a, 4))                          # [-0.583   0.0996]

# 4) 특이점 검사: det J ≈ 0 이면 역속도 계산 불가
if abs(np.linalg.det(J)) < 1e-6:
    print("특이점 근처: θ2 ≈ 0° 또는 180°")
