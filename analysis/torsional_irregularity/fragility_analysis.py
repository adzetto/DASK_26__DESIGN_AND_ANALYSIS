#!/usr/bin/env python3
"""
Advanced Fragility Analysis for DASK 2026 V9 Twin Towers
Lognormal MLE fragility curves per FEMA P-58 / HAZUS methodology
"""
import numpy as np
from scipy.stats import norm
import os

# Section & material properties
A = 0.36; Wel = 0.036; fy = 9600.0
Py = fy * A; My = fy * Wel

gms = {
    'KYH1': ('analysis/torsional_irregularity/results/th_KYH1/element_forces/sample_forces.txt', 0.335),
    'KYH2': ('analysis/torsional_irregularity/results/th_KYH2/element_forces/sample_forces.txt', 1.243),
    'KYH3': ('analysis/torsional_irregularity/results/th_KYH3/element_forces/sample_forces.txt', 1.896),
}

all_dcr = {}; all_sb = {}; all_tau = {}; all_M = {}; all_V = {}
pgas = []

for gm, (fp, pga) in gms.items():
    data = np.loadtxt(fp)
    ne = data.shape[1] // 12
    dcr_l = []; sb_l = []; tau_l = []; m_l = []; v_l = []
    for i in range(ne):
        ef = data[:, i*12:(i+1)*12]
        P = np.max(np.abs((ef[:,0] + ef[:,6]) / 2))
        My_ = np.max(np.maximum(np.abs(ef[:,4]), np.abs(ef[:,10])))
        Mz_ = np.max(np.maximum(np.abs(ef[:,5]), np.abs(ef[:,11])))
        M = np.sqrt(My_**2 + Mz_**2)
        Vy = np.max(np.abs(ef[:,1])); Vz = np.max(np.abs(ef[:,2]))
        V = np.sqrt(Vy**2 + Vz**2)
        dcr_l.append(P/Py + M/My)
        sb_l.append(M/Wel)
        tau_l.append(1.5*V/A)
        m_l.append(M); v_l.append(V)
    all_dcr[gm] = np.array(dcr_l); all_sb[gm] = np.array(sb_l)
    all_tau[gm] = np.array(tau_l); all_M[gm] = np.array(m_l); all_V[gm] = np.array(v_l)
    pgas.append(pga)

pgas = np.array(pgas)

# =============================================
# FRAGILITY - Lognormal CDF
# =============================================
# DCR scales linearly with PGA (elastic model)
# k_i = DCR_max_i / PGA_i for each GM
k_vals = []
for gm, pga in zip(['KYH1','KYH2','KYH3'], pgas):
    k = np.max(all_dcr[gm]) / pga
    k_vals.append(k)

k_mean = np.mean(k_vals)
k_std = np.std(k_vals)

print(f"Linear scaling k = DCR_max/PGA: {[f'{k:.5f}' for k in k_vals]}")
print(f"k_mean = {k_mean:.5f}, CoV = {k_std/k_mean:.4f}")

# Lognormal parameters
# PGA_ds = ds_threshold / k for each record
# theta = exp(mean(ln(PGA_ds))), beta_r = std(ln(PGA_ds))
ln_pga_c = np.log([1.0/k for k in k_vals])
beta_r = np.std(ln_pga_c, ddof=0)
beta_u = 0.30  # epistemic uncertainty (FEMA P-58 typical)
beta_total = np.sqrt(beta_r**2 + beta_u**2)

print(f"\nbeta_r (kayit-kayit) = {beta_r:.4f}")
print(f"beta_u (epistemik) = {beta_u:.2f}")
print(f"beta_total = {beta_total:.4f}")

# DS thresholds
ds_thresholds = {'DS-1': 0.25, 'DS-2': 0.50, 'DS-3': 0.75, 'Gocme': 1.00}

