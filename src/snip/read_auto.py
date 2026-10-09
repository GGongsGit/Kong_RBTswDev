def read_lines(path):
    """utf-8(-sig) → cp949 순서로 시도해서 한글 파일을 안전하게 읽는다."""
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read().splitlines(), enc
        except UnicodeDecodeError:
            continue
    raise ValueError(f"인코딩을 알 수 없음: {path}")

lines, enc = read_lines(r"C:\KONG_2027Prg\RBTSW_Results\input_data.txt")
print(enc, lines[:3])
