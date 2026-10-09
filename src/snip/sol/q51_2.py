# 5-1 예상문제 2 : 이산 PID 출력 계산
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q51_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q51_2_output.txt"
Kp, Ki, Kd, Ts = 2.0, 0.5, 0.1, 0.1

errs = []
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        if line.strip() and not line.startswith("#"):
            errs.append(float(line.split()[1]))

I, e_prev = 0.0, errs[0]                          # 첫 샘플은 미분항 0
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("k e P I D u\n")
    for k, e in enumerate(errs):
        I += Ki*Ts*e                              # 적분: Σ Ki·Ts·e
        D = Kd*(e - e_prev)/Ts                    # 미분: Kd·Δe/Ts
        P = Kp*e
        f.write(f"{k} {e:.2f} {P:.3f} {I:.3f} {D:.3f} {P + I + D:.3f}\n")
        e_prev = e
