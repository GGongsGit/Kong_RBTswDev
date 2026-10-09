import heapq

# ---------- Dijkstra ----------
def dijkstra(graph, start):
    INF = float('inf')
    # dist = {v: INF for v in graph}
    dist = {}
    
    print("\n####### 0 =============")
    print("graph : ", graph)

    print("\n####### 1 =============")
    for v in graph:
        dist[v] = INF
        print(f"v: {v}")
        print(f"dist[v]: {dist[v]}")
    prev = {v: None for v in graph}
    print("\n####### 2 =============")
    print(f"prev: {prev}")

    dist[start] = 0
    pq = [(0, start)]
    print("\n####### 3 =============")    
    print(f"pq = {pq}")

    while pq:  # 우선순위 큐에 노드가 남아 있는 동안 반복
        current_dist, current_node = heapq.heappop(pq)  # 가장 짧은 거리 후보 꺼내기
        print("\n####### 4 =============")  
        print(f"current_dist = {current_dist}")
        print(f"current_node = {current_node}")
        print(f"dist[current_node] = {dist[current_node]}")
        # 만약 꺼낸 후보 거리가 이미 알고 있는 최단거리보다 크면 무시
        if current_dist > dist[current_node]:
            continue
        # 현재 노드(current_node)의 모든 이웃(neighbor) 확인
        for neighbor, weight in graph[current_node].items():
            new_dist = current_dist + weight  # 시작점 → 현재 노드 → 이웃까지의 거리
            print("\n####### 5 =============")  
            print(f"current_dist = {current_dist}")
            print(f"weight = {weight}")
            print(f"new_dist = {new_dist}")
            print(f"dist[neighbor] = {dist[neighbor]}")

            # 이웃까지의 더 짧은 경로를 찾은 경우 갱신
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist         # 최단거리 갱신
                prev[neighbor] = current_node     # 경로 추적을 위해 이전 노드 기록
                print("\n####### 6 =============")  
                print(f"dist[neighbor] = {dist[neighbor]}")
                print(f"prev[neighbor] = {prev[neighbor]}")
                heapq.heappush(pq, (new_dist, neighbor))  # 새 후보를 큐에 추가
    return dist, prev

def reconstruct(prev, start, goal):
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path if path and path[0] == start else []

# ---------- 실행 예시 ----------
if __name__ == "__main__":
    graph = {
        'A': {'B': 5, 'C': 4},
        'B': {'A': 5, 'C': 2, 'D': 5},
        'C': {'A': 4, 'B': 2, 'D': 1},
        'D': {'B': 5, 'C': 1}
    }

    start = 'A'
    goal = "B"
    # goal = input("목표 노드(비우면 전체): ").strip().upper() or None

    dist, prev = dijkstra(graph, start)
    print("시작 POINT:", start)
    print("GOAL POINT:", goal)

    print("최단거리:", dist)

    if goal and goal in graph:
        path = reconstruct(prev, start, goal)
        print(f"{start} → {goal} 경로: {path} | 거리: {dist[goal]}")
    else:
        print(f"※ 목표 노드가 없으므로 {start}에서 모든 노드까지 경로를 표시합니다.")
        for v in graph:
            if v == start:
                continue
            path = reconstruct(prev, start, v)
            print(f"{start} → {v} : {path} | 거리: {dist[v]}")
