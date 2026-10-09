# 8-1 예상문제 2 : 저분산(systematic) 재샘플링
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q71_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q71_2_output.txt"
R0 = 0.05                                       # 시험에서는 난수 대신 고정값을 준다

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    w = [float(s) for s in f if s.strip() and not s.startswith("#")]
M = len(w)

idx, c, i = [], w[0], 0
for m in range(M):
    u = (R0 + m) / M                              # 0.05/5, 1.05/5, ...  간격 1/M
    while u > c:
        i += 1; c += w[i]
    idx.append(i)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("selected " + " ".join(map(str, idx)) + "\n")
    f.write("counts " + " ".join(str(idx.count(k)) for k in range(M)) + "\n")
