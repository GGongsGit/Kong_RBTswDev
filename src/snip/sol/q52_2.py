# 6-1 예상문제 2 : 1링크 중력 토크와 최대값
import math

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q52_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q52_2_output.txt"
m, lc, g = 3.0, 0.4, 9.81                         # 질량 kg, 무게중심 거리 m

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    angles = [float(s) for s in f.read().split()]

taus = [m*g*lc*math.cos(math.radians(a)) for a in angles]   # θ=0 이 수평
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("deg tau(Nm)\n")
    for a, t in zip(angles, taus):
        f.write(f"{a:.0f} {round(t, 3) + 0.0:.3f}\n")
    i = max(range(len(taus)), key=lambda k: abs(taus[k]))
    f.write(f"max |tau| {abs(taus[i]):.3f} at {angles[i]:.0f} deg\n")
