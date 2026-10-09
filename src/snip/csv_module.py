import csv

CSV_FILE = r"C:\KONG_2027Prg\RBTSW_Results\joint_data.csv"

# ---------- 쓰기 ----------
rows = [(0.0, 30.0, 45.0), (0.5, 35.2, 47.1), (1.0, 40.0, 50.0)]
with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:   # newline="" 필수
    w = csv.writer(f)
    w.writerow(["time(s)", "θ1(deg)", "θ2(deg)"])                   # 머리글
    for t, th1, th2 in rows:
        w.writerow([f"{t:.2f}", f"{th1:.3f}", f"{th2:.3f}"])       # 자리수 고정

# ---------- 읽기 (열 번호로) ----------
data = []
with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as f:
    r = csv.reader(f)
    header = next(r)                      # 첫 줄(머리글) 건너뛰기
    for row in r:
        if not row:                       # 빈 줄 건너뛰기
            continue
        data.append([float(v) for v in row])
print(header, data[0])                    # ['time(s)', 'θ1(deg)', 'θ2(deg)'] [0.0, 30.0, 45.0]

# ---------- 읽기 (머리글 이름으로) ----------
with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as f:
    for d in csv.DictReader(f):
        print(float(d["time(s)"]), float(d["θ1(deg)"]))
