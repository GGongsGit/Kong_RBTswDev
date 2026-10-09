# 7-2 예상문제 2 : CANopen SDO 업로드 요청 프레임(SLCAN 문자열) 만들기
IN_FILE  = r"C:\KONG_2027Prg\RBTSW_Results\q62_2_input.txt"
OUT_FILE = r"C:\KONG_2027Prg\RBTSW_Results\q62_2_output.txt"

def sdo_upload_req(node, index, sub):
    cob_id = 0x600 + node                              # 요청 ID = 0x600 + 노드
    data = bytes([0x40, index & 0xFF, (index >> 8) & 0xFF, sub, 0, 0, 0, 0])
    return f"t{cob_id:03X}8{data.hex().upper()}"       # 끝에 '\r'을 붙여 전송

with open(IN_FILE, "r", encoding="utf-8-sig") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    for line in fin:
        if not line.strip() or line.startswith("#"):
            continue
        node, idx, sub = line.split()
        fout.write(f"{sdo_upload_req(int(node), int(idx, 16), int(sub))}   reply ID 0x{0x580 + int(node):03X}\n")
