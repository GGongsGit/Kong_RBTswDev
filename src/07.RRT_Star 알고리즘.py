# -*- coding: utf-8 -*-
"""
RRT* on 2D occupancy grid (0: free, 1: obstacle)
- Tk/Qt GUI 오류 회피를 위해 Agg 백엔드 사용(파일 저장 중심)
- 목표 바이어스, 동적 탐색 반경, 재배선(rewiring) 포함
- 결과 이미지를 저장하고(기본 rrtstar_result.png), 옵션으로 화면 표시
"""

import os
import sys
import math
import random
import numpy as np

# --- Matplotlib 백엔드 사전 설정 (Tk/Qt 오류 회피)
import matplotlib
try:
    if matplotlib.get_backend().lower() not in ["agg", "module://matplotlib_inline.backend_inline"]:
        matplotlib.use("Agg")
except Exception:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt


plt.rc("font", family="Gulim")

# -----------------------
# 유틸 함수
# -----------------------
def euclidean(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def collision_free(grid, p, q):
    """
    p, q: (r, c) 실수 좌표.
    p->q 직선을 1칸 간격으로 샘플링하여 모든 점이 free(0)인지 검사합니다.
    """
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
    """
    p_near에서 p_rand 방향으로 step_size만큼 확장한 새 점 p_new를 반환합니다.
    """
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
    goal_sample_rate=0.05,   # 5% 확률로 goal을 직접 샘플
    gamma_rrt=30.0,          # 동적 탐색 반경 계수 (값 클수록 더 많이 연결)
    early_stop_after=800     # 최적 경로 발견 후 개선 없으면 조기 종료
):
    """
    grid: np.ndarray, 0/1 격자
    start, goal: (r, c) - 정수 또는 실수
    반환: (path(list[(r,c)]), total_cost(float), tree_edges(list[(u,v)]))
          경로가 없으면 (None, inf, tree_edges)
    """
    grid = np.asarray(grid, dtype=int)
    R, C = grid.shape

    def in_bounds(p):
        return 0 <= p[0] < R and 0 <= p[1] < C

    def free(p):
        rr, cc = int(round(p[0])), int(round(p[1]))
        return in_bounds((rr, cc)) and grid[rr, cc] == 0

    if not (free(start) and free(goal)):
        return None, float('inf'), []

    # 트리 구조
    nodes = [tuple(map(float, start))]   # 노드 좌표 (r, c)
    parent = [-1]                        # 부모 인덱스
    cost = [0.0]                         # 루트까지 누적 비용
    tree_edges = []                      # 시각화용 간선 집합

    best_goal = None           # (idx, total_cost)
    best_iter_improved = -1

    # 작업 공간 대각선 길이를 반경 상한으로 사용
    space_diag = math.hypot(R, C)

    rnd = random.Random(0)  # 재현 가능성 (원하면 seed 변경/제거)

    for it in range(1, max_iter + 1):
        # 1) 샘플링 (goal bias)
        if rnd.random() < goal_sample_rate:
            p_rand = (float(goal[0]), float(goal[1]))
        else:
            p_rand = (rnd.uniform(0, R - 1), rnd.uniform(0, C - 1))

        # 2) 가장 가까운 노드
        dists = [euclidean(p, p_rand) for p in nodes]
        idx_near = int(np.argmin(dists))
        p_near = nodes[idx_near]

        # 3) 스티어 → 새 노드 후보
        p_new = steer(p_near, p_rand, step_size)

        # 4) 유효/충돌 검사
        if not free(p_new):
            continue
        if not collision_free(grid, p_near, p_new):
            continue

        # 5) 동적 탐색 반경으로 주변 이웃 찾기
        #    RRT* 이론(2D): r(n) ~ gamma * sqrt(log n / n)
        n = len(nodes) + 1
        rad = min(gamma_rrt * math.sqrt(max(math.log(n) / n, 1e-9)), space_diag)
        near_idx = [i for i, p in enumerate(nodes) if euclidean(p, p_new) <= rad]

        # 6) 최적 부모 선택
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

        # 7) 새 노드 추가
        nodes.append(p_new)
        parent.append(best_parent)
        cost.append(best_cost)
        tree_edges.append((best_parent, len(nodes) - 1))

        # 8) 재배선(rewire): 새 노드를 부모로 삼아 더 짧아지는 이웃 갱신
        for i in near_idx:
            if i == best_parent or i == len(nodes) - 1:
                continue
            new_cost = best_cost + euclidean(p_new, nodes[i])
            if new_cost + 1e-9 < cost[i] and collision_free(grid, p_new, nodes[i]):
                parent[i] = len(nodes) - 1
                cost[i] = new_cost
                # 간선 목록 업데이트(시각화 단순화: 기존 간선 삭제는 생략)

        # 9) 목표 연결 시도: p_new가 goal 근처이고, 충돌 없이 연결 가능하면 후보 경로
        if euclidean(p_new, goal) <= goal_tolerance and collision_free(grid, p_new, goal):
            total = best_cost + euclidean(p_new, goal)
            if (best_goal is None) or (total < best_goal[1] - 1e-9):
                best_goal = (len(nodes) - 1, total)
                best_iter_improved = it

        # 10) 조기 종료(선택): 일정 반복 동안 개선 없으면 중단
        if best_goal is not None and early_stop_after is not None:
            if it - best_iter_improved >= early_stop_after:
                break

    if best_goal is None:
        return None, float('inf'), tree_edges

    # 경로 복원
    idx = best_goal[0]
    path = [tuple(map(int, map(round, goal)))]
    p = nodes[idx]
    while idx != -1:
        path.append(tuple(map(int, map(round, nodes[idx]))))
        idx = parent[idx]
    path.reverse()
    return path, best_goal[1], tree_edges


