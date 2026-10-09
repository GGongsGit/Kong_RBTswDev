INF = float('inf')
a = [[0,   2,   INF, 4  ],
     [2,   0,   INF, 5  ],
     [3,   INF, 0,   INF],
     [INF, 2,   1,   0  ]]
n = len(a)
dist = [row[:] for row in a]                 # 원본 보존용 복사

for k in range(n):                           # 경유 노드 k가 가장 바깥 반복
    for i in range(n):
        for j in range(n):
            if dist[i][k] + dist[k][j] < dist[i][j]:
                dist[i][j] = dist[i][k] + dist[k][j]

for row in dist:
    print(row)
# [0, 2, 5, 4] / [2, 0, 6, 5] / [3, 5, 0, 7] / [4, 2, 1, 0]
