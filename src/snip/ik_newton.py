import numpy as np

L1, L2 = 1.0, 1.0
target = np.array([1.2, 0.7])          # 목표 말단 위치 (x, y)

def fk(th):
    t1, t2 = th
    return np.array([L1*np.cos(t1) + L2*np.cos(t1 + t2),
                     L1*np.sin(t1) + L2*np.sin(t1 + t2)])

def jacobian(th):                      # 2-3 동기구학의 J(θ)와 같은 행렬
    t1, t2 = th
    s1, c1 = np.sin(t1), np.cos(t1)
    s12, c12 = np.sin(t1 + t2), np.cos(t1 + t2)
    return np.array([[-L1*s1 - L2*s12, -L2*s12],
                     [ L1*c1 + L2*c12,  L2*c12]])

def ik_newton(th0_deg, tol=1e-10, max_iter=50):
    th = np.deg2rad(np.array(th0_deg, dtype=float))     # 초기값 (deg → rad)
    for k in range(1, max_iter + 1):
        f = fk(th) - target                             # 잔차: 지금 위치 − 목표
        err = np.linalg.norm(f)
        if err < tol:
            return th, k - 1, err                       # 수렴
        J = jacobian(th)
        if abs(np.linalg.det(J)) < 1e-9:
            raise RuntimeError("특이점: 초기값을 바꾸세요")
        th = th - np.linalg.solve(J, f)                 # θ ← θ − J⁻¹·f
        print(f"  {k:2d}  θ1={np.degrees(th[0]):10.4f}  θ2={np.degrees(th[1]):10.4f}  |f|={err:.2e}")
    raise RuntimeError("수렴하지 않음")

for guess in ([-20, 80], [70, -80]):                    # 초기값에 따라 다른 해
    print(f"초기값 {guess}")
    th, n, err = ik_newton(guess)
    print(f"  → θ1={np.degrees(th[0]):.3f}°, θ2={np.degrees(th[1]):.3f}°  ({n}회, 오차 {err:.1e})")
# 해석해와 같음: (-15.746°, 92.006°), (76.259°, -92.006°)
