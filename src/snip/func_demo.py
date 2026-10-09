# 실기 코드에서 자주 쓰는 함수 실행해 보기
import math
import heapq
import numpy as np

# 1) 문자열 → 숫자 : strip, split, replace, float, map
line = "  30 45.5 -10\n"
vals = [float(v) for v in line.strip().split()]
print("1) split + float  :", vals)
row = "0.1,0.25,1.2"
print("   쉼표 입력       :", list(map(float, row.replace(",", " ").split())))

# 2) 형식 출력 : f-문자열
x, y = 0.683013, 1.183013
print(f"2) f-문자열        : {x:.2f} {y:.2f} | {x:8.3f} | {0.000123:.3e} | {7:03d}")

# 3) 도 ↔ 라디안, 삼각함수
th = np.deg2rad(60)
print(f"3) cos 60°         : {np.cos(th):.4f}   (np.cos(60) = {np.cos(60):.4f} ← 라디안으로 착각한 값)")

# 4) arctan2 : 사분면 구분
print(f"4) arctan2(1, -1)  : {np.degrees(np.arctan2(1, -1)):.1f}°   atan(1/-1) = {np.degrees(np.arctan(1 / -1)):.1f}°")

# 5) arccos + clip
c = 1.0000001
print("5) arccos(1.0000001):", np.arccos(c) if abs(c) <= 1 else "nan (범위 밖)",
      "→ clip 후", np.degrees(np.arccos(np.clip(c, -1, 1))))

# 6) 거리
print("6) hypot / dist    :", np.hypot(3, 4), math.dist((0, 0), (3, 4)))

# 7) 행렬 : @, solve
M = np.array([[2.0, 1.0], [1.0, 3.0]])
b = np.array([3.0, 5.0])
sol = np.linalg.solve(M, b)
print("7) solve(M, b)     :", sol, " 검산 M @ x =", M @ sol)

# 8) heapq : 가장 작은 거리부터
h = []
for item in [(5, "B"), (2, "A"), (7, "C")]:
    heapq.heappush(h, item)
print("8) heappop 순서     :", [heapq.heappop(h) for _ in range(3)])

# 9) 경로 역추적 후 뒤집기
parent = {"D": "C", "C": "A", "A": None}
path, node = [], "D"
while node is not None:
    path.append(node)
    node = parent.get(node)
print("9) 경로             :", "-".join(path[::-1]))

# 10) 바이트 ↔ 정수 (CAN)
data = bytes.fromhex("10 27 05 00")
rpm = int.from_bytes(data[0:2], "little")
print("10) CAN 바이트      :", data.hex(" "), "→ rpm =", rpm)
