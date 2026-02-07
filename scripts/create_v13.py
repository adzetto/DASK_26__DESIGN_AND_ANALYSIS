"""
V13 Model - Rijit Diyafram Güçlendirmesi
========================================
Hedef: ηbi < 1.4 (2024 Tebliği)
Strateji: Kat 1'de XY düzlem çaprazları ile rijit diyafram
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os

print("=" * 80)
print("V13 MODEL - RİJİT DİYAFRAM GÜÇLENDİRMESİ")
print("=" * 80)

pos = pd.read_csv('data/twin_position_matrix_v9.csv')
conn = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

node_coords = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in pos.iterrows()}

# Ağırlık
b_section = 0.6
A_section = b_section ** 2
density_kg_cm3 = 160 / 1e6

v9_weight = conn['length'].sum() * A_section * density_kg_cm3
available_length = (1.4 - v9_weight) / (A_section * density_kg_cm3)

print(f"V9 Ağırlık: {v9_weight:.4f} kg")
print(f"Kalan bütçe: {available_length:.1f} cm")

def calc_length(n1, n2):
    x1, y1, z1 = node_coords[n1]
    x2, y2, z2 = node_coords[n2]
    return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

next_elem_id = conn['element_id'].max() + 1
new_elements = []
total_added = 0

def add_brace(ni, nj, etype):
    global next_elem_id, total_added
    if ni is None or nj is None:
        return None
    length = calc_length(ni, nj)
    if total_added + length > available_length:
        return None
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
    total_added += length
    return elem

# Kat 1 düğümlerini çek (Tower 1 only, y <= 16)
floor1_t1 = pos[(np.abs(pos['z'] - 9) < 0.5) & (pos['y'] <= 17)]
floor1_nodes = {(row['x'], row['y']): int(row['node_id']) for _, row in floor1_t1.iterrows()}

print("\n--- KAT 1 DİYAFRAM ÇAPRAZLARI (XY Düzlem) ---")

# X ekseni boyunca her grid hücresine çapraz ekle
# Grid: x = [0, 3, 11, 14.4, 15.6, 19, 27, 30]
#       y = [0, 7.4, 8.6, 16]

x_coords = sorted(set([x for x, y in floor1_nodes.keys()]))
y_coords = sorted(set([y for x, y in floor1_nodes.keys()]))

print(f"X koordinatları: {x_coords}")
print(f"Y koordinatları: {y_coords}")

# Her hücreye XY çapraz ekle
for i in range(len(x_coords) - 1):
    for j in range(len(y_coords) - 1):
        x1, x2 = x_coords[i], x_coords[i+1]
        y1, y2 = y_coords[j], y_coords[j+1]
        
        # 4 köşe düğümü
        n_bl = floor1_nodes.get((x1, y1))  # bottom-left
        n_br = floor1_nodes.get((x2, y1))  # bottom-right
        n_tl = floor1_nodes.get((x1, y2))  # top-left
        n_tr = floor1_nodes.get((x2, y2))  # top-right
        
        if n_bl and n_tr:
            e = add_brace(n_bl, n_tr, 'diaphragm')
            if e: 
                new_elements.append(e)
                print(f"  ✓ ({x1:.0f},{y1:.0f})→({x2:.0f},{y2:.0f})")
        
        if n_br and n_tl:
            e = add_brace(n_br, n_tl, 'diaphragm')
            if e: 
                new_elements.append(e)

print(f"\nToplam eklenen eleman: {len(new_elements)}")
print(f"Toplam eklenen uzunluk: {total_added:.1f} cm")

# V13 oluştur
conn_v13 = pd.concat([conn, pd.DataFrame(new_elements)], ignore_index=True)
v13_weight = conn_v13['length'].sum() * A_section * density_kg_cm3
print(f"V13 toplam ağırlık: {v13_weight:.4f} kg {'✓' if v13_weight <= 1.4 else '✗'}")

pos.to_csv('data/twin_position_matrix_v13.csv', index=False)
conn_v13.to_csv('data/twin_connectivity_matrix_v13.csv', index=False)

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

for _, r in conn_v13.iterrows():
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
    f_elems = conn_v13[(conn_v13['node_i'].isin(f_nodes)) | (conn_v13['node_j'].isin(f_nodes))]
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

W = v13_weight * 9.81 / 1000
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
print("V13 SONUÇ")
print("=" * 80)
status_eta = '✓' if max_eta <= 1.4 else '✗'
print(f"""
┌────────────────────────────────────────────┐
│            V13 MODEL SONUÇLARI             │
├────────────────────────────────────────────┤
│ Ağırlık   : {v13_weight:.4f} kg {'✓' if v13_weight <= 1.4 else '✗'}               │
│ T1        : {T1:.4f} s                    │
│ A1a ηbi   : {max_eta:.3f} (< 1.4) {status_eta}            │
│ Drift     : {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}             │
└────────────────────────────────────────────┘
""")

results = pd.DataFrame({
    'Parametre': ['Model', 'Eleman', 'Ağırlık', 'T1', 'ηbi_max', 'δ/h_max', 'Kritik_Kat'],
    'Değer': ['V13', len(conn_v13), f'{v13_weight:.4f}', f'{T1:.4f}', 
              f'{max_eta:.3f}', f'{max_drift:.6f}', str(critical_floor)]
})
results.to_csv('results/data/structural_design_check_v13.csv', index=False)

print("V13 ANALİZ TAMAMLANDI")
