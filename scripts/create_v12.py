"""
V12 Model - Agresif Köşe Güçlendirmesi
======================================
Hedef: ηbi < 1.4 (2024 Tebliği)
Strateji: Tüm köşelerde YZ ve XZ çaprazları
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os

print("=" * 80)
print("V12 MODEL - AGRESİF KÖŞE GÜÇLENDİRMESİ")
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

# Kat 1 düğümlerini analiz et
floor1 = pos[np.abs(pos['z'] - 9) < 0.5]
print(f"\nKat 1 düğüm koordinatları:")
for _, row in floor1.iterrows():
    print(f"  Node {int(row['node_id'])}: x={row['x']:.1f}, y={row['y']:.1f}")

def calc_length(n1, n2):
    x1, y1, z1 = node_coords[n1]
    x2, y2, z2 = node_coords[n2]
    return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

next_elem_id = conn['element_id'].max() + 1
new_elements = []
total_added = 0

def add_brace(ni, nj, etype, tower='1'):
    global next_elem_id, total_added
    if ni is None or nj is None:
        return None
    length = calc_length(ni, nj)
    if total_added + length > available_length:
        print(f"  ⚠ Bütçe aşıldı")
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

# Zemin ve kat 1 düğümlerini eşleştir
floor0 = pos[np.abs(pos['z'] - 0) < 0.5]
floor1 = pos[np.abs(pos['z'] - 9) < 0.5]

print("\n--- ZEMIN-KAT1 DÜĞÜM EŞLEŞTİRME ---")

# X ve Y koordinatlarına göre eşleştir
matches = []
for _, r0 in floor0.iterrows():
    x0, y0 = r0['x'], r0['y']
    for _, r1 in floor1.iterrows():
        x1, y1 = r1['x'], r1['y']
        if abs(x0 - x1) < 0.5 and abs(y0 - y1) < 0.5:
            matches.append((int(r0['node_id']), int(r1['node_id']), x0, y0))

print(f"Eşleşen düğüm çifti: {len(matches)}")

# Köşeler (Tower 1): x=0 veya x=30, y=0 veya y=16
corner_pairs = [(n0, n1, x, y) for n0, n1, x, y in matches 
                if (abs(x) < 0.5 or abs(x-30) < 0.5) and (abs(y) < 0.5 or abs(y-16) < 0.5)]
print(f"Köşe düğüm çifti: {len(corner_pairs)}")

# Köşe çaprazları (YZ düzlem)
print("\n--- YZ KÖŞE ÇAPRAZLARI ---")
for n0, n1, x, y in corner_pairs:
    # Bu köşeden bir sonraki Y düğümüne çapraz
    # y=0 ise y=4.8'e, y=16 ise y=11.2'ye
    y_next = 4.8 if abs(y) < 0.5 else 11.2
    
    # Kat 1'de y_next konumundaki düğüm
    n1_diag = None
    for _, r1 in floor1.iterrows():
        if abs(r1['x'] - x) < 0.5 and abs(r1['y'] - y_next) < 0.5:
            n1_diag = int(r1['node_id'])
            break
    
    if n1_diag:
        e = add_brace(n0, n1_diag, 'corner_yz')
        if e: 
            new_elements.append(e)
            print(f"  ✓ {n0}→{n1_diag} (x={x:.0f}, y={y:.0f}→{y_next:.0f})")

# Ters çaprazlar
print("\n--- YZ TERS ÇAPRAZLAR ---")
for n0, n1, x, y in corner_pairs:
    y_prev = 4.8 if abs(y) < 0.5 else 11.2
    
    # Zemin katta y_prev konumundaki düğüm
    n0_diag = None
    for _, r0 in floor0.iterrows():
        if abs(r0['x'] - x) < 0.5 and abs(r0['y'] - y_prev) < 0.5:
            n0_diag = int(r0['node_id'])
            break
    
    if n0_diag:
        e = add_brace(n0_diag, n1, 'corner_yz_rev')
        if e: 
            new_elements.append(e)
            print(f"  ✓ {n0_diag}→{n1} (x={x:.0f}, y={y_prev:.0f}→{y:.0f})")

# XZ köşe çaprazları
print("\n--- XZ KÖŞE ÇAPRAZLARI ---")
for n0, n1, x, y in corner_pairs:
    # x=0 ise x=3'e, x=30 ise x=27'ye
    x_next = 3.0 if abs(x) < 0.5 else 27.0
    
    n1_diag = None
    for _, r1 in floor1.iterrows():
        if abs(r1['x'] - x_next) < 0.5 and abs(r1['y'] - y) < 0.5:
            n1_diag = int(r1['node_id'])
            break
    
    if n1_diag:
        e = add_brace(n0, n1_diag, 'corner_xz')
        if e: 
            new_elements.append(e)
            print(f"  ✓ {n0}→{n1_diag} (x={x:.0f}→{x_next:.0f}, y={y:.0f})")

# XZ ters çaprazlar
print("\n--- XZ TERS ÇAPRAZLAR ---")
for n0, n1, x, y in corner_pairs:
    x_prev = 3.0 if abs(x) < 0.5 else 27.0
    
    n0_diag = None
    for _, r0 in floor0.iterrows():
        if abs(r0['x'] - x_prev) < 0.5 and abs(r0['y'] - y) < 0.5:
            n0_diag = int(r0['node_id'])
            break
    
    if n0_diag:
        e = add_brace(n0_diag, n1, 'corner_xz_rev')
        if e: 
            new_elements.append(e)
            print(f"  ✓ {n0_diag}→{n1} (x={x_prev:.0f}→{x:.0f}, y={y:.0f})")

print(f"\nToplam eklenen eleman: {len(new_elements)}")
print(f"Toplam eklenen uzunluk: {total_added:.1f} cm")

# V12 oluştur
conn_v12 = pd.concat([conn, pd.DataFrame(new_elements)], ignore_index=True)
v12_weight = conn_v12['length'].sum() * A_section * density_kg_cm3
print(f"V12 toplam ağırlık: {v12_weight:.4f} kg {'✓' if v12_weight <= 1.4 else '✗'}")

pos.to_csv('data/twin_position_matrix_v12.csv', index=False)
conn_v12.to_csv('data/twin_connectivity_matrix_v12.csv', index=False)

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

for _, r in conn_v12.iterrows():
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
    f_elems = conn_v12[(conn_v12['node_i'].isin(f_nodes)) | (conn_v12['node_j'].isin(f_nodes))]
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

W = v12_weight * 9.81 / 1000
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
print("V12 SONUÇ")
print("=" * 80)
status_eta = '✓' if max_eta <= 1.4 else '✗'
print(f"""
┌────────────────────────────────────────────┐
│            V12 MODEL SONUÇLARI             │
├────────────────────────────────────────────┤
│ Ağırlık   : {v12_weight:.4f} kg {'✓' if v12_weight <= 1.4 else '✗'}               │
│ T1        : {T1:.4f} s                    │
│ A1a ηbi   : {max_eta:.3f} (< 1.4) {status_eta}            │
│ Drift     : {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}             │
└────────────────────────────────────────────┘
""")

results = pd.DataFrame({
    'Parametre': ['Model', 'Eleman', 'Ağırlık', 'T1', 'ηbi_max', 'δ/h_max', 'Kritik_Kat'],
    'Değer': ['V12', len(conn_v12), f'{v12_weight:.4f}', f'{T1:.4f}', 
              f'{max_eta:.3f}', f'{max_drift:.6f}', str(critical_floor)]
})
results.to_csv('results/data/structural_design_check_v12.csv', index=False)

print("V12 ANALİZ TAMAMLANDI")