def plot_rrtstar(grid, start, goal, path, tree_edges, nodes,
                 save_path="rrtstar_result.png", show=False, dpi=160):
    """
    RRT* 트리와 최종 경로를 시각화합니다.
    """
    grid = np.asarray(grid, dtype=int)
    R, C = grid.shape
    fig, ax = plt.subplots(figsize=(min(10, C * 0.9), min(10, R * 0.9)))

    ax.imshow(grid, origin="lower")  # 0/1 격자 표시
    ax.set_xticks(range(C)); ax.set_yticks(range(R))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_xlim(-0.5, C - 0.5); ax.set_ylim(-0.5, R - 0.5)
    ax.set_title("RRT* on Grid")

    # 트리 간선
    for u, v in tree_edges:
        pu = nodes[u]; pv = nodes[v]
        ax.plot([pu[1], pv[1]], [pu[0], pv[0]], linewidth=0.7, alpha=0.6)

    # 최종 경로
    if path:
        ys = [p[0] for p in path]; xs = [p[1] for p in path]
        ax.plot(xs, ys, linewidth=2.5)
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
    return save_path


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

    # 파라미터는 환경 크기/장애물 밀도에 따라 조정하십시오.
    path, total_cost, tree_edges = rrt_star(
        grid, start, goal,
        max_iter=6000,
        step_size=2.0,
        goal_tolerance=2.0,
        goal_sample_rate=0.07,   # 목표 바이어스 7%
        gamma_rrt=35.0,
        early_stop_after=1000
    )
    
    if path is None:
        print("경로를 찾지 못했습니다.")
        nodes = []  # 시각화가 필요하면 rrt_star 내부 구조를 약간 수정해 nodes 반환
    else:
        print(f"경로 길이(노드 수): {len(path)}, 총 비용(근사): {total_cost:.3f}")

    # 시각화를 위해 rrt_star 내부 노드 목록이 필요합니다.
    # 간단히 tree_edges에 등장한 인덱스로 nodes를 재구성합니다.
    # (실전 코드에서는 rrt_star가 nodes도 함께 반환하도록 변경 권장)
    # 여기서는 가벼운 편의 조치로 rrt_star를 살짝 바꿔도 됩니다.


# -----------------------
# 시각화
# -----------------------


