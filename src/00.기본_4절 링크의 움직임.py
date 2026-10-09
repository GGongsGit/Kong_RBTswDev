# Four-bar linkage (MATLAB → Python)
import numpy as np
import matplotlib
# 필요 시 GUI 없이 사용하려면 다음 줄의 주석을 해제하세요.
# matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----- 링크 파라미터 -----
l1 = 1.0
l2 = 1.0
l3 = 1.0
l4 = 1.0

# ----- 플롯 준비 -----
fig, ax = plt.subplots()
ax.set_xlim([-1, 2])
ax.set_ylim([-1, 2])
ax.set_aspect('equal', adjustable='box')
ax.grid(True)
ax.set_title('Four bar')
ax.set_xlabel('x axis (m)')
ax.set_ylabel('y axis (m)')

def _clip(x):  # asin/acos 안전 보정
    return np.clip(x, -1.0, 1.0)

# i = 0:40
for i in range(0, 10):   # 10으ㅏ 원래 값 41
    # 구동 각 (원문: theta1 = pi/3 + pi/2 - pi/60 * i 로 해석)
    theta1 = np.pi/3 + np.pi/2 - (np.pi/60.0) * i

    # 기하 계산
    s = np.sqrt(l1**2 + l2**2 - 2*l1*l2*np.cos(theta1))             # 두 변 사이 길이
    beta = np.arcsin(_clip(l2*np.sin(theta1) / s))
    psi  = np.arccos(_clip((l3**2 + s**2 - l4**2) / (2*l3*s)))
    lam  = np.arcsin(_clip(l3*np.sin(psi) / l4))                     # lambda

    theta2 = psi - beta
    theta3 = 2*np.pi - (lam + beta)

    # 조인트 좌표 (r1: 링크2 끝, r2: 링크3 끝, r3: 링크4 끝)
    r1x = l2*np.cos(theta1)
    r1y = l2*np.sin(theta1)

    r2x = l2*np.cos(theta1) + l3*np.cos(theta2)
    r2y = l2*np.sin(theta1) + l3*np.sin(theta2)

    r3x = r2x + l4*np.cos(beta - lam)
    r3y = r2y - l4*np.sin(beta - lam)

    # (원문) Forward kinematics: 말단을 링크3 끝으로 표시
    x = r2x
    y = r2y

    # 로봇 바디 그리기
    rx = [0.0, r1x, r2x, r3x]
    ry = [0.0, r1y, r2y, r3y]
    ax.plot(rx, ry, '-')
    ax.plot(x, y, 'o')  # 말단 표시

# plt.savefig("four_bar.png", dpi=160)  # GUI 없이 저장만 할 때 사용
plt.show()
