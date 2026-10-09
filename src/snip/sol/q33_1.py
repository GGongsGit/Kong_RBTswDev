# 3-3 예상문제 1 : RRT* 트리에서 경로 역추적
import math

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q33_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q33_1_output.txt"
GOAL = (4.5, 4.5)
GOAL_TOL = 1.0

pos, parent = {}, {}
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        if not line.strip() or line.startswith("#"):
            continue
        i, x, y, p = line.split()
        pos[int(i)] = (float(x), float(y)); parent[int(i)] = int(p)

def cost(i):                                          # 루트까지 누적 거리
    c = 0.0
    while parent[i] != -1:
        c += math.dist(pos[i], pos[parent[i]]); i = parent[i]
    return c

cands = [i for i in pos if math.dist(pos[i], GOAL) <= GOAL_TOL]
best = min(cands, key=lambda i: cost(i) + math.dist(pos[i], GOAL))

path, i = [], best
while i != -1:
    path.append(i); i = parent[i]
path.reverse()

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("path " + " -> ".join(map(str, path)) + " -> GOAL\n")
    f.write(f"length {cost(best) + math.dist(pos[best], GOAL):.3f}\n")
