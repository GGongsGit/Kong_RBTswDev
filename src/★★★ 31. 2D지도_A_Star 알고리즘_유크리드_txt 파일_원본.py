from heapq import heappush, heappop
from math import sqrt
import numpy as np

Grid_path_filename = r"C:\KONG_2027Prg\RBTSW_Results\Astar_grid.txt"
Path_path_filename = r"C:\KONG_2027Prg\RBTSW_Results\Astar_path.txt"


def astar(grid, start, goal):
    grid = np.array(grid, dtype=int)
    R, C = grid.shape
    sr, sc = start
    gr, gc = goal
    
    NEI = [(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),
           (1,1,sqrt(2)),(1,-1,sqrt(2)),(-1,1,sqrt(2)),(-1,-1,sqrt(2))]
    
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
    
    return None, float('inf')

def save_grid_to_txt(grid, start, goal, filename=Grid_path_filename):
    """그리드 데이터를 TXT로 저장"""
    R, C = len(grid), len(grid[0])
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Grid Data 1 : Block, 0 : 통로\n")
        for r in range(R):
            for c in range(C):
                f.write(str(grid[r][c]) + " ")
            f.write("\n")

def save_path_to_txt(grid, start, goal, filename=Path_path_filename):
    """경로 데이터를 TXT로 저장"""
    path, cost = astar(grid, start, goal)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Step 행 열 누적거리\n")
        
        dist = 0
        if path:
            for i, (r, c) in enumerate(path, 1):
                if i > 1:
                    pr, pc = path[i-2]
                    dist += sqrt((r-pr)**2 + (c-pc)**2)
                f.write(f"{i} {r} {c} {dist:.3f}\n")
    
    return cost, len(path) if path else 0

if __name__ == "__main__":
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
    goal = (6, 6)
    
    # 1. 그리드 데이터 저장
    save_grid_to_txt(grid, start, goal, Grid_path_filename)
    print(f"✓ 저장: {Grid_path_filename} (그리드 데이터)")
    
    # 2. 경로 데이터 저장
    cost, path_len = save_path_to_txt(grid, start, goal, Path_path_filename)
    print(f"✓ 저장: {Path_path_filename}  (경로 데이터)")
    print(f"✓ 비용: {cost:.3f}, 경로: {path_len} 노드")
