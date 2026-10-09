import sympy as sp
import numpy as np

# -------------------------------
# 1) 문제 설정
# -------------------------------
l1v, l2v = 1.0, 1.0
x_target, y_target = 1.2, 0.7

# -------------------------------
# 2) 심볼릭 정의 + DH 기반 FK
#    (클래식 DH: A_i(theta_i, d_i, a_i, alpha_i))
# -------------------------------
t1, t2 = sp.symbols('t1 t2', real=True)
l1, l2 = sp.symbols('l1 l2', positive=True, real=True)

def A_DH(theta, d, a, alpha):
    """클래식 DH 변환행렬(4x4) - SymPy 심볼릭"""
    ct, st = sp.cos(theta), sp.sin(theta)
    ca, sa = sp.cos(alpha), sp.sin(alpha)
    return sp.Matrix([
        [ct, -st*ca,  st*sa, a*ct],
        [st,  ct*ca, -ct*sa, a*st],
        [ 0,     sa,     ca,   d ],
        [ 0,      0,      0,   1 ]
    ])

# 2R 평면 로봇: (t1, 0, l1, 0) -> (t2, 0, l2, 0)
A1 = A_DH(t1, 0, l1, 0)
A2 = A_DH(t2, 0, l2, 0)
T  = A1 * A2

# 말단 위치 (x, y) 추출
x = sp.simplify(T[0, 3])
y = sp.simplify(T[1, 3])

# 잔차 벡터 f = [x - x*, y - y*]
f1 = x - x_target
f2 = y - y_target
f  = sp.Matrix([f1, f2])

# 야코비안 J = df/d[t1,t2]
J = f.jacobian([t1, t2])

# 수치 함수화
f_func = sp.lambdify((t1, t2, l1, l2), f, "numpy")
J_func = sp.lambdify((t1, t2, l1, l2), J, "numpy")

# -------------------------------
# 3) 뉴턴–랩슨 반복 함수 (로그 출력)
# -------------------------------
def newton_log(theta0, tol=1e-12, max_iter=50, damping=1.0):
    """
    theta0: (t1, t2) 초기값 (rad)
    damping: 감쇠 계수 (0<damping<=1), 1이면 표준 뉴턴
    """
    th = np.array(theta0, dtype=float)
    print("\n[Newton-Raphson] init =", tuple(th))
    print(f"{'iter':>4} | {'theta1(rad)':>13} {'theta2(rad)':>13} | {'step_norm':>10} | {'res_norm':>10}")
    print("-"*66)

    for k in range(1, max_iter+1):
        # 잔차/야코비안 계산
        fv = np.array(f_func(th[0], th[1], l1v, l2v), dtype=float).reshape(2)
        Jv = np.array(J_func(th[0], th[1], l1v, l2v), dtype=float)

        # 수렴 검사
        res_norm = np.linalg.norm(fv)
        if res_norm < tol:
            print(f"{k:4d} | {th[0]:13.9f} {th[1]:13.9f} | {'-':>10} | {res_norm:10.3e}")
            print(" -> converged")
            break

        # 선형계 풀이: J * delta = f
        try:
            delta = np.linalg.solve(Jv, fv)
        except np.linalg.LinAlgError:
            print(f"{k:4d} | {th[0]:13.9f} {th[1]:13.9f} | {'nan':>10} | {res_norm:10.3e}")
            print(" -> Jacobian singular or ill-conditioned")
            break

        step = damping * delta
        step_norm = np.linalg.norm(step)
        th = th - step

        print(f"{k:4d} | {th[0]:13.9f} {th[1]:13.9f} | {step_norm:10.3e} | {res_norm:10.3e}")

        if step_norm < tol:
            print(" -> step small; treat as converged")
            break
    return th

# -------------------------------
# 4) 실행: 두 해 찾기 (elbow-down / elbow-up)
# -------------------------------
sol1 = newton_log(theta0=(-0.3,  1.6), tol=1e-12, max_iter=50, damping=1.0)  # elbow-down
sol2 = newton_log(theta0=( 1.3, -1.6), tol=1e-12, max_iter=50, damping=1.0)  # elbow-up

# -------------------------------
# 5) 결과 검증 및 출력 (deg, FK 오차)
# -------------------------------
def fk(th):
    t1v, t2v = th
    # DH 기반과 동일 결과: alpha=0, d=0 이므로 고전 2R 공식과 일치
    xv = l1v*np.cos(t1v) + l2v*np.cos(t1v + t2v)
    yv = l1v*np.sin(t1v) + l2v*np.sin(t1v + t2v)
    return xv, yv

def summarize(th, tag):
    xv, yv = fk(th)
    ex, ey = x_target - xv, y_target - yv
    print(f"\n[{tag}]")
    print(f"  theta1 = {th[0]:.9f} rad  ({np.degrees(th[0]):.6f} deg)")
    print(f"  theta2 = {th[1]:.9f} rad  ({np.degrees(th[1]):.6f} deg)")
    print(f"  FK error: dx={ex:.3e}, dy={ey:.3e}, norm={np.hypot(ex,ey):.3e}")

summarize(sol1, "elbow-down")
summarize(sol2, "elbow-up")
