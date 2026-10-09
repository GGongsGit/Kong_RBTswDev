# 8-2 예상문제 1 : OccupancyGrid 값 → PGM 픽셀 (위아래 뒤집기 포함)
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q72_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q72_1_output.txt"

def to_pgm(v):
    if v < 0:
        return 205          # 모름: 회색
    if v >= 65:
        return 0            # 점유: 검정
    return 254              # 비어 있음: 흰색

with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    grid = [[int(s) for s in line.split()] for line in f if line.strip()]

img = [[to_pgm(v) for v in row] for row in grid][::-1]   # ROS는 아래가 0행 → 뒤집기
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(f"P2\n{len(img[0])} {len(img)}\n255\n")       # 텍스트형 PGM 머리글
    for row in img:
        f.write(" ".join(map(str, row)) + "\n")
