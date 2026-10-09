print("################################################################")
print("################################################################")
print("################################################################")


import numpy as np
import sys
import matplotlib.pyplot as plt


inputfilePath = "D:/K2027_Program/07.로봇SW개발기사/data/input.txt"
outputfilePath = "D:/K2027_Program/07.로봇SW개발기사/data/output.txt"


datalist = []  # 전체 데이터를 저장할 리스트

with open(inputfilePath, 'r', encoding='utf-8') as f:
    for text in f:  # 파일 객체 f를 반복
        text = text.strip()  # 줄 끝의 개행 문자 제거
        if text:  # 빈 줄 제외
            words = text.split(" ")  # 공백으로 분할
            datalist.append(words)  # 리스트에 추가

for i, data in enumerate(datalist):
    print(data)
    l1 = float(data[0])    # link 1 길이
    l2 = float(data[1])    # link 2 길이
    x  = float(data[2])    # x축 값 
    y  = float(data[3])    # y축 값

    r2 = x**2 + y**2
    r = np.hypot(x, y)

    # 도달 가능성 확인
    if r > (l1 + l2) + 1e-9 or r < abs(l1 - l2) - 1e-9:
        raise ValueError("Target point is unreachable.")
    else:
        print()
        print("Data is no problem !!")

    # [수정] atan(y/x) → arctan2(y, x) : x<0(2·3사분면), x=0 에서도 올바른 각도
    # [수정] 중간값 반올림 제거 : 반올림은 파일에 쓸 때(:.2f)만 한다
    # [수정] arccos 인자는 수치 오차로 ±1을 살짝 넘을 수 있으므로 clip
    d_val = np.hypot(x, y)
    phi   = np.arctan2(y, x)
    beta  = np.arccos(np.clip((l1**2 + d_val**2 - l2**2)/(2*l1*d_val), -1.0, 1.0))
    gamma = np.arccos(np.clip((d_val**2 - l1**2 - l2**2)/(2*l1*l2), -1.0, 1.0))
    theta1_elbup = phi + beta
    theta1_elbdn = phi - beta
    theta2_elbup = -gamma
    theta2_elbdn =  gamma

    print("theta1_theta2_elbup_rad : ", theta1_elbup, theta2_elbup)
    print("theta1_theta2_elbdn_rad : ", theta1_elbdn, theta2_elbdn)
    print("theta1_theta2_elbup_degree : ", np.degrees(theta1_elbup),  np.degrees(theta2_elbup))
    print("theta1_theta2_elbdn_degree : ", np.degrees(theta1_elbdn),  np.degrees(theta2_elbdn))
    print("##############################################################3")

    # ===== Elbow Up 좌표 계산 =====
    x1_up = l1 * np.cos(theta1_elbup)
    y1_up = l1 * np.sin(theta1_elbup)
    x2_up = x1_up + l2 * np.cos(theta1_elbup + theta2_elbup)
    y2_up = y1_up + l2 * np.sin(theta1_elbup + theta2_elbup)
    
    # ===== Elbow Down 좌표 계산 =====
    x1_dn = l1 * np.cos(theta1_elbdn)
    y1_dn = l1 * np.sin(theta1_elbdn)
    x2_dn = x1_dn + l2 * np.cos(theta1_elbdn + theta2_elbdn)
    y2_dn = y1_dn + l2 * np.sin(theta1_elbdn + theta2_elbdn)


    mode = 'w' if i == 0 else 'a' 
    with open(outputfilePath, mode, encoding='utf-8') as f:
        if i == 0:
           f.write("No l1 l2 x y t1_eu t2_eu x1_up y1_up x2_up y2_up t1_ed t2_ed x1_dn y1_dn x2_dn y2_dn\n")
        f.write(f"{i+1} ")
        f.write(f"{l1} {l2} {x} {y} ")
        f.write(f"{np.degrees(theta1_elbup):.2f} {np.degrees(theta2_elbup):.2f} ")
        f.write(f"{x1_up:.2f} {y1_up:.2f} {x2_up:.2f} {y2_up:.2f} ")
        f.write(f"{np.degrees(theta1_elbdn):.2f} {np.degrees(theta2_elbdn):.2f} ")
        f.write(f"{x1_dn:.2f} {y1_dn:.2f} {x2_dn:.2f} {y2_dn:.2f}\n")

