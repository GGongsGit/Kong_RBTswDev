import heapq

def dijkstra(graph, start):

    INF = float('inf')

    # 1) 모든 노드까지의 거리를 무한대로 시작, 이전 노드는 아직 모름(None)
    dist = {node: INF for node in graph}
    prev = {node: None for node in graph}

    # 2) 시작 노드는 거리 0, 우선순위 큐(가장 가까운 노드부터 탐색)
    dist[start] = 0
    pq = [(0, start)]  # (현재까지 거리, 노드)

    # 3) 큐가 빌 때까지 반복
    while pq:
        cur_dist, cur_node = heapq.heappop(pq)

        # 이미 더 짧은 경로가 있다면 건너뛴다 (오래된 후보 제거)
        if cur_dist > dist[cur_node]:
            continue

        # 4) 이웃 노드를 살펴보며 "더 짧은 길"이면 업데이트
        for neighbor, weight in graph[cur_node].items():
            new_dist = cur_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist      # 더 짧은 거리로 갱신
                prev[neighbor] = cur_node      # 경로에서 바로 앞 노드 기록
                heapq.heappush(pq, (new_dist, neighbor))

    return dist, prev


def build_path(prev, start, goal):
    """
    prev 정보를 사용해 start -> goal 최단 경로를 리스트로 만들어 돌려준다.
    경로가 없으면 빈 리스트 반환.
    """
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path if path and path[0] == start else []


# -------- 사용 예시 --------
if __name__ == "__main__":
    graph = {
        'A': {'B': 5, 'C': 4},
        'B': {'A': 5, 'C': 2, 'D': 5},
        'C': {'A': 4, 'B': 2, 'D': 1},
        'D': {'B': 5, 'C': 1}
    }

    start = 'A'
    goal = 'D'

    dist, prev = dijkstra(graph, start)
    path = build_path(prev, start, goal)

    # 출력 예 (필요 시만 사용)
    print(f"시작 노드 = {start}, goal = {goal}")
    print("A에서 각 노드까지의 최단거리:", dist)
    print(f"{start} → {goal} 최단 경로:", path, "| 거리:", dist[goal])


    """
    graph 예시:
      {
        'A': {'B': 5, 'C': 4},
        'B': {'A': 5, 'C': 2, 'D': 5},
        'C': {'A': 4, 'B': 2, 'D': 1},
        'D': {'B': 5, 'C': 1}
      }
    start: 시작 노드 (예: 'A')

    반환:
      dist: 시작노드에서 각 노드까지의 최단거리 딕셔너리
      prev: 최단 경로에서 각 노드의 직전 노드(경로 복원용)
    """