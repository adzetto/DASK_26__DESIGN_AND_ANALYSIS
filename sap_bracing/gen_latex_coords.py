"""Generate all LaTeX pgfplots coordinate strings from report_data.json."""
import json, math
from scipy.stats import norm

with open(r"c:\Users\lenovo\Desktop\DASK_NEW\results\sap_bracing\report_data.json") as f:
    d = json.load(f)

print("="*80)
print("DRIFT COORDINATES (x=drift%, y=floor)")
print("="*80)
for case in ["KYH1_X", "KYH2_X", "KYH3_X"]:
    gm = case.split("_")[0]
    coords = " ".join(f"({dr:.3f},{fl})" for fl, dr in d["floor_drift"][case])
    print(f"% {gm}:")
    print(f"    {coords}")
    mx = max(d["floor_drift"][case], key=lambda x: x[1])
    print(f"  max={mx[1]:.3f}% at floor {mx[0]}")

print("\n" + "="*80)
print("DISPLACEMENT COORDINATES (x=disp_cm, y=floor)")
print("="*80)
for case in ["KYH1_X", "KYH2_X", "KYH3_X"]:
    gm = case.split("_")[0]
    # Skip ground (index 0), floors 1-25
    pts = d["floor_disp"][case][1:]  # skip (0,0)
    coords = " ".join(f"({u:.3f},{i+1})" for i, (z, u) in enumerate(pts))
    print(f"% {gm}:")
    print(f"    {coords}")
    print(f"  roof={pts[-1][1]:.4f} cm")

print("\n" + "="*80)
print("ROOF ACCELERATION COORDINATES")
print("="*80)
PGA = {"KYH1": 0.335, "KYH2": 1.243, "KYH3": 1.896}
ra = d["roof_accel"]
coords = " ".join(f"({PGA[gm]},{ra[gm]})" for gm in ["KYH1","KYH2","KYH3"])
print(f"    {coords}")
for gm in ["KYH1","KYH2","KYH3"]:
    omega = ra[gm] / PGA[gm]
    print(f"  {gm}: Omega={omega:.2f}")

print("\n" + "="*80)
print("STRESS BAR COORDINATES (MPa)")
print("="*80)
for case in ["KYH1_X", "KYH2_X", "KYH3_X"]:
    gm = case.split("_")[0]
    sigmas_mpa = [s/100.0 for s in d["stress_bar_Ncm2"][case]]
    coords = "\n    ".join(f"({j+1},{s:.2f})" for j, s in enumerate(sigmas_mpa))
    print(f"% {gm}:")
    print(f"    {coords}")
    print(f"  max={max(sigmas_mpa):.2f} MPa")

print("\n" + "="*80)
print("FRAGILITY COORDINATES")
print("="*80)
theta_ds = d["fragility"]["theta_ds"]
beta_T = d["fragility"]["beta_T"]
pga_range = [0.05,0.10,0.15,0.20,0.25,0.30,0.335,0.40,0.50,0.60,0.70,0.80,
             1.00,1.50,2.00,3.00,5.00,10.00]

for ds, th in theta_ds.items():
    coords = " ".join(f"({p},{norm.cdf(math.log(p/th)/beta_T):.6f})" for p in pga_range)
    pdd2 = norm.cdf(math.log(0.335/th)/beta_T)
    print(f"% {ds} (theta={th:.3f}g, P_DD2={pdd2:.4f}):")
    print(f"    {coords}")

# CI bounds for collapse
n_data = 3
se = beta_T / math.sqrt(n_data)
th_col = theta_ds["Collapse"]
th_lo = th_col * math.exp(-1.645*se)
th_hi = th_col * math.exp(+1.645*se)
print(f"\n% CI lower (theta_lo={th_lo:.3f}):")
coords = " ".join(f"({p},{norm.cdf(math.log(p/th_lo)/beta_T):.6f})" for p in pga_range)
print(f"    {coords}")
print(f"% CI upper (theta_hi={th_hi:.3f}):")
coords = " ".join(f"({p},{norm.cdf(math.log(p/th_hi)/beta_T):.6f})" for p in pga_range)
print(f"    {coords}")

# 2nd critical element fragility
sec = d["fragility"].get("second_critical", d.get("second_crit", {}))
th2 = sec.get("theta", 1.0)
coords = " ".join(f"({p},{norm.cdf(math.log(p/th2)/beta_T):.6f})" for p in pga_range)
print(f"\n% 2nd critical (theta={th2}g):")
print(f"    {coords}")

