import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import sys

#######################################################################
###   tb = (tf* v_max -qf + q0) / v_max          (v_max가 주어질 때)

###   [수정] a_max가 주어질 때:  qf - q0 = a_max*tb*(tf - tb)
###           tb² - tf*tb + (qf-q0)/a_max = 0
###           coeffs = [1, -tf, (qf-q0) / a_max]
###           roots = np.roots(coeffs)
###           tb = roots.min().real              (작은 근)
###   LSPB 가능 조건: tf² - 4*(qf-q0)/a_max >= 0  →  a_max >= 4*(qf-q0)/tf²

###
###
#######################################################################

csv_path_filename = r"D:\K2027_Program\RBTSW_Results\LSPB_trajectory.csv"

# 파라미터 설정
q0 = np.pi / 6      # 시작 위치 (rad)
qf = np.pi / 2      # 목표 위치 (rad)
tf = 2.0            # 총 시간 (s)
a_max = 2.0         # 최대 가속도 (rad/s²)
t_pts = 1000        # 샘플 포인트 수


def lspb(q0, qf, tf, a_max, t_pts=1000):
 
    # ✅ tb 계산 (이차방정식) ########################################
    coeffs = [1, -tf, (qf-q0) / a_max]
    roots = np.roots(coeffs)
    tb = roots.min().real
    print (f"tb = {tb}")
    ################################################################

    v_max = a_max * tb 
    a = a_max 
    
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



def check_lspb_feasibility(q0, qf, tf, a_max, v_max=None):
    """✅ LSPB 검사 - 올바른 버전"""
    
    delta_q = qf - q0
    h = abs(delta_q)
    sign = np.sign(delta_q) if delta_q != 0 else 1.0
    
    if np.isclose(h, 0.0):
        return True, 0.0, tf, 0.0, "✅ 이동 거리 없음"


    # ✅ 올바른 계수: [1, -tf, h/a_max]
    discriminant = tf**2 - 4.0 * (h / a_max)
    
    if discriminant < -1e-12:
        h_max = 0.25 * a_max * tf**2
        return False, None, None, None, (
            f"❌ 가속도 부족 (필요: {4.0*h/(tf**2):.4f} > a_max: {a_max:.4f})"
        )
    
    discriminant = max(0.0, discriminant)
    
    # ✅ tb 계산
    tb = (tf - np.sqrt(discriminant)) / 2.0
    t_const = tf - 2.0 * tb
    
    if abs(t_const) < 1e-12:
        t_const = 0.0
    
    v_peak = a_max * tb
    v = sign * v_peak
    
    if v_max is not None and v_peak > v_max + 1e-12:
        return False, tb, t_const, v, "❌ 최대 속도 초과"
    
    profile = "삼각형" if np.isclose(t_const, 0.0) else "사다리꼴"
    return True, tb, t_const, v, f"✅ LSPB 가능 ({profile})"


# ===== 메인 실행 =====
if __name__ == "__main__":

    # lspb 적용 가능성 체크
    mode, tb_val, t_cost, v_val, message = check_lspb_feasibility(q0, qf, tf, a_max, v_max=None)
    print(f"mode = {mode}, tb = {tb_val}, message = {message}")
    
    # LSPB 궤적 계산
    t, q, qd, qdd, tb, v_max = lspb(q0, qf, tf, a_max, t_pts)
    
    # CSV 파일 저장
    csv_path, df = save_to_csv(t, q, qd, qdd, csv_path_filename)
    
    print(f"CSV 파일 저장: {csv_path}")
    print("=" * 30)
