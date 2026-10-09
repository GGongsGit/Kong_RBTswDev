# 7-3 예상문제 1 : 히스테리시스 팬 제어 (ON ≥ 48°C, OFF < 40°C)
import csv

IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q63_1_input.csv"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q63_1_output.csv"
ON_C, OFF_C = 48.0, 40.0

fan, switches = False, 0
with open(IN_FILE, "r", newline="", encoding="utf-8-sig") as fin, \
     open(OUT_FILE, "w", newline="", encoding="utf-8-sig") as fout:
    w = csv.writer(fout)
    w.writerow(["time", "t_max", "fan"])
    for row in csv.DictReader(fin):
        t_max = max(float(row[j]) for j in ("J1", "J2", "J3"))
        new = fan
        if not fan and t_max >= ON_C:
            new = True
        elif fan and t_max < OFF_C:
            new = False
        switches += (new != fan); fan = new
        w.writerow([row["time"], f"{t_max:.1f}", "ON" if fan else "OFF"])
print(f"팬 전환 횟수: {switches}")
