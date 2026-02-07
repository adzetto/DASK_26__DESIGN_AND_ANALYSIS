"""
V11 Model - Köprü Güçlendirmesi + Merkez Rijitlik
==================================================
Hedef: ηbi < 1.4 (2024 Tebliği)
Strateji: Köprü bölgesini X yönünde güçlendirmek
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os

print("=" * 80)
print("V11 MODEL - KÖPRÜ GÜÇLENDİRMESİ")
print("=" * 80)

# V9 verilerini oku (temiz başlangıç)
pos = pd.read_csv('data/twin_position_matrix_v9.csv')
conn = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

node_coords = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in pos.iterrows()}

# Ağırlık
b_section = 0.6
A_section = b_section ** 2
density_kg_cm3 = 160 / 1e6

v9_weight = conn['length'].sum() * A_section * density_kg_cm3
available_weight = 1.4 - v9_weight
available_length = available_weight / (A_section * density_kg_cm3)

print(f"V9 Ağırlık: {v9_weight:.4f} kg")
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

next_elem_id = conn['element_id'].max() + 1
new_elements = []
total_added = 0

def add_brace(ni, nj, etype, tower='1'):
    global next_elem_id, total_added
    length = calc_length(ni, nj)
    if total_added + length > available_length:
        print(f"  ⚠ Bütçe aşıldı: {ni} → {nj}")
        return None
    elem = {
        'element_id': next_elem_id,
        'node_i': ni,
        'node_j': nj,
        'element_type': etype,
        'tower': tower,
        'connection': 'rigid',
        'length': round(length, 4)
    }
    next_elem_id += 1
    total_added += length
    return elem

print("\n--- KÖPRÜ ÇAPRAZLARI (XY düzlem, z=9) ---")

# Köprü düğümleri: y=7.4 ve y=8.6 arasındaki x=11-19 bölgesi
# z=9 (kat 1) seviyesinde XY çaprazları

# Köprü sol: (11, 7.4, 9) - (11, 8.6, 9) arası
# Köprü sağ: (19, 7.4, 9) - (19, 8.6, 9) arası

# XY düzlem çaprazları - köprüyü X yönünde rijitleştir
# (11, 7.4) → (14.4, 8.6) ve ters
n1 = find_node_at(11, 7.4, 9)
n2 = find_node_at(14.4, 8.6, 9)
print(f"Köprü sol-1: {n1} → {n2}")
if n1 and n2:
    e = add_brace(n1, n2, 'bridge_xy')
    if e: new_elements.append(e); print(f"  ✓ L={e['length']:.1f}")

n1 = find_node_at(11, 8.6, 9)
n2 = find_node_at(14.4, 7.4, 9)
if n1 and n2:
    e = add_brace(n1, n2, 'bridge_xy')
    if e: new_elements.append(e); print(f"  ✓ L={e['length']:.1f}")

# Sağ taraf
n1 = find_node_at(15.6, 7.4, 9)
n2 = find_node_at(19, 8.6, 9)
print(f"Köprü sağ-1: {n1} → {n2}")
if n1 and n2:
    e = add_brace(n1, n2, 'bridge_xy')
    if e: new_elements.append(e); print(f"  ✓ L={e['length']:.1f}")

n1 = find_node_at(15.6, 8.6, 9)
n2 = find_node_at(19, 7.4, 9)
if n1 and n2:
    e = add_brace(n1, n2, 'bridge_xy')
    if e: new_elements.append(e); print(f"  ✓ L={e['length']:.1f}")

print("\n--- YZ KÖŞE ÇAPRAZLARI (kat 0-1) ---")

# V10'daki başarılı köşe çaprazları
corners = [
    (0, 0, '1'), (0, 16, '1'), (30, 0, '1'), (30, 16, '1'),
]

for x, y, tw in corners:
    n0 = find_node_at(x, y, 0)
    n1_up = find_node_at(x, y + 1.2 if y == 0 else y - 1.2, 9)  # y yönünde kayık
    if n0 and n1_up:
        e = add_brace(n0, n1_up, 'corner_yz', tw)
        if e: new_elements.append(e); print(f"  ✓ ({x},{y}) L={e['length']:.1f}")
    
    n0_shift = find_node_at(x, y + 1.2 if y == 0 else y - 1.2, 0)
    n1 = find_node_at(x, y, 9)
    if n0_shift and n1:
        e = add_brace(n0_shift, n1, 'corner_yz', tw)
        if e: new_elements.append(e); print(f"  ✓ ({x},{y}) L={e['length']:.1f}")

print("\n--- MERKEZ X-ÇAPRAZLARI (z=9, y=7.4/8.6) ---")

# x=11 → x=14.4 arası XZ çaprazları (z sabit=9)
# Aslında XY düzlem çaprazları (köprü içi)

# x=14.4 → x=15.6 arası (köprü merkezi)
n1 = find_node_at(14.4, 7.4, 9)
n2 = find_node_at(15.6, 8.6, 9)
if n1 and n2:
    e = add_brace(n1, n2, 'bridge_center')
    if e: new_elements.append(e); print(f"  ✓ merkez: L={e['length']:.1f}")

n1 = find_node_at(14.4, 8.6, 9)
n2 = find_node_at(15.6, 7.4, 9)
if n1 and n2:
    e = add_brace(n1, n2, 'bridge_center')
    if e: new_elements.append(e); print(f"  ✓ merkez: L={e['length']:.1f}")

print(f"\nEklenen eleman: {len(new_elements)}")
print(f"Eklenen uzunluk: {total_added:.1f} cm")

# V11 oluştur
conn_v11 = pd.concat([conn, pd.DataFrame(new_elements)], ignore_index=True)
v11_weight = conn_v11['length'].sum() * A_section * density_kg_cm3
print(f"V11 toplam ağırlık: {v11_weight:.4f} kg {'✓' if v11_weight <= 1.4 else '✗'}")

pos.to_csv('data/twin_position_matrix_v11.csv', index=False)
conn_v11.to_csv('data/twin_connectivity_matrix_v11.csv', index=False)

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

for _, r in conn_v11.iterrows():
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
    f_elems = conn_v11[(conn_v11['node_i'].isin(f_nodes)) | (conn_v11['node_j'].isin(f_nodes))]
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

def Sae(T):
    TA = 0.2 * SD1 / SDS
    if T < TA: return (0.4 + 0.6 * T / TA) * SDS
    return SDS if T <= SD1/SDS else SD1 / T

W = v11_weight * 9.81 / 1000
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
print("A1a BURULMA KONTROLÜ (2024 TEBLİĞ: ηbi < 1.4)")
print("=" * 80)

print(f"\n{'Kat':<6}{'δmax':<12}{'δort':<12}{'ηbi':<8}{'Durum':<10}")
print("-" * 48)

max_eta = 0
critical_floor = 0
for floor in [1, 5, 10, 15, 20, 25]:
    z_f = floor_z.iloc[floor]
    f_nodes = pos[np.abs(pos['z'] - z_f) < 0.5]['node_id'].astype(int).tolist()
    
    disps = [abs(ops.nodeDisp(n, 1)) * 10 for n in f_nodes if n in node_coords]
    d_max, d_avg = max(disps), np.mean(disps)
    eta = d_max / d_avg if d_avg > 0 else 1.0
    
    status = "✓" if eta <= 1.4 else "✗"
    print(f"{floor:<6}{d_max:<12.4f}{d_avg:<12.4f}{eta:<8.3f}{status:<10}")
    
    if eta > max_eta:
        max_eta = eta
        critical_floor = floor

print("-" * 48)
print(f"Kritik Kat: {critical_floor}")
print(f"Maksimum ηbi = {max_eta:.3f}")

if max_eta <= 1.2:
    result = "YOK ✓"
elif max_eta <= 1.4:
    result = "2024 TEBLİĞ SAĞLANDI ✓"
else:
    result = f"AŞIM: +{(max_eta/1.4-1)*100:.1f}% ✗"
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
print("V11 SONUÇ")
print("=" * 80)
status_eta = '✓' if max_eta <= 1.4 else '✗'
print(f"""
┌────────────────────────────────────────────┐
│            V11 MODEL SONUÇLARI             │
├────────────────────────────────────────────┤
│ Ağırlık   : {v11_weight:.4f} kg {'✓' if v11_weight <= 1.4 else '✗'}               │
│ T1        : {T1:.4f} s                    │
│ A1a ηbi   : {max_eta:.3f} (< 1.4) {status_eta}            │
│ Drift     : {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}             │
└────────────────────────────────────────────┘
""")

results = pd.DataFrame({
    'Parametre': ['Model', 'Eleman', 'Ağırlık', 'T1', 'ηbi_max', 'δ/h_max', 'Kritik_Kat'],
    'Değer': ['V11', len(conn_v11), f'{v11_weight:.4f}', f'{T1:.4f}', 
              f'{max_eta:.3f}', f'{max_drift:.6f}', str(critical_floor)]
})
os.makedirs('results/data', exist_ok=True)
results.to_csv('results/data/structural_design_check_v11.csv', index=False)

print("V11 ANALİZ TAMAMLANDI")
