import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import sys

#######################################################################
###   [수정] BBPB(Bang-Bang Parabolic Blend) = 등속 구간이 없는 LSPB
###   tb = tf/2 로 고정되므로 가속도는 고를 수 없고 아래 값으로 '정해진다'
###           qf - q0 = a*tb*(tf - tb) = a*tf²/4
###           a = 4*(qf - q0) / tf**2
###   a_max는 '이 가속도를 낼 수 있는지' 확인용으로만 쓴다:  |a| <= a_max

###
###
#######################################################################

csv_path_filename = r"C:\KONG_2027Prg\RBTSW_Results\BBPB_trajectory.csv"

# 파라미터 설정
q0 = np.pi / 6      # 시작 위치 (rad)
qf = np.pi / 2      # 목표 위치 (rad)
tf = 2.0            # 총 시간 (s)
a_max = 2.0         # 최대 가속도 (rad/s²)
t_pts = 1000        # 샘플 포인트 수




def bbpb(q0, qf, tf, a_max, t_pts=1000):

    ###################################
    ############## BBPB ###############
    ###################################
    tb = tf/2
    a = 4*(qf - q0) / tf**2          # [수정] a_max가 아니라 Δq와 tf로 계산
    if abs(a) > a_max:
        print(f"경고: 필요한 가속도 {abs(a):.4f} > a_max {a_max} → 이 tf로는 불가능")
    ###################################

    v_max = a * tb 
    
    # 시간 배열
    t = np.linspace(0, tf, t_pts)
    q = np.zeros_like(t)
    qd = np.zeros_like(t)
    qdd = np.zeros_like(t)
    
    # 구간 1: 가속
    mask1 = (t >= 0) & (t <= tb)
    q[mask1] = q0 + 0.5 * a * (t[mask1] ** 2)
    qd[mask1] = a * t[mask1]
    qdd[mask1] = a
    
    q_at_tb = q0 + 0.5 * a * (tb ** 2)
    
    # 구간 2: 등속
    mask2 = (t > tb) & (t <= tf - tb)
    q[mask2] = q_at_tb + v_max * (t[mask2] - tb)
    qd[mask2] = v_max
    qdd[mask2] = 0

    q_at_tf_tb = q_at_tb + v_max*(tf-2*tb)

    
    # 구간 3: 감속
    mask3 = (t > tf - tb) & (t <= tf)
    # tau = tf - t[mask3]
    q[mask3] = q_at_tb + v_max*(tf-2*tb) + 0.5*a*(tb**2) - 0.5 * a * ((tf-t[mask3])** 2)
    qd[mask3] = a * (tf-t[mask3])
    qdd[mask3] = -a
    
    return t, q, qd, qdd, tb, v_max


def save_to_csv(t, q, qd, qdd, csv_path_filename):
    # DataFrame 생성
    df = pd.DataFrame({
        'Time(s)': np.round(t, 3),
        'Pos(rad)': np.round(q, 4),
        'Vel(rad/s)': np.round(qd, 4),
        'Acc(rad/s^2)': np.round(qdd, 4)
    })

  
    # CSV 저장
    df.to_csv(csv_path_filename, index=False, encoding='utf-8-sig')
    
    return csv_path_filename, df


# ===== 메인 실행 =====
if __name__ == "__main__":

    # BBPB 궤적 계산
    t, q, qd, qdd, tb, v_max = bbpb(q0, qf, tf, a_max, t_pts)
    print(f"tb = {tb:.4f} s, a = {4*(qf-q0)/tf**2:.4f} rad/s², q(tf) = {q[-1]:.4f} rad (목표 {qf:.4f})")
    
    # CSV 파일 저장
    csv_path, df = save_to_csv(t, q, qd, qdd, csv_path_filename)
    
    print(f"CSV 파일 저장: {csv_path}")
    print("=" * 30)
