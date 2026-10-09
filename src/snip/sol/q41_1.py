# 4-1 예상문제 1 : 무방향 그래프, A에서 모든 노드까지 최단 거리
import heapq

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q41_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q41_1_output.txt"

graph = {}
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        if not line.strip():
            continue
        u, v, w = line.split()
        graph.setdefault(u, {})[v] = float(w)
        graph.setdefault(v, {})[u] = float(w)          # 무방향: 양쪽에 추가

dist = {n: float("inf") for n in graph}
dist["A"] = 0
pq = [(0, "A")]
while pq:
    d, u = heapq.heappop(pq)
    if d > dist[u]:
        continue
    for v, w in graph[u].items():
        if d + w < dist[v]:
            dist[v] = d + w
            heapq.heappush(pq, (dist[v], v))

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for n in sorted(dist):
        f.write(f"{n} {dist[n]:g}\n")
