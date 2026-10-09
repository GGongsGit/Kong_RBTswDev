import os
import sys
import subprocess
from heapq import heappush, heappop
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

def astar_grid(grid, start, goal):
    grid = np.asarray(grid, dtype=int)
    R, C = grid.shape
    sr, sc = start
    gr, gc = goal

    def in_bounds(r, c): 
        return 0 <= r < R and 0 <= c < C
    
    def passable(r, c):  
        return grid[r, c] == 0

    # 8방향 이동 (대각 허용)
    NEI = [(1,0,1.0),(-1,0,1.0),(0,1,1.0),(0,-1,1.0),
           (1,1,sqrt(2)),(1,-1,sqrt(2)),(-1,1,sqrt(2)),(-1,-1,sqrt(2))]
    
    # 유클리드 거리 휴리스틱
    def h(r, c):
        dr, dc = abs(r - gr), abs(c - gc)
        return sqrt(dr**2 + dc**2)

    if not (in_bounds(sr, sc) and in_bounds(gr, gc) and passable(sr, sc) and passable(gr, gc)):
        return None, float('inf')

    open_heap = []
    g_score = {(sr, sc): 0.0}
    f0 = h(sr, sc)
    heappush(open_heap, (f0, f0, sr, sc))
    came_from = {}
    closed = set()

    while open_heap:
        _, _, r, c = heappop(open_heap)
        if (r, c) in closed:
            continue
        if (r, c) == (gr, gc):
            path = [(r, c)]
            while (r, c) in came_from:
                r, c = came_from[(r, c)]
                path.append((r, c))
            path.reverse()
            return path, g_score[(gr, gc)]
        closed.add((r, c))

        for dr, dc, step_cost in NEI:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc) or not passable(nr, nc):
                continue
            tentative_g = g_score[(r, c)] + step_cost
            if tentative_g < g_score.get((nr, nc), float('inf')):
                came_from[(nr, nc)] = (r, c)
                g_score[(nr, nc)] = tentative_g
                fn = tentative_g + h(nr, nc)
                heappush(open_heap, (fn, h(nr, nc), nr, nc))

    return None, float('inf')


def plot_astar(grid, start, goal, save_path="astar_result.png", show=False, dpi=160):

    path, cost = astar_grid(grid, start, goal)

    grid_np = np.asarray(grid, dtype=int)
    R, C = grid_np.shape
    fig, ax = plt.subplots(figsize=(min(10, C*0.9), min(10, R*0.9)))

    im = ax.imshow(grid_np, origin='lower')
    ax.set_xticks(range(C)); ax.set_yticks(range(R))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_xlim(-0.5, C-0.5); ax.set_ylim(-0.5, R-0.5)

    title = f"A* Path (8-way, cost={cost:.3f})" if path else "No path found"
    ax.set_title(title)

    if path:
        ys = [r for (r, c) in path]; xs = [c for (r, c) in path]
        ax.plot(xs, ys, linewidth=2)
        ax.scatter([start[1]], [start[0]], s=80, marker='o', zorder=3, label='Start')
        ax.scatter([goal[1]],  [goal[0]],  s=140, marker='*', zorder=3, label='Goal')
        ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')

    if show:
        try:
            plt.show()
        except Exception:
            pass
    else:
        plt.close(fig)

    return save_path, cost, path


def open_image_with_os(path: str) -> bool:

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
            return True
        elif sys.platform == "darwin":
            subprocess.check_call(["open", path])
            return True
        else:
            subprocess.check_call(["xdg-open", path])
            return True
    except Exception:
        return False


def show_image_with_matplotlib(path: str):

    try:
        img = plt.imread(path)
        plt.figure()
        plt.imshow(img)
        plt.axis("off")
        plt.title(os.path.basename(path))
        plt.tight_layout()
        plt.show()
    except Exception:
        pass


if __name__ == "__main__":
    # 예시 격자
    grid = [
        [0,0,0,1,0,1,0],
        [1,1,0,1,0,1,0],
        [0,0,0,0,0,1,0],
        [0,1,0,0,1,0,0],
        [0,1,1,0,1,1,0],
        [0,1,0,0,0,0,0],
        [0,0,0,1,0,1,0],
    ]

    start = (3, 2)
    goal  = (5, 6)   # 행/열 = (5,6) 5행 6열

    # 8방향 경로 탐색 (대각 허용)
    p, cost, path = plot_astar(grid, start, goal, 
                                save_path="astar_result_8dir.png", show=False)

    print("[저장 완료]")
    print(f" 파일: {os.path.abspath(p)}")
    print(f" 비용: {cost:.3f}")
    print(f" 경로 길이: {len(path) if path else 0}")

    # --- 저장된 파일 표시/열기 ---
    opened = open_image_with_os(p)

    if not opened:
        show_image_with_matplotlib(p)
