# 8-1 예상문제 1 : 1차원 파티클 가중치·정규화·추정
import math

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q71_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q71_1_output.txt"
LANDMARK, Z, SIGMA = 10.0, 3.0, 0.5

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    xs = [float(s) for s in f if s.strip() and not s.startswith("#")]

w = [math.exp(-((LANDMARK - x) - Z)**2 / (2*SIGMA**2)) for x in xs]   # 가우시안 우도
s = sum(w)
w = [v / s for v in w]                                                # 정규화
est = sum(x*v for x, v in zip(xs, w))                                 # 가중 평균

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("x expected_z weight\n")
    for x, v in zip(xs, w):
        f.write(f"{x:.1f} {LANDMARK - x:.1f} {v:.4f}\n")
    f.write(f"estimate {est:.3f}\n")
