import numpy as np


def ik_1link(x, y, L):
    r = np.hypot(x, y)
    print(f"r= {r}")
    if abs(r - L) > 1e-9:
        raise ValueError("Target is not exactly on the circle of radius L.")
    theta = np.atan2(y, x)
    return theta, np.degrees(theta)

# 예시
L = 1.0
x, y = 0.6, 0.8
theta_rad, theta_deg = ik_1link(x, y, L)

print("\ntheta(rad) =", np.round(theta_rad, 3))
print("theta(deg) =", np.round(theta_deg, 3))