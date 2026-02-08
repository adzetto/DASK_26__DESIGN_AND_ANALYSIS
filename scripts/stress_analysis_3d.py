"""
V10 STRESS ANALYSIS - 3D Plotly Visualization
===============================================
Gravity + Lateral (spectral) load → element axial/bending stress
3D interactive plot colored by stress magnitude

Units: m, kN, tonne, s  →  stress in kPa (→ MPa for display)
"""
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import openseespy.opensees as ops
from collections import defaultdict
import plotly.graph_objects as go

DATA = Path(__file__).parent.parent / 'data'
pos_df = pd.read_csv(DATA / 'twin_position_matrix_v10.csv')
conn_df = pd.read_csv(DATA / 'twin_connectivity_matrix_v10.csv')

pos_df['node_id'] = pos_df['node_id'].astype(int)
conn_df['node_i'] = conn_df['node_i'].astype(int)
conn_df['node_j'] = conn_df['node_j'].astype(int)
conn_df['element_id'] = conn_df['element_id'].astype(int)

print("=" * 70)
print("V10 STRESS ANALYSIS (3D)")
print("=" * 70)

# ============================================
# MATERIAL & SECTION PROPERTIES
# ============================================
S = 0.01           # cm → m
E_long = 3.5e6     # kPa  (balsa longitudinal)
G_balsa = 0.2e6    # kPa
b = 0.006           # m (6 mm)
A = b**2            # m²
I = b**4 / 12       # m⁴
J = 0.1406 * b**4   # m⁴
y_max = b / 2       # distance to extreme fiber (m)

# ============================================
# BUILD OPENSEES MODEL
# ============================================
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

print(f"Nodes: {len(pos_df)}, Elements: {len(conn_df)}, Base fixed: {len(base_nodes)}")

ops.geomTransf('Linear', 1, 0, 1, 0)  # horizontal X
ops.geomTransf('Linear', 2, 1, 0, 0)  # horizontal Y
ops.geomTransf('Linear', 3, 0, 1, 0)  # vertical / diagonal

ops.uniaxialMaterial('Elastic', 100, E_long)

pin_types = {'brace_xz', 'brace_yz', 'floor_brace',
             'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top'}

elem_info = {}  # eid -> (type, ni, nj, is_truss)
n_frame, n_truss = 0, 0

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])
    et = row['element_type']
    p1, p2 = node_map[ni], node_map[nj]
    dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])

    if et in pin_types:
        ops.element('Truss', eid, ni, nj, A, 100)
        elem_info[eid] = (et, ni, nj, True)
        n_truss += 1
    else:
        t = 3
        if dz < 0.1 * max(dx, dy, 1e-9):
            t = 1 if dx > dy else 2
        ops.element('elasticBeamColumn', eid, ni, nj,
                    A, E_long, G_balsa, J, I, I, t)
        elem_info[eid] = (et, ni, nj, False)
        n_frame += 1

print(f"Frame: {n_frame}, Truss: {n_truss}")

# ============================================
# MASS
# ============================================
node_mass = defaultdict(float)
all_int_nodes = [int(n) for n in pos_df['node_id'].tolist()]

MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
total_plate_mass = 0.0
for f in MASS_FLOORS:
    fnodes = [int(n) for n in pos_df[pos_df['floor'] == f]['node_id'].tolist()]
    m = 1.60 / 1000 / len(fnodes)
    for nid in fnodes:
        node_mass[nid] += m
    total_plate_mass += 1.60 / 1000

tf = int(pos_df['floor'].max())
rnodes = [int(n) for n in pos_df[pos_df['floor'] == tf]['node_id'].tolist()]
mr = 2.22 / 1000 / len(rnodes)
for nid in rnodes:
    node_mass[nid] += mr

SELF_KG = 1.168
ms = SELF_KG / 1000 / len(all_int_nodes)
for nid in all_int_nodes:
    node_mass[nid] += ms

total_mass = total_plate_mass + 2.22/1000 + SELF_KG/1000

for nid, m in node_mass.items():
    ops.mass(nid, m, m, m, 0, 0, 0)

print(f"Total mass: {total_mass*1000:.2f} kg")

# ============================================
# GRAVITY LOAD (self weight + plate weights)
# ============================================
g = 9.81  # m/s²

ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply gravity as nodal forces (F = m*g downward = negative Z)
for nid, m in node_mass.items():
    ops.load(nid, 0.0, 0.0, -m * g, 0.0, 0.0, 0.0)

# ============================================
# EQUIVALENT LATERAL FORCE (ELF) - TBDY2018
# ============================================
# Spectral acceleration from design spectrum
SDS = 1.0    # Short period spectral acceleration (g) - approximate
SD1 = 0.4    # 1s spectral acceleration (g) - approximate

