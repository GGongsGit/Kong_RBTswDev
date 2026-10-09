import numpy as np
import matplotlib.pyplot as plt
import sys

### 경계 조건 ###########################################################
### q(0) = q0,  v(0) = 0
### q(tf) = qf, v(tf) = 0
### ta = tb   대칭 관계이므로
#######################################################################

### 수식 유도 : 전체 증가분은 각 구간 별 증가분의 합과 같음  #################
### 위치 이동 증가 분 : qf-q0
### 구간 별 증가분의 합 : 델타q1 + 델타q2 + 델타q3
###       qf-q0 = 델타q1 + 델타q2 + 델타q3
###  
###  v_max = a_max * tb, t_const = tf - 2tb
###  
###  (0 <= t <= tb) 에서      델타 q1 = (1/2)*a_max*(tb**2)
###  (tb < t <= tf - tb) 에서 델타 q2 = v_max*(tf-2*tb) = a_max*tb*(tf-2*tb)
###  (tf - tb < t <= tf) 에서 델타 q3 = (1/2)*a_max*(tb**2) 
###  
###  qf-q0 = (1/2)*a_max*(tb**2) + a_max*tb*(tf-2*tb) + (1/2)*a_max*(tb**2)
###  tb**2 - tf*tb + (qf-q0)/a_max = 0
###  coeffs = [1, -tf, (qf-q0)/a_max]
#######################################################################

# 파라미터 설정
q0 = np.pi / 6      # 시작 위치 (rad)
qf = np.pi / 2      # 목표 위치 (rad)
tf = 2.0            # 총 시간 (s)
a_max = 2.0         # 최대 가속도 (rad/s²)

def tb_cal(q0, qf, tf, a_max, t_pts=1000):
 
    # ✅ tb 계산 (이차방정식) #############################################
    coeffs = [1, -tf, (qf-q0) / a_max]
    roots = np.roots(coeffs)
    tb = roots.min().real       # .real은 허수부를 버리고 실수부만 가져오는 것
    print (f"tb = {tb}")
    #####################################################################

# ===== 메인 실행 =====
if __name__ == "__main__":

    # LSPB tb
    tb_cal(q0, qf, tf, a_max)



    # # ✅ tb1 계산 (이차방정식) ########################################
    # coeffs1 = [1, 3, 2]
    # print (f"coeffs = {coeffs1}")
    # roots1 = np.roots(coeffs1)
    # print (f"roots1 = {roots1}")
    # tb1 = roots.min().real
    # print (f"tb1 = {tb1}")
    # ################################################################


    