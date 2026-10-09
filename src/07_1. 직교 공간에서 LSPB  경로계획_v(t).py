import numpy as np
import matplotlib.pyplot as plt

def lspb_profile(L, Vmax, amax, dt=0.001):
    # 1. 가감속 구간 시간
    t_a = Vmax / amax
    d_a = 0.5 * amax * t_a**2

    # 2. 등속구간 거리
    d_c = L - 2 * d_a

    if d_c >= 0:  # 등속구간 존재
        t_c = d_c / Vmax
        T = 2 * t_a + t_c
        t_arr = np.arange(0, T+dt, dt)
        s = np.zeros_like(t_arr)
        v = np.zeros_like(t_arr)
        a = np.zeros_like(t_arr)
        
        for i, t in enumerate(t_arr):
            if t < t_a:  # 가속 구간
                s[i] = 0.5 * amax * t**2
                v[i] = amax * t
                a[i] = amax
            elif t < t_a + t_c:  # 등속 구간
                s[i] = d_a + Vmax * (t - t_a)
                v[i] = Vmax
                a[i] = 0
            else:  # 감속 구간
                tau = t - t_a - t_c
                s[i] = d_a + d_c + Vmax * tau - 0.5 * amax * tau**2
                v[i] = Vmax - amax * tau
                a[i] = -amax
    else:  # 등속구간 없음
        Vpeak = np.sqrt(L * amax)
        t_a = Vpeak / amax
        T = 2 * t_a
        t_arr = np.arange(0, T+dt, dt)
        s = np.zeros_like(t_arr)
        v = np.zeros_like(t_arr)
        a = np.zeros_like(t_arr)
        
        for i, t in enumerate(t_arr):
            if t < t_a:
                s[i] = 0.5 * amax * t**2
                v[i] = amax * t
                a[i] = amax
            else:
                tau = t - t_a
                s[i] = 0.5 * Vpeak**2 / amax + Vpeak * tau - 0.5 * amax * tau**2
                v[i] = Vpeak - amax * tau
                a[i] = -amax
    
    return t_arr, s, v, a, t_a, d_a, t_c if d_c >= 0 else 0, d_c if d_c >= 0 else 0

# 파라미터
L = 0.76      # 총 거리 (m)
Vmax = 0.70   # 최대 속도 (m/s)
amax = 1.0    # 최대 가속도 (m/s²)

# LSPB 프로필 생성
t, s, v, a, t_a, d_a, t_c, d_c = lspb_profile(L, Vmax, amax)

# 구간 정보 계산
T = t[-1]
t_a_end = t_a
t_c_start = t_a
t_c_end = t_a + t_c
t_dec_start = t_a + t_c
t_dec_end = T

print("=" * 60)
print("LSPB (Linear Segment with Parabolic Blends) 분석")
print("=" * 60)
print(f"총 거리 (L): {L:.4f} m")
print(f"최대 속도 (Vmax): {Vmax:.4f} m/s")
print(f"최대 가속도 (amax): {amax:.4f} m/s²")
print("-" * 60)
print(f"[가속 구간]")
print(f"  시간: 0 ~ {t_a_end:.4f} s")
print(f"  거리: 0 ~ {d_a:.4f} m")
print(f"  식: s(t) = 0.5 * amax * t²")
print("-" * 60)
print(f"[등속 구간]")
print(f"  시간: {t_c_start:.4f} ~ {t_c_end:.4f} s")
print(f"  거리: {d_a:.4f} ~ {d_a + d_c:.4f} m")
print(f"  식: s(t) = d_a + Vmax * (t - t_a)")
print("-" * 60)
print(f"[감속 구간]")
print(f"  시간: {t_dec_start:.4f} ~ {t_dec_end:.4f} s")
print(f"  거리: {d_a + d_c:.4f} ~ {L:.4f} m")
print(f"  식: s(t) = d_a + d_c + Vmax * τ - 0.5 * amax * τ²")
print("-" * 60)
print(f"전체 소요 시간 (T): {T:.4f} s")
print("=" * 60)

