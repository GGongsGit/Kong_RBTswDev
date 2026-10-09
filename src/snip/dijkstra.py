import heapq

def dijkstra(graph, start):
    dist = {n: float('inf') for n in graph}
    prev = {n: None for n in graph}
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:                 # 이미 더 짧은 길이 확정됨
            continue
        for v, w in graph[u].items():
            if d + w < dist[v]:
                dist[v] = d + w
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))
    return dist, prev

def build_path(prev, goal):
    path = []
    while goal is not None:
        path.append(goal)
        goal = prev[goal]
    return path[::-1]

graph = {'A': {'B': 5, 'C': 4}, 'B': {'A': 5, 'C': 2, 'D': 5},
         'C': {'A': 4, 'B': 2, 'D': 1}, 'D': {'B': 5, 'C': 1}}
dist, prev = dijkstra(graph, 'A')
print(dist['D'], build_path(prev, 'D'))   # 5 ['A', 'C', 'D']
