import numpy as np

L = 1.0
Px, Py = 0.6, 0.8

def ik_1link(x, y, L):
    r = np.hypot(x, y)
    # print(f"r= {r}")
    if abs(r - L) > 1e-9:
        raise ValueError("Target is not exactly on the circle of radius L.")
    theta = np.atan2(y, x)
    return theta, np.degrees(theta)


if __name__ == "__main__":

    theta_rad, theta_deg = ik_1link(Px, Py, L)

    print(f"theta(rad) = {np.round(theta_rad, 3)}")
    print(f"theta(deg) = {np.round(theta_deg, 3)}")