# -*- coding: utf-8 -*-
"""
RRT* on 2D occupancy grid (0: free, 1: obstacle)
- 바로 화면에 띄우는 버전 (PNG 저장 없음)
"""

import math
import random
import numpy as np
import matplotlib.pyplot as plt

plt.rc("font", family="Gulim")

# -----------------------
# 유틸 함수
# -----------------------
def euclidean(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])

def collision_free(grid, p, q):
    R, C = grid.shape
    dist = euclidean(p, q)
    steps = max(int(dist), 1)
    rs = np.linspace(p[0], q[0], steps + 1)
    cs = np.linspace(p[1], q[1], steps + 1)
    for r, c in zip(rs, cs):
        rr, cc = int(round(r)), int(round(c))
        if rr < 0 or rr >= R or cc < 0 or cc >= C or grid[rr, cc] == 1:
            return False
    return True

def steer(p_near, p_rand, step_size):
    dr = p_rand[0] - p_near[0]
    dc = p_rand[1] - p_near[1]
    d = math.hypot(dr, dc)
    if d <= 1e-9:
        return p_near
    scale = min(1.0, step_size / d)
    return (p_near[0] + dr * scale, p_near[1] + dc * scale)

# -----------------------
# RRT* 구현
# -----------------------
def rrt_star(
    grid,
    start,
    goal,
    max_iter=5000,
    step_size=2.0,
    goal_tolerance=2.0,
    goal_sample_rate=0.05,
    gamma_rrt=30.0,
    early_stop_after=800
):
    grid = np.asarray(grid, dtype=int)
    R, C = grid.shape

    def in_bounds(p):
        return 0 <= p[0] < R and 0 <= p[1] < C
    def free(p):
        rr, cc = int(round(p[0])), int(round(p[1]))
        return in_bounds((rr, cc)) and grid[rr, cc] == 0

    if not (free(start) and free(goal)):
        return None, float('inf'), [], []

    nodes = [tuple(map(float, start))]
    parent = [-1]
    cost = [0.0]
    tree_edges = []

    best_goal = None
    best_iter_improved = -1
    space_diag = math.hypot(R, C)

    rnd = random.Random(0)

    for it in range(1, max_iter + 1):
        if rnd.random() < goal_sample_rate:
            p_rand = (float(goal[0]), float(goal[1]))
        else:
            p_rand = (rnd.uniform(0, R - 1), rnd.uniform(0, C - 1))

        dists = [euclidean(p, p_rand) for p in nodes]
        idx_near = int(np.argmin(dists))
        p_near = nodes[idx_near]

        p_new = steer(p_near, p_rand, step_size)

        if not free(p_new):
            continue
        if not collision_free(grid, p_near, p_new):
            continue

        n = len(nodes) + 1
        rad = min(gamma_rrt * math.sqrt(max(math.log(n) / n, 1e-9)), space_diag)
        near_idx = [i for i, p in enumerate(nodes) if euclidean(p, p_new) <= rad]

        best_parent = idx_near
        best_cost = cost[idx_near] + euclidean(p_near, p_new)
        for i in near_idx:
            if i == idx_near:
                continue
            if collision_free(grid, nodes[i], p_new):
                c = cost[i] + euclidean(nodes[i], p_new)
                if c < best_cost:
                    best_cost = c
                    best_parent = i

        nodes.append(p_new)
        parent.append(best_parent)
        cost.append(best_cost)
        tree_edges.append((best_parent, len(nodes) - 1))

        for i in near_idx:
            if i == best_parent or i == len(nodes) - 1:
                continue
            new_cost = best_cost + euclidean(p_new, nodes[i])
            if new_cost + 1e-9 < cost[i] and collision_free(grid, p_new, nodes[i]):
                parent[i] = len(nodes) - 1
                cost[i] = new_cost

        if euclidean(p_new, goal) <= goal_tolerance and collision_free(grid, p_new, goal):
            total = best_cost + euclidean(p_new, goal)
            if (best_goal is None) or (total < best_goal[1] - 1e-9):
                best_goal = (len(nodes) - 1, total)
                best_iter_improved = it

        if best_goal is not None and early_stop_after is not None:
            if it - best_iter_improved >= early_stop_after:
                break

    if best_goal is None:
        return None, float('inf'), tree_edges, nodes

    idx = best_goal[0]
    path = [tuple(map(int, map(round, goal)))]
    while idx != -1:
        path.append(tuple(map(int, map(round, nodes[idx]))))
        idx = parent[idx]
    path.reverse()
    return path, best_goal[1], tree_edges, nodes

# -----------------------
# 시각화 (저장 X, 바로 화면 표시)
# -----------------------
def plot_rrtstar(grid, start, goal, path, tree_edges, nodes):
    grid = np.asarray(grid, dtype=int)
    R, C = grid.shape
    fig, ax = plt.subplots(figsize=(min(10, C * 0.9), min(10, R * 0.9)))

    ax.imshow(grid, origin="lower", cmap="gray_r")
    ax.set_xticks(range(C)); ax.set_yticks(range(R))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_xlim(-0.5, C - 0.5); ax.set_ylim(-0.5, R - 0.5)
    ax.set_title("RRT* on Grid")

    for u, v in tree_edges:
        pu = nodes[u]; pv = nodes[v]
        ax.plot([pu[1], pv[1]], [pu[0], pv[0]], linewidth=0.7, alpha=0.6)

    if path:
        ys = [p[0] for p in path]; xs = [p[1] for p in path]
        ax.plot(xs, ys, linewidth=2.5, color="tab:red", label="Path")
        ax.legend(loc="upper right")

    ax.scatter([start[1]], [start[0]], s=80, marker='o', color="tab:blue", zorder=3)
    ax.scatter([goal[1]],  [goal[0]],  s=140, marker='*', color="tab:orange", zorder=3)

    plt.tight_layout()
    plt.show()

# -----------------------
# 예시 실행
# -----------------------
if __name__ == "__main__":
    grid = np.array([
        [0,0,0,0,0,0,0,0,0,0],
        [1,1,0,1,0,1,0,0,0,0],
        [0,0,0,1,0,1,0,1,1,0],
        [0,1,1,0,0,0,0,0,1,0],
        [0,0,0,0,1,1,0,0,1,0],
        [0,1,0,0,0,0,0,0,1,0],
        [0,0,0,1,0,0,0,1,1,0],
        [0,1,0,0,0,1,0,0,0,0],
        [0,0,0,0,0,1,0,1,0,0],
        [0,0,0,0,0,0,0,1,0,0],
    ], dtype=int)

    start = (0, 0)
    goal  = (9, 9)

    path, total_cost, tree_edges, nodes = rrt_star(
        grid, start, goal,
        max_iter=6000,
        step_size=2.0,
        goal_tolerance=2.0,
        goal_sample_rate=0.07,
        gamma_rrt=35.0,
        early_stop_after=1000
    )

    if path is None:
        print("경로를 찾지 못했습니다.")
    else:
        print(f"경로 길이(노드 수): {len(path)}, 총 비용(근사): {total_cost:.3f}")

    plot_rrtstar(grid, start, goal, path, tree_edges, nodes)
