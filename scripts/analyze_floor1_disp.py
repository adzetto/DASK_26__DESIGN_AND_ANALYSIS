"""Kat 1 deplasman analizi - yüksek deplasmanı hangi köşede"""
import numpy as np
import pandas as pd
import openseespy.opensees as ops

pos = pd.read_csv('data/twin_position_matrix_v10.csv')
conn = pd.read_csv('data/twin_connectivity_matrix_v10.csv')

node_coords = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in pos.iterrows()}

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

for nid, (x, y, z) in node_coords.items():
    ops.node(nid, x, y, z)

base = pos[pos['z'] == 0]['node_id'].astype(int).tolist()
for n in base:
    ops.fix(n, 1, 1, 1, 1, 1, 1)

ops.geomTransf('Linear', 1, 1, 0, 0)
ops.geomTransf('Linear', 2, 0, 0, 1)
ops.geomTransf('Linear', 3, 0, 0, 1)

b = 0.6
A, E, G = b**2, 170.0, 170/2.6
J, I = 0.1406*b**4, (b**4)/12

for _, r in conn.iterrows():
    ni, nj = int(r['node_i']), int(r['node_j'])
    if ni in node_coords and nj in node_coords:
        xi, yi, zi = node_coords[ni]
        xj, yj, zj = node_coords[nj]
        dx, dy, dz = abs(xj-xi), abs(yj-yi), abs(zj-zi)
        tr = 1 if dz > max(dx, dy)*0.9 else (2 if dx > dy else 3)
        try:
            ops.element('elasticBeamColumn', int(r['element_id']), ni, nj, A, E, G, J, I, I, tr)
        except: pass

MASS_CONV = 1e-5
for floor in range(26):
    z_f = pos.groupby('floor')['z'].first().sort_index().iloc[floor]
    f_nodes = pos[np.abs(pos['z'] - z_f) < 0.5]['node_id'].astype(int).tolist()
    f_elems = conn[(conn['node_i'].isin(f_nodes)) | (conn['node_j'].isin(f_nodes))]
    m = f_elems['length'].sum() / 2 * A * 160e-6 * MASS_CONV / len(f_nodes)
    for n in f_nodes:
        try: ops.mass(n, m, m, m, 0, 0, 0)
        except: pass

ops.eigen(12)

ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
W = conn['length'].sum() * A * 160e-6 * 9.81 / 1000
V = 0.687 * W
H = 153.0

for floor in range(1, 26):
    z_f = pos.groupby('floor')['z'].first().sort_index().iloc[floor]
    f_nodes = pos[np.abs(pos['z'] - z_f) < 0.5]['node_id'].astype(int).tolist()
    Fi = V * (z_f / H) / 26 / len(f_nodes)
    for n in f_nodes:
        try: ops.load(n, Fi, 0, 0, 0, 0, 0)
        except: pass

ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Newton')
ops.analysis('Static')
ops.analyze(1)

print('Kat 1 Deplasman Analizi (Tower 1):')
print('node_id  x       y       ux(mm)')
print('-' * 40)

floor1_t1 = pos[(pos['floor'] == 1) & (pos['tower'].astype(str) == '1')]
results = []
for _, r in floor1_t1.iterrows():
    nid = int(r['node_id'])
    ux = ops.nodeDisp(nid, 1) * 10
    results.append((nid, r['x'], r['y'], ux))
    print(f"{nid:<8} {r['x']:<7.1f} {r['y']:<7.1f} {ux:.4f}")

# Köşe analizi
print('\n' + '=' * 40)
print('Köşe Deplasmanları:')
print('=' * 40)

corners = [
    (0.0, 0.0, 'Sol-Alt'),
    (30.0, 0.0, 'Sağ-Alt'),
    (0.0, 16.0, 'Sol-Üst'),
    (30.0, 16.0, 'Sağ-Üst'),
]

for x, y, name in corners:
    match = [r for r in results if abs(r[1]-x) < 0.1 and abs(r[2]-y) < 0.1]
    if match:
        print(f"{name}: node {match[0][0]}, ux = {match[0][3]:.4f} mm")

# Min/max bulma
ux_vals = [r[3] for r in results]
print(f'\nMinimum: {min(ux_vals):.4f} mm')
print(f'Maximum: {max(ux_vals):.4f} mm')
print(f'Ortalama: {np.mean(ux_vals):.4f} mm')
print(f'ηbi = {max(ux_vals)/np.mean(ux_vals):.3f}')
