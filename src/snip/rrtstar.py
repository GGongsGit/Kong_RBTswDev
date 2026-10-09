import math, random

def collision_free(grid, p, q):
    """p→q 직선을 0.5칸 간격으로 샘플링해서 모두 빈칸(0)인지 검사"""
    n = max(int(math.dist(p, q) / 0.5), 1)
    for i in range(n + 1):
        r = p[0] + (q[0] - p[0]) * i / n
        c = p[1] + (q[1] - p[1]) * i / n
        rr, cc = int(round(r)), int(round(c))
        if not (0 <= rr < len(grid) and 0 <= cc < len(grid[0])) or grid[rr][cc] == 1:
            return False
    return True

def rrt_star(grid, start, goal, max_iter=3000, step=2.0,
             goal_rate=0.05, goal_tol=1.5, gamma=30.0, seed=1):
    random.seed(seed)
    R, C = len(grid), len(grid[0])
    nodes, parent, cost = [start], [-1], [0.0]
    best = None                                            # (목표 근처 노드 번호, 총 비용)
    for it in range(1, max_iter + 1):
        # 1) 샘플링: 5% 확률로 목표를 직접 뽑음 (goal bias)
        x = goal if random.random() < goal_rate else (random.uniform(0, R-1), random.uniform(0, C-1))
        # 2) 가장 가까운 노드
        i_near = min(range(len(nodes)), key=lambda i: math.dist(nodes[i], x))
        p = nodes[i_near]
        # 3) steer: p에서 x 쪽으로 최대 step만큼만 전진
        d = math.dist(p, x)
        if d < 1e-9:
            continue
        s = min(1.0, step / d)
        new = (p[0] + (x[0] - p[0]) * s, p[1] + (x[1] - p[1]) * s)
        if not collision_free(grid, p, new):
            continue
        # 4) 반경 안의 이웃 중 비용이 가장 싼 부모 고르기
        n = len(nodes) + 1
        radius = min(gamma * math.sqrt(math.log(n) / n), step * 3)
        near = [i for i in range(len(nodes)) if math.dist(nodes[i], new) <= radius]
        best_p, best_c = i_near, cost[i_near] + math.dist(p, new)
        for i in near:
            c = cost[i] + math.dist(nodes[i], new)
            if c < best_c and collision_free(grid, nodes[i], new):
                best_p, best_c = i, c
        nodes.append(new); parent.append(best_p); cost.append(best_c)
        k = len(nodes) - 1
        # 5) rewire: 새 노드를 거치는 게 더 싸면 이웃의 부모를 바꿈
        for i in near:
            c = best_c + math.dist(new, nodes[i])
            if c < cost[i] and collision_free(grid, new, nodes[i]):
                parent[i], cost[i] = k, c
        # 6) 목표 도달 확인
        if math.dist(new, goal) <= goal_tol and collision_free(grid, new, goal):
            total = best_c + math.dist(new, goal)
            if best is None or total < best[1]:
                best = (k, total)
    if best is None:
        return None, float("inf")
    path, i = [goal], best[0]                              # 부모를 따라 역추적
    while i != -1:
        path.append(nodes[i]); i = parent[i]
    # rewire로 중간 비용이 바뀌었을 수 있으니 경로 길이를 다시 계산
    path = path[::-1]
    length = sum(math.dist(path[j], path[j+1]) for j in range(len(path) - 1))
    return path, length

grid = [[0]*20 for _ in range(20)]
for r in range(3, 17):                                     # 가운데 벽 (위아래 3칸씩 통로)
    grid[r][10] = 1
path, length = rrt_star(grid, (1.0, 1.0), (18.0, 18.0))
print(f"경로 점 {len(path)}개, 길이 {length:.2f}")   # 경로 점 16개, 길이 26.14 (seed=1)
