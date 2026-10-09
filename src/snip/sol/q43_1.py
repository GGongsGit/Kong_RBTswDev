# 4-3 예상문제 1 : 플로이드-워셜 모든 쌍 최단 거리
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q43_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q43_1_output.txt"
INF = float("inf")

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    d = [[INF if v == "INF" else float(v) for v in line.split()] for line in f if line.strip()]
n = len(d)

for k in range(n):
    for i in range(n):
        for j in range(n):
            if d[i][k] + d[k][j] < d[i][j]:
                d[i][j] = d[i][k] + d[k][j]

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for row in d:
        f.write(" ".join("INF" if v == INF else f"{v:g}" for v in row) + "\n")
