#!/usr/bin/env python3
"""
Advanced Lognormal Fragility Analysis — DASK 2026 V9 Twin Towers
================================================================
Per-element & per-joint MLE fragility curves via scipy
- Baker (2015) MLE method for lognormal CDF fitting
- FEMA P-58 multi-DS framework
- Joint (connection) capacity as governing mode
- Bootstrap confidence intervals
- System-level fragility via first-yield / weakest-link
"""

import numpy as np
from scipy.stats import norm, lognorm
from scipy.optimize import minimize_scalar, minimize
import os, sys

# =====================================================================
# 1. MATERIAL & SECTION PROPERTIES
# =====================================================================
# Balsa wood MOR (modulus of rupture) — real: 35 MPa = 3.5 kN/cm²
f_b_real = 3.5        # kN/cm² (unscaled balsa bending strength)
scale_factor = 240     # model scaling for stiffness
f_b = f_b_real * scale_factor  # 840 kN/cm² (scaled model)

# Connection efficiency factor (glue joint / birleşim verimi)
# Balsa PVA joints: η ≈ 0.30–0.40 (FEMA P-58, wood-frame fragility)
eta_joint = 0.35
f_joint = eta_joint * f_b  # 294 kN/cm² — governing capacity

# Section: 6mm × 6mm square
b = 0.6   # cm
h = 0.6   # cm
A  = b * h                    # 0.36 cm²
I  = b * h**3 / 12            # 0.0108 cm⁴
Wel = b * h**2 / 6            # 0.036 cm³

# Capacities
M_member = f_b * Wel           # 30.24 kN·cm (member MOR)
M_joint  = f_joint * Wel       # 10.584 kN·cm (joint — governing)
V_member = 0.6 * f_b * A * 0.5  # shear (conservative)
P_member = f_b * A             # 302.4 kN (axial)

print("=" * 70)
print("MATERIAL & SECTION PROPERTIES")
print("=" * 70)
print(f"  f_b (real balsa MOR)   = {f_b_real} kN/cm² (35 MPa)")
print(f"  Scale factor           = ×{scale_factor}")
print(f"  f_b (model)            = {f_b} kN/cm²")
print(f"  η_joint                = {eta_joint}")
print(f"  f_joint                = {f_joint} kN/cm²")
print(f"  Section                = {b*10:.0f}mm × {h*10:.0f}mm")
print(f"  A = {A} cm², Wel = {Wel} cm³, I = {I} cm⁴")
print(f"  M_member               = {M_member:.2f} kN·cm")
print(f"  M_joint (governing)    = {M_joint:.3f} kN·cm")

# =====================================================================
# 2. LOAD ELEMENT FORCES FROM ALL 3 GROUND MOTIONS
# =====================================================================
base = os.path.join(os.path.dirname(__file__), "results")
gm_info = {
    'KYH-1': {'file': 'th_KYH1/element_forces/sample_forces.txt', 'pga': 0.335},
    'KYH-2': {'file': 'th_KYH2/element_forces/sample_forces.txt', 'pga': 1.243},
    'KYH-3': {'file': 'th_KYH3/element_forces/sample_forces.txt', 'pga': 1.896},
}

# Storage: elem_data[elem_idx][gm_name] = dict of max forces
elem_data = {}
n_elem = None

