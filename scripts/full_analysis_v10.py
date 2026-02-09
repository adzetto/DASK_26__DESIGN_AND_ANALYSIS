"""
DASK 2026 - V10 FULL ANALYSIS SUITE
====================================
1) Modal analysis (eigenvalue)
2) KYH-1/2/3 time-history analysis (ZTAH) in X and Y
3) BOL090 time-history analysis (ZTAH) in X and Y
4) Pushover analysis in X and Y

Units throughout: m, kN, tonne, s
Stress output: MPa
Displacement output: cm

Outputs saved to: results/ folder
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
import json
import time as timer
from collections import defaultdict
import openseespy.opensees as ops

# ============================================================
# PATHS
# ============================================================
ROOT = Path(__file__).parent.parent
DATA = ROOT / 'data'
GM_DASK = ROOT / 'ground_motion_dask'
GM_BOL = ROOT / 'ground_motion'
RESULTS = ROOT / 'results'
RESULTS.mkdir(exist_ok=True)

# ============================================================
# 0) HELPER FUNCTIONS
# ============================================================

def parse_dask_gm(filepath):
    """Parse DASK competition ground-motion text file (tab-separated, g units)."""
    t_list, a_list = [], []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('Time') or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    t_list.append(float(parts[0]))
                    a_list.append(float(parts[1]))
                except ValueError:
                    continue
    t = np.array(t_list)
    a = np.array(a_list)
    dt = t[1] - t[0] if len(t) > 1 else 0.001
    return t, a, dt

def parse_at2(filepath):
    """Parse PEER AT2 format."""
    import re
    with open(filepath, 'r') as f:
        lines = f.readlines()
    header = lines[3]
    npts = int(re.search(r'NPTS\s*=\s*(\d+)', header).group(1))
    dt = float(re.search(r'DT\s*=\s*([.\d]+)', header).group(1))
    acc = []
    for line in lines[4:]:
        for val in line.split():
            try:
                acc.append(float(val))
            except ValueError:
                pass
    a = np.array(acc[:npts])
    t = np.arange(npts) * dt
    return t, a, dt

def build_model():
    """Build V10 OpenSees model. Returns pos_df, conn_df, node_map, elem_info, etc."""
    pos_df = pd.read_csv(DATA / 'twin_position_matrix_v10.csv')
    conn_df = pd.read_csv(DATA / 'twin_connectivity_matrix_v10.csv')
    pos_df['node_id'] = pos_df['node_id'].astype(int)
    conn_df['node_i'] = conn_df['node_i'].astype(int)
    conn_df['node_j'] = conn_df['node_j'].astype(int)
    conn_df['element_id'] = conn_df['element_id'].astype(int)

    S = 0.01
    E_long = 3.5e6    # kPa
    G_balsa = 0.2e6   # kPa
    b_sec = 0.006
    A = b_sec**2
    Iz = b_sec**4 / 12
    J = 0.1406 * b_sec**4

    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)

    node_map = {}
    for _, row in pos_df.iterrows():
        nid = int(row['node_id'])
        x, y, z = row['x'] * S, row['y'] * S, row['z'] * S
        ops.node(nid, x, y, z)
        node_map[nid] = (x, y, z)

    base_nodes = [int(n) for n in pos_df[pos_df['floor'] == 0]['node_id'].tolist()]
    for nid in base_nodes:
        ops.fix(nid, 1, 1, 1, 1, 1, 1)

    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.geomTransf('Linear', 2, 1, 0, 0)
    ops.geomTransf('Linear', 3, 0, 1, 0)
    ops.uniaxialMaterial('Elastic', 100, E_long)

    pin_types = {'brace_xz', 'brace_yz', 'floor_brace',
                 'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top'}

    elem_info = {}
    for _, row in conn_df.iterrows():
        eid = int(row['element_id'])
        ni, nj = int(row['node_i']), int(row['node_j'])
        et = row['element_type']
        p1, p2 = node_map[ni], node_map[nj]
        dx = abs(p1[0]-p2[0]); dy = abs(p1[1]-p2[1]); dz = abs(p1[2]-p2[2])

        if et in pin_types:
            ops.element('Truss', eid, ni, nj, A, 100)
            elem_info[eid] = (et, ni, nj, True)
        else:
            t = 3
            if dz < 0.1 * max(dx, dy, 1e-9):
                t = 1 if dx > dy else 2
            ops.element('elasticBeamColumn', eid, ni, nj,
                        A, E_long, G_balsa, J, Iz, Iz, t)
            elem_info[eid] = (et, ni, nj, False)

    # ---- MASS ----
    node_mass = defaultdict(float)
    all_nodes = [int(n) for n in pos_df['node_id'].tolist()]
    MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
    for f in MASS_FLOORS:
        fnodes = [int(n) for n in pos_df[pos_df['floor'] == f]['node_id'].tolist()]
        m = 1.60 / 1000 / len(fnodes)
        for nid in fnodes:
            node_mass[nid] += m

    tf = int(pos_df['floor'].max())
    rnodes = [int(n) for n in pos_df[pos_df['floor'] == tf]['node_id'].tolist()]
    mr = 2.22 / 1000 / len(rnodes)
    for nid in rnodes:
        node_mass[nid] += mr

    SELF_KG = 1.168
    ms = SELF_KG / 1000 / len(all_nodes)
    for nid in all_nodes:
        node_mass[nid] += ms

    for nid, m in node_mass.items():
        ops.mass(nid, m, m, m, 0.0, 0.0, 0.0)

    total_mass = sum(node_mass.values())  # tonne

    # Floor node sets for drift calculation
    floors = sorted(pos_df['floor'].unique())
    floor_nodes = {}
    floor_z = {}
    for f in floors:
        fnids = [int(n) for n in pos_df[pos_df['floor'] == f]['node_id'].tolist()]
        floor_nodes[int(f)] = fnids
        floor_z[int(f)] = pos_df[pos_df['floor'] == f]['z'].iloc[0] * S  # m

    return (pos_df, conn_df, node_map, elem_info, base_nodes,
            all_nodes, node_mass, total_mass, floors, floor_nodes, floor_z)


def run_modal(num_modes=12):
    """Run eigenvalue analysis, return periods and mode shapes info."""
    vals = ops.eigen('-genBandArpack', num_modes)
    periods = [2*np.pi/np.sqrt(v) for v in vals]
    return periods


def get_roof_nodes(pos_df):
    """Get top-floor node IDs."""
    tf = int(pos_df['floor'].max())
    return [int(n) for n in pos_df[pos_df['floor'] == tf]['node_id'].tolist()]


def max_floor_disp(floor_nodes, dof=1):
    """Get max absolute displacement at each floor for given DOF (1=X, 2=Y)."""
    result = {}
    for f, nids in floor_nodes.items():
        mx = 0.0
        for nid in nids:
            try:
                u = abs(ops.nodeDisp(nid, dof))
                mx = max(mx, u)
            except:
                pass
        result[f] = mx
    return result


def interstory_drift(floor_disp, floor_z):
    """Compute interstory drift ratio from floor displacements."""
    floors_sorted = sorted(floor_disp.keys())
    drift = {}
    for i in range(1, len(floors_sorted)):
        f = floors_sorted[i]
        f_prev = floors_sorted[i-1]
        dz = floor_z[f] - floor_z[f_prev]
        if dz > 1e-6:
            drift[f] = abs(floor_disp[f] - floor_disp[f_prev]) / dz
    return drift


# ============================================================
# 1) BUILD MODEL & MODAL
# ============================================================
print("=" * 80)
print("  DASK 2026 - V10 FULL ANALYSIS SUITE")
print("=" * 80)

t0_global = timer.time()

(pos_df, conn_df, node_map, elem_info, base_nodes,
 all_nodes, node_mass, total_mass, floors, floor_nodes, floor_z) = build_model()

print(f"\nModel built: {len(pos_df)} nodes, {len(conn_df)} elements")
print(f"Total mass: {total_mass*1000:.2f} kg = {total_mass:.4f} tonne")
print(f"Floors: {len(floors)}, Height: {max(floor_z.values())*100:.0f} cm")

roof_nodes = get_roof_nodes(pos_df)
H_total = max(floor_z.values())  # m

# Modal
periods = run_modal(12)
print(f"\nModal Analysis:")
for i in range(min(6, len(periods))):
    print(f"  Mode {i+1}: T = {periods[i]:.4f} s  ({1/periods[i]:.1f} Hz)")

omega1 = 2*np.pi / periods[0]
omega2 = 2*np.pi / periods[1] if len(periods) > 1 else omega1*3.5

# Rayleigh damping: xi = 5% at modes 1 and 3.5*omega1
xi = 0.05
omega_a = omega1
omega_b = 3.5 * omega1
a0 = 2 * xi * omega_a * omega_b / (omega_a + omega_b)
a1 = 2 * xi / (omega_a + omega_b)
print(f"\nRayleigh damping: a0={a0:.4f}, a1={a1:.6f}")
print(f"  omega_a={omega_a:.2f}, omega_b={omega_b:.2f} rad/s")


# ============================================================
# 2) TIME-HISTORY ANALYSIS FUNCTION
# ============================================================

def run_time_history(gm_name, time_arr, acc_g, dt_gm, direction='X',
                     integrator_dt=0.001, xi_val=0.05):
    """
    Run Newmark time-history analysis.
    acc_g: acceleration in g units
    direction: 'X' (DOF 1) or 'Y' (DOF 2)
    Returns dict with roof displacement/acceleration/velocity time histories
    and peak interstory drift profile.
    """
    # Rebuild model fresh
    (_, _, _, _, _, _, _, _, _, fn, fz) = build_model()
    roof_nds = get_roof_nodes(pos_df)

    # Modal for Rayleigh
    pds = run_modal(6)
    om1 = 2*np.pi / pds[0]
    om_b = 3.5 * om1
    r_a0 = 2*xi_val*om1*om_b/(om1+om_b)
    r_a1 = 2*xi_val/(om1+om_b)

    # Convert acc from g to m/s^2
    acc_ms2 = acc_g * 9.81

    # Create time series & pattern
    ops.timeSeries('Path', 1, '-dt', dt_gm, '-values', *acc_ms2.tolist(), '-factor', 1.0)
    dof = 1 if direction == 'X' else 2
    ops.pattern('UniformExcitation', 1, dof, '-accel', 1)

    # Rayleigh damping
    ops.rayleigh(r_a0, r_a1, 0.0, 0.0)

    # Analysis parameters (Newmark average acceleration)
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-8, 50)
    ops.algorithm('Newton')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis('Transient')

    nsteps = int(time_arr[-1] / integrator_dt) + 1
    duration = time_arr[-1]

    # Storage
    t_hist = []
    u_roof_hist = []
    v_roof_hist = []
    a_roof_hist = []
    peak_floor_disp_x = {f: 0.0 for f in fn}
    peak_floor_disp_y = {f: 0.0 for f in fn}

    # Reference node for roof (first roof node)
    ref_node = roof_nds[0]

    print(f"    Running {gm_name}_{direction}: {nsteps} steps, dt={integrator_dt}s, "
          f"duration={duration:.1f}s ...")

    t_start = timer.time()
    ok = 0
    ct = 0.0
    step_count = 0
    record_interval = max(1, nsteps // 2000)  # ~2000 data points

    while ct < duration - 1e-10:
        ok = ops.analyze(1, integrator_dt)

        if ok != 0:
            # Try smaller dt
            for sub_dt in [integrator_dt/2, integrator_dt/4, integrator_dt/10]:
                ok = ops.analyze(1, sub_dt)
                if ok == 0:
                    break
            if ok != 0:
                print(f"    *** FAILED at t={ct:.3f}s ***")
                break

        ct += integrator_dt
        step_count += 1

        if step_count % record_interval == 0:
            t_hist.append(ct)
            u_roof_hist.append(ops.nodeDisp(ref_node, dof))
            v_roof_hist.append(ops.nodeVel(ref_node, dof))
            a_roof_hist.append(ops.nodeAccel(ref_node, dof))

        # Track peak floor displacements
        if step_count % (record_interval * 5) == 0:
            for f, nids in fn.items():
                for nid in nids:
                    try:
                        ux = abs(ops.nodeDisp(nid, 1))
                        uy = abs(ops.nodeDisp(nid, 2))
                        peak_floor_disp_x[f] = max(peak_floor_disp_x[f], ux)
                        peak_floor_disp_y[f] = max(peak_floor_disp_y[f], uy)
                    except:
                        pass

    elapsed = timer.time() - t_start
    print(f"    Completed in {elapsed:.1f}s ({step_count} steps)")

    # Final peak sweep
    for f, nids in fn.items():
        for nid in nids:
            try:
                ux = abs(ops.nodeDisp(nid, 1))
                uy = abs(ops.nodeDisp(nid, 2))
                peak_floor_disp_x[f] = max(peak_floor_disp_x[f], ux)
                peak_floor_disp_y[f] = max(peak_floor_disp_y[f], uy)
            except:
                pass

    t_hist = np.array(t_hist)
    u_roof = np.array(u_roof_hist)
    v_roof = np.array(v_roof_hist)
    a_roof = np.array(a_roof_hist)

    # Peak values
    u_max = np.max(np.abs(u_roof)) if len(u_roof) > 0 else 0
    v_max = np.max(np.abs(v_roof)) if len(v_roof) > 0 else 0
    a_max = np.max(np.abs(a_roof)) if len(a_roof) > 0 else 0

    # Interstory drift
    disp_for_drift = peak_floor_disp_x if direction == 'X' else peak_floor_disp_y
    drift = interstory_drift(disp_for_drift, fz)
    max_drift_floor = max(drift, key=drift.get) if drift else 0
    max_drift_val = max(drift.values()) if drift else 0

    pga = np.max(np.abs(acc_g))
    amp_factor = (a_max / 9.81) / pga if pga > 0 else 0

    result = {
        'name': f"{gm_name}_{direction}",
        'pga_g': float(pga),
        'u_max_cm': float(u_max * 100),
        'v_max_cm_s': float(v_max * 100),
        'a_max_g': float(a_max / 9.81),
        'amp_factor': float(amp_factor),
        'max_drift_pct': float(max_drift_val * 100),
        'max_drift_floor': int(max_drift_floor),
        'drift_profile': {str(k): float(v*100) for k, v in drift.items()},
        'peak_floor_disp_x_cm': {str(k): float(v*100) for k,v in peak_floor_disp_x.items()},
        'peak_floor_disp_y_cm': {str(k): float(v*100) for k,v in peak_floor_disp_y.items()},
        'time': t_hist.tolist(),
        'u_roof_cm': (u_roof * 100).tolist(),
        'a_roof_g': (a_roof / 9.81).tolist(),
        'status': 'OK' if ok == 0 else 'FAILED',
        'elapsed_s': float(elapsed),
    }

    return result


# ============================================================
# 3) PUSHOVER ANALYSIS FUNCTION
# ============================================================

def run_pushover(direction='X', target_drift_pct=5.0, n_steps=500):
    """
    Displacement-controlled pushover.
    Lateral load: inverted triangular distribution.
    target_drift: fraction of total height.
    """
    (_, _, nm, _, bn, an, nmass, tmass, fls, fn, fz) = build_model()
    _ = run_modal(4)  # just to verify model

    dof = 1 if direction == 'X' else 2
    target_disp = target_drift_pct / 100.0 * H_total  # m

    # Create lateral load pattern: inverted triangular, proportional to m*z
    ops.timeSeries('Linear', 2)
    ops.pattern('Plain', 2, 2)

    total_mz = 0.0
    free_nodes = [int(n) for n in pos_df[pos_df['floor'] > 0]['node_id'].tolist()]
    for nid in free_nodes:
        m = nmass.get(nid, 0.0)
        z = nm[nid][2]
        mz = m * z
        total_mz += mz

    if total_mz < 1e-12:
        print("  ERROR: No mass*z for pushover loading")
        return None

    for nid in free_nodes:
        m = nmass.get(nid, 0.0)
        z = nm[nid][2]
        f_ratio = m * z / total_mz
        if f_ratio > 1e-12:
            if dof == 1:
                ops.load(nid, f_ratio, 0.0, 0.0, 0.0, 0.0, 0.0)
            else:
                ops.load(nid, 0.0, f_ratio, 0.0, 0.0, 0.0, 0.0)

    # Control node: top floor, closest to center
    roof_nds = get_roof_nodes(pos_df)
    cx = np.mean([nm[n][0] for n in roof_nds])
    cy = np.mean([nm[n][1] for n in roof_nds])
    ctrl_node = min(roof_nds, key=lambda n: (nm[n][0]-cx)**2 + (nm[n][1]-cy)**2)

    print(f"    Pushover {direction}: ctrl_node={ctrl_node}, target={target_disp*100:.2f}cm, "
          f"{n_steps} steps")

    # Analysis setup
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-6, 100)
    ops.algorithm('Newton')

    disp_incr = target_disp / n_steps
    ops.integrator('DisplacementControl', ctrl_node, dof, disp_incr)
    ops.analysis('Static')

    # Storage
    disp_hist = [0.0]
    force_hist = [0.0]

    t_start = timer.time()
    for step in range(n_steps):
        ok = ops.analyze(1)
        if ok != 0:
            ops.algorithm('NewtonLineSearch')
            ok = ops.analyze(1)
            if ok != 0:
                ops.algorithm('ModifiedNewton')
                ok = ops.analyze(1)
                if ok != 0:
                    print(f"    Pushover failed at step {step}")
                    break
            ops.algorithm('Newton')

        u_ctrl = ops.nodeDisp(ctrl_node, dof)
        # Base shear = sum of base reactions
        vbase = 0.0
        for nid in bn:
            try:
                vbase += ops.nodeReaction(nid, dof)
            except:
                pass

        disp_hist.append(u_ctrl)
        force_hist.append(-vbase)  # reaction is opposite

    elapsed = timer.time() - t_start
    print(f"    Completed in {elapsed:.1f}s ({len(disp_hist)-1} steps)")

    disp_arr = np.array(disp_hist)
    force_arr = np.array(force_hist)

    # Find yield point (bilinear approximation)
    # Use 0.2% offset or max slope change
    if len(disp_arr) > 10:
        k_initial = force_arr[5] / disp_arr[5] if abs(disp_arr[5]) > 1e-12 else 0
    else:
        k_initial = 0

    result = {
        'name': f"Pushover_{direction}",
        'direction': direction,
        'ctrl_node': int(ctrl_node),
        'u_max_cm': float(np.max(np.abs(disp_arr)) * 100),
        'v_base_max_kN': float(np.max(np.abs(force_arr))),
        'v_base_max_N': float(np.max(np.abs(force_arr)) * 1000),
        'k_initial_kN_m': float(k_initial),
        'disp_cm': (disp_arr * 100).tolist(),
        'force_N': (force_arr * 1000).tolist(),
        'elapsed_s': float(elapsed),
        'n_steps_completed': len(disp_hist) - 1,
    }

    return result


# ============================================================
# 4) RUN ALL ANALYSES
# ============================================================

all_results = {
    'modal': {
        'periods': [float(p) for p in periods[:12]],
        'omega1': float(omega1),
        'rayleigh_a0': float(a0),
        'rayleigh_a1': float(a1),
        'total_mass_kg': float(total_mass * 1000),
    },
    'time_history': {},
    'pushover': {},
}

# --- KYH-1/2/3 ---
print("\n" + "=" * 80)
print("  KYH-1/2/3 TIME HISTORY ANALYSES")
print("=" * 80)

for kyh_num in [1, 2, 3]:
    gm_file = GM_DASK / f'KYH{kyh_num}.txt'
    if not gm_file.exists():
        print(f"  WARNING: {gm_file} not found, skipping")
        continue

    t_gm, a_gm, dt_gm = parse_dask_gm(gm_file)
    pga = np.max(np.abs(a_gm))
    print(f"\n  KYH-{kyh_num}: {len(a_gm)} points, dt={dt_gm:.5f}s, "
          f"duration={t_gm[-1]:.1f}s, PGA={pga:.4f}g")

    for dire in ['X', 'Y']:
        key = f"KYH{kyh_num}_{dire}"
        res = run_time_history(f"KYH{kyh_num}", t_gm, a_gm, dt_gm,
                               direction=dire, integrator_dt=0.0005)
        all_results['time_history'][key] = res
        print(f"    >> u_max={res['u_max_cm']:.3f}cm, a_max={res['a_max_g']:.3f}g, "
              f"drift={res['max_drift_pct']:.3f}% (floor {res['max_drift_floor']})")


# --- BOL090 ---
print("\n" + "=" * 80)
print("  BOL090 (Düzce 1999) TIME HISTORY ANALYSIS")
print("=" * 80)

bol_file = GM_BOL / 'BOL090.AT2'
if bol_file.exists():
    t_bol, a_bol, dt_bol = parse_at2(bol_file)
    pga_bol = np.max(np.abs(a_bol))
    print(f"  BOL090: {len(a_bol)} points, dt={dt_bol:.4f}s, "
          f"duration={t_bol[-1]:.1f}s, PGA={pga_bol:.4f}g")

    for dire in ['X', 'Y']:
        key = f"BOL090_{dire}"
        res = run_time_history("BOL090", t_bol, a_bol, dt_bol,
                               direction=dire, integrator_dt=0.001)
        all_results['time_history'][key] = res
        print(f"    >> u_max={res['u_max_cm']:.3f}cm, a_max={res['a_max_g']:.3f}g, "
              f"drift={res['max_drift_pct']:.3f}% (floor {res['max_drift_floor']})")
else:
    print(f"  WARNING: {bol_file} not found")


# --- BOL090 scaled 1:50 ---
bol_scaled_file = GM_BOL / 'BOL090_scaled_1_50.AT2'
if bol_scaled_file.exists():
    t_bols, a_bols, dt_bols = parse_at2(bol_scaled_file)
    pga_bols = np.max(np.abs(a_bols))
    print(f"\n  BOL090 (1:50 scaled): PGA={pga_bols:.4f}g")

    for dire in ['X', 'Y']:
        key = f"BOL090_scaled_{dire}"
        res = run_time_history("BOL090_scaled", t_bols, a_bols, dt_bols,
                               direction=dire, integrator_dt=0.001)
        all_results['time_history'][key] = res
        print(f"    >> u_max={res['u_max_cm']:.3f}cm, a_max={res['a_max_g']:.3f}g, "
              f"drift={res['max_drift_pct']:.3f}% (floor {res['max_drift_floor']})")


# --- PUSHOVER ---
print("\n" + "=" * 80)
print("  PUSHOVER ANALYSIS")
print("=" * 80)

for dire in ['X', 'Y']:
    res = run_pushover(direction=dire, target_drift_pct=3.0, n_steps=300)
    if res:
        all_results['pushover'][dire] = res
        print(f"    >> Pushover {dire}: V_base_max={res['v_base_max_N']:.1f}N, "
              f"u_max={res['u_max_cm']:.2f}cm, k0={res['k_initial_kN_m']:.1f}kN/m")


# ============================================================
# 5) SUMMARY TABLE
# ============================================================
print("\n" + "=" * 80)
print("  RESULTS SUMMARY")
print("=" * 80)

print(f"\n{'Analysis':<25} {'PGA(g)':<10} {'u_max(cm)':<12} {'a_max(g)':<12} "
      f"{'drift(%)':<10} {'floor':<6} {'amp':<8}")
print("-" * 90)

for key, res in all_results['time_history'].items():
    print(f"{key:<25} {res['pga_g']:<10.4f} {res['u_max_cm']:<12.4f} "
          f"{res['a_max_g']:<12.4f} {res['max_drift_pct']:<10.4f} "
          f"{res['max_drift_floor']:<6} {res['amp_factor']:<8.2f}")

print("-" * 90)
for dire, res in all_results['pushover'].items():
    print(f"Pushover_{dire:<20} {'---':<10} {res['u_max_cm']:<12.2f} "
          f"{'---':<12} {'---':<10} {'---':<6} {res['v_base_max_N']:.0f}N")

print("-" * 90)

# ============================================================
# 6) SAVE RESULTS
# ============================================================

# Save compact JSON (no huge arrays for the summary)
summary = {}
for key, res in all_results['time_history'].items():
    summary[key] = {k: v for k, v in res.items()
                    if k not in ('time', 'u_roof_cm', 'a_roof_g')}
summary['pushover'] = {}
for dire, res in all_results['pushover'].items():
    summary['pushover'][dire] = {k: v for k, v in res.items()
                                  if k not in ('disp_cm', 'force_N')}
summary['modal'] = all_results['modal']

with open(RESULTS / 'full_analysis_v10_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

# Save full results (with time histories) as separate JSON
with open(RESULTS / 'full_analysis_v10_full.json', 'w') as f:
    json.dump(all_results, f, indent=2)

# Save pushover curves as CSV
for dire, res in all_results['pushover'].items():
    po_df = pd.DataFrame({
        'disp_cm': res['disp_cm'],
        'force_N': res['force_N'],
    })
    po_df.to_csv(RESULTS / f'pushover_{dire}_v10.csv', index=False)

# Save time history envelopes
th_summary = []
for key, res in all_results['time_history'].items():
    th_summary.append({
        'case': key,
        'PGA_g': res['pga_g'],
        'u_max_cm': res['u_max_cm'],
        'a_max_g': res['a_max_g'],
        'v_max_cm_s': res['v_max_cm_s'],
        'max_drift_pct': res['max_drift_pct'],
        'max_drift_floor': res['max_drift_floor'],
        'amp_factor': res['amp_factor'],
        'status': res['status'],
    })
pd.DataFrame(th_summary).to_csv(RESULTS / 'time_history_summary_v10.csv', index=False)

total_elapsed = timer.time() - t0_global
print(f"\nAll results saved to: results/")
print(f"Total elapsed: {total_elapsed:.0f}s ({total_elapsed/60:.1f}min)")
print("=" * 80)
print("  DONE")
print("=" * 80)
