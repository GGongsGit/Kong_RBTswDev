import heapq
import networkx as nx
import matplotlib.pyplot as plt

plt.rc("font", family="Gulim")

# ---------- Dijkstra ----------
def dijkstra(graph, start):
    INF = float('inf')
    dist = {v: INF for v in graph}
    prev = {v: None for v in graph}
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        current_dist, current_node = heapq.heappop(pq)
        if current_dist > dist[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))
    return dist, prev

def reconstruct(prev, start, goal):
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path if path and path[0] == start else []

# ---------- 공통: 그래프/레이아웃 ----------
def to_nx_graph(graph_dict):
    G = nx.Graph()
    for u, nbrs in graph_dict.items():
        for v, w in nbrs.items():
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)
    return G

# 교차 없는 고정 좌표 (사각형 배치)
#  A(1,0), B(1,1), C(0,0), D(0,1)
POS = {"A": (1, 0), "B": (1, 1), "C": (0, 0), "D": (0, 1)}

def draw_all(graph_dict, start):
    G = to_nx_graph(graph_dict)
    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}

    dist, prev = dijkstra(graph_dict, start)

    # 그릴 대상 목표들 (예: A->B, A->C, A->D)
    goals = [n for n in graph_dict if n != start]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    ax_all = axes[0, 0]

    # (1) 전체 그래프
    nx.draw(G, POS, with_labels=True, node_color="#cfe8ff",
            node_size=1500, width=2, ax=ax_all, font_size=12)
    nx.draw_networkx_edge_labels(G, POS, edge_labels=edge_labels, ax=ax_all)
    ax_all.set_title(f"전체 그래프 (시작: {start})")

    # (2~4) 개별 최단 경로 강조
    for ax, goal in zip(axes.flatten()[1:], goals):
        # 기본 그래프
        nx.draw(G, POS, with_labels=True, node_color="#cfe8ff",
                node_size=1500, width=2, ax=ax, font_size=12)
        nx.draw_networkx_edge_labels(G, POS, edge_labels=edge_labels, ax=ax)

        # 최단 경로 계산/강조
        path = reconstruct(prev, start, goal)
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, POS, edgelist=path_edges,
                               width=4, edge_color="red", ax=ax)
        ax.set_title(f"{start} → {goal} 최단 경로  (거리: {dist[goal]})")

    plt.tight_layout()
    plt.show()

# ---------- 실행 예시 ----------
if __name__ == "__main__":
    graph = {
        'A': {'B': 5, 'C': 4},
        'B': {'A': 5, 'C': 2, 'D': 3},
        'C': {'A': 4, 'B': 2, 'D': 1},
        'D': {'B': 3, 'C': 1}
    }
    draw_all(graph, start='A')


# import math
# import heapq
# import matplotlib.pyplot as plt
# import numpy as np

# plt.rc("font", family="Gulim")

# # ---------- Dijkstra ----------
# def dijkstra(graph, start):
#     INF = float('inf')
#     # dist = {v: INF for v in graph}
#     dist = {}
#     for v in graph:
#         dist[v] = INF
#     prev = {v: None for v in graph}

#     dist[start] = 0
#     pq = [(0, start)]

#     while pq:  # 우선순위 큐에 노드가 남아 있는 동안 반복
#         current_dist, current_node = heapq.heappop(pq)  # 가장 짧은 거리 후보 꺼내기

#         # 만약 꺼낸 후보 거리가 이미 알고 있는 최단거리보다 크면 무시
#         if current_dist > dist[current_node]:
#             continue

#         # 현재 노드(current_node)의 모든 이웃(neighbor) 확인
#         for neighbor, weight in graph[current_node].items():
#             new_dist = current_dist + weight  # 시작점 → 현재 노드 → 이웃까지의 거리

#             # 이웃까지의 더 짧은 경로를 찾은 경우 갱신
#             if new_dist < dist[neighbor]:
#                 dist[neighbor] = new_dist         # 최단거리 갱신
#                 prev[neighbor] = current_node     # 경로 추적을 위해 이전 노드 기록
#                 heapq.heappush(pq, (new_dist, neighbor))  # 새 후보를 큐에 추가
#     return dist, prev

# def reconstruct(prev, start, goal):
#     path = []
#     cur = goal
#     while cur is not None:
#         path.append(cur)
#         cur = prev[cur]
#     path.reverse()
#     return path if path and path[0] == start else []

