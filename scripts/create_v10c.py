"""
V10c Model - Orta Bölge Güçlendirmesi
=====================================
ηbi = 1.453, yüksek deplasman y=7.4-8.6 bölgesinde
Bu bölgeye XZ çaprazları ekleyerek burulmayı azaltıyoruz.
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os

print("=" * 80)
print("V10c MODEL - ORTA BÖLGE GÜÇLENDİRMESİ")
print("=" * 80)

# V10 verilerini oku (V10b değil, orijinal V10)
pos = pd.read_csv('data/twin_position_matrix_v10.csv')
conn_v10 = pd.read_csv('data/twin_connectivity_matrix_v10.csv')

node_coords = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in pos.iterrows()}

# Ağırlık kontrolü
b_section = 0.6
A_section = b_section ** 2
density_kg_cm3 = 160 / 1e6

v10_weight = conn_v10['length'].sum() * A_section * density_kg_cm3
available_weight = 1.4 - v10_weight
available_length = available_weight / (A_section * density_kg_cm3)

print(f"\nV10 Ağırlık: {v10_weight:.4f} kg")
print(f"Kalan bütçe: {available_weight:.4f} kg ({available_length:.1f} cm)")

# Yüksek deplasmanı olan düğümler: x=11, y=7.4/8.6
# Bu düğümlere giden XZ çaprazları ekle

def calc_length(n1, n2):
    x1, y1, z1 = node_coords[n1]
    x2, y2, z2 = node_coords[n2]
    return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

def find_node(z, x, y):
    for nid, (nx, ny, nz) in node_coords.items():
        if abs(nz-z) < 0.5 and abs(nx-x) < 0.5 and abs(ny-y) < 0.5:
            return nid
    return None

next_elem_id = conn_v10['element_id'].max() + 1
new_elements = []

def add_brace(ni, nj, tower):
    global next_elem_id
    length = calc_length(ni, nj)
    elem = {
        'element_id': next_elem_id,
        'node_i': ni,
        'node_j': nj,
        'element_type': 'center_brace',
        'tower': tower,
        'connection': 'rigid',
        'length': round(length, 4)
    }
    next_elem_id += 1
    return elem

# Tower 1: y=7.4 ve y=8.6 kenarlarına XZ çaprazları
# x=8 → x=11 (3 cm açıklık)
# x=11 → x=14.4 (3.4 cm açıklık)

# Kat 0 ve 1'deki düğümler
# y=7.4 kenarı
n_8_74_0 = find_node(0, 11, 7.4)   # node 9
n_11_74_0 = find_node(0, 11, 7.4)  # node 9
n_14_74_0 = find_node(0, 14.4, 7.4) # node 13

n_8_74_9 = find_node(9, 11, 7.4)   # node 41
n_11_74_9 = find_node(9, 11, 7.4)  # node 41
n_14_74_9 = find_node(9, 14.4, 7.4) # node 45

print(f"\nHedef düğümler:")
print(f"  (11, 7.4, 0) → node {n_11_74_0}")
print(f"  (14.4, 7.4, 0) → node {n_14_74_0}")
print(f"  (11, 7.4, 9) → node {n_11_74_9}")
print(f"  (14.4, 7.4, 9) → node {n_14_74_9}")

total_added = 0

# X-brace at y=7.4 (x=11 to x=14.4)
if n_11_74_0 and n_14_74_9:
    length = calc_length(n_11_74_0, n_14_74_9)
    if total_added + length < available_length:
        new_elements.append(add_brace(n_11_74_0, n_14_74_9, 'tower1'))
        total_added += length
        print(f"  Eklendi: {n_11_74_0} → {n_14_74_9}, L={length:.1f}")

if n_14_74_0 and n_11_74_9:
    length = calc_length(n_14_74_0, n_11_74_9)
    if total_added + length < available_length:
        new_elements.append(add_brace(n_14_74_0, n_11_74_9, 'tower1'))
        total_added += length
        print(f"  Eklendi: {n_14_74_0} → {n_11_74_9}, L={length:.1f}")

# y=8.6 kenarı
n_11_86_0 = find_node(0, 11, 8.6)   # node 10
n_14_86_0 = find_node(0, 14.4, 8.6) # node 14
n_11_86_9 = find_node(9, 11, 8.6)   # node 42
n_14_86_9 = find_node(9, 14.4, 8.6) # node 46

if n_11_86_0 and n_14_86_9:
    length = calc_length(n_11_86_0, n_14_86_9)
    if total_added + length < available_length:
        new_elements.append(add_brace(n_11_86_0, n_14_86_9, 'tower1'))
        total_added += length
        print(f"  Eklendi: {n_11_86_0} → {n_14_86_9}, L={length:.1f}")

if n_14_86_0 and n_11_86_9:
    length = calc_length(n_14_86_0, n_11_86_9)
    if total_added + length < available_length:
        new_elements.append(add_brace(n_14_86_0, n_11_86_9, 'tower1'))
        total_added += length
        print(f"  Eklendi: {n_14_86_0} → {n_11_86_9}, L={length:.1f}")

# Sağ taraf: x=15.6 to x=19
n_16_74_0 = find_node(0, 15.6, 7.4)  # node 17
n_19_74_0 = find_node(0, 19, 7.4)    # node 21
n_16_74_9 = find_node(9, 15.6, 7.4)  # node 49
n_19_74_9 = find_node(9, 19, 7.4)    # node 53

if n_16_74_0 and n_19_74_9:
    length = calc_length(n_16_74_0, n_19_74_9)
    if total_added + length < available_length:
        new_elements.append(add_brace(n_16_74_0, n_19_74_9, 'tower1'))
        total_added += length
        print(f"  Eklendi: {n_16_74_0} → {n_19_74_9}, L={length:.1f}")

if n_19_74_0 and n_16_74_9:
    length = calc_length(n_19_74_0, n_16_74_9)
    if total_added + length < available_length:
        new_elements.append(add_brace(n_19_74_0, n_16_74_9, 'tower1'))
        total_added += length
        print(f"  Eklendi: {n_19_74_0} → {n_16_74_9}, L={length:.1f}")

print(f"\nEklenen eleman: {len(new_elements)}")
print(f"Eklenen uzunluk: {total_added:.1f} cm")

# V10c oluştur
conn_v10c = pd.concat([conn_v10, pd.DataFrame(new_elements)], ignore_index=True)
v10c_weight = conn_v10c['length'].sum() * A_section * density_kg_cm3

print(f"V10c toplam ağırlık: {v10c_weight:.4f} kg")
if v10c_weight <= 1.4:
    print("✓ Ağırlık uygun")
else:
    print("⚠ Limit aşıldı!")

# Kaydet
pos.to_csv('data/twin_position_matrix_v10c.csv', index=False)
conn_v10c.to_csv('data/twin_connectivity_matrix_v10c.csv', index=False)

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

for _, r in conn_v10c.iterrows():
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
    f_elems = conn_v10c[(conn_v10c['node_i'].isin(f_nodes)) | (conn_v10c['node_j'].isin(f_nodes))]
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

W = v10c_weight * 9.81 / 1000
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
    result = "MEVCUT ✗"
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
print("V10c SONUÇ")
print("=" * 80)
print(f"""
┌────────────────────────────────────────────┐
│            V10c MODEL SONUÇLARI            │
├────────────────────────────────────────────┤
│ Ağırlık   : {v10c_weight:.4f} kg {'✓' if v10c_weight <= 1.4 else '✗'}               │
│ T1        : {T1:.4f} s                    │
│ A1a ηbi   : {max_eta:.3f} {result:<20}│
│ Drift     : {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}             │
└────────────────────────────────────────────┘
""")

# Kaydet
results = pd.DataFrame({
    'Parametre': ['Model', 'Eleman', 'Ağırlık', 'T1', 'ηbi_max', 'δ/h_max'],
    'Değer': ['V10c', len(conn_v10c), f'{v10c_weight:.4f}', f'{T1:.4f}', 
              f'{max_eta:.3f}', f'{max_drift:.6f}']
})
os.makedirs('results/data', exist_ok=True)
results.to_csv('results/data/structural_design_check_v10c.csv', index=False)

print("V10c ANALİZ TAMAMLANDI")
