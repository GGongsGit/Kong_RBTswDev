# 4-2 예상문제 2 : 8방향 + 유클리드 A*, 대각선 모서리 통과 금지
from heapq import heappush, heappop
from math import sqrt, hypot

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q42_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q42_2_output.txt"
START, GOAL = (0, 0), (5, 5)
NEI = [(1,0,1), (-1,0,1), (0,1,1), (0,-1,1),
       (1,1,sqrt(2)), (1,-1,sqrt(2)), (-1,1,sqrt(2)), (-1,-1,sqrt(2))]

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    grid = [[int(v) for v in line.split()] for line in f if line.strip()]
R, C = len(grid), len(grid[0])

def free(r, c):
    return 0 <= r < R and 0 <= c < C and grid[r][c] == 0

h = lambda p: hypot(p[0] - GOAL[0], p[1] - GOAL[1])
g = {START: 0.0}; came = {}; pq = [(h(START), START)]
while pq:
    _, cur = heappop(pq)
    if cur == GOAL:
        break
    r, c = cur
    for dr, dc, w in NEI:
        nr, nc = r + dr, c + dc
        if not free(nr, nc):
            continue
        if dr and dc and (not free(r, nc) or not free(nr, c)):   # 모서리 통과 금지
            continue
        if g[cur] + w < g.get((nr, nc), float("inf")):
            g[(nr, nc)] = g[cur] + w; came[(nr, nc)] = cur
            heappush(pq, (g[(nr, nc)] + h((nr, nc)), (nr, nc)))

path = [GOAL]
while path[-1] in came:
    path.append(came[path[-1]])
path.reverse()

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("Step 행 열 누적거리\n")
    acc = 0.0
    for i, (r, c) in enumerate(path):
        if i:
            acc += hypot(r - path[i-1][0], c - path[i-1][1])
        f.write(f"{i+1} {r} {c} {acc:.3f}\n")
