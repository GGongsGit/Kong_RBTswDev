# 3-2 예상문제 2 : LSPB 가능 여부 판정
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q32_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q32_2_output.txt"

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    fout.write("dq tf a_max a_min result\n")
    for line in fin:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        dq, tf, a = map(float, line.split())
        a_min = 4*abs(dq) / tf**2                       # 판별식 tf² - 4Δq/a ≥ 0
        if abs(a - a_min) < 1e-9:
            res = "BBPB(triangle)"
        elif a > a_min:
            res = "LSPB(trapezoid)"
        else:
            res = "IMPOSSIBLE"
        fout.write(f"{dq} {tf} {a} {a_min:.3f} {res}\n")