print("\n" + "="*80)
print("ELEMENT THETA COORDINATES")
print("="*80)
# Compute element theta from stress data & capacity
sigma_cap = d["capacity"]["sigma_cap_Ncm2"]  # 700 N/cm2
sel_frames = d["top43_frames"]
# theta_i = PGA * sigma_cap / sigma_i for geometric mean across 3 GMs
elem_thetas = []
for j in range(len(sel_frames)):
    caps = []
    for case, pga in zip(["KYH1_X","KYH2_X","KYH3_X"], [0.335,1.243,1.896]):
        s = d["stress_bar_Ncm2"][case][j]
        if s > 0:
            caps.append(pga * sigma_cap / s)
        else:
            caps.append(999.0)
    import numpy as np
    geo_mean = math.exp(np.mean(np.log([min(c, 999) for c in caps])))
    elem_thetas.append(min(geo_mean, 55.0))

coords = "\n    ".join(f"({j+1},{t:.1f})" for j, t in enumerate(elem_thetas))
print(f"    {coords}")
print(f"  median={float(np.median(elem_thetas)):.1f}, mean={float(np.mean(elem_thetas)):.1f}")
print(f"  min={min(elem_thetas):.1f}, p5={float(np.percentile(elem_thetas,5)):.1f}")
print(f"  q1={float(np.percentile(elem_thetas,25)):.1f}, q3={float(np.percentile(elem_thetas,75)):.1f}")
n_below10 = sum(1 for t in elem_thetas if t < 10)
print(f"  n_below10={n_below10}")

# Find critical elements
sorted_idx = sorted(range(len(elem_thetas)), key=lambda i: elem_thetas[i])
crit1 = sorted_idx[0]
crit2 = sorted_idx[1]
print(f"  Critical: el.{crit1+1} (frame {sel_frames[crit1]}) theta={elem_thetas[crit1]:.1f}g")
print(f"  2nd crit: el.{crit2+1} (frame {sel_frames[crit2]}) theta={elem_thetas[crit2]:.1f}g")

print("\n" + "="*80)
print("PARAMETRIC DAMPING COORDINATES")
print("="*80)
pd = d["parametric_damping"]
coords = " ".join(f"({xi},{u})" for xi, u in pd)
print(f"    {coords}")

print("\n" + "="*80)
print("RAYLEIGH CURVES (for 3 xi_0 values)")
print("="*80)
ray = d["rayleigh"]
omega1 = ray["omega1"]
omega2 = ray["omega2"]
A_mat = [[1/(2*omega1), omega1/2], [1/(2*omega2), omega2/2]]
A = np.array(A_mat)
rayleigh_T = [0.020, 0.030, 0.050, 0.070, 0.100, 0.135, 0.200, 0.300, 0.500]
for xi0 in [0.02, 0.05, 0.10]:
    a0i, a1i = np.linalg.solve(A, [xi0, xi0])
    curve = []
    for t in rayleigh_T:
        w = 2*math.pi/t
        xi_eff = a0i/(2*w) + a1i*w/2
        curve.append((t, xi_eff))
    coords = " ".join(f"({t},{xi:.4f})" for t, xi in curve)
    print(f"% xi0={xi0}:")
    print(f"    {coords}")

print("\n" + "="*80)
print("SUMMARY VALUES FOR TEXT")
print("="*80)
print(f"T1={d['modal']['T1']:.4f}s, T2={d['modal']['T2']:.4f}s, T3={d['modal']['T3']:.4f}s, T4={d['modal']['T4']:.4f}s")
print(f"Sae(T1)={d['spectral']['T1']['Sae']:.3f}g, Sae(T2)={d['spectral']['T2']['Sae']:.3f}g, Sae(T3)={d['spectral']['T3']['Sae']:.3f}g, Sae(T4)={d['spectral']['T4']['Sae']:.3f}g")
print(f"Joints={d['model']['n_joints']}, Frames={d['model']['n_frames']}")
print(f"omega1={ray['omega1']:.2f}, omega2={ray['omega2']:.2f}, a0={ray['a0']:.4f}, a1={ray['a1']:.7f}")
print(f"sigma_cap={sigma_cap:.0f} N/cm2 = {sigma_cap/100:.1f} MPa")
print(f"TKO_DD2={d['tko']['max_dd2']:.3f}, TKO_KYH3={d['tko']['max_kyh3']:.3f}")
print(f"theta_collapse={theta_ds['Collapse']:.3f}g, beta_T={beta_T:.3f}")
for ds, th in theta_ds.items():
    pdd2 = norm.cdf(math.log(0.335/th)/beta_T)
    print(f"  {ds}: theta={th:.3f}g, P(DD-2)={pdd2:.4e}")

# Max drift per case
for case in ["KYH1_X","KYH2_X","KYH3_X"]:
    mx = max(d["floor_drift"][case], key=lambda x: x[1])
    print(f"Drift max {case}: {mx[1]:.3f}% at floor {mx[0]}")

# Roof disp
for case in ["KYH1_X","KYH2_X","KYH3_X"]:
    print(f"Roof disp {case}: {d['floor_disp'][case][-1][1]:.4f} cm")

# Omega
for gm in ["KYH1","KYH2","KYH3"]:
    print(f"Omega {gm}: {ra[gm]/PGA[gm]:.2f}")
