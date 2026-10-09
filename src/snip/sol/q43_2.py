# 4-3 예상문제 2 : 플로이드-워셜 + 경로 복원 (next 행렬)
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q43_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q43_2_output.txt"
INF = float("inf")
QUERIES = [(1, 3), (3, 1), (0, 2)]

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    d = [[INF if v == "INF" else float(v) for v in line.split()] for line in f if line.strip()]
n = len(d)
nxt = [[j if d[i][j] < INF and i != j else None for j in range(n)] for i in range(n)]

for k in range(n):
    for i in range(n):
        for j in range(n):
            if d[i][k] + d[k][j] < d[i][j]:
                d[i][j] = d[i][k] + d[k][j]
                nxt[i][j] = nxt[i][k]                 # i→j 첫 걸음은 i→k 첫 걸음과 같음

def path(i, j):
    if nxt[i][j] is None:
        return None
    p = [i]
    while i != j:
        i = nxt[i][j]; p.append(i)
    return p

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for s, g in QUERIES:
        p = path(s, g)
        f.write(f"{s}->{g}: " + ("NO PATH" if p is None else f"{'-'.join(map(str, p))} cost={d[s][g]:g}") + "\n")
