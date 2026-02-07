"""
V10 Model - V9 Tabanlı Düzeltilmiş Versiyon
============================================
V9 structural_design_check.py mantığı korunarak,
sadece A1a burulma düzensizliğini azaltmak için
köşe çaprazları eklenir.

Sorun: V9'da Kat 1'de ηbi = 1.455 > 1.4
Çözüm: Her iki kule için 4 köşeye YZ-düzlemi çaprazları
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os

print("=" * 80)
print("V10 MODEL - DÜZELTME ANALİZİ")
print("=" * 80)

# ============================================================================
# VERİ OKUMA
# ============================================================================

pos_df = pd.read_csv('data/twin_position_matrix_v9.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

print(f"\nV9 Düğüm: {len(pos_df)}, Eleman: {len(conn_df)}")

# Node koordinat sözlüğü (V9 mantığı)
node_coords = {}
for _, row in pos_df.iterrows():
    node_coords[int(row['node_id'])] = (row['x'], row['y'], row['z'])

# ============================================================================
# V10 İÇİN YENİ ELEMANLAR
# ============================================================================

total_floors = pos_df['floor'].max() + 1
floor_z = pos_df.groupby('floor')['z'].first().sort_index()

# Kat 0 ve 1 düğümlerini bul
z_floor0 = floor_z.iloc[0]  # z=0
z_floor1 = floor_z.iloc[1]  # z=9

floor0_nodes = pos_df[np.abs(pos_df['z'] - z_floor0) < 0.5]
floor1_nodes = pos_df[np.abs(pos_df['z'] - z_floor1) < 0.5]

print(f"\nKat 0 (z={z_floor0}): {len(floor0_nodes)} düğüm")
print(f"Kat 1 (z={z_floor1}): {len(floor1_nodes)} düğüm")

# Köşe düğümleri (min/max x,y)
# Tower 1: nodes 0-31 (y: 0-16)
# Tower 2: nodes 832-863 (y: 24-40)

# Tower 1 köşeleri - tower sütununu kullan
t1_f0 = floor0_nodes[floor0_nodes['tower'].astype(str) == '1']
t1_f1 = floor1_nodes[floor1_nodes['tower'].astype(str) == '1']

print(f"Tower 1 Kat 0 düğüm sayısı: {len(t1_f0)}")
print(f"Tower 1 Kat 1 düğüm sayısı: {len(t1_f1)}")

x_min = t1_f0['x'].min()
x_max = t1_f0['x'].max()
y_min_t1 = t1_f0['y'].min()  # 0
y_max_t1 = t1_f0['y'].max()  # 16

print(f"\nTower 1 boyutları: x=[{x_min}, {x_max}], y=[{y_min_t1}, {y_max_t1}]")

# Köşe düğümleri bul
def find_corner(df, x, y):
    match = df[(np.abs(df['x'] - x) < 0.1) & (np.abs(df['y'] - y) < 0.1)]
    if len(match) > 0:
        return int(match.iloc[0]['node_id'])
    return None

# Tower 1 Floor 0
c0_bl = find_corner(t1_f0, x_min, y_min_t1)  # 0
c0_br = find_corner(t1_f0, x_max, y_min_t1)  # 28
c0_tl = find_corner(t1_f0, x_min, y_max_t1)  # 3
c0_tr = find_corner(t1_f0, x_max, y_max_t1)  # 31

# Tower 1 Floor 1
c1_bl = find_corner(t1_f1, x_min, y_min_t1)  # 32
c1_br = find_corner(t1_f1, x_max, y_min_t1)  # 60
c1_tl = find_corner(t1_f1, x_min, y_max_t1)  # 35
c1_tr = find_corner(t1_f1, x_max, y_max_t1)  # 63

print(f"Tower 1 köşe düğümleri:")
print(f"  F0: BL={c0_bl}, BR={c0_br}, TL={c0_tl}, TR={c0_tr}")
print(f"  F1: BL={c1_bl}, BR={c1_br}, TL={c1_tl}, TR={c1_tr}")

# V10 için yeni çaprazlar
new_elements = []
next_elem_id = conn_df['element_id'].max() + 1

def calc_length(n1, n2):
    x1, y1, z1 = node_coords[n1]
    x2, y2, z2 = node_coords[n2]
    return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

def add_brace(ni, nj, tower_name):
    global next_elem_id
    length = calc_length(ni, nj)
    elem = {
        'element_id': next_elem_id,
        'node_i': ni,
        'node_j': nj,
        'element_type': 'corner_brace_yz',
        'tower': tower_name,
        'connection': 'rigid',
        'length': round(length, 4)
    }
    next_elem_id += 1
    return elem

# Tower 1 - Sol kenar X-brace (YZ düzlemi, x=0)
new_elements.append(add_brace(c0_bl, c1_tl, 'tower1'))  # 0 → 35 (çapraz yukarı)
new_elements.append(add_brace(c0_tl, c1_bl, 'tower1'))  # 3 → 32 (çapraz aşağı)

# Tower 1 - Sağ kenar X-brace (YZ düzlemi, x=30)
new_elements.append(add_brace(c0_br, c1_tr, 'tower1'))  # 28 → 63
new_elements.append(add_brace(c0_tr, c1_br, 'tower1'))  # 31 → 60

# Tower 2 - Aynı pattern
t2_f0 = floor0_nodes[floor0_nodes['tower'].astype(str) == '2']
t2_f1 = floor1_nodes[floor1_nodes['tower'].astype(str) == '2']

if len(t2_f0) > 0:
    y_min_t2 = t2_f0['y'].min()  # 24
    y_max_t2 = t2_f0['y'].max()  # 40
    
    c0_bl_t2 = find_corner(t2_f0, x_min, y_min_t2)
    c0_br_t2 = find_corner(t2_f0, x_max, y_min_t2)
    c0_tl_t2 = find_corner(t2_f0, x_min, y_max_t2)
    c0_tr_t2 = find_corner(t2_f0, x_max, y_max_t2)
    
    c1_bl_t2 = find_corner(t2_f1, x_min, y_min_t2)
    c1_br_t2 = find_corner(t2_f1, x_max, y_min_t2)
    c1_tl_t2 = find_corner(t2_f1, x_min, y_max_t2)
    c1_tr_t2 = find_corner(t2_f1, x_max, y_max_t2)
    
    print(f"\nTower 2 köşe düğümleri:")
    print(f"  F0: BL={c0_bl_t2}, BR={c0_br_t2}, TL={c0_tl_t2}, TR={c0_tr_t2}")
    print(f"  F1: BL={c1_bl_t2}, BR={c1_br_t2}, TL={c1_tl_t2}, TR={c1_tr_t2}")
    
    if all([c0_bl_t2, c0_br_t2, c0_tl_t2, c0_tr_t2, c1_bl_t2, c1_br_t2, c1_tl_t2, c1_tr_t2]):
        new_elements.append(add_brace(c0_bl_t2, c1_tl_t2, 'tower2'))
        new_elements.append(add_brace(c0_tl_t2, c1_bl_t2, 'tower2'))
        new_elements.append(add_brace(c0_br_t2, c1_tr_t2, 'tower2'))
        new_elements.append(add_brace(c0_tr_t2, c1_br_t2, 'tower2'))

# V10 connectivity oluştur
conn_v10 = pd.concat([conn_df, pd.DataFrame(new_elements)], ignore_index=True)

# Ağırlık hesabı
BALSA_DENSITY = 160  # kg/m³
b_section = 0.6  # cm
A_section = b_section ** 2
density_kg_cm3 = BALSA_DENSITY / 1e6

added_length = sum(e['length'] for e in new_elements)
added_weight = added_length * A_section * density_kg_cm3
total_length = conn_v10['length'].sum()
total_weight = total_length * A_section * density_kg_cm3

print(f"\nEklenen eleman: {len(new_elements)}")
print(f"Eklenen uzunluk: {added_length:.2f} cm")
print(f"Eklenen ağırlık: {added_weight:.4f} kg")
print(f"V10 toplam ağırlık: {total_weight:.4f} kg")

if total_weight > 1.4:
    print("⚠ UYARI: Ağırlık limiti aşıldı!")
else:
    print("✓ Ağırlık limiti içinde")

# V10 dosyalarını kaydet
pos_df.to_csv('data/twin_position_matrix_v10.csv', index=False)
conn_v10.to_csv('data/twin_connectivity_matrix_v10.csv', index=False)
print("\nV10 dosyaları kaydedildi.")

# ============================================================================
# OPENSEES MODELİ (V9 structural_design_check.py MANTIĞI)
# ============================================================================
print("\n" + "=" * 80)
print("OPENSEES MODELİ")
print("=" * 80)

BALSA_E = 170.0  # kN/cm²
BALSA_G = BALSA_E / 2.6
Iz = (b_section**4) / 12
Iy = (b_section**4) / 12
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

print(f"Düğümler: {len(pos_df)}")
print(f"Mesnetler: {len(base_nodes)}")

# Transformasyonlar - V9 ile AYNI
ops.geomTransf('Linear', 1, 1, 0, 0)  # Kolonlar
ops.geomTransf('Linear', 2, 0, 0, 1)  # X-kirişler
ops.geomTransf('Linear', 3, 0, 0, 1)  # Y-kirişler

# Elemanlar - V9 ile AYNI mantık
elem_count = 0
for _, row in conn_v10.iterrows():
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
    
    # V9 transformation mantığı (DOĞRU)
    transf = 1 if dz > max(dx, dy) * 0.9 else (2 if dx > dy else 3)
    
    try:
        ops.element('elasticBeamColumn', eid, ni, nj, A_section, BALSA_E, BALSA_G, J, Iy, Iz, transf)
        elem_count += 1
    except:
        pass

print(f"Elemanlar: {elem_count}")

# Kütle ataması
MASS_CONV = 1e-5  # kg → kN*s²/cm
floor_z_vals = pos_df.groupby('floor')['z'].first().sort_index()

for floor in range(total_floors):
    z_floor = floor_z_vals.iloc[floor]
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    # Kata ait elemanların contributary uzunluğu
    floor_elements = conn_v10[
        (conn_v10['node_i'].isin(floor_node_ids)) | 
        (conn_v10['node_j'].isin(floor_node_ids))
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

total_mass_kg = total_weight
print(f"Toplam kütle: {total_mass_kg:.4f} kg")

# ============================================================================
# MODAL ANALİZ
# ============================================================================
print("\n" + "=" * 80)
print("MODAL ANALİZ")
print("=" * 80)

num_modes = 12
eigenvalues = ops.eigen(num_modes)

# TBDY parametreleri
SS, S1 = 0.877, 0.243
FS, F1 = 1.149, 2.114
SDS = SS * FS
SD1 = S1 * F1
TA = 0.2 * SD1 / SDS
TB = SD1 / SDS

def Sae(T):
    if T <= 0:
        return 0.4 * SDS
    elif T < TA:
        return (0.4 + 0.6 * T / TA) * SDS
    elif T <= TB:
        return SDS
    else:
        return SD1 / T

def spectral_region(T):
    if T < TA:
        return "Yükselen"
    elif T <= TB:
        return "Plato"
    else:
        return "Azalan"

print(f"\n{'Mod':<6}{'T(s)':<12}{'f(Hz)':<12}{'Sae(g)':<12}{'Bölge':<12}")
print("-" * 52)

periods = []
for i, ev in enumerate(eigenvalues):
    omega = np.sqrt(ev)
    T = 2 * np.pi / omega
    f = 1 / T
    periods.append(T)
    print(f"{i+1:<6}{T:<12.4f}{f:<12.2f}{Sae(T):<12.3f}{spectral_region(T):<12}")

T1 = periods[0]
print("-" * 52)
print(f"\nTemel Periyot: T1 = {T1:.4f} s")
print(f"Prototip Periyodu: T1_proto = {T1 * np.sqrt(50):.3f} s")

# ============================================================================
# YATAY YÜK ANALİZİ
# ============================================================================
print("\n" + "=" * 80)
print("YATAY YÜK ANALİZİ")
print("=" * 80)

ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# V9 ile AYNI birim sistemi: g = 9.81 m/s² (SI), W in kN
W_total = total_mass_kg * 9.81 / 1000  # kN (SI birimleri)
Vte = Sae(T1) * W_total

print(f"Toplam ağırlık: {W_total:.6f} kN")
print(f"Sae(T1) = {Sae(T1):.3f} g")
print(f"Elastik taban kesme: Vte = {Vte:.6f} kN")

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

# ============================================================================
# BURULMA DÜZENSİZLİĞİ KONTROLÜ
# ============================================================================
print("\n" + "=" * 80)
print("A1a BURULMA DÜZENSİZLİĞİ KONTROLÜ")
print("=" * 80)

print(f"\n{'Kat':<6}{'δmax(mm)':<12}{'δmin(mm)':<12}{'δort(mm)':<12}{'ηbi':<8}")
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
        d_max = max(displacements) * 10  # mm
        d_min = min(displacements) * 10
        d_avg = np.mean(displacements) * 10
        
        eta = d_max / d_avg if d_avg > 0 else 1.0
        if eta > max_eta:
            max_eta = eta
        
        print(f"{floor:<6}{d_max:<12.4f}{d_min:<12.4f}{d_avg:<12.4f}{eta:<8.3f}")

print("-" * 50)
print(f"Maksimum ηbi = {max_eta:.3f}")

if max_eta <= 1.2:
    torsion_status = "A1a Burulma düzensizliği YOK ✓"
elif max_eta <= 1.4:
    torsion_status = "A1a 2024 Tebliğ SAĞLANDI (ηbi ≤ 1.4) ✓"
else:
    torsion_status = "A1a Burulma düzensizliği MEVCUT ✗"
print(torsion_status)

# ============================================================================
# GÖRELİ KAT ÖTELEMESİ
# ============================================================================
print("\n" + "=" * 80)
print("GÖRELİ KAT ÖTELEMESİ KONTROLÜ")
print("=" * 80)

print(f"\n{'Kat':<6}{'δi(mm)':<12}{'δi/hi':<15}{'TBDY 0.008':<12}")
print("-" * 45)

max_drift = 0
prev_avg_disp = 0
for floor in [5, 10, 15, 20, 25]:
    z_floor = floor_z_vals.iloc[floor]
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    total_disp = 0
    for nid in floor_node_ids:
        try:
            ux = abs(ops.nodeDisp(nid, 1))
            total_disp += ux
        except:
            pass
    
    avg_disp = total_disp / len(floor_node_ids) if len(floor_node_ids) > 0 else 0
    
    hi = 6.0  # cm
    delta_i = (avg_disp - prev_avg_disp) * 10  # mm
    drift = abs(delta_i) / (hi * 10)
    
    if drift > max_drift:
        max_drift = drift
    
    status = "✓" if drift <= 0.008 else "✗"
    print(f"{floor:<6}{delta_i:<12.4f}{drift:<15.6f}{status:<12}")
    prev_avg_disp = avg_disp

print("-" * 45)
print(f"Maksimum δi/hi = {max_drift:.6f}")

if max_drift <= 0.008:
    drift_status = "Göreli kat ötelemesi SAĞLANDI ✓"
else:
    drift_status = "Göreli kat ötelemesi AŞILDI ✗"
print(drift_status)

# ============================================================================
# SONUÇ
# ============================================================================
print("\n" + "=" * 80)
print("V10 SONUÇ ÖZETİ")
print("=" * 80)

print(f"""
┌────────────────────────────────────────────────────┐
│              V10 MODEL SONUÇLARI                   │
├────────────────────────────────────────────────────┤
│ Eleman Sayısı    : {len(conn_v10):<6}                          │
│ Toplam Ağırlık   : {total_weight:.4f} kg {'✓' if total_weight <= 1.4 else '✗'}                   │
│ Temel Periyot    : {T1:.4f} s                       │
│ Spektral Bölge   : {spectral_region(T1):<12}                   │
├────────────────────────────────────────────────────┤
│ A1a Burulma      : ηbi = {max_eta:.3f} {'✓' if max_eta <= 1.4 else '✗'}                  │
│ Drift            : δ/h = {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}           │
└────────────────────────────────────────────────────┘
""")

# Sonuç kaydet
results = pd.DataFrame({
    'Parametre': ['Model', 'Eleman', 'Ağırlık', 'T1', 'ηbi_max', 'δ/h_max'],
    'Değer': ['V10', len(conn_v10), f'{total_weight:.4f}', f'{T1:.4f}', 
              f'{max_eta:.3f}', f'{max_drift:.6f}']
})
os.makedirs('results/data', exist_ok=True)
results.to_csv('results/data/structural_design_check_v10.csv', index=False)

print("=" * 80)
print("V10 ANALİZ TAMAMLANDI")
print("=" * 80)
