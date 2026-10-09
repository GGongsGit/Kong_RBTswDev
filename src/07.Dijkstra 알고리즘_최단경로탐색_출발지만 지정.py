import heapq  # 우선순위 큐 구현을 위함

# graph = {
#     'A': {'B': 8, 'C': 1, 'D': 2},
#     'B': {},
#     'C': {'B': 5, 'D': 2},
#     'D': {'E': 3, 'F': 5},
#     'E': {'F': 1},
#     'F': {'A': 5}
# }



graph = {
    'A': {'B': 4, 'C': 1},
    'B': {'A': 4, 'C': 1, 'D': 5},
    'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
    'D': {'B': 5, 'C': 8, 'E': 2, 'F': 6},
    'E': {'C': 10,'D': 2, 'F': 3},
    'F': {'D': 6, 'E': 3},
}


def dijkstra(graph, start):
  # start로 부터의 거리 값을 저장하기 위함
  distances = {node: float('inf') for node in graph}  
  
  distances[start] = 0  # 시작 값은 0이어야 함
  
  # 시작 노드부터 탐색 시작 하기 위함.
  queue = []
  heapq.heappush(queue, [distances[start], start])  

  # queue에 남아 있는 노드가 없으면 끝 
  while queue:  
    # 탐색 할 노드, 거리를 가져옴.
    current_distance, current_destination = heapq.heappop(queue)  
    # 기존에 있는 거리보다 길다면, 볼 필요도 없음
    if distances[current_destination] < current_distance:  
      continue
    
    for new_destination, new_distance in graph[current_destination].items():
      distance = current_distance + new_distance  # 해당 노드를 거쳐 갈 때 거리
      if distance < distances[new_destination]:  # 알고 있는 거리 보다 작으면 갱신
        distances[new_destination] = distance
        # 다음 인접 거리를 계산 하기 위해 큐에 삽입
        heapq.heappush(queue, [distance, new_destination]) 
    
  return distances

print(dijkstra(graph, 'D'))