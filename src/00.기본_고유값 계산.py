import sympy as sp
import sys
import numpy as np

# 기호 변수 정의
a = sp.symbols('a')

# print (dir(sp))

# sys.exit()
# 행렬 정의
# A = sp.Matrix([
#     [2 - a, 1, 1],
#     [1, 2 - a, 1],
#     [0, 0, 3 - a]
# ])

A = np.array([
    [2 - a, 1, 1],
    [1, 2 - a, 1],
    [0, 0, 3 - a]
])

# 행렬 출력
# print("A =")
# sp.pprint(A)


# 행렬식 계산
# f = A.det()
# print("\nDeterminant f =")
# sp.pprint(f)

f_np = np.linalg.det(A)

# 해 구하기
# solutions = sp.solve(f, a)
# print("\nSolutions =")
# print(solutions)

solutions_np = np.linalg.solve(f_np, A)
print(solutions_np)
print(f_np)

