# 5-1 예상문제 1 : 1차계 + PI 제어 계단 응답
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q51_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q51_1_output.txt"

p = {}
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        if line.strip():
            k, v = line.split(); p[k] = float(v)

K, tau, Kp, Ki, Ts = p["K"], p["tau"], p["Kp"], p["Ki"], p["Ts"]
N = round(p["T_end"] / Ts)
y = I = 0.0
ys = []
for k in range(N + 1):
    ys.append(y)
    e = 1.0 - y                                   # 목표 r = 1 (t=0부터 계단)
    u = Kp*e + I
    I += Ki*Ts*e
    y += Ts*(-y + K*u) / tau                       # τ·ẏ = -y + K·u  (오일러)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for t in (1, 2, 5, 10):
        f.write(f"y({t}s) {ys[round(t/Ts)]:.4f}\n")
    f.write(f"overshoot {max(0.0, (max(ys) - 1)*100):.2f} %\n")
