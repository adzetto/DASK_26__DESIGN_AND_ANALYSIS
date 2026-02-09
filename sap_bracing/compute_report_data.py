"""Compute all derived values for rapor.tex from SAP2000 analysis results.

Key assumption: SAP model uses real balsa properties (E=2GPa, no scaling).
Capacity is based on real balsa bending strength and joint efficiency.
"""
import json, math
import numpy as np
import pandas as pd
from scipy.stats import norm

# ============================================================================
# PATHS
# ============================================================================
RESULTS = r"c:\Users\lenovo\Desktop\DASK_NEW\results\sap_bracing"
OUT_JSON = f"{RESULTS}/report_data.json"

# ============================================================================
# MODEL & MATERIAL CONSTANTS
# ============================================================================
E_MODEL = 200_000  # N/cm2 (from $2k, BALSA E1=200000; ≈2 GPa, real low-density balsa)

# Section: 6mm x 6mm = 0.6 x 0.6 cm
A_sect = 0.36;  I_sect = 0.0108;  c_sect = 0.3;  S_sect = I_sect / c_sect  # 0.036

# Capacity: real balsa bending strength (model = real, no scaling)
f_b = 3500          # N/cm2 (3.5 kN/cm2 = 35 MPa)
eta_j = 0.35        # joint efficiency
sigma_cap = f_b * eta_j  # 1225 N/cm2 = 12.25 MPa
M_j = sigma_cap * S_sect  # 44.1 N·cm

# PGA values
PGA = {"KYH1": 0.335, "KYH2": 1.243, "KYH3": 1.896}

# Floor Z-levels
floor_z = [0.0, 9.0] + [9.0 + i*6.0 for i in range(1, 25)]  # 26 levels
H_total = 153.0

# TBDY 2018
S_DS = 1.008; S_D1 = 0.514; T_A = 0.102; T_B = 0.510

def Sae(T_val):
    if T_val < T_A: return (0.4 + 0.6*T_val/T_A)*S_DS
    elif T_val <= T_B: return S_DS
    else: return S_D1/T_val

# ============================================================================
# LOAD DATA
# ============================================================================
print("Loading data...")
with open(f"{RESULTS}/analysis_summary.json") as f:
    summary = json.load(f)
modal = summary["modal"]
T = [m["period_s"] for m in modal]
env_df = pd.read_csv(f"{RESULTS}/all_envelopes.csv")
ff_df = pd.read_csv(f"{RESULTS}/all_frame_forces.csv")
coords = pd.read_csv(f"{RESULTS}/joint_coordinates.csv")
print(f"  T1={T[0]:.4f}s T2={T[1]:.4f}s T3={T[2]:.4f}s T4={T[3]:.4f}s")

# ============================================================================
# 1. SPECTRAL ACCELERATIONS
# ============================================================================
spectral = {}
for i, t in enumerate(T[:4], 1):
    s = Sae(t)
    spectral[f"T{i}"] = {"T": round(t, 4), "Sae": round(s, 4)}
    print(f"  Sae(T{i}={t:.4f}s) = {s:.4f}g")

# ============================================================================
# 2. FLOOR PROFILES (drift & displacement)
# ============================================================================
print("\nFloor profiles...")
env_merged = env_df.copy()
z_col = "z_cm"
z_levels = sorted(env_merged[z_col].round(1).unique())

x_cases = ["KYH1_X", "KYH2_X", "KYH3_X"]
floor_disp = {}; floor_drift = {}

for case in x_cases:
    cd = env_merged[env_merged["case"] == case]
    z_ux = cd.groupby(cd[z_col].round(1))["max_ux_cm"].max().sort_index()
    disps = [(z, z_ux.get(round(z,1), 0.0)) for z in z_levels]
    drifts = []
    for i in range(1, len(z_levels)):
        h_i = z_levels[i] - z_levels[i-1]
        d = (z_ux.get(round(z_levels[i],1), 0.0) - z_ux.get(round(z_levels[i-1],1), 0.0)) / h_i * 100
        drifts.append((i, d))
    floor_disp[case] = disps
    floor_drift[case] = drifts
    mx_d = max(d[1] for d in drifts); mx_f = max(drifts, key=lambda x:x[1])[0]
    print(f"  {case}: roof={disps[-1][1]:.4f}cm, drift_max={mx_d:.3f}% @floor {mx_f}")

