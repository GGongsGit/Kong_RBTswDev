# 4-1 예상문제 2 : 방향 그래프, 출발→도착 경로와 비용
import heapq

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q41_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q41_2_output.txt"

graph, start, goal = {}, None, None
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        p = line.split()
        if not p:
            continue
        if p[0] == "start": start = p[1]; continue
        if p[0] == "goal":  goal = p[1];  continue
        graph.setdefault(p[0], {})[p[1]] = float(p[2])
        graph.setdefault(p[1], {})

def dijkstra(s, g):
    dist = {n: float("inf") for n in graph}; prev = {n: None for n in graph}
    dist[s] = 0; pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == g:
            break
        if d > dist[u]:
            continue
        for v, w in graph[u].items():
            if d + w < dist[v]:
                dist[v], prev[v] = d + w, u
                heapq.heappush(pq, (dist[v], v))
    if dist[g] == float("inf"):
        return None, None
    path = [g]
    while prev[path[-1]] is not None:
        path.append(prev[path[-1]])
    return path[::-1], dist[g]

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for s, g in [(start, goal), (goal, start)]:          # 정방향, 역방향 둘 다
        path, c = dijkstra(s, g)
        f.write(f"{s}->{g}: " + ("NO PATH" if path is None else f"{' '.join(path)} cost={c:g}") + "\n")