for gm_name, info in gm_info.items():
    fp = os.path.join(base, info['file'])
    data = np.loadtxt(fp)
    ne = data.shape[1] // 12
    if n_elem is None:
        n_elem = ne
        for i in range(ne):
            elem_data[i] = {}

    for i in range(ne):
        ef = data[:, i*12:(i+1)*12]
        # Node I forces
        Fx_i = ef[:, 0]   # axial
        Vy_i = ef[:, 1]   # shear-y
        Vz_i = ef[:, 2]   # shear-z
        My_i = ef[:, 4]   # moment-y
        Mz_i = ef[:, 5]   # moment-z
        # Node J forces
        Fx_j = ef[:, 6]
        Vy_j = ef[:, 7]
        Vz_j = ef[:, 8]
        My_j = ef[:, 10]
        Mz_j = ef[:, 11]

        # Envelope maxima
        P_max = np.max(np.abs(Fx_i))  # axial (tension or compression)
        # Moment at both ends — take SRSS of biaxial
        M_i = np.sqrt(My_i**2 + Mz_i**2)
        M_j = np.sqrt(My_j**2 + Mz_j**2)
        M_max = max(np.max(M_i), np.max(M_j))
        # Shear — SRSS
        V_i = np.sqrt(Vy_i**2 + Vz_i**2)
        V_j = np.sqrt(Vy_j**2 + Vz_j**2)
        V_max = max(np.max(V_i), np.max(V_j))

        # DCR — member capacity
        DCR_member = P_max / P_member + M_max / M_member
        # DCR — joint capacity (governing)
        DCR_joint  = M_max / M_joint  # joints fail in bending, axial negligible

        # Stresses
        sigma_b = M_max / Wel       # bending stress
        tau     = 1.5 * V_max / A   # shear stress

        elem_data[i][gm_name] = {
            'P': P_max, 'M': M_max, 'V': V_max,
            'DCR_member': DCR_member, 'DCR_joint': DCR_joint,
            'sigma_b': sigma_b, 'tau': tau,
            'pga': info['pga'],
        }

print(f"\nLoaded {n_elem} elements × {len(gm_info)} ground motions")

# =====================================================================
# 3. PER-ELEMENT MLE LOGNORMAL FRAGILITY FITTING (Baker 2015)
# =====================================================================
#
# Baker (2015) "Efficient Analytical Fragility Function Fitting Using
# Dynamic Structural Analysis"
#
# For each element i, under GM j with PGA_j:
#   DCR_ij = k_i * PGA_j  (linear elastic)
#   k_i = DCR_ij / PGA_j
#
# For a given DS threshold (DCR_ds), PGA capacity:
#   PGA_cap_ij = DCR_ds / k_ij
#
# MLE fit of lognormal:
#   theta_i = exp( mean( ln(PGA_cap_ij) ) )
#   beta_r_i = std( ln(PGA_cap_ij) )
#
# Total uncertainty: beta_T = sqrt(beta_r² + beta_u²)
# where beta_u accounts for:
#   - model uncertainty (beta_m = 0.20)
#   - material variability (beta_mat = 0.15)
#   - connection variability (beta_conn = 0.20)
#   beta_u = sqrt(0.20² + 0.15² + 0.20²) = 0.32

beta_m   = 0.20   # model uncertainty
beta_mat = 0.15   # material variability
beta_conn = 0.20  # connection quality variability
beta_u = np.sqrt(beta_m**2 + beta_mat**2 + beta_conn**2)

print(f"\n{'='*70}")
print("PER-ELEMENT MLE FRAGILITY (Baker 2015)")
print(f"{'='*70}")
print(f"  beta_m (model)        = {beta_m}")
print(f"  beta_mat (material)   = {beta_mat}")
print(f"  beta_conn (connection) = {beta_conn}")
print(f"  beta_u (epistemic)    = {beta_u:.4f}")

# DS thresholds (DCR levels)
ds_levels = {
    'DS-1': 0.25,   # Hemen Kullanım sınırı
    'DS-2': 0.50,   # Can Güvenliği sınırı
    'DS-3': 0.75,   # Göçmenin Önlenmesi
    'Göçme': 1.00,  # Göçme
}

# Compute per-element k values and fragility parameters
gm_names = ['KYH-1', 'KYH-2', 'KYH-3']
elem_fragility = {}  # elem_idx -> {ds_name: {theta, beta_r, beta_T}}

