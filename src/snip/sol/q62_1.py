# 7-2 예상문제 1 : SLCAN ASCII 줄 해석 (잘못된 줄은 건너뜀)
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q62_1_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q62_1_output.txt"

def parse(line):
    """'tIIIL DD..' → (id, dlc, data) / 형식 오류면 None"""
    if len(line) < 5 or line[0] != "t":              # 표준 ID('t')만 처리
        return None
    try:
        arb = int(line[1:4], 16); dlc = int(line[4], 16)
        if dlc > 8 or len(line[5:]) != 2*dlc:
            return None
        return arb, dlc, bytes.fromhex(line[5:])
    except ValueError:
        return None

ok = bad = 0
with open(IN_FILE, "r", encoding="ascii") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    for line in fin:
        fr = parse(line.strip())
        if fr is None:
            bad += 1; fout.write(f"SKIP {line.strip()}\n"); continue
        ok += 1
        arb, dlc, data = fr
        fout.write(f"ID=0x{arb:03X} DLC={dlc} DATA={data.hex(' ').upper()}\n")
    fout.write(f"valid {ok}, skipped {bad}\n")
