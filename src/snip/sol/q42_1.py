# 4-2 예상문제 1 : 4방향 + 맨해튼 A*
from heapq import heappush, heappop

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q42_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q42_1_output.txt"
START, GOAL = (0, 0), (4, 4)

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    grid = [[int(v) for v in line.split()] for line in f if line.strip()]
R, C = len(grid), len(grid[0])

def h(p):
    return abs(p[0] - GOAL[0]) + abs(p[1] - GOAL[1])

g = {START: 0}; came = {}; pq = [(h(START), START)]
while pq:
    _, cur = heappop(pq)
    if cur == GOAL:
        break
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        n = (cur[0] + dr, cur[1] + dc)
        if 0 <= n[0] < R and 0 <= n[1] < C and grid[n[0]][n[1]] == 0:
            if g[cur] + 1 < g.get(n, float("inf")):
                g[n] = g[cur] + 1; came[n] = cur
                heappush(pq, (g[n] + h(n), n))

path = [GOAL]
while path[-1] in came:
    path.append(came[path[-1]])
path.reverse()

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("Step 행 열\n")
    for i, (r, c) in enumerate(path, 1):
        f.write(f"{i} {r} {c}\n")
    f.write(f"cost {g[GOAL]}\n")