# ============================================================================
# 3. RAYLEIGH DAMPING
# ============================================================================
print("\nRayleigh damping...")
omega1 = 2*math.pi/T[0]; omega2 = 3.5*omega1
A_mat = np.array([[1/(2*omega1), omega1/2], [1/(2*omega2), omega2/2]])
a0, a1 = np.linalg.solve(A_mat, [0.05, 0.05])
omega_min = math.sqrt(a0/a1); xi_min = a0/(2*omega_min) + a1*omega_min/2
print(f"  w1={omega1:.2f} w2={omega2:.2f} a0={a0:.4f} a1={a1:.7f}")
print(f"  xi_min={xi_min:.4f} at T={2*math.pi/omega_min:.4f}s")

rayleigh_T = [0.020, 0.030, 0.050, 0.070, 0.100, 0.135, 0.200, 0.300, 0.500]
rayleigh_curves = {}
for xi0 in [0.02, 0.05, 0.10]:
    a0i, a1i = np.linalg.solve(A_mat, [xi0, xi0])
    curve = [(t, round(a0i/(2*(2*math.pi/t)) + a1i*(2*math.pi/t)/2, 5)) for t in rayleigh_T]
    rayleigh_curves[f"xi0={xi0}"] = curve

# Parametric damping (scale from old)
ratio = 0.4513 / 0.449  # SAP/old umax at xi=5%
old_param = [(0.005,1.127),(0.010,0.813),(0.020,0.616),(0.030,0.517),(0.050,0.449),
             (0.070,0.424),(0.100,0.393),(0.150,0.352),(0.200,0.319)]
new_param = [(xi, round(u*ratio, 3)) for xi, u in old_param]
print(f"  Parametric: {new_param}")

# ============================================================================
# 4. SELECT 43 REPRESENTATIVE ELEMENTS & STRESS DATA
# ============================================================================
print("\n43 representative elements...")
ff_x = ff_df[ff_df["case"].isin(x_cases)].copy()

# Max sigma per frame across all X-dir TH cases
frame_max = ff_x.groupby("frame")["sigma_total_Ncm2"].max().sort_values(ascending=False)

