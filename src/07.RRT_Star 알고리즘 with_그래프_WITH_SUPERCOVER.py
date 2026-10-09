# -*- coding: utf-8 -*-
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

def in_bounds_cell(grid, r, c):
    R, C = grid.shape
    return 0 <= r < R and 0 <= c < C

def is_free_cell(grid, r, c):
    return in_bounds_cell(grid, r, c) and grid[r, c] == 0

def steer(p_near, p_rand, step_size):
    dr = p_rand[0] - p_near[0]
    dc = p_rand[1] - p_near[1]
    d = math.hypot(dr, dc)
    if d <= 1e-9:
        return p_near
    scale = min(1.0, step_size / d)
    return (p_near[0] + dr * scale, p_near[1] + dc * scale)

# -----------------------
# 충돌 검사 (슈퍼커버 라인 + 코너컷 방지)
# -----------------------
def supercover_cells_between(p, q):
    """
    p, q : (r, c) 실수 좌표.
    선분 p->q 가 '지나가는 모든 격자 셀'을 나열 (슈퍼커버 Bresenham 계열).
    """
    r0, c0 = p
    r1, c1 = q
    # 셀 좌표로 반올림 (원한다면 floor/round 정책을 바꿔도 무방)
    r0, c0 = int(round(r0)), int(round(c0))
    r1, c1 = int(round(r1)), int(round(c1))

    cells = []
    dr = abs(r1 - r0)
    dc = abs(c1 - c0)
    sr = 1 if r1 >= r0 else -1
    sc = 1 if c1 >= c0 else -1

    r, c = r0, c0
    cells.append((r, c))

    if dc >= dr:
        # 주로 가로로 진행
        err = dc / 2
        while c != c1:
            c += sc
            err -= dr
            if err < 0:
                # 슈퍼커버: 주 이동 + 보조 이동 모두 포함
                r += sr
                err += dc
                cells.append((r, c))        # 주 이동 후 위치
                cells.append((r - sr, c))   # 보조 이동으로 지나간 셀도 포함
            else:
                cells.append((r, c))
    else:
        # 주로 세로로 진행
        err = dr / 2
        while r != r1:
            r += sr
            err -= dc
            if err < 0:
                c += sc
                err += dr
                cells.append((r, c))
                cells.append((r, c - sc))
            else:
                cells.append((r, c))

    # 중복 제거
    uniq = []
    seen = set()
    for rc in cells:
        if rc not in seen:
            seen.add(rc)
            uniq.append(rc)
    return uniq

def collision_free_supercover(grid, p, q):
    """
    선분 p->q 가 통과하는 '모든 셀'을 검사하여
    - 장애물 셀(=1) 통과 시 False
    - 대각선 코너-컷 방지: (r,c)->(r+1,c+1)형 대각 이동 시,
      양 옆 직교 셀 중 하나라도 장애물이면 차단
    """
    cells = supercover_cells_between(p, q)
    R, C = grid.shape

    # 장애물 직접 통과 여부
    for r, c in cells:
        if not in_bounds_cell(grid, r, c) or grid[r, c] == 1:
            return False

    # 코너-컷 방지: 인접한 대각 셀로 넘어갈 때,
    # 양 옆(직교) 중 하나라도 벽이면 '대각 통과 금지'
    for (r0, c0), (r1, c1) in zip(cells, cells[1:]):
        dr, dc = r1 - r0, c1 - c0
        if abs(dr) == 1 and abs(dc) == 1:  # 대각 이동
            # 예: (r0,c0)->(r0+1,c0+1) 이면 (r0+1,c0), (r0,c0+1) 체크
            if not (is_free_cell(grid, r0 + dr, c0) and is_free_cell(grid, r0, c0 + dc)):
                return False

    return True

