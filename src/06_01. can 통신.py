import can
import cantools

# DBC 불러오기
path = r"C:\MyProgram\로봇SW개발기사\예상문제\motor.dbc"
db = cantools.database.load_file(path)
msg_def = db.get_message_by_frame_id(0x200)  # ID 0x200 메시지

# 윈도우즈 CAN Bus Open : Kvaser 사용
bus = can.interface.Bus(channel=0, bustype="kvaser", bitrate=500000)

print("온도 수신 시작 (Ctrl+C 종료)")
try:
    while True:
        msg = bus.recv(1.0)  # 1초 대기
        if msg and msg.arbitration_id == 0x200:
            decoded = msg_def.decode(msg.data)
            print(f"Temperature = {decoded['Temperature']} °C")
except KeyboardInterrupt:
    pass




import cantools

path = r"C:\MyProgram\로봇SW개발기사\예상문제\motor.dbc"
db = cantools.database.load_file(path )
msg = db.get_message_by_frame_id(0x200)  # 512 decimal = 0x200 hex

raw_data = bytes([0x10, 0x27, 0x05, 0x00, 0x32, 0x01, 0x00, 0x00])
decoded = msg.decode(raw_data)

print(decoded)