# # ---------- 배치 & 그리기 (Matplotlib 전용) ----------
# def circular_layout(nodes, radius=1.0):
#     """노드를 원형으로 균일 배치"""
#     n = len(nodes)
#     angles = np.linspace(0, 2*np.pi, n, endpoint=False)
#     pos = {}
#     for i, node in enumerate(nodes):
#         x = radius * np.cos(angles[i])
#         y = radius * np.sin(angles[i])
#         pos[node] = (x, y)
#     return pos

# def draw_on_axis(ax, graph, pos, path=None, title=None):
#     """한 축(ax)에 그래프와 가중치, (선택) 최단경로 강조까지 그림"""
#     ax.set_aspect('equal')
#     ax.axis('off')

#     # 1) 모든 간선(무방향 중복 방지)
#     drawn = set()
#     for v, edges in graph.items():
#         x1, y1 = pos[v]
#         for u, w in edges.items():
#             key = tuple(sorted((v, u)))
#             if key in drawn or v == u:
#                 continue
#             drawn.add(key)
#             x2, y2 = pos[u]
#             # 기본 간선
#             ax.plot([x1, x2], [y1, y2], linewidth=1.5)
#             # 가중치 라벨(중점)
#             mx, my = (x1 + x2) / 2, (y1 + y2) / 2
#             ax.text(mx, my, f"{w}", fontsize=10, ha='center', va='center',
#                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))

#     # 2) 최단 경로 강조(빨간색)
#     if path and len(path) >= 2:
#         for a, b in zip(path, path[1:]):
#             x1, y1 = pos[a]
#             x2, y2 = pos[b]
#             ax.plot([x1, x2], [y1, y2], linewidth=3, color='red')

#     # 3) 노드
#     for node, (x, y) in pos.items():
#         circ = plt.Circle((x, y), 0.08, fc='lightblue', ec='black', lw=1.2)
#         ax.add_patch(circ)
#         ax.text(x, y, node, ha='center', va='center', fontsize=12)

#     if title:
#         ax.set_title(title, fontsize=12, pad=8)

# def draw_split_views(graph, start, paths_dict):
#     """
#     한 Figure(창) 안을 서브플롯으로 나눠 표시.
#     - 첫 서브플롯: 전체 그래프(경로 미강조)
#     - 이후: 목적지별 최단경로 강조 그래프
#     """
#     nodes = sorted(graph.keys())
#     pos = circular_layout(nodes, radius=1.0)

#     n_paths = len(paths_dict)
#     total = 1 + n_paths  # 전체 1 + 각 경로
#     cols = 2 if total >= 2 else 1
#     rows = math.ceil(total / cols)

#     fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows))
#     if isinstance(axes, np.ndarray):
#         axes = axes.ravel()
#     else:
#         axes = [axes]

#     # (1) 전체 그래프
#     draw_on_axis(axes[0], graph, pos, path=None, title=f"전체 그래프 (시작: {start})")

#     # (2) 각 목적지 경로
#     idx = 1
#     for goal, path in paths_dict.items():
#         draw_on_axis(axes[idx], graph, pos, path=path, title=f"{start} → {goal} 최단 경로")
#         idx += 1

#     # 남는 축은 숨김
#     for k in range(idx, len(axes)):
#         axes[k].set_visible(False)
  
#     plt.tight_layout()
#     plt.show()

# # ---------- 실행 예시 ----------
# if __name__ == "__main__":
#     graph = {
#         'A': {'B': 5, 'C': 4},
#         'B': {'A': 5, 'C': 2, 'D': 3},
#         'C': {'A': 4, 'B': 2, 'D': 1},
#         'D': {'B': 3, 'C': 1}
#     }

#     start = 'A'
#     goal = "ALL"
#     # goal = input("목표 노드(비우면 전체): ").strip().upper() or None

#     dist, prev = dijkstra(graph, start)
#     print("시작 POINT:", start)
#     print("GOAL POINT:", goal)
#     print("최단거리:", dist)

#     if goal and goal in graph:
#         path = reconstruct(prev, start, goal)
#         print(f"{start} → {goal} 경로: {path} | 거리: {dist[goal]}")
#         # 하나의 Figure에 2분할(전체 / start→goal)
#         draw_split_views(graph, start, {goal: path})
#     else:
#         print(f"※ 목표 노드가 없으므로 {start}에서 모든 노드까지 경로를 표시합니다.")
#         paths = {}
#         for v in graph:
#             if v == start:
#                 continue
#             p = reconstruct(prev, start, v)
#             print(f"{start} → {v} : {p} | 거리: {dist[v]}")
#             paths[v] = p
#         # 하나의 Figure에 (전체 + 목적지별) 그리드로 표시
#         draw_split_views(graph, start, paths)








