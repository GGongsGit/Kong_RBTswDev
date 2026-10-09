from heapq import heappush, heappop
from math import sqrt

def astar(grid, start, goal):
    R, C = len(grid), len(grid[0])
    gr, gc = goal
    NEI = [(1,0,1), (-1,0,1), (0,1,1), (0,-1,1),                 # (행 변화, 열 변화, 비용)
           (1,1,sqrt(2)), (1,-1,sqrt(2)), (-1,1,sqrt(2)), (-1,-1,sqrt(2))]

    def h(r, c):                                                 # 유클리드 휴리스틱
        return sqrt((r - gr)**2 + (c - gc)**2)

    open_heap = [(h(*start), start)]
    g = {start: 0}
    came_from = {}
    while open_heap:
        _, cur = heappop(open_heap)
        if cur == goal:                                          # 목표 도착 → 역추적
            path = [cur]
            while cur in came_from:
                cur = came_from[cur]
                path.append(cur)
            return path[::-1], g[goal]
        r, c = cur
        for dr, dc, cost in NEI:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 0:
                ng = g[cur] + cost
                if ng < g.get((nr, nc), float('inf')):
                    g[(nr, nc)] = ng
                    came_from[(nr, nc)] = cur
                    heappush(open_heap, (ng + h(nr, nc), (nr, nc)))
    return None, float('inf')

grid = [[0,0,0,1,0,1,0],
        [1,1,0,1,0,1,0],
        [0,0,0,0,0,1,0],
        [0,1,0,0,1,0,0],
        [0,1,1,0,1,1,0],
        [0,1,0,0,0,0,0],
        [0,0,0,1,0,1,0]]
path, cost = astar(grid, (0, 0), (6, 6))
print(f"cost = {cost:.3f}, nodes = {len(path)}")   # cost = 9.657, nodes = 9
