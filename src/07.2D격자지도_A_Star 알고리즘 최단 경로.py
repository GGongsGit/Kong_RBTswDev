import os
import sys
import subprocess
from heapq import heappush, heappop
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

def astar_grid(grid, start, goal, allow_diagonal=False):
    grid = np.asarray(grid, dtype=int)
    R, C = grid.shape
    sr, sc = start
    gr, gc = goal

    def in_bounds(r, c): return 0 <= r < R and 0 <= c < C
    def passable(r, c):  return grid[r, c] == 0

    if allow_diagonal:
        NEI = [(1,0,1.0),(-1,0,1.0),(0,1,1.0),(0,-1,1.0),
               (1,1,sqrt(2)),(1,-1,sqrt(2)),(-1,1,sqrt(2)),(-1,-1,sqrt(2))]
        def h(r, c):
            dr, dc = abs(r - gr), abs(c - gc)
            m, n = max(dr, dc), min(dr, dc)
            return m + (sqrt(2) - 1.0) * n  # Octile
    else:
        NEI = [(1,0,1.0),(-1,0,1.0),(0,1,1.0),(0,-1,1.0)]
        def h(r, c): return abs(r - gr) + abs(c - gc)  # Manhattan

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


def plot_astar(grid, start, goal, allow_diagonal=False,
               save_path="astar_result.png", show=False, dpi=160):

    path, cost = astar_grid(grid, start, goal, allow_diagonal=allow_diagonal)

    grid_np = np.asarray(grid, dtype=int)
    R, C = grid_np.shape
    fig, ax = plt.subplots(figsize=(min(10, C*0.9), min(10, R*0.9)))

    im = ax.imshow(grid_np, origin='lower')
    ax.set_xticks(range(C)); ax.set_yticks(range(R))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_xlim(-0.5, C-0.5); ax.set_ylim(-0.5, R-0.5)

    title = f"A* Path (cost={cost:.3f})" if path else "No path found"
    ax.set_title(title)

    if path:
        ys = [r for (r, c) in path]; xs = [c for (r, c) in path]
        ax.plot(xs, ys, linewidth=2)
        ax.scatter([start[1]], [start[0]], s=80, marker='o', zorder=3)
        ax.scatter([goal[1]],  [goal[0]],  s=140, marker='*', zorder=3)

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
        # 표시 실패 시 조용히 무시(로그만 남기고 싶다면 print 사용)
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
   

    start = (0, 0)
    goal  = (6, 6)

    # 4방향 (파일 저장)
    p1, cost4, _ = plot_astar(grid, start, goal, allow_diagonal=False,
                               save_path="astar_result_4dir.png", show=False)
    # 8방향 (대각 허용)
    p2, cost8, _ = plot_astar(grid, start, goal, allow_diagonal=True,
                               save_path="astar_result_8dir.png", show=False)

    print("[저장 완료]")
    print(" 4방향:", os.path.abspath(p1), " cost=", cost4)
    print(" 8방향:", os.path.abspath(p2), " cost=", cost8)

    # --- 저장된 파일 표시/열기 ---
    # 1) 먼저 OS 기본 이미지 뷰어로 열기 시도
    opened1 = open_image_with_os(p1)
    opened2 = open_image_with_os(p2)

    # 2) 실패한 경우에만 Matplotlib으로 표시(가능한 환경에서)
    if not opened1:
        show_image_with_matplotlib(p1)
    if not opened2:
        show_image_with_matplotlib(p2)
