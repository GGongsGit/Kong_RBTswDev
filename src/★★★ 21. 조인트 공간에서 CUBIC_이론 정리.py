import numpy as np
import pandas as pd
import sys

# Boundary Condition
theta0 = 0.0      # 시작 위치 (rad)
thetaf = 1.0      # 목표 위치 (rad)
deg_vel0 = 0.0          # 시작 속도 (rad/s)
deg_velf = 0.0          # 종료 속도 (rad/s)
t0 = 0.0          # 경로 총 시간 (초)
tf = 3.0
data_gap = 0.01

# t_total = tf-t0

######## cubic은 3차 다항식이므로 일반식은  theta = a0 + a1*t + a2*(t**2) + a3*(t**3) 임
# 일반식 생성
# theta(t)   = a0 + a1*t + a2*(t**2) + a3*(t**3)
# deg_vel(t) = a1 + 2*a2*t + 3*a3*(t**2)    # theta를 t로 미분
# deg_acc(t) = 2*a2 + 6*a3                  # deg_vel를 t로 미분
# AX = B

######## 일반식에 Boundary Condition을 적용해서 변수의 개수와 동일한 방정식 생성
# 변수가 4개(a0, a1, a2, a3)이므로 방정식 4개 생성
# theta0 = a0 + a1*t0 + a2*(t0**2) + a3*(t0**3)
# deg_vel0 = a1 + 2*a2*t0 + 3*a3*(t0**2)
# thetaf = a0 + a1*tf + a2*(tf**2) + a3*(tf**3)
# deg_velf = a1 + 2*a2*tf + 3*a3*(tf**2)


def cubic_joint(t0, tf, theta0, thetaf, deg_vel0, deg_velf, data_gap):
    

    A = np.array([[1, t0, t0**2, t0**3],
                 [0, 1, 2*t0, 3*(t0**2)],
                 [1, tf, tf**2, tf**3],
                 [0, 1, 2*tf, 3*(tf**2)]])

    B = np.array([theta0, deg_vel0, thetaf, deg_velf])
    X = np.linalg.solve(A,B)

    print("===============================================")
    print ("X : = ", X)
    print (f"a0 = {np.round(X[0], 4)}, a1= {np.round(X[1], 4)}, a2= {np.round(X[2], 4)}, a3 = {np.round(X[3], 4)}")
    print("===============================================")

    #############################################################
    t = np.arange(t0, tf + data_gap/2, data_gap)   # [수정] tf 포함 (부동소수 오차로 한 칸 더 생기는 것 방지)
    # print(t)
    # sys.exit()     # [수정] 확인용 종료 줄 비활성화 → 궤적 계산·CSV 저장까지 실행
    theta = X[0] + X[1]*(t-t0) + X[2]*(t-t0)**2 + X[3]*(t-t0)**3
    deg_vel = X[1] + 2*X[2]*(t-t0) + 3*X[3]*(t-t0)**2
    deg_acc = 2*X[2] + 6*X[3]*(t-t0)
    #############################################################

    return t, theta, deg_vel, deg_acc


def save_to_csv(t, theta, vel, acc, filename='cubic_joint_trajectory.csv'):
    # Create DataFrame
    df = pd.DataFrame({
        'Time(s)': t,
        'theta(rad) - position': theta,
        'deg_Vel(rad/s)': vel,
        'deg_acc(rad/s²)': acc
    })
    
    # Save to CSV
    df.to_csv(filename, index=False)

    print(f"✓ CSV file saved successfully: '{filename}'")
    print(f"  - Total rows: {len(df)}")
    print(f"  - Time range: {t[0]:.2f}s ~ {t[-1]:.2f}s")
    
    return df

# 궤적 계산
t, theta, deg_vel, deg_acc = cubic_joint(t0, tf, theta0, thetaf, deg_vel0, deg_velf, data_gap)

# CSV 파일로 저장
df = save_to_csv(t, theta, deg_vel, deg_acc, filename='cubic_joint_trajectory_kong.csv')

# 처음 10개 행 표시
print("\n[ 처음 10개 데이터 ]")
print(df.head(10).to_string(index=False))

