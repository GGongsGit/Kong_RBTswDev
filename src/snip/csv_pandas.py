import numpy as np
import pandas as pd

CSV_FILE = r"C:\KONG_2027Prg\RBTSW_Results\cubic_trajectory.csv"

t = np.linspace(0, 1, 11)
q = 0.5236 + 3.1416*t**2 - 2.0944*t**3

# ---------- 쓰기 ----------
df = pd.DataFrame({"Time(s)": t, "Pos(rad)": q})
df.to_csv(CSV_FILE, index=False,                 # 행 번호(0,1,2…) 열 빼기
          encoding="utf-8-sig",                  # 엑셀에서 한글 안 깨짐
          float_format="%.4f")                   # 소수 4자리

# ---------- 읽기 ----------
df2 = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
print(df2.columns.tolist())                      # ['Time(s)', 'Pos(rad)']
print(df2["Pos(rad)"].iloc[-1])                  # 1.5708
q_arr = df2["Pos(rad)"].to_numpy()               # 계산용 numpy 배열
