import os
import numpy as np


A = np.array([[2, 3, 1], [1, 2, 1], [1, -1, 3]])
R = np.array([5, 3, 5])
Equ_Val = np.linalg.solve(A, R)

print(A)
print(R)
print(Equ_Val)

