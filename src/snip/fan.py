ON_C, OFF_C, CRIT_C = 48.0, 40.0, 80.0

def fan_command(temps, fan_on):
    """temps: {'J1': 45.2, ...}  →  (fan_on, pwm%)"""
    t_max = max(temps.values())
    if t_max >= CRIT_C:
        return True, 100                  # 치명 온도: 최대 출력 + 경고
    if not fan_on and t_max >= ON_C:      # 켜기 기준 (높은 값)
        fan_on = True
    elif fan_on and t_max < OFF_C:        # 끄기 기준 (낮은 값) → 히스테리시스
        fan_on = False
    return fan_on, (40 if fan_on else 0)

state = False
for temps in [{'J1': 45}, {'J1': 49}, {'J1': 44}, {'J1': 39}]:
    state, pwm = fan_command(temps, state)
    print(temps['J1'], state, pwm)        # 45 off → 49 on → 44 on(유지) → 39 off
