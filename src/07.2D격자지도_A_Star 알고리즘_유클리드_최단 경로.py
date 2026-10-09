# A* Path Planning on 5x5 Grid (8-connected only)
# - 8방향(상하좌우 + 대각선) 이동으로 최단 경로 탐색
# - 경로 단계 번호 및 누적 cost를 흰색 글자로 표시

from __future__ import annotations
import math, heapq
from typing import List, Tuple, Optional, Dict, Callable
import numpy as np
import matplotlib.pyplot as plt

Grid = List[List[int]]   # 0=free, 1=obstacle
Coord = Tuple[int, int]  # (x, y)

# 8방향 이동: 상하좌우 4개 + 대각선 4개
DIRS8 = [(1, 0), (-1, 0), (0, 1), (0, -1),
         (1, 1), (1, -1), (-1, 1), (-1, -1)]

# ---------- A* core ----------
def euclidean(a: Coord, b: Coord) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])

def neighbors_xy(x: int, y: int, W: int, H: int) -> List[Coord]:
    res = []
    for dx, dy in DIRS8:
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H:
            res.append((nx, ny))
    return res

def step_cost(a: Coord, b: Coord) -> float:
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return math.sqrt(2.0) if dx == 1 and dy == 1 else 1.0

def reconstruct(came_from: Dict[Coord, Coord], goal: Coord) -> List[Coord]:
    path = [goal]
    cur = goal
    while cur in came_from:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path

def a_star(grid: Grid, start: Coord, goal: Coord,
           heuristic: Callable[[Coord, Coord], float] = euclidean) -> Optional[List[Coord]]:
    H, W = len(grid), len(grid[0])
    sx, sy = start; gx, gy = goal
    if not (0 <= sx < W and 0 <= sy < H and 0 <= gx < W and 0 <= gy < H):
        return None
    if grid[sy][sx] == 1 or grid[gy][gx] == 1:
        return None

    g: Dict[Coord, float] = {start: 0.0}
    f: Dict[Coord, float] = {start: heuristic(start, goal)}
    came_from: Dict[Coord, Coord] = {}
    pq: List[Tuple[float, float, int, int]] = []
    heapq.heappush(pq, (f[start], heuristic(start, goal), sx, sy))
    closed = set()

    while pq:
        _, _, x, y = heapq.heappop(pq)
        u = (x, y)
        if u in closed:
            continue
        if u == goal:
            return reconstruct(came_from, goal)
        closed.add(u)

        for v in neighbors_xy(x, y, W, H):
            vx, vy = v
            if grid[vy][vx] == 1:
                continue
            tentative_g = g[u] + step_cost(u, v)
            if tentative_g < g.get(v, float('inf')):
                came_from[v] = u
                g[v] = tentative_g
                fv = tentative_g + heuristic(v, goal)
                f[v] = fv
                heapq.heappush(pq, (fv, heuristic(v, goal), vx, vy))
    return None

# ---------- helpers ----------
def total_path_cost(path: List[Coord]) -> float:
    if not path or len(path) < 2:
        return 0.0
    return sum(step_cost(path[i], path[i + 1]) for i in range(len(path) - 1))

def cumulative_costs(path: List[Coord]) -> List[float]:
    cum = [0.0]
    for i in range(1, len(path)):
        cum.append(cum[-1] + step_cost(path[i - 1], path[i]))
    return cum

def draw_case(ax, grid: Grid, start: Coord, goal: Coord, title: str):
    arr = np.array(grid)
    ax.imshow(arr, origin="lower", interpolation="nearest")
    ax.set_xlabel("x"); ax.set_ylabel("y")

    path = a_star(grid, start, goal)
    if path is None:
        ax.set_title(f"{title} — No path")
        ax.scatter([start[0], goal[0]], [start[1], goal[1]])
        return

    xs = [p[0] for p in path]
    ys = [p[1] for p in path]
    ax.plot(xs, ys, linewidth=2, color="yellow")
    ax.scatter([start[0], goal[0]], [start[1], goal[1]], c="red")

    cum = cumulative_costs(path)
    for i, (x, y) in enumerate(path):
        ax.text(x + 0.05, y + 0.05, f"{i}\n{cum[i]:.2f}",
                fontsize=8, color="white")

    ax.set_title(f"{title} — Total cost: {total_path_cost(path):.3f}")

# ---------- example ----------
if __name__ == "__main__":
    grid = [
        [0, 0, 1, 0, 0],
        [1, 0, 0, 0, 1],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0],
    ]
    start = (0, 0)
    goal  = (4, 4)

    fig, ax = plt.subplots(figsize=(6, 6))
    draw_case(ax, grid, start, goal, "A* (8-connected)")
    plt.tight_layout()
    plt.show()