for i in range(n_elem):
    # k_i for each GM (joint DCR)
    k_vals = []
    for gm in gm_names:
        d = elem_data[i][gm]
        k = d['DCR_joint'] / d['pga']
        k_vals.append(k)

    k_arr = np.array(k_vals)
    # ln(PGA_cap) = ln(DCR_ds) - ln(k)
    ln_k = np.log(k_arr)
    mu_ln_k = np.mean(ln_k)      # MLE estimate of mean
    beta_r_i = np.std(ln_k, ddof=0)  # MLE estimate of record-to-record

    # If beta_r is too small (< 0.05), floor it at 0.10
    # (ATC-58 recommendation for limited data)
    beta_r_i = max(beta_r_i, 0.10)

    beta_T_i = np.sqrt(beta_r_i**2 + beta_u**2)
    k_median_i = np.exp(mu_ln_k)

    ds_params = {}
    for ds_name, ds_thr in ds_levels.items():
        theta_ds = ds_thr / k_median_i
        ds_params[ds_name] = {
            'theta': theta_ds,
            'beta_r': beta_r_i,
            'beta_T': beta_T_i,
        }
    elem_fragility[i] = {
        'k_median': k_median_i,
        'beta_r': beta_r_i,
        'beta_T': beta_T_i,
        'ds_params': ds_params,
    }

# =====================================================================
# 4. SYSTEM-LEVEL FRAGILITY (Weakest-Link / Series System)
# =====================================================================
# P(system DS | PGA) = 1 - Π(1 - P(DS_i | PGA))
# For well-correlated elements, approximate as:
# P(system) ≈ max_i P(DS_i | PGA)  (upper bound by most critical)
#
# More refined: use the first element to reach DS threshold
# theta_system = min_i (theta_i)  — conservative
# beta_system = beta_T of that critical element

print(f"\n{'='*70}")
print("SYSTEM-LEVEL FRAGILITY (weakest-link)")
print(f"{'='*70}")

system_fragility = {}
for ds_name in ds_levels:
    # Find element with lowest theta (most vulnerable)
    thetas = [elem_fragility[i]['ds_params'][ds_name]['theta'] for i in range(n_elem)]
    crit_idx = np.argmin(thetas)
    theta_sys = thetas[crit_idx]
    beta_T_sys = elem_fragility[crit_idx]['beta_T']

    # Refined: use harmonic-like combination
    # Actually, for series system with lognormal components:
    # theta_sys ≈ min(theta_i), beta_sys ≈ beta_T (if all similar)
    # For a proper treatment, compute system fragility numerically
    # P_sys(pga) = 1 - prod(1 - Phi((ln(pga/theta_i))/beta_i))
    # Then fit a lognormal to that curve via MLE

    # Numerical system fragility
    pga_range = np.logspace(-1.5, 1.2, 500)
    p_sys = np.zeros_like(pga_range)
    for j, pga in enumerate(pga_range):
        surv = 1.0
        for i in range(n_elem):
            th_i = elem_fragility[i]['ds_params'][ds_name]['theta']
            bt_i = elem_fragility[i]['beta_T']
            p_i = norm.cdf(np.log(pga / th_i) / bt_i)
            surv *= (1.0 - p_i)
        p_sys[j] = 1.0 - surv

    # MLE fit of lognormal to the numerical system curve
    # Minimize sum of squared errors in probability space
    def neg_ll(params):
        ln_theta, beta = params
        if beta <= 0.01:
            return 1e12
        p_pred = norm.cdf((np.log(pga_range) - ln_theta) / beta)
        # Weighted least squares (more weight near 0.5)
        w = p_sys * (1 - p_sys) + 0.001
        return np.sum(w * (p_pred - p_sys)**2)

    from scipy.optimize import minimize
    res = minimize(neg_ll, x0=[np.log(theta_sys), beta_T_sys],
                   method='Nelder-Mead', options={'xatol': 1e-6, 'fatol': 1e-10})
    theta_fit = np.exp(res.x[0])
    beta_fit = abs(res.x[1])

    system_fragility[ds_name] = {
        'theta_min': theta_sys,
        'crit_elem': crit_idx + 1,
        'theta_fit': theta_fit,
        'beta_fit': beta_fit,
        'pga_range': pga_range,
        'p_sys': p_sys,
    }

    p_dd2 = norm.cdf(np.log(0.335 / theta_fit) / beta_fit)
    print(f"  {ds_name}:")
    print(f"    Critical element     = {crit_idx + 1}")
    print(f"    θ_min (weakest)      = {theta_sys:.3f} g")
    print(f"    θ_sys (MLE fit)      = {theta_fit:.3f} g")
    print(f"    β_sys (MLE fit)      = {beta_fit:.3f}")
    print(f"    P({ds_name}|DD-2)    = {p_dd2:.4e}")

