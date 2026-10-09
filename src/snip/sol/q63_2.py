# 7-3 예상문제 2 : 이동평균(3개) 후 과전류 경보 (8.0 A 초과)
import csv

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q63_2_input.csv"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q63_2_output.txt"
N, LIMIT = 3, 8.0

with open(IN_FILE, "r", newline="", encoding="utf-8-sig") as f:
    rows = [(float(r["time"]), float(r["current"])) for r in csv.DictReader(f)]

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("time raw avg alarm\n")
    for i in range(N - 1, len(rows)):                  # 앞 N-1개는 평균 못 냄
        avg = sum(c for _, c in rows[i-N+1:i+1]) / N
        f.write(f"{rows[i][0]:.1f} {rows[i][1]:.1f} {avg:.2f} {'ALARM' if avg > LIMIT else '-'}\n")
