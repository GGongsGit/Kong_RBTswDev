import heapq
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional

Node = Any
Graph = Dict[Node, List[Tuple[Node, float]]]

def dijkstra(graph: Graph, start: Node, goal: Optional[Node] = None):
    INF = float("inf")
    dist: Dict[Node, float] = {n: INF for n in graph}
    prev: Dict[Node, Optional[Node]] = {n: None for n in graph}
    dist[start] = 0.0

    pq: List[Tuple[float, Node]] = [(0.0, start)]
    visited = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        if goal is not None and u == goal:
            break

        for v, w in graph.get(u, []):
            nd = d + float(w)
            if nd < dist.get(v, INF):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    return dist, prev

def reconstruct_path(prev: Dict[Node, Optional[Node]], start: Node, goal: Node) -> List[Node]:
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        if cur == start:
            break
        cur = prev[cur]
    path.reverse()
    return path if path and path[0] == start else []

def draw_graph(graph: Graph, path: List[Node]):
    G = nx.DiGraph()   # 방향 그래프 (무방향으로 하고 싶으면 Graph() 사용)
    for u in graph:
        for v, w in graph[u]:
            G.add_edge(u, v, weight=w)

    pos = nx.spring_layout(G, seed=42)  # 노드 배치

    # 간선 가중치 레이블
    edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}

    # 최단 경로 간선
    path_edges = list(zip(path, path[1:])) if path else []

    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightblue")
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")

    # 전체 간선
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color="gray")

    # 최단 경로 간선은 강조 표시
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=3, edge_color="red")

    # 간선 가중치 텍스트
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="black")

    plt.title("Dijkstra Shortest Path", fontsize=14)
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    # 예시 그래프
    graph: Graph = {
        "A": [("B", 4), ("C", 2)],
        "B": [("A", 4), ("C", 1), ("D", 5)],
        "C": [("A", 2), ("B", 1), ("D", 8), ("E", 10)],
        "D": [("B", 5), ("C", 8), ("E", 2), ("F", 6)],
        "E": [("C", 10), ("D", 2), ("F", 3)],
        "F": [("D", 6), ("E", 3)],
    }

    start, goal = "D", "A"
    dist, prev = dijkstra(graph, start, goal=goal)
    path = reconstruct_path(prev, start, goal)

    print("최단경로:", path)
    print("총 비용:", dist[goal])

    draw_graph(graph, path)