# =====================================================================
# 5. KEY RESULTS
# =====================================================================
print(f"\n{'='*70}")
print("KEY RESULTS FOR LATEX")
print(f"{'='*70}")

# Per-element stats
print("\n--- Per-element θ_collapse distribution ---")
thetas_collapse = [elem_fragility[i]['ds_params']['Göçme']['theta'] for i in range(n_elem)]
print(f"  min  = {min(thetas_collapse):.3f} g  (elem {np.argmin(thetas_collapse)+1})")
print(f"  max  = {max(thetas_collapse):.3f} g  (elem {np.argmax(thetas_collapse)+1})")
print(f"  mean = {np.mean(thetas_collapse):.3f} g")
print(f"  med  = {np.median(thetas_collapse):.3f} g")
print(f"  CoV  = {np.std(thetas_collapse)/np.mean(thetas_collapse):.3f}")

betas_r = [elem_fragility[i]['beta_r'] for i in range(n_elem)]
betas_T = [elem_fragility[i]['beta_T'] for i in range(n_elem)]
print(f"\n--- Per-element β distribution ---")
print(f"  β_r: mean={np.mean(betas_r):.3f}, range=[{min(betas_r):.3f}, {max(betas_r):.3f}]")
print(f"  β_T: mean={np.mean(betas_T):.3f}, range=[{min(betas_T):.3f}, {max(betas_T):.3f}]")

# System-level summary
print(f"\n--- System fragility (MLE fit) ---")
for ds_name in ['DS-1', 'DS-2', 'DS-3', 'Göçme']:
    sf = system_fragility[ds_name]
    p_dd2 = norm.cdf(np.log(0.335 / sf['theta_fit']) / sf['beta_fit'])
    print(f"  {ds_name}: θ={sf['theta_fit']:.3f}g, β={sf['beta_fit']:.3f}, "
          f"P(DD-2)={p_dd2:.4e}, crit.elem={sf['crit_elem']}")

# Annual collapse
sf_c = system_fragility['Göçme']
p_c = norm.cdf(np.log(0.335 / sf_c['theta_fit']) / sf_c['beta_fit'])
lam_dd2 = 1.0 / 475
p_annual = lam_dd2 * p_c
p_50yr = 1 - (1 - p_annual)**50
print(f"\n  Annual collapse prob     = {p_annual:.2e}")
print(f"  50-year collapse prob    = {p_50yr:.2e}")
print(f"  ASCE 7-22 annual limit   = 1.0e-04")
print(f"  ASCE 7-22 50yr target    = 1%")

# =====================================================================
# 6. PGFPLOTS COORDINATES FOR LATEX
# =====================================================================
print(f"\n{'='*70}")
print("PGFPLOTS COORDINATES — System Fragility Curves")
print(f"{'='*70}")

pga_pts = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30, 0.335, 0.40,
           0.50, 0.60, 0.70, 0.80, 0.90, 1.0, 1.2, 1.5, 2.0, 2.5,
           3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0]

for ds_name in ['DS-1', 'DS-2', 'DS-3', 'Göçme']:
    sf = system_fragility[ds_name]
    th = sf['theta_fit']
    bt = sf['beta_fit']
    coords = []
    for p in pga_pts:
        prob = norm.cdf(np.log(p / th) / bt)
        coords.append(f"({p},{prob:.6f})")
    print(f"\n% {ds_name} (θ_sys={th:.3f}g, β_sys={bt:.3f}):")
    line = "    " + " ".join(coords)
    print(line)

# =====================================================================
# 7. PER-ELEMENT θ_collapse BAR DATA FOR PGFPLOTS
# =====================================================================
print(f"\n{'='*70}")
print("PER-ELEMENT θ_collapse — pgfplots coordinates")
print(f"{'='*70}")
coords = " ".join(f"({i+1},{thetas_collapse[i]:.3f})" for i in range(n_elem))
print(f"% theta_collapse per element:")
print(f"    {coords}")

