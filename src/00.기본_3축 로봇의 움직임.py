# 3링크 평면 로봇 순기구학 (MATLAB → Python 변환)
import numpy as np
import matplotlib
# matplotlib.use("Agg")  # GUI 창 없이 이미지로만 저장할 때 사용
import matplotlib.pyplot as plt

# 링크 길이
l1 = 0.5
l2 = 0.4
l3 = 0.3

# 플롯 초기화
fig, ax = plt.subplots()
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_aspect('equal', adjustable='box')
ax.grid(True)
ax.set_title('Three link robot')
ax.set_xlabel('x axis (m)')
ax.set_ylabel('y axis (m)')

# i = 1:20
for i in range(1, 21):
    theta3 = np.pi/6 + np.pi/60 * i
    theta2 = np.pi/6 + np.pi/60 * i
    theta1 = np.pi/6 + np.pi/60 * i

    # 각 관절 위치
    j1_x = l1 * np.cos(theta1)                                # 1번 조인트 끝
    j1_y = l1 * np.sin(theta1)

    j2_x  = l1*np.cos(theta1) + l2*np.cos(theta1 + theta2)     # 2번 조인트 끝
    j2_y  = l1*np.sin(theta1) + l2*np.sin(theta1 + theta2)

    # 순기구학(말단)
    x = l1*np.cos(theta1) + l2*np.cos(theta1 + theta2) + l3*np.cos(theta1 + theta2 + theta3)
    y = l1*np.sin(theta1) + l2*np.sin(theta1 + theta2) + l3*np.sin(theta1 + theta2 + theta3)

    # 로봇 링크 그리기
    rx = [0.0, j1_x, j2_x, x]
    ry = [0.0, j1_y, j2_y, y]
    ax.plot(rx, ry, '-')
    ax.plot(x, y, '*')  # 말단 표시

# 표시 또는 저장
# plt.savefig("three_link_robot.png", dpi=150)  # GUI를 쓰지 않을 때
plt.show()