# Use modal T1 to get Sa
T1 = 0.115  # s (from modal analysis)
TA = 0.2 * SD1 / SDS
TB = SD1 / SDS

if T1 <= TA:
    Sa = SDS * (0.4 + 0.6 * T1 / TA)
elif T1 <= TB:
    Sa = SDS
else:
    Sa = SD1 / T1

# Base shear V = Sa * W / R (assume R=1 for elastic analysis)
R = 1.0
W = total_mass * g  # kN
V_base = Sa * W / R
print(f"\nELF Analysis:")
print(f"  T1 = {T1:.3f} s, Sa = {Sa:.3f} g")
print(f"  W = {W:.4f} kN, V_base = {V_base:.4f} kN")

# Distribute lateral force by height (inverted triangle)
ops.timeSeries('Linear', 2)
ops.pattern('Plain', 2, 2)

# Lateral force distribution: F_i = V * (m_i * h_i) / sum(m_j * h_j)
sum_mh = 0.0
node_mh = {}
for nid, m in node_mass.items():
    h = node_map[nid][2]  # z coordinate
    mh = m * h
    node_mh[nid] = mh
    sum_mh += mh

if sum_mh > 0:
    for nid, mh in node_mh.items():
        Fi = V_base * mh / sum_mh
        # Apply in Y direction (weak axis, T1 direction)
        ops.load(nid, 0.0, Fi, 0.0, 0.0, 0.0, 0.0)

print(f"  Lateral forces applied (Y direction)")

# ============================================
# STATIC ANALYSIS
# ============================================
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

result = ops.analyze(1)
if result != 0:
    print("ANALYSIS FAILED!")
    sys.exit(1)
print("Static analysis complete.")

# ============================================
# EXTRACT ELEMENT FORCES & STRESSES
# ============================================
print("\nExtracting element stresses...")

stress_data = []
for eid, (etype, ni, nj, is_truss) in elem_info.items():
    p1 = np.array(node_map[ni])
    p2 = np.array(node_map[nj])
    mid = (p1 + p2) / 2.0  # midpoint in m

    if is_truss:
        # Truss: axial force only
        forces = ops.eleResponse(eid, 'axialForce')
        if forces and len(forces) > 0:
            axial = forces[0]
        else:
            forces = ops.eleResponse(eid, 'forces')
            axial = forces[0] if forces else 0.0
        sigma_axial = axial / A  # kPa
        sigma_bending = 0.0
    else:
        # Frame: 12 DOF forces [Ni, Vyi, Vzi, Ti, Myi, Mzi, Nj, Vyj, Vzj, Tj, Myj, Mzj]
        forces = ops.eleForce(eid)
        if forces and len(forces) >= 12:
            N_i = forces[0]
            My_i = forces[4]
            Mz_i = forces[5]
            My_j = forces[10]
            Mz_j = forces[11]

            sigma_axial = N_i / A  # kPa
            # Max bending stress at extreme fiber
            M_max = max(abs(My_i), abs(Mz_i), abs(My_j), abs(Mz_j))
            sigma_bending = M_max * y_max / I  # kPa
        else:
            sigma_axial = 0.0
            sigma_bending = 0.0

    # Combined stress (absolute max)
    sigma_combined = abs(sigma_axial) + abs(sigma_bending)  # kPa
    sigma_mpa = sigma_combined / 1000.0  # MPa

    stress_data.append({
        'element_id': eid,
        'element_type': etype,
        'is_truss': is_truss,
        'ni': ni, 'nj': nj,
        'mid_x': mid[0], 'mid_y': mid[1], 'mid_z': mid[2],
        'x1': p1[0], 'y1': p1[1], 'z1': p1[2],
        'x2': p2[0], 'y2': p2[1], 'z2': p2[2],
        'sigma_axial_kPa': sigma_axial,
        'sigma_bending_kPa': sigma_bending,
        'sigma_combined_kPa': sigma_combined,
        'sigma_combined_MPa': sigma_mpa,
    })

stress_df = pd.DataFrame(stress_data)

# Stats
print(f"\n{'='*70}")
print("STRESS SUMMARY")
print(f"{'='*70}")
print(f"  Elements analyzed: {len(stress_df)}")
print(f"  Max combined stress: {stress_df['sigma_combined_MPa'].max():.2f} MPa")
print(f"  Mean combined stress: {stress_df['sigma_combined_MPa'].mean():.2f} MPa")
print(f"  Balsa compressive strength: ~12-20 MPa (longitudinal)")
print(f"  Balsa tensile strength: ~15-25 MPa (longitudinal)")

