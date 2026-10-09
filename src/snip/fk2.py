import numpy as np

def fk_2link(l1, l2, th1_deg, th2_deg):
    t1 = np.deg2rad(th1_deg)
    t2 = np.deg2rad(th2_deg)
    x1, y1 = l1*np.cos(t1), l1*np.sin(t1)              # 관절 2 위치
    x2 = x1 + l2*np.cos(t1 + t2)                       # 말단(End-effector)
    y2 = y1 + l2*np.sin(t1 + t2)
    return x1, y1, x2, y2

x1, y1, x2, y2 = fk_2link(0.85, 0.65, 30, 45)
print(f"말단 = ({x2:.4f}, {y2:.4f})")   # 말단 = (0.9044, 1.0529)
