# motor.dbc:  BO_ 512 MotorStatus: 8
#  SG_ RPM          : 0|16@1+  (1,0)     "rpm"
#  SG_ PhaseCurrent : 16|16@1- (0.01,0)  "A"
#  SG_ Temperature  : 32|8@1+  (1,0)     "°C"
#  SG_ FaultFlags   : 40|8@1+  (1,0)
raw = bytes([0x10, 0x27, 0x05, 0x00, 0x32, 0x01, 0x00, 0x00])

rpm   = int.from_bytes(raw[0:2], "little")                    # @1 = Intel(little endian)
cur_a = int.from_bytes(raw[2:4], "little", signed=True) * 0.01  # '-' = signed, factor 0.01
temp  = raw[4]
fault = raw[5]
print(rpm, cur_a, temp, fault)        # 10000 0.05 50 1

# cantools가 있으면 같은 결과
# import cantools
# db = cantools.database.load_file("motor.dbc")
# print(db.get_message_by_frame_id(0x200).decode(raw))