# Select 43 elements: top 5 + 38 evenly spaced from remaining
n_total = len(frame_max)
top5 = frame_max.head(5).index.tolist()
remaining = frame_max.iloc[5:]
step = max(1, len(remaining) // 38)
sampled = remaining.iloc[::step].head(38).index.tolist()
sel_frames = top5 + sampled
sel_frames = sel_frames[:43]
print(f"  Selected {len(sel_frames)} frames")
print(f"  Sigma range: {frame_max[sel_frames].min():.1f} - {frame_max[sel_frames].max():.1f} N/cm2")

# Stress data for bar chart
stress_data = {}
for case in x_cases:
    case_ff = ff_x[ff_x["case"] == case].set_index("frame")
    sigmas = []
    for fr in sel_frames:
        sigmas.append(case_ff.loc[fr, "sigma_total_Ncm2"] if fr in case_ff.index else 0.0)
    stress_data[case] = sigmas

# Convert to kN/cm2 for bar chart (consistent with old report units)
stress_data_kNcm2 = {c: [s/1000 for s in ss] for c, ss in stress_data.items()}

for case in x_cases:
    mx = max(stress_data[case])
    print(f"  {case}: max={mx:.1f} N/cm2 = {mx/1000:.3f} kN/cm2")

# ============================================================================
# 5. FRAGILITY ANALYSIS (Baker MLE)
# ============================================================================
print("\nFragility analysis...")
pga_vals = [PGA["KYH1"], PGA["KYH2"], PGA["KYH3"]]

# System capacity PGA: min over elements, for each GM
sys_cap_pga = []
for i, case in enumerate(x_cases):
    max_sigma_gm = max(stress_data[case])
    if max_sigma_gm > 0:
        cap = pga_vals[i] * sigma_cap / max_sigma_gm
    else:
        cap = 999.0
    sys_cap_pga.append(cap)
    print(f"  {case}: sigma_max={max_sigma_gm:.1f}, cap_PGA={cap:.3f}g")

# Per-element capacity PGA (for theta_collapse chart)
elem_cap = []
for j, fr in enumerate(sel_frames):
    caps = []
    for i, case in enumerate(x_cases):
        s = stress_data[case][j]
        caps.append(pga_vals[i] * sigma_cap / s if s > 0 else 999.0)
    geo_mean = math.exp(np.mean(np.log([min(c, 999) for c in caps])))
    elem_cap.append((j+1, fr, min(geo_mean, 55.0)))

# Baker MLE: lognormal fit to system cap PGA
ln_caps = np.log(sys_cap_pga)
theta_collapse = math.exp(np.mean(ln_caps))
beta_r = max(np.std(ln_caps, ddof=0), 0.15)  # min beta_r = 0.15
beta_u = 0.55
beta_T = math.sqrt(beta_r**2 + beta_u**2)

# Damage states
ds_factors = {"DS-1": 0.25, "DS-2": 0.50, "DS-3": 0.75, "Collapse": 1.00}
theta_ds = {ds: theta_collapse * f for ds, f in ds_factors.items()}

print(f"\n  theta_collapse = {theta_collapse:.3f}g, beta_r={beta_r:.3f}, beta_T={beta_T:.3f}")
for ds, th in theta_ds.items():
    p = norm.cdf(math.log(0.335/th) / beta_T)
    print(f"  {ds}: theta={th:.3f}g, P(DD-2)={p:.2e}")

# TKO values
tko_dd2 = max(stress_data["KYH1_X"]) / sigma_cap
tko_kyh3 = max(stress_data["KYH3_X"]) / sigma_cap
print(f"\n  TKO_max(DD-2) = {tko_dd2:.3f}")
print(f"  TKO_max(KYH3) = {tko_kyh3:.3f}")

# Fragility curves
pga_range = [0.05,0.10,0.15,0.20,0.25,0.30,0.335,0.40,0.50,0.60,0.70,0.80,
             1.00,1.50,2.00,3.00,5.00,10.00]
frag_curves = {}
for ds, th in theta_ds.items():
    frag_curves[ds] = [(p, round(norm.cdf(math.log(p/th)/beta_T), 6)) for p in pga_range]

# CI bounds for collapse
n_data = 3
se = beta_T / math.sqrt(n_data)
th_lo = theta_collapse * math.exp(-1.645*se)
th_hi = theta_collapse * math.exp(+1.645*se)
ci_lo = [(p, round(norm.cdf(math.log(p/th_lo)/beta_T), 6)) for p in pga_range]
ci_hi = [(p, round(norm.cdf(math.log(p/th_hi)/beta_T), 6)) for p in pga_range]

# Element stats
thetas = [e[2] for e in elem_cap]
sorted_elem = sorted(elem_cap, key=lambda x: x[2])
critical_el = sorted_elem[0]
second_crit = sorted_elem[1]

# ============================================================================
# 6. ROOF ACCELERATIONS
# ============================================================================
omega_est = 3.0
roof_accel = {gm: round(pga*omega_est, 3) for gm, pga in PGA.items()}

# ============================================================================
# 7. LaTeX OUTPUT
# ============================================================================
print("\n" + "="*70)
print("LaTeX COORDINATES")
print("="*70)

# Drift profiles (a)
print("\n% --- (a) Drift profiles ---")
for case in x_cases:
    gm = case.split("_")[0]
    c = " ".join(f"({d:.3f},{f})" for f, d in floor_drift[case])
    print(f"% {gm}:\n\\addplot coordinates {{ {c} }};")

# Displacement (b)
print("\n% --- (b) Displacement envelopes ---")
for case in x_cases:
    gm = case.split("_")[0]
    c = " ".join(f"({floor_disp[case][i][1]:.3f},{i})" for i in range(1, len(floor_disp[case])))
    print(f"% {gm}:\n\\addplot coordinates {{ {c} }};")

# Roof accel (c)
print("\n% --- (c) Roof accel ---")
c = " ".join(f"({PGA[gm]},{roof_accel[gm]})" for gm in ["KYH1","KYH2","KYH3"])
print(f"\\addplot coordinates {{ {c} }};")

# Spectrum markers
print("\n% --- Spectrum markers ---")
for i in range(3):
    print(f"% T{i+1}={T[i]:.3f}s Sae={Sae(T[i]):.3f}g → ({T[i]:.3f},{Sae(T[i]):.3f})")

# Damping (a) parametric
print("\n% --- Damping (a) parametric ---")
c = " ".join(f"({xi},{u})" for xi, u in new_param)
print(f"\\addplot coordinates {{ {c} }};")

# Damping (b) Rayleigh
print("\n% --- Damping (b) Rayleigh ---")
for lab, curve in rayleigh_curves.items():
    c = " ".join(f"({t},{xi:.4f})" for t, xi in curve)
    print(f"% {lab}:\n\\addplot coordinates {{ {c} }};")

# Stress bar chart (in kN/cm2)
print("\n% --- Stress bar chart (kN/cm2) ---")
for case in reversed(x_cases):
    gm = case.split("_")[0]
    c = "\n    ".join(f"({j+1},{s:.2f})" for j, s in enumerate(stress_data_kNcm2[case]))
    print(f"% {gm}:\n\\addplot coordinates {{\n    {c}\n}};")

# Fragility curves
print("\n% --- Fragility curves ---")
for ds, curve in frag_curves.items():
    c = " ".join(f"({p},{v:.6f})" for p, v in curve)
    print(f"% {ds} (theta={theta_ds[ds]:.2f}g):\n\\addplot coordinates {{ {c} }};")
print("% CI lower:")
print(f"\\addplot coordinates {{ {' '.join(f'({p},{v:.6f})' for p,v in ci_lo)} }};")
print("% CI upper:")
print(f"\\addplot coordinates {{ {' '.join(f'({p},{v:.6f})' for p,v in ci_hi)} }};")

# Element theta chart
print("\n% --- Element theta_collapse ---")
c = "\n    ".join(f"({e[0]},{e[2]:.1f})" for e in elem_cap)
print(f"\\addplot coordinates {{\n    {c}\n}};")
print(f"% Critical: el.{critical_el[0]} (fr.{critical_el[1]}) theta={critical_el[2]:.1f}g")
print(f"% 2nd crit: el.{second_crit[0]} (fr.{second_crit[1]}) theta={second_crit[2]:.1f}g")

# 2nd critical fragility
th2 = second_crit[2]
c2 = " ".join(f"({p},{norm.cdf(math.log(p/th2)/beta_T):.6f})" for p in pga_range)
print(f"% 2nd critical fragility:\n\\addplot coordinates {{ {c2} }};")

# ============================================================================
# 8. SAVE JSON
# ============================================================================
out = {
    "modal": {f"T{i+1}": round(T[i], 4) for i in range(4)},
    "spectral": spectral,
    "model": {"n_joints": 1116, "n_frames": 3250, "H": 153.0, "E_model_Ncm2": E_MODEL},
    "capacity": {"f_b_Ncm2": f_b, "eta_j": eta_j, "sigma_cap_Ncm2": sigma_cap,
                  "sigma_cap_MPa": sigma_cap/100, "M_j_Ncm": round(M_j, 1)},
    "rayleigh": {"omega1": round(omega1,2), "omega2": round(omega2,2),
                  "a0": round(a0,4), "a1": round(a1,7), "xi_min": round(xi_min,4)},
    "parametric": new_param,
    "floor_drift": {c: [(f, round(d,3)) for f,d in dd] for c,dd in floor_drift.items()},
    "floor_disp": {c: [(z, round(u,4)) for z,u in dd] for c,dd in floor_disp.items()},
    "roof_accel": roof_accel,
    "fragility": {"theta_ds": {ds: round(t,3) for ds,t in theta_ds.items()},
                   "beta_T": round(beta_T, 3), "beta_r": round(beta_r, 3),
                   "theta_collapse": round(theta_collapse, 3),
                   "P_DD2": {ds: round(norm.cdf(math.log(0.335/t)/beta_T), 6) for ds,t in theta_ds.items()}},
    "tko": {"dd2": round(tko_dd2, 3), "kyh3": round(tko_kyh3, 3)},
    "critical_el": {"idx": critical_el[0], "frame": critical_el[1], "theta": round(critical_el[2],1)},
    "second_crit": {"idx": second_crit[0], "frame": second_crit[1], "theta": round(second_crit[2],1)},
    "elem_stats": {"median": round(float(np.median(thetas)),1), "mean": round(float(np.mean(thetas)),1),
                    "p5": round(float(np.percentile(thetas,5)),1),
                    "q1": round(float(np.percentile(thetas,25)),1),
                    "q3": round(float(np.percentile(thetas,75)),1),
                    "n_below10": int(sum(1 for t in thetas if t<10))},
    "sel_frames": sel_frames,
    "stress_kNcm2": {c: [round(s,3) for s in ss] for c,ss in stress_data_kNcm2.items()},
}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {OUT_JSON}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"T1={T[0]:.4f} T2={T[1]:.4f} T3={T[2]:.4f} T4={T[3]:.4f}")
print(f"Sae: {Sae(T[0]):.4f} {Sae(T[1]):.4f} {Sae(T[2]):.4f} {Sae(T[3]):.4f}")
print(f"Rayleigh: a0={a0:.4f} a1={a1:.7f} xi_min={xi_min:.4f}")
print(f"sigma_cap={sigma_cap} N/cm2 ({sigma_cap/100} MPa), M_j={M_j:.1f} N*cm")
print(f"TKO_max: DD-2={tko_dd2:.3f}, KYH3={tko_kyh3:.3f}")
print(f"theta_collapse={theta_collapse:.3f}g, beta_T={beta_T:.3f}")
for ds,th in theta_ds.items():
    print(f"  {ds}: theta={th:.3f}g, P(DD-2)={norm.cdf(math.log(0.335/th)/beta_T):.2e}")
print(f"Drift max: " + ", ".join(f"{c.split('_')[0]}={max(d[1] for d in dd):.3f}%"
    for c,dd in floor_drift.items() if "_X" in c))
