# 3-1 예상문제 2 : 3축 등속 동기화
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q31_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q31_2_output.txt"

axes = []
with open(IN_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, t0, t1, vmax = line.split()
        axes.append((name, float(t0), float(t1), float(vmax)))

T_each = [abs(t1 - t0) / vmax for _, t0, t1, vmax in axes]
T_sync = max(T_each)                                    # 가장 느린 축에 맞춤

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(f"T_sync {T_sync:.3f}\n")
    f.write("axis T_alone v_sync(deg/s)\n")
    for (name, t0, t1, _), T in zip(axes, T_each):
        f.write(f"{name} {T:.3f} {(t1 - t0) / T_sync:.3f}\n")
