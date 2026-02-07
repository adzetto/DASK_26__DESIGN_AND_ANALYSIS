"""
Kat 1 Burulma Detaylı Analizi
=============================
Her düğümün deplasmanını görselleştir
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops

print("=" * 80)
print("KAT 1 BURULMA DETAYLI ANALİZ")
print("=" * 80)

pos = pd.read_csv('data/twin_position_matrix_v9.csv')
conn = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

node_coords = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in pos.iterrows()}

# Model kur
b_section = 0.6
A_section = b_section ** 2
density_kg_cm3 = 160 / 1e6

BALSA_E = 170.0
BALSA_G = BALSA_E / 2.6
Iz = Iy = (b_section**4) / 12
J = 0.1406 * b_section**4

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

for _, r in conn.iterrows():
    ni, nj = int(r['node_i']), int(r['node_j'])
    if ni in node_coords and nj in node_coords:
        xi, yi, zi = node_coords[ni]
        xj, yj, zj = node_coords[nj]
        dx, dy, dz = abs(xj-xi), abs(yj-yi), abs(zj-zi)
        tr = 1 if dz > max(dx, dy)*0.9 else (2 if dx > dy else 3)
        try:
            ops.element('elasticBeamColumn', int(r['element_id']), ni, nj, A_section, BALSA_E, BALSA_G, J, Iy, Iz, tr)
        except: pass

floor_z = pos.groupby('floor')['z'].first().sort_index()
MASS_CONV = 1e-5

for floor in range(26):
    z_f = floor_z.iloc[floor]
    f_nodes = pos[np.abs(pos['z'] - z_f) < 0.5]['node_id'].astype(int).tolist()
    f_elems = conn[(conn['node_i'].isin(f_nodes)) | (conn['node_j'].isin(f_nodes))]
    m = f_elems['length'].sum() / 2 * A_section * density_kg_cm3 * MASS_CONV / len(f_nodes)
    for n in f_nodes:
        try: ops.mass(n, m, m, m, 0, 0, 0)
        except: pass

ops.eigen(12)

# Yük
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

SS, S1, FS, F1 = 0.877, 0.243, 1.149, 2.114
SDS, SD1 = SS * FS, S1 * F1

def Sae(T):
    T1 = 0.0479
    TA = 0.2 * SD1 / SDS
    if T < TA: return (0.4 + 0.6 * T / TA) * SDS
    return SDS if T <= SD1/SDS else SD1 / T

W = conn['length'].sum() * A_section * density_kg_cm3 * 9.81 / 1000
V = Sae(0.0479) * W
H = 153.0

for floor in range(1, 26):
    z_f = floor_z.iloc[floor]
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

# Kat 1 Tower 1 düğümleri (y <= 16)
floor1_t1 = pos[(np.abs(pos['z'] - 9) < 0.5) & (pos['y'] <= 17)]

print("\n" + "=" * 80)
print("KAT 1 - TOWER 1 DEPLASMAN HARİTASI")
print("=" * 80)

print(f"\n{'Node':<8}{'X':<8}{'Y':<8}{'ux (mm)':<12}{'Durum':<10}")
print("-" * 46)

disps = []
for _, row in floor1_t1.sort_values(['y', 'x']).iterrows():
    nid = int(row['node_id'])
    x, y = row['x'], row['y']
    ux = abs(ops.nodeDisp(nid, 1)) * 10  # mm
    disps.append({'node': nid, 'x': x, 'y': y, 'ux': ux})

df = pd.DataFrame(disps)
d_avg = df['ux'].mean()
d_max = df['ux'].max()

for _, r in df.iterrows():
    status = "MAX" if r['ux'] == d_max else ("LOW" if r['ux'] < d_avg * 0.8 else "")
    print(f"{r['node']:<8}{r['x']:<8.1f}{r['y']:<8.1f}{r['ux']:<12.4f}{status:<10}")

print("-" * 46)
print(f"Ortalama: {d_avg:.4f} mm")
print(f"Maksimum: {d_max:.4f} mm")
print(f"ηbi = {d_max/d_avg:.3f}")

# Y koordinatına göre grupla
print("\n" + "=" * 80)
print("Y KOORDINATINA GÖRE ORTALAMA DEPLASMAN")
print("=" * 80)

for y in sorted(df['y'].unique()):
    y_avg = df[df['y'] == y]['ux'].mean()
    print(f"y = {y:5.1f}: {y_avg:.4f} mm  (ort'a oranı: {y_avg/d_avg:.2f})")

print("\n" + "=" * 80)
print("X KOORDINATINA GÖRE ORTALAMA DEPLASMAN")
print("=" * 80)

for x in sorted(df['x'].unique()):
    x_avg = df[df['x'] == x]['ux'].mean()
    print(f"x = {x:5.1f}: {x_avg:.4f} mm  (ort'a oranı: {x_avg/d_avg:.2f})")

print("\n" + "=" * 80)
print("SONUÇ")
print("=" * 80)

# En yüksek ve en düşük deplasmanlar
high_disp = df[df['ux'] > d_avg * 1.2]
low_disp = df[df['ux'] < d_avg * 0.8]

print("\nYüksek deplasmanlı düğümler (> 1.2 × ort):")
for _, r in high_disp.iterrows():
    print(f"  Node {int(r['node'])}: x={r['x']:.1f}, y={r['y']:.1f}, ux={r['ux']:.4f}")

print("\nDüşük deplasmanlı düğümler (< 0.8 × ort):")
for _, r in low_disp.iterrows():
    print(f"  Node {int(r['node'])}: x={r['x']:.1f}, y={r['y']:.1f}, ux={r['ux']:.4f}")

print(f"""
ÖNERİ:
------
δmax = {d_max:.4f} mm (y=7.4-8.6 bölgesi)
δort = {d_avg:.4f} mm
ηbi = {d_max/d_avg:.3f}

Hedef: ηbi < 1.4
Gerekli δmax: < {1.4 * d_avg:.4f} mm
Azaltılması gereken: {d_max - 1.4*d_avg:.4f} mm ({(1 - 1.4*d_avg/d_max)*100:.1f}%)

Strateji: y=7.4 ve y=8.6 düğümlerinin deplasmanını azaltmak
""")