# -----------------------
# RRT* 구현
# -----------------------
def rrt_star(
    grid,
    start,
    goal,
    max_iter=5000,
    step_size=1.5,         # 조금 더 보수적으로
    goal_tolerance=1.5,    # 셀 스케일에 맞춰 조정
    goal_sample_rate=0.07,
    gamma_rrt=35.0,
    early_stop_after=800
):
    grid = np.asarray(grid, dtype=int)
    R, C = grid.shape

    def free_point(p):
        rr, cc = int(round(p[0])), int(round(p[1]))
        return in_bounds_cell(grid, rr, cc) and grid[rr, cc] == 0

    if not (free_point(start) and free_point(goal)):
        return None, float('inf'), [], []

    nodes  = [tuple(map(float, start))]
    parent = [-1]
    cost   = [0.0]
    tree_edges = []

    best_goal = None
    best_iter_improved = -1
    space_diag = math.hypot(R, C)
    rnd = random.Random(0)

    for it in range(1, max_iter + 1):
        # 1) 샘플링
        if rnd.random() < goal_sample_rate:
            p_rand = (float(goal[0]), float(goal[1]))
        else:
            p_rand = (rnd.uniform(0, R - 1), rnd.uniform(0, C - 1))

        # 2) 최근접
        idx_near = int(np.argmin([euclidean(p, p_rand) for p in nodes]))
        p_near = nodes[idx_near]

        # 3) 스티어
        p_new = steer(p_near, p_rand, step_size)

        # 4) 충돌 검사 (슈퍼커버)
        if not free_point(p_new):
            continue
        if not collision_free_supercover(grid, p_near, p_new):
            continue

        # 5) 근방 이웃
        n = len(nodes) + 1
        rad = min(gamma_rrt * math.sqrt(max(math.log(n) / n, 1e-9)), space_diag)
        near_idx = [i for i, p in enumerate(nodes) if euclidean(p, p_new) <= rad]

        # 6) 최적 부모
        best_parent = idx_near
        best_cost = cost[idx_near] + euclidean(p_near, p_new)
        for i in near_idx:
            if i == idx_near:
                continue
            if collision_free_supercover(grid, nodes[i], p_new):
                c = cost[i] + euclidean(nodes[i], p_new)
                if c < best_cost:
                    best_cost = c
                    best_parent = i

        # 7) 추가
        nodes.append(p_new)
        parent.append(best_parent)
        cost.append(best_cost)
        tree_edges.append((best_parent, len(nodes) - 1))

        # 8) 재배선
        for i in near_idx:
            if i in (best_parent, len(nodes) - 1):
                continue
            new_cost = best_cost + euclidean(p_new, nodes[i])
            if new_cost + 1e-9 < cost[i] and collision_free_supercover(grid, p_new, nodes[i]):
                parent[i] = len(nodes) - 1
                cost[i]   = new_cost

        # 9) 목표 연결
        if euclidean(p_new, goal) <= goal_tolerance and collision_free_supercover(grid, p_new, goal):
            total = best_cost + euclidean(p_new, goal)
            if best_goal is None or total < best_goal[1] - 1e-9:
                best_goal = (len(nodes) - 1, total)
                best_iter_improved = it

        # 10) 조기 종료
        if best_goal is not None and early_stop_after is not None:
            if it - best_iter_improved >= early_stop_after:
                break

    if best_goal is None:
        return None, float('inf'), tree_edges, nodes

    # 경로 복원
    idx = best_goal[0]
    path = [tuple(map(int, map(round, goal)))]
    while idx != -1:
        path.append(tuple(map(int, map(round, nodes[idx]))))
        idx = parent[idx]
    path.reverse()
    return path, best_goal[1], tree_edges, nodes

# -----------------------
# 시각화 (화면 표시)
# -----------------------
def plot_rrtstar(grid, start, goal, path, tree_edges, nodes):
    grid = np.asarray(grid, dtype=int)
    R, C = grid.shape
    fig, ax = plt.subplots(figsize=(min(10, C * 0.9), min(10, R * 0.9)))

    ax.imshow(grid, origin="lower", cmap="gray_r")
    ax.set_xticks(range(C)); ax.set_yticks(range(R))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_xlim(-0.5, C - 0.5); ax.set_ylim(-0.5, R - 0.5)
    ax.set_title("RRT* on Grid (supercover collision)")

    for u, v in tree_edges:
        pu = nodes[u]; pv = nodes[v]
        ax.plot([pu[1], pv[1]], [pu[0], pv[0]], linewidth=0.6, alpha=0.5)

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
        step_size=1.5,         # 보수적 스텝
        goal_tolerance=1.5,
        goal_sample_rate=0.07,
        gamma_rrt=35.0,
        early_stop_after=1000
    )

    if path is None:
        print("경로를 찾지 못했습니다.")
    else:
        print(f"경로 길이(노드 수): {len(path)}, 총 비용(근사): {total_cost:.3f}")

    plot_rrtstar(grid, start, goal, path, tree_edges, nodes)
