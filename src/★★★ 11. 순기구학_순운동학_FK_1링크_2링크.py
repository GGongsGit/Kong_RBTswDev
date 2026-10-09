import numpy as np

th_data_pathfilename = r"C:\KONG_2027Prg\RBTSW_Results\Theta_data.txt"
PxPy_pathfilename = r"C:\KONG_2027Prg\RBTSW_Results\PxPy_data.txt"

l1 = 0.85
l2 = 0.65
PI = np.pi


# ============================================================================
# 【 1 LINK 】
# ============================================================================

th1_deg = 30
th1_rad = th1_deg * PI / 180


Px1 = l1 * np.cos(th1_rad)
Py1 = l1 * np.sin(th1_rad)

print(f"Px1 = {np.round(Px1, 4)},   Py1 = {np.round(Py1, 4)}")



# ============================================================================
# 【 2 LINK - 데이터 읽기 함수 】
# ============================================================================

def theta_data(filename):
    th1_deg = []
    th2_deg = []
    
    with open(filename, mode='r', encoding='utf-8') as file:
        for line in file:
            # 데이터 파싱 (쉼표 또는 공백 기준)
            data = line.replace(',', ' ').split()
            th1_deg.append(float(data[0]))
            th2_deg.append(float(data[1]))
    return th1_deg, th2_deg


# ============================================================================
# 【 2-Link 순기구학 계산 함수 】
# ============================================================================

def calculate_2link_position(l1, l2, th1_deg, th2_deg):
    # ✅ 수정: numpy 배열로 변환 필수!
    th1_rad = np.array(th1_deg) * PI / 180
    th2_rad = np.array(th2_deg) * PI / 180
    
    # Joint 1 위치
    Px1 = l1 * np.cos(th1_rad)
    Py1 = l1 * np.sin(th1_rad)
    
    # Joint 2 위치 (엔드 이펙터)
    Px2 = Px1 + l2 * np.cos(th1_rad + th2_rad)
    Py2 = Py1 + l2 * np.sin(th1_rad + th2_rad)
    
    return Px1, Py1, Px2, Py2


# ============================================================================
# 【 txt 파일로 저장 함수 】
# ============================================================================

def save_PxPy_data_txt(filename, th1_deg, th2_deg, Px1, Py1, Px2, Py2):
    with open(filename, mode='w', encoding='utf-8') as file:
        file.write("Px0(m) Py0(m) Px1(m) Py1(m) Px2(m) Py2(m)\n")
        for i in range(len(Px1)):
            file.write(f"0 0 {Px1[i]:0.4f} {Py1[i]:0.4f} {Px2[i]:0.4f} {Py2[i]:0.4f}\n")
    return True
    

# ============================================================================
# 【 메인 프로그램 】
# ============================================================================

if __name__ == "__main__":
    
    th1_deg, th2_deg = theta_data(th_data_pathfilename)
    print(f"th1_deg: {th1_deg}")
    print(f"th2_deg: {th2_deg}")
    print()
    
    # Step 2: 순기구학 계산
    print("-" * 20)
    Px1, Py1, Px2, Py2 = calculate_2link_position(l1, l2, th1_deg, th2_deg)
    save_PxPy_data_txt(PxPy_pathfilename, th1_deg, th2_deg, Px1, Py1, Px2, Py2) 
