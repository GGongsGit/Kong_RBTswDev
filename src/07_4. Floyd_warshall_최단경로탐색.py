import matplotlib.pyplot as plt
import networkx as nx
import sys
INF = sys.maxsize

n = 4
a  = [ [0,2,INF,4], [2,0,INF,5], [3,INF,0,INF], [INF,2,1,0] ]


#=========================================================================
# 그래프 객체 생성
G = nx.DiGraph()

# 노드
G.add_nodes_from(range(n))

# 간선 추가
for i in range(n):
    for j in range(n):
        if i != j and a[i][j] != INF:
            G.add_edge(i, j, weight=a[i][j])

pos = nx.circular_layout(G)
plt.rc("font", family="Gulim")
plt.figure(figsize=(6,6))

# 노드 그리기
nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1000)
nx.draw_networkx_labels(G, pos, font_size=15, font_weight='bold')

# 간선 개별 그리기 (방향 화살표 표시 강조)
edges = G.edges()
weights = [G[u][v]['weight'] for u,v in edges]
nx.draw_networkx_edges(
    G, pos,
    edgelist=edges,
    arrowstyle='->',            # 깔끔한 화살표
    arrowsize=24,                   # 화살표 크기 크게
    connectionstyle='arc3,rad=0.1', # 살짝 곡선(방향 중복시 구분)
    width=2
)

# 간선 라벨(가중치)
edge_labels={(u,v): G[u][v]['weight'] for u,v in edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=13, label_pos=0.38)

plt.title('방향 표시가 명확한 가중치 그래프')
plt.axis('off')
plt.show()
#=========================================================================


def Floyd_Warshall():
    dist = [[INF]*n for i in range(n)]

    for i in range(n):         
        for j in range(n):     
           dist[i][j] = a[i][j]

    for k in range(n):        
        for i in range(n):     
            for j in range(n): 
              if dist[i][j] > dist[i][k] + dist[k][j]:
                 dist[i][j] = dist[i][k] + dist[k][j]

    return dist


dist = Floyd_Warshall()

print ("\n==============================")
for i in range(n):
    print("모든 정점 간의 최단 경로 값,  정점 = ", i)
    for j in range(n):
        print(dist[i][j], end='')
    print()

