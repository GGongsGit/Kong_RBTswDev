import numpy as np

# ---------- DH 파라미터 (3R 평면 로봇) ----------
#  i | θ_i (관절 변수) | d_i | a_i (링크 길이) | α_i
#  1 |      θ1        |  0  |      L1         |  0
#  2 |      θ2        |  0  |      L2         |  0
#  3 |      θ3        |  0  |      L3         |  0
L = [1.0, 0.8, 0.5]
DH = [(0.0, L[0], 0.0), (0.0, L[1], 0.0), (0.0, L[2], 0.0)]   # (d, a, α)

def A(theta, d, a, alpha):
    """표준 DH 변환행렬 A = Rz(θ)·Tz(d)·Tx(a)·Rx(α)"""
    ct, st, ca, sa = np.cos(theta), np.sin(theta), np.cos(alpha), np.sin(alpha)
    return np.array([[ct, -st*ca,  st*sa, a*ct],
                     [st,  ct*ca, -ct*sa, a*st],
                     [ 0,     sa,     ca,    d],
                     [ 0,      0,      0,    1]])

def fk_dh(th):
    """T = A1·A2·A3 → 말단 (x, y, φ)"""
    T = np.eye(4)
    for q, (d, a, al) in zip(th, DH):
        T = T @ A(q, d, a, al)
    return np.array([T[0, 3], T[1, 3], np.arctan2(T[1, 0], T[0, 0])])

# ---------- 1) 해석법: 손목점(wrist point)으로 2링크 문제로 줄이기 ----------
def ik3_analytic(x, y, phi, elbow=+1):
    xw = x - L[2]*np.cos(phi)                 # 3번 링크를 빼서 손목 위치를 구함
    yw = y - L[2]*np.sin(phi)
    c2 = (xw**2 + yw**2 - L[0]**2 - L[1]**2) / (2*L[0]*L[1])
    if abs(c2) > 1:
        return None                           # 도달 불가
    t2 = elbow*np.arccos(c2)
    t1 = np.arctan2(yw, xw) - np.arctan2(L[1]*np.sin(t2), L[0] + L[1]*np.cos(t2))
    t3 = phi - t1 - t2                        # 말단 방향 = θ1 + θ2 + θ3
    return np.array([t1, t2, t3])

# ---------- 2) 뉴턴-랩슨: DH 기반 FK + 수치 자코비안 ----------
def jac_numeric(th, h=1e-6):
    J = np.zeros((3, 3))
    for i in range(3):
        dth = np.zeros(3); dth[i] = h
        J[:, i] = (fk_dh(th + dth) - fk_dh(th - dth)) / (2*h)   # 중앙 차분
    return J

def wrap(a):
    return (a + np.pi) % (2*np.pi) - np.pi

def ik3_newton(target, th0, tol=1e-10, max_iter=50):
    th = np.array(th0, dtype=float)
    for k in range(max_iter):
        f = fk_dh(th) - target
        f[2] = wrap(f[2])                     # 각도 오차는 [-π, π]로
        if np.linalg.norm(f) < tol:
            return th, k
        th = th - np.linalg.solve(jac_numeric(th), f)
    raise RuntimeError("수렴하지 않음")

# ---------- 실행 ----------
target = np.array([1.2, 1.0, np.deg2rad(45)])   # 말단 x, y (m), 방향 φ
for elbow in (+1, -1):
    th = ik3_analytic(*target, elbow)
    print(f"해석법 elbow={elbow:+d}: θ = {np.round(np.degrees(th), 3)} °  "
          f"DH 검산 = {np.round(fk_dh(th) * [1, 1, 180/np.pi], 4)}")

th, n = ik3_newton(target, np.deg2rad([10, 60, -20]))
print(f"뉴턴-랩슨 ({n}회): θ = {np.round(np.degrees(th), 3)} °")
# 해석법 elbow=+1: θ = [ -8.08  108.423 -55.343] °   DH 검산 = [1.2 1. 45.]
# 해석법 elbow=-1: θ = [ 82.819 -108.423  70.603] °  DH 검산 = [1.2 1. 45.]
# 뉴턴-랩슨 (5회): θ = [ -8.08  108.423 -55.343] °
