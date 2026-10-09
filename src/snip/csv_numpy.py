import numpy as np

CSV_FILE = r"C:\KONG_2027Prg\RBTSW_Results\xy_data.csv"

xy = np.array([[0.68, 1.18], [0.00, 1.21], [-0.50, 0.87]])

# ---------- 쓰기 : 숫자만 있는 표에 가장 짧다 ----------
np.savetxt(CSV_FILE, xy, delimiter=",", fmt="%.2f",
           header="x,y", comments="",            # comments="" 없으면 머리글 앞에 '# '가 붙음
           encoding="utf-8")

# ---------- 읽기 ----------
arr = np.loadtxt(CSV_FILE, delimiter=",", skiprows=1, encoding="utf-8")
print(arr.shape, arr[0])                         # (3, 2) [0.68 1.18]
