# Three Link Planar Robot: FK + IK (MATLAB → Python)
import numpy as np
import matplotlib
# matplotlib.use("Agg")  # 창 없이 파일로만 저장할 때 사용
import matplotlib.pyplot as plt

# 링크 길이
l1, l2, l3 = 0.5, 0.4, 0.3

# 플롯 준비
fig, ax = plt.subplots()
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_aspect('equal', adjustable='box')
ax.grid(True)
ax.set_title('Three Link Planar Robot')
ax.set_xlabel('x axis (m)')
ax.set_ylabel('y axis (m)')

# 루프: i = 1:16
for i in range(1, 17):
    theta3 = np.pi/6 + np.pi/50 * i
    theta2 = np.pi/6 + np.pi/50 * i
    theta1 = np.pi/6 + np.pi/50 * i
    phi    = theta1 + theta2 + theta3

    # 조인트 위치 (J1, J2)
    j1_x = l1 * np.cos(theta1)
    j1_y = l1 * np.sin(theta1)
    j2_x  = l1*np.cos(theta1) + l2*np.cos(theta1 + theta2)
    j2_y  = l1*np.sin(theta1) + l2*np.sin(theta1 + theta2)

    # 순기구학 (말단)
    x = l1*np.cos(theta1) + l2*np.cos(theta1+theta2) + l3*np.cos(theta1+theta2+theta3)
    y = l1*np.sin(theta1) + l2*np.sin(theta1+theta2) + l3*np.sin(theta1+theta2+theta3)

    # 로봇 링크 그리기
    rx = [0.0, j1_x, j2_x, x]
    ry = [0.0, j1_y, j2_y, y]
    ax.plot(rx, ry, '-')
    ax.plot(x, y, '*')  # FK 말단 표시

    # ===== 역기구학 (이미지에 있던 공식을 그대로 구현) =====
    # A, th2 (elbow-up)
    A   = (j2_x**2 + j2_y**2 - (l1**2 + l2**2)) / (2*l1*l2)
    A   = np.clip(A, -1.0, 1.0)              # 수치 안정화
    th2 = np.arctan2(np.sqrt(1 - A*A), A)

    # B 행렬 (캡처된 수식과 동일하게 구성)
    B = np.array([
        [-l2*np.sin(th2),          (l1 + l2*np.cos(th2))],
        [ (l1 + l2*np.cos(th2)),    l2*np.sin(th2)     ]
    ])

    # sc = inv(B)*[rrx; rry]
    sc = np.linalg.solve(B, np.array([j2_x, j2_y]))

    # MATLAB 코드에 맞춰 atan2(sc(1), sc(2)) 사용
    th1_ik = np.arctan2(sc[0], sc[1])        # 주: 순서 유지(이미지 공식과 동일)
    th3_ik = phi - th1_ik - th2

    # IK로 재계산한 말단 (검증용)
    xi = l1*np.cos(th1_ik) + l2*np.cos(th1_ik+th2) + l3*np.cos(th1_ik+th2+th3_ik)
    yi = l1*np.sin(th1_ik) + l2*np.sin(th1_ik+th2) + l3*np.sin(th1_ik+th2+th3_ik)

    ax.plot(xi, yi, 'o', markersize=3)       # IK 말단 표시(원형)

# 표시 / 저장
# plt.savefig("three_link_planar_fk_ik.png", dpi=160)
plt.show()
