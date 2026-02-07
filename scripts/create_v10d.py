"""
V10d Model - XY Düzlem Diyafram Güçlendirmesi
=============================================
Kat 1'de XY düzlem çaprazları ekleyerek rijit diyafram etkisi
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os

print("=" * 80)
print("V10d MODEL - XY DİYAFRAM GÜÇLENDİRMESİ")
print("=" * 80)

# V10 verilerini oku (orijinal)
pos = pd.read_csv('data/twin_position_matrix_v10.csv')
conn_v10 = pd.read_csv('data/twin_connectivity_matrix_v10.csv')

node_coords = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in pos.iterrows()}

# Kat 1 düğümleri
floor1_nodes = pos[np.abs(pos['z'] - 9) < 0.5]
print(f"\nKat 1 düğüm sayısı: {len(floor1_nodes)}")

# Y koordinatları
y_coords = sorted(floor1_nodes['y'].unique())
print(f"Y koordinatları: {y_coords}")

# Ağırlık kontrolü
b_section = 0.6
A_section = b_section ** 2
density_kg_cm3 = 160 / 1e6

v10_weight = conn_v10['length'].sum() * A_section * density_kg_cm3
available_weight = 1.4 - v10_weight
available_length = available_weight / (A_section * density_kg_cm3)

print(f"\nV10 Ağırlık: {v10_weight:.4f} kg")
print(f"Kalan bütçe: {available_weight:.4f} kg ({available_length:.1f} cm)")

def calc_length(n1, n2):
    x1, y1, z1 = node_coords[n1]
    x2, y2, z2 = node_coords[n2]
    return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

def find_node_at(x, y, z):
    for nid, (nx, ny, nz) in node_coords.items():
        if abs(nz-z) < 0.5 and abs(nx-x) < 0.5 and abs(ny-y) < 0.5:
            return nid
    return None

next_elem_id = conn_v10['element_id'].max() + 1
new_elements = []

def add_brace(ni, nj, etype):
    global next_elem_id
    length = calc_length(ni, nj)
    elem = {
        'element_id': next_elem_id,
        'node_i': ni,
        'node_j': nj,
        'element_type': etype,
        'tower': '1',
        'connection': 'rigid',
        'length': round(length, 4)
    }
    next_elem_id += 1
    return elem

# X koordinatlarını analiz et
x_coords_f1 = sorted(floor1_nodes['x'].unique())
print(f"Kat 1 X koordinatları: {x_coords_f1}")

# Köşeden merkeze bağlayan XY çaprazları
# Her köşeden merkeze (y=0 → y=7.4 ve y=16 → y=8.6)
total_added = 0

# Sol alt köşe (0,0,9) → (0,7.4,9)
n1 = find_node_at(0, 0, 9)
n2 = find_node_at(0, 4.8, 9)
print(f"\nSol köşe: {n1} → {n2}")
if n1 and n2:
    length = calc_length(n1, n2)
    if total_added + length < available_length:
        new_elements.append(add_brace(n1, n2, 'xy_diag'))
        total_added += length
        print(f"  Eklendi: {n1} → {n2}, L={length:.1f}")

# Sağ alt köşe (30,0,9) → (30,7.4,9)
n1 = find_node_at(30, 0, 9)
n2 = find_node_at(30, 4.8, 9)
print(f"Sağ köşe: {n1} → {n2}")
if n1 and n2:
    length = calc_length(n1, n2)
    if total_added + length < available_length:
        new_elements.append(add_brace(n1, n2, 'xy_diag'))
        total_added += length
        print(f"  Eklendi: {n1} → {n2}, L={length:.1f}")

# Sol üst köşe (0,16,9) → (0,11.2,9) 
n1 = find_node_at(0, 16, 9)
n2 = find_node_at(0, 11.2, 9)
if n1 and n2:
    length = calc_length(n1, n2)
    if total_added + length < available_length:
        new_elements.append(add_brace(n1, n2, 'xy_diag'))
        total_added += length
        print(f"  Eklendi: {n1} → {n2}, L={length:.1f}")

# Sağ üst köşe (30,16,9) → (30,11.2,9)
n1 = find_node_at(30, 16, 9)
n2 = find_node_at(30, 11.2, 9)
if n1 and n2:
    length = calc_length(n1, n2)
    if total_added + length < available_length:
        new_elements.append(add_brace(n1, n2, 'xy_diag'))
        total_added += length
        print(f"  Eklendi: {n1} → {n2}, L={length:.1f}")

print(f"\nEklenen eleman: {len(new_elements)}")
print(f"Eklenen uzunluk: {total_added:.1f} cm")

# V10d oluştur
conn_v10d = pd.concat([conn_v10, pd.DataFrame(new_elements)], ignore_index=True)
v10d_weight = conn_v10d['length'].sum() * A_section * density_kg_cm3

print(f"V10d toplam ağırlık: {v10d_weight:.4f} kg")

# Kaydet
pos.to_csv('data/twin_position_matrix_v10d.csv', index=False)
conn_v10d.to_csv('data/twin_connectivity_matrix_v10d.csv', index=False)

# ============================================================================
# ANALIZ
# ============================================================================
print("\n" + "=" * 80)
print("OPENSEES ANALİZİ")
print("=" * 80)

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

for _, r in conn_v10d.iterrows():
    ni, nj = int(r['node_i']), int(r['node_j'])
    if ni in node_coords and nj in node_coords:
        xi, yi, zi = node_coords[ni]
        xj, yj, zj = node_coords[nj]
        dx, dy, dz = abs(xj-xi), abs(yj-yi), abs(zj-zi)
        tr = 1 if dz > max(dx, dy)*0.9 else (2 if dx > dy else 3)
        try:
            ops.element('elasticBeamColumn', int(r['element_id']), ni, nj, A_section, BALSA_E, BALSA_G, J, Iy, Iz, tr)
        except: pass

total_floors = 26
MASS_CONV = 1e-5
floor_z = pos.groupby('floor')['z'].first().sort_index()

for floor in range(total_floors):
    z_f = floor_z.iloc[floor]
    f_nodes = pos[np.abs(pos['z'] - z_f) < 0.5]['node_id'].astype(int).tolist()
    f_elems = conn_v10d[(conn_v10d['node_i'].isin(f_nodes)) | (conn_v10d['node_j'].isin(f_nodes))]
    m = f_elems['length'].sum() / 2 * A_section * density_kg_cm3 * MASS_CONV / len(f_nodes)
    for n in f_nodes:
        try: ops.mass(n, m, m, m, 0, 0, 0)
        except: pass

eigenvalues = ops.eigen(12)
T1 = 2 * np.pi / np.sqrt(eigenvalues[0])
print(f"T1 = {T1:.4f} s")

# Yük
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

SS, S1, FS, F1 = 0.877, 0.243, 1.149, 2.114
SDS, SD1 = SS * FS, S1 * F1
TA = 0.2 * SD1 / SDS

def Sae(T):
    if T < TA: return (0.4 + 0.6 * T / TA) * SDS
    return SDS if T <= SD1/SDS else SD1 / T

W = v10d_weight * 9.81 / 1000
V = Sae(T1) * W
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

# Burulma
print("\n" + "=" * 80)
print("A1a BURULMA KONTROLÜ")
print("=" * 80)

print(f"\n{'Kat':<6}{'δmax':<12}{'δort':<12}{'ηbi':<8}")
print("-" * 38)

max_eta = 0
for floor in [1, 6, 11, 16, 21]:
    z_f = floor_z.iloc[floor]
    f_nodes = pos[np.abs(pos['z'] - z_f) < 0.5]['node_id'].astype(int).tolist()
    
    disps = [abs(ops.nodeDisp(n, 1)) * 10 for n in f_nodes if n in node_coords]
    d_max, d_avg = max(disps), np.mean(disps)
    eta = d_max / d_avg if d_avg > 0 else 1.0
    if eta > max_eta:
        max_eta = eta
    print(f"{floor:<6}{d_max:<12.4f}{d_avg:<12.4f}{eta:<8.3f}")

print("-" * 38)
print(f"Maksimum ηbi = {max_eta:.3f}")

if max_eta <= 1.2:
    result = "YOK ✓"
elif max_eta <= 1.4:
    result = "2024 Tebliğ SAĞLANDI ✓"
else:
    result = "VAR ✗"
print(f"A1a Burulma: {result}")

# Drift
max_drift = 0
prev = 0
for floor in [5, 10, 15, 20, 25]:
    z_f = floor_z.iloc[floor]
    f_nodes = pos[np.abs(pos['z'] - z_f) < 0.5]['node_id'].astype(int).tolist()
    avg = np.mean([abs(ops.nodeDisp(n, 1)) for n in f_nodes])
    delta = (avg - prev) * 10
    drift = abs(delta) / 60
    if drift > max_drift:
        max_drift = drift
    prev = avg

print(f"\nDrift: δ/h = {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}")

# Özet
print("\n" + "=" * 80)
print("V10d SONUÇ")
print("=" * 80)
print(f"""
┌────────────────────────────────────────────┐
│            V10d MODEL SONUÇLARI            │
├────────────────────────────────────────────┤
│ Ağırlık   : {v10d_weight:.4f} kg {'✓' if v10d_weight <= 1.4 else '✗'}               │
│ T1        : {T1:.4f} s                    │
│ A1a ηbi   : {max_eta:.3f} {result:<20}│
│ Drift     : {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}             │
└────────────────────────────────────────────┘
""")

results = pd.DataFrame({
    'Parametre': ['Model', 'Eleman', 'Ağırlık', 'T1', 'ηbi_max', 'δ/h_max'],
    'Değer': ['V10d', len(conn_v10d), f'{v10d_weight:.4f}', f'{T1:.4f}', 
              f'{max_eta:.3f}', f'{max_drift:.6f}']
})
results.to_csv('results/data/structural_design_check_v10d.csv', index=False)

print("V10d ANALİZ TAMAMLANDI")
