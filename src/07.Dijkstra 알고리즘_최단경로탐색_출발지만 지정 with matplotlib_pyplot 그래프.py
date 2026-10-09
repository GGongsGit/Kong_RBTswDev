import heapq
import matplotlib.pyplot as plt
import networkx as nx

graph = {
    'A': {'B': 4, 'C': 1},
    'B': {'A': 4, 'C': 1, 'D': 5},
    'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
    'D': {'B': 5, 'C': 8, 'E': 2, 'F': 6},
    'E': {'C': 10, 'D': 2, 'F': 3},
    'F': {'D': 6, 'E': 3},
}

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    
    queue = []
    heapq.heappush(queue, [distances[start], start])
    
    while queue:
        current_distance, current_destination = heapq.heappop(queue)
        
        if distances[current_destination] < current_distance:
            continue
        
        for new_destination, new_distance in graph[current_destination].items():
            distance = current_distance + new_distance
            if distance < distances[new_destination]:
                distances[new_destination] = distance
                heapq.heappush(queue, [distance, new_destination])
    
    return distances

def draw_graph(graph, start_node):
    """그래프를 시각화"""
    # NetworkX 그래프 생성
    G = nx.Graph()
    
    # 노드 추가
    for node in graph:
        G.add_node(node)
    
    # 엣지 추가 (가중치 포함)
    for node, neighbors in graph.items():
        for neighbor, weight in neighbors.items():
            G.add_edge(node, neighbor, weight=weight)
    
    # 레이아웃 설정
    pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
    
    # 그래프 그리기
    plt.figure(figsize=(10, 8))
    
    # 노드 그리기
    node_colors = []
    for node in G.nodes():
        if node == start_node:
            node_colors.append('red')  # 시작 노드 = 빨강
        else:
            node_colors.append('lightblue')  # 다른 노드 = 하늘색
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000)
    
    # 엣지 그리기
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.6)
    
    # 노드 레이블
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    
    # 엣지 가중치 (거리) 표시
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=10)
    
    plt.title(f"Dijkstra Graph (Start: {start_node})", fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('dijkstra_graph.png', dpi=150, bbox_inches='tight')
    plt.show()

def print_results(start_node, distances):
    """결과를 보기 좋게 출력"""
    print("\n" + "="*50)
    print(f"다익스트라 알고리즘 (시작점: {start_node})")
    print("="*50)
    
    # 거리순으로 정렬
    sorted_distances = sorted(distances.items(), key=lambda x: x[1])
    
    print(f"\n{'노드':<10}{'거리':<15}")
    print("-"*50)
    
    for node, distance in sorted_distances:
        if distance == float('inf'):
            print(f"{node:<10}{'도달 불가':<15}")
        else:
            print(f"{node:<10}{distance:<15.1f}")
    
    print("="*50 + "\n")

# 실행
if __name__ == "__main__":
    start_node = 'D'
    result = dijkstra(graph, start_node)
    
    # 결과 출력
    print_results(start_node, result)
    
    # 그래프 시각화
    print("그래프를 생성하고 있습니다...")
    draw_graph(graph, start_node)
    
    print("✓ 저장: dijkstra_graph.png")
