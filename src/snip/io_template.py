import numpy as np

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\input_data.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\output_data.txt"
L1, L2, L3 = 0.5, 0.5, 0.5          # 링크 길이 (m)

def fk_3link(th1_deg, th2_deg, th3_deg):
    t1 = np.deg2rad(th1_deg)          # 각도는 반드시 rad로 변환
    t12 = t1 + np.deg2rad(th2_deg)
    t123 = t12 + np.deg2rad(th3_deg)
    x = L1*np.cos(t1) + L2*np.cos(t12) + L3*np.cos(t123)
    y = L1*np.sin(t1) + L2*np.sin(t12) + L3*np.sin(t123)
    return x, y

# 1) 읽기: 한 줄 = "θ1 θ2 θ3"
rows = []
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if not line:                  # 빈 줄 건너뛰기
            continue
        th = [float(v) for v in line.replace(",", " ").split()]
        rows.append(th)

# 2) 계산 + 3) 쓰기
with open(OUT_FILE, "w", encoding="utf-8-sig") as f:
    for th in rows:
        x, y = fk_3link(*th)
        f.write(f"{x:.2f} {y:.2f}\n")
