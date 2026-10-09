import os
import numpy as np
import matplotlib.pyplot as plt

# 링크 길이
l1 = 0.4
l2 = 0.4

# 플롯 설정
plt.figure()
plt.axis([-1, 1, -1, 1])
plt.gca().set_aspect('equal', adjustable='box')
plt.title('2 link robot')
plt.xlabel('x axis (m)')
plt.ylabel('y axis (m)')
plt.grid(True)

# 궤적 포인트 저장용
traj_x = []
traj_y = []

# i = 1, 2, 3
for i in range(1, 5):
    theta2 = np.pi/6 * i
    theta1 = np.pi/6 * i

    # 첫 번째 조인트 위치
    x1 = l1 * np.cos(theta1)
    y1 = l1 * np.sin(theta1)

    # 끝단(EE) 위치 (순기구학)
    x = l1 * np.cos(theta1) + l2 * np.cos(theta1 + theta2)
    y = l1 * np.sin(theta1) + l2 * np.sin(theta1 + theta2)

    # 로봇 링크(원점 -> 조인트1 -> EE) 그리기
    rx = [0.0, x1, x]
    ry = [0.0, y1, y]
    plt.plot(rx, ry, 'b-')       # 링크
    plt.plot(rx, ry, 'ro')       # 조인트 표시

    # EE 좌표 텍스트 표시
    plt.text(x + 0.05, y + 0.05, f'({x:.2f}, {y:.2f})', fontsize=9, color='blue')

    # 궤적 누적
    traj_x.append(x)
    traj_y.append(y)

# EE 궤적 표시
plt.plot(traj_x, traj_y, 'k*')

plt.show()