# Per-element DCR at DD-2
dcrs_dd2 = [elem_data[i]['KYH-1']['DCR_joint'] for i in range(n_elem)]
coords_dcr = " ".join(f"({i+1},{dcrs_dd2[i]:.4f})" for i in range(n_elem))
print(f"\n% DCR_joint at DD-2 (KYH-1):")
print(f"    {coords_dcr}")

# Per-element P(collapse|DD-2)
pc_elem = []
for i in range(n_elem):
    th = elem_fragility[i]['ds_params']['Göçme']['theta']
    bt = elem_fragility[i]['beta_T']
    p = norm.cdf(np.log(0.335 / th) / bt)
    pc_elem.append(p)
coords_pc = " ".join(f"({i+1},{pc_elem[i]:.2e})" for i in range(n_elem))
print(f"\n% P(collapse|DD-2) per element:")
print(f"    {coords_pc}")

# =====================================================================
# 8. BOOTSTRAP CONFIDENCE INTERVAL (90%)
# =====================================================================
print(f"\n{'='*70}")
print("BOOTSTRAP 90% CONFIDENCE INTERVAL — System Collapse")
print(f"{'='*70}")

np.random.seed(42)
n_boot = 2000
theta_boot = []

# Bootstrap over the 3 GMs
for b_iter in range(n_boot):
    # Resample GM indices with replacement
    gm_idx = np.random.choice(3, size=3, replace=True)
    gm_sample = [gm_names[j] for j in gm_idx]
    pga_sample = [gm_info[gm]['pga'] for gm in gm_sample]

    # For system theta: find minimum theta across elements
    min_theta = 1e10
    for i in range(n_elem):
        k_vals_b = []
        for gm, pga in zip(gm_sample, pga_sample):
            k = elem_data[i][gm]['DCR_joint'] / pga
            k_vals_b.append(k)
        ln_k = np.log(k_vals_b)
        k_med = np.exp(np.mean(ln_k))
        theta_i = 1.0 / k_med  # collapse threshold
        if theta_i < min_theta:
            min_theta = theta_i
    theta_boot.append(min_theta)

theta_boot = np.array(theta_boot)
ci_5  = np.percentile(theta_boot, 5)
ci_50 = np.percentile(theta_boot, 50)
ci_95 = np.percentile(theta_boot, 95)
print(f"  θ_collapse 90% CI: [{ci_5:.3f}, {ci_50:.3f}, {ci_95:.3f}] g")
print(f"  Mean: {np.mean(theta_boot):.3f} g")

# P(collapse|DD-2) at CI bounds
for label, th in [('5th', ci_5), ('median', ci_50), ('95th', ci_95)]:
    p = norm.cdf(np.log(0.335 / th) / sf_c['beta_fit'])
    print(f"  P(collapse|DD-2) at {label} θ = {p:.2e}")

# =====================================================================
# 9. TOP-10 CRITICAL ELEMENTS TABLE
# =====================================================================
print(f"\n{'='*70}")
print("TOP-10 CRITICAL ELEMENTS (lowest θ_collapse)")
print(f"{'='*70}")
ranked = sorted(range(n_elem), key=lambda i: thetas_collapse[i])
print(f"  {'Sıra':<6} {'Elem':<6} {'θ_göçme(g)':<12} {'β_r':<8} {'β_T':<8} "
      f"{'DCR(DD2)':<10} {'σ_b(DD2)':<12} {'P(göçme|DD2)':<14}")
for rank, idx in enumerate(ranked[:10]):
    d = elem_data[idx]['KYH-1']
    ef = elem_fragility[idx]
    p_c_i = norm.cdf(np.log(0.335 / ef['ds_params']['Göçme']['theta']) / ef['beta_T'])
    print(f"  {rank+1:<6} {idx+1:<6} {thetas_collapse[idx]:<12.3f} "
          f"{ef['beta_r']:<8.3f} {ef['beta_T']:<8.3f} "
          f"{d['DCR_joint']:<10.4f} {d['sigma_b']:<12.1f} {p_c_i:<14.2e}")

print("\n=== DONE ===")