# Top 10 stressed elements
print(f"\nTop 10 highest stress elements:")
top10 = stress_df.nlargest(10, 'sigma_combined_MPa')
for _, r in top10.iterrows():
    print(f"  E{int(r['element_id']):4d} ({r['element_type']:15s}): "
          f"σ_axial={r['sigma_axial_kPa']/1000:.2f} MPa, "
          f"σ_bend={r['sigma_bending_kPa']/1000:.2f} MPa, "
          f"σ_total={r['sigma_combined_MPa']:.2f} MPa")

# Save stress CSV
stress_df.to_csv(DATA / 'stress_results_v10.csv', index=False)
print(f"\nStress data saved: data/stress_results_v10.csv")

# ============================================
# 3D PLOTLY VISUALIZATION
# ============================================
print("\nGenerating 3D Plotly visualization...")

scale = 100.0  # m -> cm

# Filter: only columns and braces
show_types = {'column', 'brace_xz', 'brace_yz'}
show_df = stress_df[stress_df['element_type'].isin(show_types)].copy()

sigma_vals = show_df['sigma_combined_MPa'].values
sigma_max = np.percentile(sigma_vals, 99)

fig = go.Figure()

# Draw each element as a separate line colored by stress
for _, r in show_df.iterrows():
    sigma = min(r['sigma_combined_MPa'], sigma_max)
    # Normalize 0→1 for colorscale lookup
    t = sigma / sigma_max if sigma_max > 0 else 0
    # Hot colorscale: blue → cyan → green → yellow → red
    if t < 0.25:
        cr, cg, cb = 0, int(t/0.25*255), 255
    elif t < 0.5:
        cr, cg, cb = 0, 255, int((1-(t-0.25)/0.25)*255)
    elif t < 0.75:
        cr, cg, cb = int((t-0.5)/0.25*255), 255, 0
    else:
        cr, cg, cb = 255, int((1-(t-0.75)/0.25)*255), 0
    color = f'rgb({cr},{cg},{cb})'

    ht = (f"E{int(r['element_id'])} ({r['element_type']})<br>"
          f"σ_axial: {r['sigma_axial_kPa']/1000:.2f} MPa<br>"
          f"σ_bend: {r['sigma_bending_kPa']/1000:.2f} MPa<br>"
          f"σ_total: {r['sigma_combined_MPa']:.2f} MPa")

    fig.add_trace(go.Scatter3d(
        x=[r['x1']*scale, r['x2']*scale],
        y=[r['y1']*scale, r['y2']*scale],
        z=[r['z1']*scale, r['z2']*scale],
        mode='lines',
        line=dict(color=color, width=3),
        text=[ht, ht],
        hoverinfo='text',
        showlegend=False,
    ))

# Invisible colorbar trace
fig.add_trace(go.Scatter3d(
    x=[None], y=[None], z=[None],
    mode='markers',
    marker=dict(
        size=0.1,
        color=[0],
        colorscale=[[0,'rgb(0,0,255)'],[0.25,'rgb(0,255,255)'],
                    [0.5,'rgb(0,255,0)'],[0.75,'rgb(255,255,0)'],
                    [1.0,'rgb(255,0,0)']],
        cmin=0, cmax=round(sigma_max, 2),
        colorbar=dict(title=dict(text='σ (MPa)', font=dict(color='white')),
                      tickfont=dict(color='white')),
    ),
    hoverinfo='skip',
    showlegend=False,
))

fig.update_layout(
    title=dict(
        text=f'DASK V10 - Stress Distribution (Columns + Braces)<br>'
             f'<sub>Gravity + ELF (Y-dir), V_base={V_base*1000:.1f} N, '
             f'σ_max={show_df["sigma_combined_MPa"].max():.2f} MPa</sub>',
        font=dict(color='white'),
    ),
    scene=dict(
        xaxis=dict(title='X (cm)', color='white', gridcolor='gray',
                   backgroundcolor='black'),
        yaxis=dict(title='Y (cm)', color='white', gridcolor='gray',
                   backgroundcolor='black'),
        zaxis=dict(title='Z (cm)', color='white', gridcolor='gray',
                   backgroundcolor='black'),
        aspectmode='data',
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        bgcolor='black',
    ),
    paper_bgcolor='black',
    plot_bgcolor='black',
    width=1200,
    height=900,
    showlegend=False,
)

output_html = DATA.parent / 'results' / 'stress_3d_v10.html'
fig.write_html(str(output_html))
print(f"\n3D plot saved: {output_html}")
print("Opening in browser...")

import webbrowser
webbrowser.open(str(output_html.resolve()))
