"""
Extract per-floor interstory drift ratios and peak displacements from
OpenSees time history results for KYH1, KYH2, KYH3 ground motions.

Output: floor_summary.csv with columns for each ground motion.

DASK 2026 Twin Towers - V9 Model (1:50 scale)
- 25 floors per tower, floor height = 6.0 cm (model scale, = 300cm/50)
- 32 nodes per floor, each with 3 DOF (Ux, Uy, Rz)
- Drift files: OpenSees Drift recorder output = interstory drift RATIO
  (already divided by perpendicular distance = 6.0 cm node Z-spacing)
- Envelope files: 3 lines (min, max, abs_max), 96 values per line
"""

import os
import numpy as np

# ── Configuration ──────────────────────────────────────────────────────
BASE = r"c:\Users\lenovo\Desktop\DASK_NEW\analysis\torsional_irregularity\results"
OUT_CSV = os.path.join(BASE, "floor_summary.csv")

GROUND_MOTIONS = ["KYH1", "KYH2", "KYH3"]
N_FLOORS = 25
N_NODES_PER_FLOOR = 32
N_DOF = 3  # Ux, Uy, Rz
FLOOR_HEIGHT = 6.0  # cm (model scale, = 300cm prototype / 50 scale)
SCALE_FACTOR = 50  # model scale 1:50
G_CM_S2 = 981.0  # g in cm/s^2

# ── Helper functions ───────────────────────────────────────────────────

def read_single_column(filepath):
    """Read a single-column text file into a numpy array."""
    vals = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                vals.append(float(line))
    return np.array(vals)


def read_multicolumn(filepath):
    """Read a space-separated multi-column file into a 2D numpy array."""
    rows = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(x) for x in line.split()])
    return np.array(rows)