# ===== 그래프 그리기 =====
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# 1. 위치 vs 시간
ax1.plot(t, s, 'b-', linewidth=2.5, label='Position s(t)')
ax1.axvline(x=t_a_end, color='r', linestyle='--', alpha=0.7, label='Acceleration end')
ax1.axvline(x=t_c_end, color='g', linestyle='--', alpha=0.7, label='Constant velocity end')
ax1.fill_between([0, t_a_end], 0, L, alpha=0.1, color='red', label='Acceleration phase')
ax1.fill_between([t_c_start, t_c_end], 0, L, alpha=0.1, color='green', label='Constant velocity phase')
ax1.fill_between([t_dec_start, t_dec_end], 0, L, alpha=0.1, color='orange', label='Deceleration phase')
ax1.set_xlabel('Time (s)', fontsize=11)
ax1.set_ylabel('Position (m)', fontsize=11)
ax1.set_title('LSPB: Position vs Time', fontsize=13, fontweight='bold')
ax1.legend(fontsize=9, loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.set_ylim([0, L*1.1])

# 2. 속도 vs 시간
ax2.plot(t, v, 'g-', linewidth=2.5, label='Velocity v(t)')
ax2.axvline(x=t_a_end, color='r', linestyle='--', alpha=0.7)
ax2.axvline(x=t_c_end, color='g', linestyle='--', alpha=0.7)
ax2.axhline(y=Vmax, color='b', linestyle=':', alpha=0.7, label=f'Vmax = {Vmax} m/s')
ax2.fill_between([0, t_a_end], 0, Vmax*1.2, alpha=0.1, color='red')
ax2.fill_between([t_c_start, t_c_end], 0, Vmax*1.2, alpha=0.1, color='green')
ax2.fill_between([t_dec_start, t_dec_end], 0, Vmax*1.2, alpha=0.1, color='orange')
ax2.set_xlabel('Time (s)', fontsize=11)
ax2.set_ylabel('Velocity (m/s)', fontsize=11)
ax2.set_title('LSPB: Velocity vs Time', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10, loc='upper left')
ax2.grid(True, alpha=0.3)
ax2.set_ylim([0, Vmax*1.2])

# 3. 가속도 vs 시간
ax3.plot(t, a, 'r-', linewidth=2.5, label='Acceleration a(t)')
ax3.axvline(x=t_a_end, color='r', linestyle='--', alpha=0.7)
ax3.axvline(x=t_c_end, color='g', linestyle='--', alpha=0.7)
ax3.axhline(y=amax, color='b', linestyle=':', alpha=0.7, label=f'amax = {amax} m/s²')
ax3.axhline(y=-amax, color='orange', linestyle=':', alpha=0.7, label=f'-amax = {-amax} m/s²')
ax3.axhline(y=0, color='k', linestyle='-', linewidth=1, alpha=0.3)
ax3.fill_between([0, t_a_end], -amax*1.5, amax*1.5, alpha=0.1, color='red')
ax3.fill_between([t_c_start, t_c_end], -amax*1.5, amax*1.5, alpha=0.1, color='green')
ax3.fill_between([t_dec_start, t_dec_end], -amax*1.5, amax*1.5, alpha=0.1, color='orange')
ax3.set_xlabel('Time (s)', fontsize=11)
ax3.set_ylabel('Acceleration (m/s²)', fontsize=11)
ax3.set_title('LSPB: Acceleration vs Time', fontsize=13, fontweight='bold')
ax3.legend(fontsize=10, loc='upper left')
ax3.grid(True, alpha=0.3)
ax3.set_ylim([-amax*1.5, amax*1.5])

# 텍스트 박스로 구간 표시
textstr_acc = f'가속\n(0~{t_a_end:.2f}s)'
ax1.text(t_a_end/2, L*0.95, textstr_acc, ha='center', fontsize=9, 
         bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))