print("\n=== KIRILGANLIK PARAMETRELERI ===")
for ds_name, ds_thresh in ds_thresholds.items():
    theta_ds = ds_thresh / k_mean
    print(f"{ds_name}: theta = {theta_ds:.2f} g")
    # Probability at design earthquake
    p_design = norm.cdf((np.log(0.335) - np.log(theta_ds)) / beta_total)
    p_dd1 = norm.cdf((np.log(0.500) - np.log(theta_ds)) / beta_total)
    print(f"  P({ds_name}|PGA=0.335g) = {p_design:.2e}")
    print(f"  P({ds_name}|PGA=0.500g) = {p_dd1:.2e}")

# =============================================
# PGFPLOTS COORDINATES for fragility curves
# =============================================
print("\n=== PGFPLOTS COORDINATES (fragility curves) ===")
pga_plot = list(np.arange(0.1, 5.1, 0.1)) + list(np.arange(5.5, 25.5, 0.5))
for ds_name, ds_thresh in ds_thresholds.items():
    theta_ds = ds_thresh / k_mean
    coords = []
    for p in pga_plot:
        prob = norm.cdf((np.log(p) - np.log(theta_ds)) / beta_total)
        coords.append(f"({p:.1f},{prob:.4f})")
    print(f"\n% {ds_name} (theta={theta_ds:.1f}g):")
    # Print in rows of 8
    for j in range(0, len(coords), 8):
        print("    " + " ".join(coords[j:j+8]))

# =============================================
# PER-ELEMENT sigma_b and tau for dual-axis plot
# =============================================
print("\n=== ELEMAN BAZLI sigma_b (KYH-1) ===")
sb1 = all_sb['KYH1']
tau1 = all_tau['KYH1']
print("% sigma_b:")
coords_sb = " ".join([f"({i+1},{s:.1f})" for i, s in enumerate(sb1)])
print(f"    {coords_sb}")
print("% tau:")
coords_tau = " ".join([f"({i+1},{t:.2f})" for i, t in enumerate(tau1)])
print(f"    {coords_tau}")

# Stats for text
print(f"\n=== ISTATISTIKLER ===")
for gm in ['KYH1','KYH2','KYH3']:
    dcr = all_dcr[gm]
    sb = all_sb[gm]
    tau = all_tau[gm]
    print(f"{gm}:")
    print(f"  DCR: mean={np.mean(dcr):.4f}, std={np.std(dcr):.4f}, max={np.max(dcr):.4f}")
    print(f"  sigma_b: mean={np.mean(sb):.1f}, std={np.std(sb):.1f}, max={np.max(sb):.1f}")
    print(f"  tau: mean={np.mean(tau):.2f}, std={np.std(tau):.2f}, max={np.max(tau):.2f}")
    print(f"  M: mean={np.mean(all_M[gm]):.3f}, max={np.max(all_M[gm]):.3f}")
    print(f"  V: mean={np.mean(all_V[gm]):.4f}, max={np.max(all_V[gm]):.4f}")

# Annual collapse probability (TBDY 2018 hazard curve integration approx)
# DD-2: 475yr return -> lambda = 1/475 = 0.002105
# Approximate: P_annual_collapse ~ lambda_DD2 * P(collapse|DD-2)
theta_c = 1.0 / k_mean
p_collapse_dd2 = norm.cdf((np.log(0.335) - np.log(theta_c)) / beta_total)
lambda_dd2 = 1.0/475
p_annual = lambda_dd2 * p_collapse_dd2
print(f"\n=== YILLIK GOCME OLASILIGI ===")
print(f"theta_collapse = {theta_c:.1f} g")
print(f"P(collapse|DD-2) = {p_collapse_dd2:.2e}")
print(f"lambda_DD2 = {lambda_dd2:.6f}")
print(f"P_annual_collapse approx = {p_annual:.2e}")
print(f"ASCE 7-22 limit (Risk Cat II) = 1e-04")
print(f"Ratio: {p_annual/1e-4:.2e}")

# 50-year collapse probability
p_50yr = 1 - (1 - p_annual)**50
print(f"P_50yr_collapse = {p_50yr:.2e}")
print(f"ASCE 7-22 target = 1%")