def read_envelope_line(filepath, line_idx):
    """Read a specific line (0-indexed) from an envelope file.
    Returns array of values."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    # Filter out empty lines
    lines = [l.strip() for l in lines if l.strip()]
    if line_idx >= len(lines):
        return None
    return np.array([float(x) for x in lines[line_idx].split()])


# ── Extract drift ratios ──────────────────────────────────────────────

print("=" * 70)
print("DASK 2026 - Floor Data Extraction")
print("=" * 70)

# Storage: drift_ratios[gm][floor] = max abs drift ratio
drift_ratios = {}
peak_displacements = {}
peak_roof_accel = {}

for gm in GROUND_MOTIONS:
    gm_dir = os.path.join(BASE, f"th_{gm}")

    if not os.path.isdir(gm_dir):
        print(f"\nWARNING: Directory not found for {gm}: {gm_dir}")
        continue

    print(f"\n--- Processing {gm} ---")

    # ── 1) Interstory drift ratios (Tower 1) ──────────────────────────
    dr = {}
    drift_dir = os.path.join(gm_dir, "drift")
    for floor in range(1, N_FLOORS + 1):
        fpath = os.path.join(drift_dir, f"T1_drift_floor{floor}.txt")
        if not os.path.isfile(fpath):
            print(f"  WARNING: Missing {fpath}")
            dr[floor] = np.nan
            continue
        data = read_single_column(fpath)
        # Drift files already contain drift RATIOS from OpenSees Drift recorder
        # (displacement difference / perpendicular distance between nodes)
        dr[floor] = np.max(np.abs(data))

    drift_ratios[gm] = dr
    print(f"  Drift ratios: Floor 1 = {dr.get(1, 'N/A'):.6f}, "
          f"max at floor {max(dr, key=dr.get)} = {max(dr.values()):.6f}")

    # ── 2) Peak displacement from envelope (Tower 1) ─────────────────
    pd_dict = {}
    env_dir = os.path.join(gm_dir, "envelope")
    for floor in range(1, N_FLOORS + 1):
        fpath = os.path.join(env_dir, f"T1_floor{floor}_env.txt")
        if not os.path.isfile(fpath):
            print(f"  WARNING: Missing {fpath}")
            pd_dict[floor] = np.nan
            continue
        # Line 3 (index 2) = abs_max
        vals = read_envelope_line(fpath, 2)
        if vals is None:
            print(f"  WARNING: Could not read abs_max line from {fpath}")
            pd_dict[floor] = np.nan
            continue
        # Ux values are at positions 0, 3, 6, 9, ..., 93 (every 3rd starting at 0)
        ux_indices = list(range(0, N_NODES_PER_FLOOR * N_DOF, N_DOF))
        ux_vals = vals[ux_indices]
        pd_dict[floor] = np.max(ux_vals)

    peak_displacements[gm] = pd_dict
    print(f"  Peak disp: Roof = {pd_dict.get(25, 'N/A'):.6f} cm, "
          f"max at floor {max(pd_dict, key=pd_dict.get)} = {max(pd_dict.values()):.6f} cm")

    # ── 3) Roof acceleration (Tower 1) ────────────────────────────────
    accel_file = os.path.join(gm_dir, "node_accel", "roof_T1_accel.txt")
    if os.path.isfile(accel_file):
        accel_data = read_multicolumn(accel_file)
        # Column 0 = Ux acceleration (cm/s^2 in OpenSees units)
        peak_ax = np.max(np.abs(accel_data[:, 0]))
        peak_roof_accel[gm] = peak_ax
        print(f"  Peak roof accel Ux: {peak_ax:.4f} cm/s^2 = {peak_ax / G_CM_S2:.4f} g")
    else:
        print(f"  WARNING: Missing roof accel file: {accel_file}")
        peak_roof_accel[gm] = np.nan

# ── List available acceleration files ──────────────────────────────────
print("\n--- Available acceleration files ---")
for gm in GROUND_MOTIONS:
    accel_dir = os.path.join(BASE, f"th_{gm}", "node_accel")
    if os.path.isdir(accel_dir):
        files = os.listdir(accel_dir)
        print(f"  {gm}: {files}")
    else:
        print(f"  {gm}: directory not found")

# ── Write CSV ──────────────────────────────────────────────────────────

print(f"\n--- Writing CSV to {OUT_CSV} ---")

with open(OUT_CSV, 'w') as f:
    # Header
    header_parts = ["floor", "height_cm"]
    for gm in GROUND_MOTIONS:
        header_parts.extend([
            f"driftRatio_{gm}",
            f"peakDisp_cm_{gm}",
        ])
    f.write(",".join(header_parts) + "\n")

    for floor in range(1, N_FLOORS + 1):
        height = floor * FLOOR_HEIGHT
        parts = [str(floor), f"{height:.3f}"]
        for gm in GROUND_MOTIONS:
            dr_val = drift_ratios.get(gm, {}).get(floor, np.nan)
            pd_val = peak_displacements.get(gm, {}).get(floor, np.nan)
            parts.append(f"{dr_val:.8f}" if not np.isnan(dr_val) else "NaN")
            parts.append(f"{pd_val:.8f}" if not np.isnan(pd_val) else "NaN")
        f.write(",".join(parts) + "\n")

    # Add a summary section with roof accelerations
    f.write("\n")
    f.write("# Roof Peak Acceleration (Tower 1)\n")
    f.write("# ground_motion,peak_accel_cm_s2,peak_accel_g\n")
    for gm in GROUND_MOTIONS:
        pa = peak_roof_accel.get(gm, np.nan)
        if not np.isnan(pa):
            f.write(f"# {gm},{pa:.6f},{pa / G_CM_S2:.6f}\n")
        else:
            f.write(f"# {gm},NaN,NaN\n")

print("CSV written successfully.")

# ── Print summary table ───────────────────────────────────────────────

print("\n" + "=" * 70)
print("SUMMARY TABLE - Tower 1 Interstory Drift Ratios")
print("=" * 70)
print(f"{'Floor':>5} {'Height':>8}", end="")
for gm in GROUND_MOTIONS:
    print(f" {gm:>12}", end="")
print()
print("-" * (14 + 13 * len(GROUND_MOTIONS)))

for floor in range(1, N_FLOORS + 1):
    height = floor * FLOOR_HEIGHT
    print(f"{floor:>5} {height:>7.3f}cm", end="")
    for gm in GROUND_MOTIONS:
        dr_val = drift_ratios.get(gm, {}).get(floor, np.nan)
        print(f" {dr_val:>12.6f}", end="")
    print()

# Max per ground motion
print("-" * (14 + 13 * len(GROUND_MOTIONS)))
print(f"{'MAX':>5} {'':>8}", end="")
for gm in GROUND_MOTIONS:
    vals = drift_ratios.get(gm, {})
    if vals:
        max_val = max(vals.values())
        max_floor = max(vals, key=vals.get)
        print(f" {max_val:>12.6f}", end="")
    else:
        print(f" {'N/A':>12}", end="")
print()
print(f"{'@flr':>5} {'':>8}", end="")
for gm in GROUND_MOTIONS:
    vals = drift_ratios.get(gm, {})
    if vals:
        max_floor = max(vals, key=vals.get)
        print(f" {max_floor:>12}", end="")
    else:
        print(f" {'N/A':>12}", end="")
print()

print("\n" + "=" * 70)
print("SUMMARY TABLE - Tower 1 Peak Floor Displacement (cm)")
print("=" * 70)
print(f"{'Floor':>5} {'Height':>8}", end="")
for gm in GROUND_MOTIONS:
    print(f" {gm:>12}", end="")
print()
print("-" * (14 + 13 * len(GROUND_MOTIONS)))

for floor in range(1, N_FLOORS + 1):
    height = floor * FLOOR_HEIGHT
    print(f"{floor:>5} {height:>7.3f}cm", end="")
    for gm in GROUND_MOTIONS:
        pd_val = peak_displacements.get(gm, {}).get(floor, np.nan)
        print(f" {pd_val:>12.6f}", end="")
    print()

print("\n" + "=" * 70)
print("ROOF PEAK ACCELERATION (Tower 1)")
print("=" * 70)
for gm in GROUND_MOTIONS:
    pa = peak_roof_accel.get(gm, np.nan)
    print(f"  {gm}: {pa:.4f} cm/s^2 = {pa / G_CM_S2:.4f} g")

# ── Also write a pgfplots-friendly dat file ────────────────────────────
# Separate .dat files for drift ratios and displacements (tab-separated)

dat_drift = os.path.join(BASE, "floor_drift_ratios.dat")
dat_disp = os.path.join(BASE, "floor_peak_disp.dat")

print(f"\n--- Writing pgfplots-friendly files ---")

with open(dat_drift, 'w') as f:
    f.write("floor\theight")
    for gm in GROUND_MOTIONS:
        f.write(f"\t{gm}")
    f.write("\n")
    for floor in range(1, N_FLOORS + 1):
        height = floor * FLOOR_HEIGHT
        f.write(f"{floor}\t{height:.3f}")
        for gm in GROUND_MOTIONS:
            dr_val = drift_ratios.get(gm, {}).get(floor, np.nan)
            f.write(f"\t{dr_val:.8f}")
        f.write("\n")

print(f"  Drift ratios: {dat_drift}")

with open(dat_disp, 'w') as f:
    f.write("floor\theight")
    for gm in GROUND_MOTIONS:
        f.write(f"\t{gm}")
    f.write("\n")
    for floor in range(1, N_FLOORS + 1):
        height = floor * FLOOR_HEIGHT
        f.write(f"{floor}\t{height:.3f}")
        for gm in GROUND_MOTIONS:
            pd_val = peak_displacements.get(gm, {}).get(floor, np.nan)
            f.write(f"\t{pd_val:.8f}")
        f.write("\n")

print(f"  Peak displacements: {dat_disp}")

print("\nDone.")
