from heapq import heappush, heappop
from math import sqrt
import numpy as np
import matplotlib
matplotlib.use("Agg")                # 창 없이 파일로만 저장
import matplotlib.pyplot as plt

Grid_path_filename = r"C:\KONG_2027Prg\RBTSW_Results\Astar_grid.txt"
Path_path_filename = r"C:\KONG_2027Prg\RBTSW_Results\Astar_path.txt"
Block_path_filename = r"C:\KONG_2027Prg\RBTSW_Results\Astar_block.txt"

grid = [
    [0,0,0,1,0,1,0],
    [1,1,0,1,0,1,0],
    [0,0,0,0,0,1,0],
    [0,1,0,0,1,0,0],
    [0,1,1,0,1,1,0],
    [0,1,0,0,0,0,0],
    [0,0,0,1,0,1,0],
]

start = (0, 0)
goal = (6,4)

# (dr, dc, cost) -> (행(row), 열(col), 이동거리)
# (1,-1)   (1,0)   (1,1)        ↖  ↑  ↗
# (0,-1)   현재    (0,1)         ←  ●  →
# (-1,-1)  (-1,0)  (-1,1)       ↙  ↓  ↘
NEI = [(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),
      (1,1,sqrt(2)),(1,-1,sqrt(2)),(-1,1,sqrt(2)),(-1,-1,sqrt(2))]

# j2셀에 넣는 수식 =IF(INDEX($A$2:$G$8,INT((ROW()-2)/7)+1,MOD(ROW()-2,7)+1)=1,MOD(ROW()-2,7),NA())
# k2셀에 넣는 수식 =IF(INDEX($A$2:$G$8,INT((ROW()-2)/7)+1,MOD(ROW()-2,7)+1)=1,INT((ROW()-2)/7),NA())
# 총 셀의 갯수가 7*7=49개이므로, 2~50행까지 수식을 넣으면 됨
#

def astar(grid, start, goal):
    grid = np.array(grid, dtype=int)
    R, C = grid.shape
    sr, sc = start
    gr, gc = goal

    def h(r, c):
        return sqrt((r - gr)**2 + (c - gc)**2)

    open_heap = [(h(sr, sc), sr, sc)]
    g_score = {(sr, sc): 0}
    came_from = {}

    while open_heap:
        _, r, c = heappop(open_heap)

        if (r, c) == (gr, gc):
            path = []
            while (r, c) in came_from:
                path.append((r, c))
                r, c = came_from[(r, c)]
            path.append((sr, sc))
            return path[::-1], g_score[(gr, gc)]

        for dr, dc, cost in NEI:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr, nc] == 0:
                new_g = g_score[(r, c)] + cost
                if (nr, nc) not in g_score or new_g < g_score[(nr, nc)]:
                    g_score[(nr, nc)] = new_g
                    came_from[(nr, nc)] = (r, c)
                    f = new_g + h(nr, nc)
                    heappush(open_heap, (f, nr, nc))


def save_grid_to_txt(grid, filename):
    """그리드 데이터를 TXT로 저장"""
    R, C = len(grid), len(grid[0])
    with open(filename, 'w', encoding='utf-8') as f:
        # f.write("Grid Data 1 : Block, 0 : 통로\n")
        for r in range(R):
            for c in range(C):
                f.write(str(grid[r][c]) + " ")
            f.write("\n")


def save_path_to_txt(grid, start, goal, filename):
    """경로 데이터를 TXT로 저장"""
    path, cost = astar(grid, start, goal)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Step 행 열 누적거리\n")

        dist = 0
        for i, (r, c) in enumerate(path, 1):
            if i > 1:
                pr, pc = path[i-2]
                dist += sqrt((r-pr)**2 + (c-pc)**2)
            f.write(f"{i} {r} {c} {dist:.3f}\n")

    return path, cost


def save_block_to_txt(grid, filename):
    """블록 데이터를 TXT로 저장"""
    R = len(grid)       # 행 개수 (7)
    C = len(grid[0])    # 열 개수 (7)

    blocks = []                          # Block 좌표를 담을 빈 리스트
    for c in range(C):                   # 열 0 → 6 (바깥 반복)
        for r in range(R):               # 행 0 → 6 (안쪽 반복)
            if grid[r][c] == 1:          # 그 칸이 Block이면
                blocks.append((c, r))    # (열, 행) 추가
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("열 행\n")
        for c, r in blocks:
            f.write(f"{c} {r}\n")



if __name__ == "__main__":
    plt.rcParams["font.family"] = "Malgun Gothic"      # 한글 폰트 (Windows)
    plt.rcParams["axes.unicode_minus"] = False

    save_block_to_txt(grid, Block_path_filename)
    save_grid_to_txt(grid, Grid_path_filename)
    save_path_to_txt(grid, start, goal, Path_path_filename)



# blocks = [(c, r) for c in range(len(grid[0]))
#                     for r in range(len(grid))
#                     if grid[r][c] == 1]