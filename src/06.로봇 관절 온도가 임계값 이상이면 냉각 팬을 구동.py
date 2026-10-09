# -*- coding: utf-8 -*-
"""
Robot Joint Temperature Monitor → Cooling Fan Control
- Hysteresis on/off thresholds to avoid chattering
- Per-joint monitoring, global fan command
- CSV logging, critical overheat alert, graceful shutdown
- Mock sensor & mock fan by default
- Optional SerialFanController for Arduino/relay (pyserial)

사용:
  python joint_temp_fan_control.py
실장 시:
  1) read_joint_temps() 를 실제 센서/로봇 API로 교체
  2) FanController 구현체(SerialFanController 등)로 교체
"""

import csv
import time
import datetime as dt
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

# -----------------------------
# 구성 파라미터
# -----------------------------
@dataclass
class Config:
    joint_names: List[str] = field(default_factory=lambda: ["J1","J2","J3","J4","J5","J6"])
    sample_period_s: float = 0.5          # 샘플링 주기
    on_threshold_c: float = 48.0          # 팬 켜짐 (≥ 이 값인 관절이 하나라도 있으면 ON)
    off_threshold_c: float = 40.0         # 팬 꺼짐 (모든 관절 < 이 값 & 홀드시간 충족 시 OFF)
    off_hold_time_s: float = 20.0         # 끄기 전에 이 시간 동안 조건 유지 필요
    critical_threshold_c: float = 80.0     # 치명 임계 (즉시 최대속도 + 경고)
    pwm_low: int = 40                      # 팬 ON 시 최소 PWM(%)
    pwm_high: int = 100                    # 치명 영역 PWM(%)
    log_csv: str = "joint_temp_log.csv"    # 로그 파일
    print_every_n: int = 4                 # 콘솔 출력 간격(샘플 N회마다 한 번)
    use_serial_fan: bool = False           # 직렬 포트 팬 제어 사용 여부
    serial_port: str = "COM5"              # 예: Windows COM5 / Linux '/dev/ttyUSB0'
    serial_baud: int = 115200


# -----------------------------
# 팬 제어 추상화
# -----------------------------
class FanController:
    """팬 제어 인터페이스"""
    def set_speed_percent(self, percent: int):
        raise NotImplementedError
    def turn_off(self):
        self.set_speed_percent(0)

class MockFanController(FanController):
    def __init__(self):
        self._last = -1
    def set_speed_percent(self, percent: int):
        percent = max(0, min(100, int(percent)))
        if percent != self._last:
            print(f"[FAN] set {percent}%")
            self._last = percent

class SerialFanController(FanController):
    """
    간단한 직렬 제어 예시 (아두이노 등과 통신)
    - 장치 측 프로토콜 예: "PWM:0..100\\n"
    """
    def __init__(self, port: str, baud: int):
        try:
            import serial  # pip install pyserial
        except ImportError:
            raise RuntimeError("pyserial 미설치: `pip install pyserial` 후 사용하세요.")
        self.ser = serial.Serial(port=port, baudrate=baud, timeout=1)
        self._last = -1
    def set_speed_percent(self, percent: int):
        percent = max(0, min(100, int(percent)))
        if percent != self._last:
            cmd = f"PWM:{percent}\n".encode("ascii")
            self.ser.write(cmd)
            self._last = percent
    def __del__(self):
        try:
            self.ser.close()
        except Exception:
            pass


# -----------------------------
# 센서 읽기 (실장 시 교체)
# -----------------------------
def read_joint_temps(joint_names: List[str]) -> Dict[str, float]:
    """
    실제 환경에서는 로봇 API/센서(CAN/Modbus/TCP/SDK 등)로 교체:
      예) return robot.get_joint_temperatures()  # { 'J1': 43.2, ... }
    현재는 데모용 모의 센서(시간 경과에 따라 들쑥날쑥)입니다.
    """
    import math, random, time
    t = time.time()
    temps = {}
    base = 45.0 + 8.0*math.sin(t/15.0)
    for i, jn in enumerate(joint_names):
        noise = random.uniform(-1.2, 1.8)
        bump = 0.0
        if i in (2, 4):  # 일부 관절 더 뜨겁게
            bump = 10.0*max(0.0, math.sin(t/30.0))
        temps[jn] = base + bump + noise
    return temps


