text = "열 행"

print(text.encode("utf-8"))        # b'\xec\x97\xb4 \xed\x96\x89'          한글 1자 = 3바이트
print(text.encode("utf-8-sig"))    # b'\xef\xbb\xbf\xec\x97\xb4 ...'       앞에 BOM 3바이트
print(text.encode("cp949"))        # b'\xbf\xad \xc7\xe0'                  한글 1자 = 2바이트

# 같은 바이트를 다른 인코딩으로 읽으면 깨진다
raw = text.encode("utf-8")
print(raw.decode("cp949", errors="replace"))   # �뿴 �뻾  ← 모지바케(글자 깨짐)

# BOM이 있는 파일을 utf-8로 읽으면 첫 글자 앞에 '\ufeff'가 붙는다
bom = "x,y\n1,2\n".encode("utf-8-sig")
print(repr(bom.decode("utf-8")[:4]))       # '\ufeffx,y'  → 머리글 'x'가 '\ufeffx'가 됨
print(repr(bom.decode("utf-8-sig")[:4]))   # 'x,y\n'      → 깔끔
