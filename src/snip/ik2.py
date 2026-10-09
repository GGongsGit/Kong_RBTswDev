import numpy as np

def ik_2link(l1, l2, x, y):
    r = np.hypot(x, y)
    if r > l1 + l2 or r < abs(l1 - l2):
        raise ValueError("도달 불가능한 위치")
    c2 = (x**2 + y**2 - l1**2 - l2**2) / (2*l1*l2)     # 코사인 법칙
    c2 = np.clip(c2, -1.0, 1.0)                        # 수치 오차 방지
    sols = []
    for s in (+1, -1):                                 # θ2 부호로 두 해
        t2 = s*np.arccos(c2)
        t1 = np.arctan2(y, x) - np.arctan2(l2*np.sin(t2), l1 + l2*np.cos(t2))
        sols.append((np.degrees(t1), np.degrees(t2)))
    return sols   # [(θ2>0 해), (θ2<0 해)]

for t1, t2 in ik_2link(1.0, 1.0, 1.2, 0.7):
    print(f"θ1={t1:.3f}°, θ2={t2:.3f}°")