textstr_const = f'등속\n({t_c_start:.2f}~{t_c_end:.2f}s)'
ax1.text((t_c_start+t_c_end)/2, L*0.95, textstr_const, ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='green', alpha=0.3))

textstr_dec = f'감속\n({t_dec_start:.2f}~{t_dec_end:.2f}s)'
ax1.text((t_dec_start+t_dec_end)/2, L*0.95, textstr_dec, ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))

plt.tight_layout()
plt.show()




import numpy as np
import matplotlib.pyplot as plt

# 시작점과 끝점
P0 = np.array([0.0, 0.0])
P1 = np.array([0.7, 0.3])

# LSPB 프로필
t, s, v, a, t_a, d_a, t_c, d_c = lspb_profile(L, Vmax, amax)

# 1D Position → 2D 좌표 변환
lambda_ = s / L
x = P0[0] + lambda_ * (P1[0] - P0[0])
y = P0[1] + lambda_ * (P1[1] - P0[1])

# ===== 그래프 =====
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# (0, 0) 1D Position vs Time
ax = axes[0, 0]
ax.plot(t, s, 'b-', linewidth=2.5, label='s(t) - 1D Position')
ax.set_xlabel('Time (s)', fontsize=11)
ax.set_ylabel('Position s(t) (m)', fontsize=11)
ax.set_title('1D Position vs Time (시작점에서부터의 거리)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

# (0, 1) 2D 경로
ax = axes[0, 1]
ax.plot(x, y, 'b-', linewidth=2.5, label='2D Path')
ax.plot(P0[0], P0[1], 'go', markersize=12, label='Start P0')
ax.plot(P1[0], P1[1], 'ro', markersize=12, label='End P1')
ax.set_xlabel('X (m)', fontsize=11)
ax.set_ylabel('Y (m)', fontsize=11)
ax.set_title('2D Path (실제 로봇 경로)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
ax.axis('equal')

# (1, 0) X 좌표 vs Time
ax = axes[1, 0]
ax.plot(t, x, 'r-', linewidth=2.5, label='x(t)')
ax.axhline(y=P0[0], color='g', linestyle='--', alpha=0.7, label=f'Start X = {P0[0]}')
ax.axhline(y=P1[0], color='b', linestyle='--', alpha=0.7, label=f'End X = {P1[0]}')
ax.set_xlabel('Time (s)', fontsize=11)
ax.set_ylabel('X Position (m)', fontsize=11)
ax.set_title('X Coordinate vs Time', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

# (1, 1) Y 좌표 vs Time
ax = axes[1, 1]
ax.plot(t, y, 'g-', linewidth=2.5, label='y(t)')
ax.axhline(y=P0[1], color='r', linestyle='--', alpha=0.7, label=f'Start Y = {P0[1]}')
ax.axhline(y=P1[1], color='b', linestyle='--', alpha=0.7, label=f'End Y = {P1[1]}')
ax.set_xlabel('Time (s)', fontsize=11)
ax.set_ylabel('Y Position (m)', fontsize=11)
ax.set_title('Y Coordinate vs Time', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

plt.tight_layout()
plt.show()

# 특정 시간에서의 위치 출력
print("=" * 70)
print("Position의 의미 - 특정 시간에서의 좌표")
print("=" * 70)
print(f"시작점 P0: {P0}")
print(f"끝점 P1: {P1}")
print(f"총 거리 L: {L:.4f} m")
print("-" * 70)

time_indices = [0, len(t)//4, len(t)//2, 3*len(t)//4, -1]
for idx in time_indices:
    print(f"\n시간 t = {t[idx]:.4f} s:")
    print(f"  1D Position s(t) = {s[idx]:.4f} m")
    print(f"  진행 비율 λ = {s[idx]/L:.4f} ({s[idx]/L*100:.2f}%)")
    print(f"  2D 좌표 = ({x[idx]:.4f}, {y[idx]:.4f})")
    print(f"  속도 = {v[idx]:.4f} m/s")
print("=" * 70)
