"""
V10b Model - A1a Burulma İyileştirmesi
======================================
V10'da ηbi = 1.453 > 1.4 (2024 Tebliğ limiti)
Ek XZ düzlemi çaprazları ile burulma direncini artırıyoruz.

Kalan ağırlık bütçesi: 0.0056 kg (~5 eleman)
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os

print("=" * 80)
print("V10b MODEL - A1a BURULMA İYİLEŞTİRMESİ")
print("=" * 80)

# V10 verilerini oku
pos_df = pd.read_csv('data/twin_position_matrix_v10.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix_v10.csv')

print(f"\nV10 Eleman: {len(conn_df)}")

# Ağırlık kontrolü
b_section = 0.6
A_section = b_section ** 2
density_kg_cm3 = 160 / 1e6

v10_weight = conn_df['length'].sum() * A_section * density_kg_cm3
available_weight = 1.4 - v10_weight
available_length = available_weight / (A_section * density_kg_cm3)

print(f"V10 Ağırlık: {v10_weight:.4f} kg")
print(f"Kalan bütçe: {available_weight:.4f} kg ({available_length:.1f} cm)")

# Node koordinatları
node_coords = {}
for _, row in pos_df.iterrows():
    node_coords[int(row['node_id'])] = (row['x'], row['y'], row['z'])

# XZ düzlemi çaprazları ekle (ön ve arka kenarlarda)
# Floor 0-1 arası, y=0 ve y=16 (Tower 1) ve y=24, y=40 (Tower 2)

total_floors = pos_df['floor'].max() + 1
floor_z = pos_df.groupby('floor')['z'].first().sort_index()

# Kat düğümleri
floor0 = pos_df[pos_df['floor'] == 0]
floor1 = pos_df[pos_df['floor'] == 1]

# Tower 1 ve 2 ayır
t1_f0 = floor0[floor0['tower'].astype(str) == '1']
t1_f1 = floor1[floor1['tower'].astype(str) == '1']
t2_f0 = floor0[floor0['tower'].astype(str) == '2']
t2_f1 = floor1[floor1['tower'].astype(str) == '2']

def find_node(df, x, y):
    match = df[(np.abs(df['x'] - x) < 0.1) & (np.abs(df['y'] - y) < 0.1)]
    return int(match.iloc[0]['node_id']) if len(match) > 0 else None

def calc_length(n1, n2):
    x1, y1, z1 = node_coords[n1]
    x2, y2, z2 = node_coords[n2]
    return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

# Tower 1 boyutları
x_vals = sorted(t1_f0['x'].unique())
y_min_t1, y_max_t1 = t1_f0['y'].min(), t1_f0['y'].max()

# XZ düzlemi çaprazları (y=0 ve y=16 kenarlarında)
# x=0→x=3 arası çaprazlar (Tower 1)
new_elements = []
next_elem_id = conn_df['element_id'].max() + 1

def add_brace(ni, nj, tower):
    global next_elem_id
    length = calc_length(ni, nj)
    elem = {
        'element_id': next_elem_id,
        'node_i': ni,
        'node_j': nj,
        'element_type': 'xz_brace',
        'tower': tower,
        'connection': 'rigid',
        'length': round(length, 4)
    }
    next_elem_id += 1
    return elem

# Tower 1: ön kenar (y=0) XZ çaprazları
# (0,0,0) → (3,0,9) ve (3,0,0) → (0,0,9)
n_00_0 = find_node(t1_f0, 0, y_min_t1)  # 0
n_30_0 = find_node(t1_f0, 3, y_min_t1)  # 4
n_00_9 = find_node(t1_f1, 0, y_min_t1)  # 32
n_30_9 = find_node(t1_f1, 3, y_min_t1)  # 36

# Tower 1: arka kenar (y=16) XZ çaprazları
n_016_0 = find_node(t1_f0, 0, y_max_t1)  # 3
n_316_0 = find_node(t1_f0, 3, y_max_t1)  # 7
n_016_9 = find_node(t1_f1, 0, y_max_t1)  # 35
n_316_9 = find_node(t1_f1, 3, y_max_t1)  # 39

total_added_length = 0

# Sadece bütçe yettiği kadar ekle
if n_00_0 and n_30_9 and total_added_length + 9.5 < available_length:
    new_elements.append(add_brace(n_00_0, n_30_9, 'tower1'))
    total_added_length += 9.5

if n_30_0 and n_00_9 and total_added_length + 9.5 < available_length:
    new_elements.append(add_brace(n_30_0, n_00_9, 'tower1'))
    total_added_length += 9.5

# Sağ köşe (x=27-30)
n_270_0 = find_node(t1_f0, 27, y_min_t1)  # 24
n_300_0 = find_node(t1_f0, 30, y_min_t1)  # 28
n_270_9 = find_node(t1_f1, 27, y_min_t1)  # 56
n_300_9 = find_node(t1_f1, 30, y_min_t1)  # 60

if n_270_0 and n_300_9 and total_added_length + 9.5 < available_length:
    new_elements.append(add_brace(n_270_0, n_300_9, 'tower1'))
    total_added_length += 9.5

if n_300_0 and n_270_9 and total_added_length + 9.5 < available_length:
    new_elements.append(add_brace(n_300_0, n_270_9, 'tower1'))
    total_added_length += 9.5

# Tower 2 için de aynısını yap
y_min_t2, y_max_t2 = t2_f0['y'].min(), t2_f0['y'].max()

n2_00_0 = find_node(t2_f0, 0, y_min_t2)
n2_30_0 = find_node(t2_f0, 3, y_min_t2)
n2_00_9 = find_node(t2_f1, 0, y_min_t2)
n2_30_9 = find_node(t2_f1, 3, y_min_t2)

if n2_00_0 and n2_30_9 and total_added_length + 9.5 < available_length:
    new_elements.append(add_brace(n2_00_0, n2_30_9, 'tower2'))
    total_added_length += 9.5

print(f"\nEklenen çapraz: {len(new_elements)}")
print(f"Eklenen uzunluk: {total_added_length:.1f} cm")

# V10b oluştur
conn_v10b = pd.concat([conn_df, pd.DataFrame(new_elements)], ignore_index=True)
v10b_weight = conn_v10b['length'].sum() * A_section * density_kg_cm3

print(f"V10b toplam ağırlık: {v10b_weight:.4f} kg")
if v10b_weight > 1.4:
    print("⚠ Ağırlık limiti aşıldı!")
else:
    print("✓ Ağırlık uygun")

# Kaydet
pos_df.to_csv('data/twin_position_matrix_v10b.csv', index=False)
conn_v10b.to_csv('data/twin_connectivity_matrix_v10b.csv', index=False)

# ============================================================================
# OPENSEES ANALİZİ
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

# Düğümler
for nid, (x, y, z) in node_coords.items():
    ops.node(nid, x, y, z)

# Mesnetler
base_nodes = pos_df[pos_df['z'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)

# Transformasyonlar
ops.geomTransf('Linear', 1, 1, 0, 0)
ops.geomTransf('Linear', 2, 0, 0, 1)
ops.geomTransf('Linear', 3, 0, 0, 1)

# Elemanlar
elem_count = 0
for _, row in conn_v10b.iterrows():
    eid = int(row['element_id'])
    ni, nj = int(row['node_i']), int(row['node_j'])
    
    if ni not in node_coords or nj not in node_coords:
        continue
    
    xi, yi, zi = node_coords[ni]
    xj, yj, zj = node_coords[nj]
    
    length = np.sqrt((xj-xi)**2 + (yj-yi)**2 + (zj-zi)**2)
    if length < 1e-6:
        continue
    
    dx, dy, dz = abs(xj-xi), abs(yj-yi), abs(zj-zi)
    transf = 1 if dz > max(dx, dy) * 0.9 else (2 if dx > dy else 3)
    
    try:
        ops.element('elasticBeamColumn', eid, ni, nj, A_section, BALSA_E, BALSA_G, J, Iy, Iz, transf)
        elem_count += 1
    except:
        pass

print(f"Elemanlar: {elem_count}")

# Kütle ataması
MASS_CONV = 1e-5
floor_z_vals = pos_df.groupby('floor')['z'].first().sort_index()

for floor in range(total_floors):
    z_floor = floor_z_vals.iloc[floor]
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    floor_elements = conn_v10b[
        (conn_v10b['node_i'].isin(floor_node_ids)) | 
        (conn_v10b['node_j'].isin(floor_node_ids))
    ]
    tributary_length = floor_elements['length'].sum() / 2
    floor_mass_kg = tributary_length * A_section * density_kg_cm3
    
    if len(floor_node_ids) > 0 and floor_mass_kg > 0:
        mass_per_node = floor_mass_kg * MASS_CONV / len(floor_node_ids)
        for nid in floor_node_ids:
            try:
                ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
            except:
                pass

# Modal analiz
eigenvalues = ops.eigen(12)

SS, S1, FS, F1 = 0.877, 0.243, 1.149, 2.114
SDS, SD1 = SS * FS, S1 * F1
TA, TB = 0.2 * SD1 / SDS, SD1 / SDS

def Sae(T):
    if T < TA: return (0.4 + 0.6 * T / TA) * SDS
    elif T <= TB: return SDS
    else: return SD1 / T

T1 = 2 * np.pi / np.sqrt(eigenvalues[0])
print(f"Temel Periyot: T1 = {T1:.4f} s")

# Yatay yük
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

W_total = v10b_weight * 9.81 / 1000
Vte = Sae(T1) * W_total
H_max = pos_df['z'].max()

for floor in range(1, total_floors):
    z_floor = floor_z_vals.iloc[floor]
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    Fi = Vte * (z_floor / H_max) / total_floors
    force_per_node = Fi / len(floor_node_ids) if len(floor_node_ids) > 0 else 0
    
    for nid in floor_node_ids:
        try:
            ops.load(nid, force_per_node, 0, 0, 0, 0, 0)
        except:
            pass

ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Newton')
ops.analysis('Static')
ops.analyze(1)

# Burulma kontrolü
print("\n" + "=" * 80)
print("A1a BURULMA KONTROLÜ")
print("=" * 80)

print(f"\n{'Kat':<6}{'δmax':<12}{'δmin':<12}{'δort':<12}{'ηbi':<8}")
print("-" * 50)

max_eta = 0
for floor in [1, 6, 11, 16, 21]:
    z_floor = floor_z_vals.iloc[floor]
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    displacements = []
    for nid in floor_node_ids:
        try:
            ux = ops.nodeDisp(nid, 1)
            displacements.append(abs(ux))
        except:
            pass
    
    if len(displacements) > 0:
        d_max = max(displacements) * 10
        d_min = min(displacements) * 10
        d_avg = np.mean(displacements) * 10
        
        eta = d_max / d_avg if d_avg > 0 else 1.0
        if eta > max_eta:
            max_eta = eta
        
        print(f"{floor:<6}{d_max:<12.4f}{d_min:<12.4f}{d_avg:<12.4f}{eta:<8.3f}")

print("-" * 50)
print(f"Maksimum ηbi = {max_eta:.3f}")

if max_eta <= 1.2:
    print("SONUÇ: A1a Burulma düzensizliği YOK ✓")
elif max_eta <= 1.4:
    print("SONUÇ: A1a 2024 Tebliğ SAĞLANDI ✓")
else:
    print("SONUÇ: A1a Burulma düzensizliği MEVCUT ✗")

# Drift kontrolü
print("\n" + "=" * 80)
print("DRIFT KONTROLÜ")
print("=" * 80)

max_drift = 0
prev_avg = 0
for floor in [5, 10, 15, 20, 25]:
    z_floor = floor_z_vals.iloc[floor]
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    total_disp = sum(abs(ops.nodeDisp(nid, 1)) for nid in floor_node_ids if nid in node_coords)
    avg_disp = total_disp / len(floor_node_ids) if floor_node_ids else 0
    
    delta = (avg_disp - prev_avg) * 10
    drift = abs(delta) / 60
    if drift > max_drift:
        max_drift = drift
    prev_avg = avg_disp

print(f"Maksimum δ/h = {max_drift:.6f}")
print(f"TBDY 2018: {'SAĞLANDI ✓' if max_drift <= 0.008 else 'AŞILDI ✗'}")

# Özet
print("\n" + "=" * 80)
print("V10b SONUÇ")
print("=" * 80)

print(f"""
┌────────────────────────────────────────────────────┐
│              V10b MODEL SONUÇLARI                  │
├────────────────────────────────────────────────────┤
│ Ağırlık        : {v10b_weight:.4f} kg {'✓' if v10b_weight <= 1.4 else '✗'}                    │
│ T1             : {T1:.4f} s                        │
├────────────────────────────────────────────────────┤
│ A1a Burulma    : ηbi = {max_eta:.3f} {'✓' if max_eta <= 1.4 else '✗'}                   │
│ Drift          : δ/h = {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}            │
└────────────────────────────────────────────────────┘
""")

# Kaydet
results = pd.DataFrame({
    'Parametre': ['Model', 'Eleman', 'Ağırlık', 'T1', 'ηbi_max', 'δ/h_max'],
    'Değer': ['V10b', len(conn_v10b), f'{v10b_weight:.4f}', f'{T1:.4f}', 
              f'{max_eta:.3f}', f'{max_drift:.6f}']
})
results.to_csv('results/data/structural_design_check_v10b.csv', index=False)

print("=" * 80)
print("V10b ANALİZ TAMAMLANDI")
print("=" * 80)
