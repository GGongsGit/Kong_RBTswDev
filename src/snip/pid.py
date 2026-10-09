import numpy as np

class PID:
    def __init__(self, Kp, Ki, Kd, Ts, umin=-np.inf, umax=np.inf, Td=0.02):
        self.Kp, self.Ki, self.Kd, self.Ts = Kp, Ki, Kd, Ts
        self.umin, self.umax, self.Td = umin, umax, Td
        self.I = 0.0; self.e_prev = 0.0; self.d = 0.0

    def step(self, e):
        alpha = self.Td / (self.Td + self.Ts)               # D항 저역통과 필터
        self.d = alpha*self.d + (1 - alpha)*(e - self.e_prev)/self.Ts
        u_raw = self.Kp*e + self.I + self.Kd*self.d
        u = np.clip(u_raw, self.umin, self.umax)            # 출력 포화
        self.I += self.Ki*self.Ts*e + (u - u_raw)           # 안티와인드업
        self.e_prev = e
        return u

# 질량-스프링-댐퍼:  m·y'' + c·y' + k·y = u
m, c, k, Ts = 1.0, 0.6, 4.0, 0.002
pid = PID(60, 40, 4, Ts, -10, 10)
y = yd = 0.0
for i in range(int(6/Ts)):
    u = pid.step(1.0 - y)                   # 목표 1.0
    ydd = (u - c*yd - k*y)/m
    yd += Ts*ydd                            # 오일러 적분
    y  += Ts*yd
print(f"y(6s) = {y:.3f}")