# -----------------------------
# 로직
# -----------------------------
class TempGuard:
    """
    온도 기반 팬 제어 로직 (히스테리시스 + 홀드시간)
    - 하나라도 on_threshold 이상이면 팬 ON
    - 모든 관절이 off_threshold 미만 상태가 off_hold_time 동안 지속되면 팬 OFF
    - critical 이상이면 즉시 100%
    """
    def __init__(self, cfg: Config, fan: FanController):
        self.cfg = cfg
        self.fan = fan
        self._fan_on = False
        self._off_eligible_since: Optional[float] = None
        self._tick = 0

        # CSV 헤더 준비
        try:
            with open(cfg.log_csv, "x", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["timestamp"] + cfg.joint_names + ["fan_percent"])
        except FileExistsError:
            pass

    def _decide_speed(self, max_temp: float) -> int:
        c = self.cfg
        if max_temp >= c.critical_threshold_c:
            return c.pwm_high
        # 선형 맵핑 (on_threshold ~ critical 구간)
        if max_temp <= c.on_threshold_c:
            return c.pwm_low
        span = max(1e-6, c.critical_threshold_c - c.on_threshold_c)
        frac = (max_temp - c.on_threshold_c) / span
        return int(round(c.pwm_low + frac * (c.pwm_high - c.pwm_low)))

    def step(self, temps: Dict[str, float]) -> Tuple[bool, int]:
        """
        temps: {joint: temp_celsius}
        반환: (fan_on(bool), fan_pwm(int))
        """
        now = time.time()
        c = self.cfg
        max_temp = max(temps.values()) if temps else float("-inf")
        min_temp = min(temps.values()) if temps else float("inf")

        # 팬 ON 조건
        must_on = max_temp >= c.on_threshold_c
        # 팬 OFF 조건 (모든 관절이 off_threshold 미만 + 홀드시간 충족)
        off_cond = (max_temp < c.off_threshold_c)

        if must_on:
            self._fan_on = True
            self._off_eligible_since = None
        else:
            # OFF 후보 상태 누적
            if off_cond:
                if self._off_eligible_since is None:
                    self._off_eligible_since = now
                elif (now - self._off_eligible_since) >= c.off_hold_time_s:
                    self._fan_on = False
                    self._off_eligible_since = None
            else:
                self._off_eligible_since = None

        # PWM 결정
        pwm = 0
        if self._fan_on:
            pwm = self._decide_speed(max_temp)
            self.fan.set_speed_percent(pwm)
        else:
            self.fan.turn_off()

        # 로그/간이 출력
        self._tick += 1
        ts = dt.datetime.now().isoformat(timespec="seconds")
        self._write_csv(ts, temps, pwm)
        if (self._tick % c.print_every_n) == 0:
            print(f"[{ts}] max={max_temp:.1f}°C min={min_temp:.1f}°C fan={'ON' if self._fan_on else 'OFF'}({pwm}%)")

        # 치명 임계 경고
        if max_temp >= c.critical_threshold_c:
            print(f"[ALERT] CRITICAL overheat! max={max_temp:.1f}°C >= {c.critical_threshold_c:.1f}°C")

        return self._fan_on, pwm

    def _write_csv(self, ts: str, temps: Dict[str, float], pwm: int):
        row = [ts] + [round(temps.get(j, float('nan')), 2) for j in self.cfg.joint_names] + [pwm]
        try:
            with open(self.cfg.log_csv, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(row)
        except Exception as e:
            print(f"[WARN] CSV write failed: {e}")


def main():
    cfg = Config()

    # 팬 컨트롤러 선택
    if cfg.use_serial_fan:
        fan = SerialFanController(cfg.serial_port, cfg.serial_baud)
    else:
        fan = MockFanController()

    guard = TempGuard(cfg, fan)

    print("[INFO] Joint temperature monitor started.")
    print(f"       ON≥{cfg.on_threshold_c}°C  |  OFF<{cfg.off_threshold_c}°C for {cfg.off_hold_time_s}s  |  CRIT≥{cfg.critical_threshold_c}°C")
    print(f"       Logging to: {cfg.log_csv}")

    try:
        while True:
            temps = read_joint_temps(cfg.joint_names)
            guard.step(temps)
            time.sleep(cfg.sample_period_s)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping. Turning fan off.")
        try:
            fan.turn_off()
        except Exception:
            pass


if __name__ == "__main__":
    main()
