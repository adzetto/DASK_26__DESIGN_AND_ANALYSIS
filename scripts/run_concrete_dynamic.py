"""SDOF Dynamic Analysis - BALSA MODEL (1:100 Scale)
Shake table simulation with time-scaled ground motion.
"""
import numpy as np
from pathlib import Path

print("=" * 60)
print("DYNAMIC ANALYSIS - BALSA MODEL (Shake Table)")
print("=" * 60)

# Balsa model properties
T1 = 0.20       # Fundamental period (s) - user estimate
xi = 0.03       # 3% damping (balsa/wood)
H = 1.53        # Model height (m)
SCALE = 100     # Geometric scale factor

# Similitude: time_model = time_real / sqrt(SCALE)
TIME_SCALE = np.sqrt(SCALE)  # = 10

# Derived properties
omega = 2 * np.pi / T1
k = omega**2  # Normalized (m=1)
m = 1.0
c = 2 * xi * omega * m

print(f"Model Period T1 = {T1:.3f} s")
print(f"Damping = {xi*100:.0f}%")
print(f"Time compression factor = {TIME_SCALE:.1f}x")

# Load ground motion
GM_FILE = Path(__file__).parent.parent / 'ground_motion' / 'BOL090.AT2'
accel_raw = []
dt_real = 0.01
with open(GM_FILE) as f:
    for line in f.readlines()[4:]:
        accel_raw.extend([float(x) for x in line.split()])

accel_raw = np.array(accel_raw)

# Time-scale the ground motion for shake table
# dt_model = dt_real / sqrt(lambda) = 0.01 / 10 = 0.001s
dt = dt_real / TIME_SCALE  # 0.001s

# Scale acceleration to m/s² (acceleration scales as lambda for similitude)
# For shake table: a_model = a_real * SCALE (to maintain F/m similarity)
# But typically we apply the SAME acceleration (PGA) to the model
# Using same PGA approach:
accel = accel_raw * 9.81  # Convert g to m/s²

print(f"Ground motion: {len(accel)} points")
print(f"dt (model) = {dt*1000:.1f} ms")
print(f"Duration (model) = {len(accel)*dt:.1f} s")
print(f"PGA = {np.max(np.abs(accel_raw)):.3f} g")

# Newmark-Beta integration
n = len(accel)
u = np.zeros(n)
v = np.zeros(n)
a = np.zeros(n)

beta = 0.25
gamma = 0.5

a[0] = -accel[0] - c*v[0] - k*u[0]
k_eff = k + gamma/(beta*dt)*c + 1/(beta*dt**2)*m

print("\nRunning Newmark integration...")
for i in range(n-1):
    p_eff = (-m*accel[i+1]
             + m*(1/(beta*dt**2)*u[i] + 1/(beta*dt)*v[i] + (1/(2*beta)-1)*a[i])
             + c*(gamma/(beta*dt)*u[i] + (gamma/beta-1)*v[i] + dt*(gamma/(2*beta)-1)*a[i]))

    u[i+1] = p_eff / k_eff
    v[i+1] = gamma/(beta*dt)*(u[i+1]-u[i]) + (1-gamma/beta)*v[i] + dt*(1-gamma/(2*beta))*a[i]
    a[i+1] = 1/(beta*dt**2)*(u[i+1]-u[i]) - 1/(beta*dt)*v[i] - (1/(2*beta)-1)*a[i]

# Results
max_u = np.max(np.abs(u))
# Modal participation factor ~1.3
max_roof = max_u * 1.3
drift_pct = (max_roof / H) * 100

# Total mass of balsa model (approximate from data)
M_model = 0.015  # ~15 grams = 0.015 kg total mass estimate
max_V = k * max_u * M_model  # Base shear in N

# Find time of max displacement
idx_max = np.argmax(np.abs(u))
t_max = idx_max * dt

print("\n" + "=" * 60)
print("RESULTS - BALSA MODEL")
print("=" * 60)
print(f"Max SDOF Displacement: {max_u*1000:.2f} mm")
print(f"Max Roof Displacement: {max_roof*1000:.2f} mm")
print(f"Drift Ratio: {drift_pct:.2f} %")
print(f"Time of Max Response: {t_max:.2f} s (model time)")
print(f"Max Base Shear: {max_V*1000:.1f} mN ({max_V:.3f} N)")
print()

# Competition criteria
if drift_pct < 1.0:
    print("Status: EXCELLENT - Minimal damage expected")
elif drift_pct < 2.0:
    print("Status: GOOD - Light damage, repairable")
elif drift_pct < 4.0:
    print("Status: FAIR - Moderate damage")
else:
    print("Status: POOR - Severe damage / potential collapse")

# Prototype equivalent
print("\n" + "-" * 60)
print("PROTOTYPE EQUIVALENT (153m building)")
print("-" * 60)
T_proto = T1 * TIME_SCALE  # 0.4s
disp_proto = max_roof * SCALE  # Scale displacement
drift_proto = drift_pct  # Drift ratio is dimensionless, same
print(f"Equivalent Period: {T_proto:.2f} s")
print(f"Equivalent Roof Disp: {disp_proto*1000:.0f} mm = {disp_proto:.2f} m")
print(f"Drift Ratio: {drift_proto:.2f} %")

# Save results
RESULTS_DIR = Path(__file__).parent.parent / 'results' / 'concrete_sim'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

t = np.arange(n) * dt
np.savetxt(RESULTS_DIR / 'balsa_response.csv',
           np.column_stack([t, u*1000, v*1000, a]),
           header='time_s,disp_mm,vel_mm_s,accel_m_s2', delimiter=',', comments='')

print(f"\nResponse saved to: {RESULTS_DIR / 'balsa_response.csv'}")
