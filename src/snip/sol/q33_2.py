# 3-3 예상문제 2 : steer + 충돌 검사
import math

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q33_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q33_2_output.txt"
STEP = 2.0

grid, pairs, mode = [], [], "grid"
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if line.startswith("# near"):
            mode = "pair"; continue
        if not line or line.startswith("#"):
            continue
        nums = [float(v) for v in line.split()]
        (grid if mode == "grid" else pairs).append(nums)

def steer(p, x):
    d = math.dist(p, x)
    s = min(1.0, STEP / d)
    return (p[0] + (x[0]-p[0])*s, p[1] + (x[1]-p[1])*s)

def collision_free(p, q):
    n = max(int(math.dist(p, q) / 0.5), 1)            # 0.5칸 간격으로 검사
    for i in range(n + 1):
        r = round(p[0] + (q[0]-p[0])*i/n); c = round(p[1] + (q[1]-p[1])*i/n)
        if grid[r][c] == 1:
            return False
    return True

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("near new free\n")
    for nr, nc, xr, xc in pairs:
        new = steer((nr, nc), (xr, xc))
        f.write(f"({nr:.0f},{nc:.0f}) ({new[0]:.3f},{new[1]:.3f}) {'YES' if collision_free((nr, nc), new) else 'NO'}\n")
