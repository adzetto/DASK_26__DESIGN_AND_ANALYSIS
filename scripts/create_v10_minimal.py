"""
V10 Minimal Model - Sadece A1a Burulma Düzeltmesi
=================================================
V9 temel alınarak, sadece Kat 0-1 arası köşe çaprazları eklenir.
Ağırlık limiti: 1.4 kg

Sorun: V9'da kat 1'de ηbi = 1.455 > 1.4
Çözüm: 4 köşeye X-bracing ekle (toplam 8 çapraz eleman)
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import math
import os

print("=" * 80)
print("V10 MİNİMAL MODEL - A1a BURULMA DÜZELTMESİ")
print("=" * 80)

# V9 verilerini oku
pos_v9 = pd.read_csv('data/twin_position_matrix_v9.csv')
conn_v9 = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

print(f"\nV9 Eleman Sayısı: {len(conn_v9)}")
print(f"V9 Toplam Uzunluk: {conn_v9['length'].sum():.1f} cm")

# V9 ağırlık
section_area = 0.6 * 0.6  # cm²
density = 160 / 1e6  # kg/cm³
v9_weight = conn_v9['length'].sum() * section_area * density
print(f"V9 Ağırlık: {v9_weight:.4f} kg")

# Ağırlık bütçesi
weight_limit = 1.400
available_weight = weight_limit - v9_weight
available_length = available_weight / (section_area * density)
print(f"Kalan ağırlık bütçesi: {available_weight:.4f} kg ({available_length:.1f} cm eleman)")

# ============================================================================
# V10: KÖŞE ÇAPRAZLARI EKLEME
# ============================================================================
print("\n" + "=" * 80)
print("V10 KÖŞE ÇAPRAZLARI")
print("=" * 80)

# V9 düğüm yapısını analiz et
print("\nKat 0 köşe düğümleri (z=0):")
floor0_nodes = pos_v9[pos_v9['floor'] == 0]
print(floor0_nodes[['node_id', 'x', 'y', 'z', 'tower']].head(32).to_string())

print("\nKat 1 düğümleri (z>0, min z):")
floor1_nodes = pos_v9[pos_v9['floor'] == 1]
print(floor1_nodes[['node_id', 'x', 'y', 'z', 'tower']].head(32).to_string())

# Tower 1 köşe düğümleri bul
# Tower sütunu 1,2 veya 'tower1','tower2' olabilir
t1_f0 = floor0_nodes[(floor0_nodes['tower'] == 1) | (floor0_nodes['tower'] == '1')]
t1_f1 = floor1_nodes[(floor1_nodes['tower'] == 1) | (floor1_nodes['tower'] == '1')]

# Eğer boşsa, alternatif olarak ilk 32 düğümü al (Tower 1)
if len(t1_f0) == 0:
    t1_f0 = floor0_nodes.iloc[:32]
    t1_f1 = floor1_nodes.iloc[:32]

# Min/max x,y koordinatları
x_min = t1_f0['x'].min()
x_max = t1_f0['x'].max()
y_min = t1_f0['y'].min()
y_max = t1_f0['y'].max()

print(f"\nTower 1 koordinat aralığı: x=[{x_min}, {x_max}], y=[{y_min}, {y_max}]")

# Köşe düğümleri
# Floor 0
corner_f0_bl = t1_f0[(t1_f0['x'] == x_min) & (t1_f0['y'] == y_min)]['node_id'].values[0]  # Bottom-left
corner_f0_br = t1_f0[(t1_f0['x'] == x_max) & (t1_f0['y'] == y_min)]['node_id'].values[0]  # Bottom-right
corner_f0_tl = t1_f0[(t1_f0['x'] == x_min) & (t1_f0['y'] == y_max)]['node_id'].values[0]  # Top-left
corner_f0_tr = t1_f0[(t1_f0['x'] == x_max) & (t1_f0['y'] == y_max)]['node_id'].values[0]  # Top-right

# Floor 1
corner_f1_bl = t1_f1[(t1_f1['x'] == x_min) & (t1_f1['y'] == y_min)]['node_id'].values[0]
corner_f1_br = t1_f1[(t1_f1['x'] == x_max) & (t1_f1['y'] == y_min)]['node_id'].values[0]
corner_f1_tl = t1_f1[(t1_f1['x'] == x_min) & (t1_f1['y'] == y_max)]['node_id'].values[0]
corner_f1_tr = t1_f1[(t1_f1['x'] == x_max) & (t1_f1['y'] == y_max)]['node_id'].values[0]

print(f"\nTower 1 Köşe Düğümleri:")
print(f"  Floor 0: BL={corner_f0_bl}, BR={corner_f0_br}, TL={corner_f0_tl}, TR={corner_f0_tr}")
print(f"  Floor 1: BL={corner_f1_bl}, BR={corner_f1_br}, TL={corner_f1_tl}, TR={corner_f1_tr}")

# Tower 2 offset hesapla
tower2_offset = 840  # Tower 2 = Tower 1 + 840

# Yeni çaprazlar
new_elements = []
next_elem_id = conn_v9['element_id'].max() + 1

def add_diagonal(n1, n2, elem_type):
    global next_elem_id
    p1 = pos_v9[pos_v9['node_id'] == n1].iloc[0]
    p2 = pos_v9[pos_v9['node_id'] == n2].iloc[0]
    length = math.sqrt((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2 + (p2['z']-p1['z'])**2)
    
    elem = {
        'element_id': next_elem_id,
        'node_i': n1,
        'node_j': n2,
        'element_type': elem_type,
        'tower': 'tower1' if n1 < tower2_offset else 'tower2',
        'connection': 'rigid',  # Rigid bağlantı burulma direnci için
        'length': round(length, 4)
    }
    next_elem_id += 1
    return elem

# Tower 1 - Köşelere X-bracing (YZ düzlemi)
# Sol kenar (x=0)
new_elements.append(add_diagonal(corner_f0_bl, corner_f1_tl, 'corner_brace_yz'))  # 0→35
new_elements.append(add_diagonal(corner_f0_tl, corner_f1_bl, 'corner_brace_yz'))  # 3→32

# Sağ kenar (x=30)
new_elements.append(add_diagonal(corner_f0_br, corner_f1_tr, 'corner_brace_yz'))  # 28→63
new_elements.append(add_diagonal(corner_f0_tr, corner_f1_br, 'corner_brace_yz'))  # 31→60

# Tower 2 - Aynı pattern
t2_f0 = floor0_nodes[(floor0_nodes['tower'] == 2) | (floor0_nodes['tower'] == '2')]
t2_f1 = floor1_nodes[(floor1_nodes['tower'] == 2) | (floor1_nodes['tower'] == '2')]

# Eğer boşsa, alternatif olarak düğüm indekslerini kullan (Tower 2 = düğümler 840+)
if len(t2_f0) == 0:
    t2_f0 = floor0_nodes[floor0_nodes['node_id'] >= 840].head(32)
    t2_f1 = floor1_nodes[floor1_nodes['node_id'] >= 840 + 32].head(32)

if len(t2_f0) > 0:
    corner_f0_bl_t2 = t2_f0[(t2_f0['x'] == x_min) & (t2_f0['y'] == t2_f0['y'].min())]['node_id'].values[0]
    corner_f0_br_t2 = t2_f0[(t2_f0['x'] == x_max) & (t2_f0['y'] == t2_f0['y'].min())]['node_id'].values[0]
    corner_f0_tl_t2 = t2_f0[(t2_f0['x'] == x_min) & (t2_f0['y'] == t2_f0['y'].max())]['node_id'].values[0]
    corner_f0_tr_t2 = t2_f0[(t2_f0['x'] == x_max) & (t2_f0['y'] == t2_f0['y'].max())]['node_id'].values[0]
    
    corner_f1_bl_t2 = t2_f1[(t2_f1['x'] == x_min) & (t2_f1['y'] == t2_f1['y'].min())]['node_id'].values[0]
    corner_f1_br_t2 = t2_f1[(t2_f1['x'] == x_max) & (t2_f1['y'] == t2_f1['y'].min())]['node_id'].values[0]
    corner_f1_tl_t2 = t2_f1[(t2_f1['x'] == x_min) & (t2_f1['y'] == t2_f1['y'].max())]['node_id'].values[0]
    corner_f1_tr_t2 = t2_f1[(t2_f1['x'] == x_max) & (t2_f1['y'] == t2_f1['y'].max())]['node_id'].values[0]
    
    new_elements.append(add_diagonal(corner_f0_bl_t2, corner_f1_tl_t2, 'corner_brace_yz'))
    new_elements.append(add_diagonal(corner_f0_tl_t2, corner_f1_bl_t2, 'corner_brace_yz'))
    new_elements.append(add_diagonal(corner_f0_br_t2, corner_f1_tr_t2, 'corner_brace_yz'))
    new_elements.append(add_diagonal(corner_f0_tr_t2, corner_f1_br_t2, 'corner_brace_yz'))

# Eklenen uzunluk
added_length = sum(e['length'] for e in new_elements)
added_weight = added_length * section_area * density

print(f"\nEklenen çapraz sayısı: {len(new_elements)}")
print(f"Eklenen toplam uzunluk: {added_length:.1f} cm")
print(f"Eklenen ağırlık: {added_weight:.4f} kg")

# V10 bağlantı matrisini oluştur
conn_v10 = pd.concat([conn_v9, pd.DataFrame(new_elements)], ignore_index=True)
v10_weight = v9_weight + added_weight

print(f"\nV10 Eleman Sayısı: {len(conn_v10)}")
print(f"V10 Toplam Ağırlık: {v10_weight:.4f} kg")

if v10_weight > 1.4:
    print("⚠ UYARI: Ağırlık limiti aşıldı!")
else:
    print("✓ Ağırlık limiti içinde")

# V10 dosyalarını kaydet
pos_v9.to_csv('data/twin_position_matrix_v10.csv', index=False)
conn_v10.to_csv('data/twin_connectivity_matrix_v10.csv', index=False)
print("\nV10 dosyaları kaydedildi.")

# ============================================================================
# OPENSEES ANALİZİ
# ============================================================================
print("\n" + "=" * 80)
print("OPENSEES ANALİZİ")
print("=" * 80)

E = 170.0  # kN/cm²
G = 65.38  # kN/cm²
rho = 160 / 1e6  # kg/cm³

b = 0.6
h = 0.6
A = b * h
Iy = b * h**3 / 12
Iz = h * b**3 / 12
J = 0.141 * b * h**3

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Düğümler
for _, row in pos_v9.iterrows():
    ops.node(int(row['node_id']), row['x'], row['y'], row['z'])

# Mesnetler
base_nodes = pos_v9[pos_v9['z'] == 0]['node_id'].values
for node in base_nodes:
    ops.fix(int(node), 1, 1, 1, 1, 1, 1)

# Transformasyonlar
ops.geomTransf('PDelta', 1, 0, 1, 0)  # Kolonlar
ops.geomTransf('Linear', 2, 0, 0, 1)  # Kirişler
ops.geomTransf('Corotational', 3, 1, 0, 0)  # Çaprazlar

# Elemanlar
elem_count = 0
for _, row in conn_v10.iterrows():
    elem_id = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])
    elem_type = str(row['element_type'])
    
    # Vektör yönü belirle
    pi = pos_v9[pos_v9['node_id'] == ni].iloc[0]
    pj = pos_v9[pos_v9['node_id'] == nj].iloc[0]
    
    dx = pj['x'] - pi['x']
    dy = pj['y'] - pi['y']
    dz = pj['z'] - pi['z']
    
    # Transformation seç
    if 'column' in elem_type:
        transf = 1
    elif 'beam' in elem_type:
        transf = 2
    elif abs(dz) > 0.1:  # Düşey bileşeni var
        if abs(dx) > abs(dy):
            transf = 1  # XZ düzlemi
        else:
            transf = 2  # YZ düzlemi
    else:
        transf = 3
    
    try:
        ops.element('elasticBeamColumn', elem_id, ni, nj, A, E, G, J, Iy, Iz, transf)
        elem_count += 1
    except Exception as e:
        pass

print(f"Oluşturulan eleman: {elem_count}")

# Kütle ataması
g = 981.0
floors = sorted(pos_v9['floor'].unique())
floor_masses = {}

for floor in floors:
    floor_nodes = pos_v9[pos_v9['floor'] == floor]['node_id'].values
    floor_weight = 0
    
    for _, row in conn_v10.iterrows():
        ni = int(row['node_i'])
        nj = int(row['node_j'])
        fi = pos_v9[pos_v9['node_id'] == ni]['floor'].values[0]
        fj = pos_v9[pos_v9['node_id'] == nj]['floor'].values[0]
        
        if fi == floor or fj == floor:
            floor_weight += row['length'] * A * rho * 0.5
    
    floor_masses[floor] = floor_weight
    
    if len(floor_nodes) > 0:
        mass_per_node = floor_weight / len(floor_nodes) / g
        for node in floor_nodes:
            try:
                ops.mass(int(node), mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
            except:
                pass

total_mass = sum(floor_masses.values())
print(f"Toplam kütle: {total_mass:.4f} kg")

# Modal analiz
num_modes = 12
eigenvalues = ops.eigen(num_modes)

# TBDY parametreleri
SS = 0.877
S1 = 0.243
FS = 1.149
F1 = 2.114
SDS = SS * FS
SD1 = S1 * F1
TA = 0.2 * SD1 / SDS
TB = SD1 / SDS

def get_Sae(T):
    if T < TA:
        return (0.4 + 0.6 * T / TA) * SDS
    elif T <= TB:
        return SDS
    else:
        return SD1 / T

print(f"\n{'Mod':<6}{'T(s)':<12}{'f(Hz)':<12}{'Sae(g)':<12}")
print("-" * 40)

periods = []
for i, ev in enumerate(eigenvalues):
    omega = np.sqrt(ev)
    T = 2 * np.pi / omega
    f = 1 / T
    Sae = get_Sae(T)
    periods.append(T)
    print(f"{i+1:<6}{T:<12.4f}{f:<12.2f}{Sae:<12.3f}")

T1 = periods[0]
print(f"\nTemel Periyot: T1 = {T1:.4f} s")

# Prototip periyodu
scale = 50
T1_proto = T1 * np.sqrt(scale)
print(f"Prototip Periyodu: {T1_proto:.3f} s")

# ============================================================================
# BURULMA ANALİZİ
# ============================================================================
print("\n" + "=" * 80)
print("A1a BURULMA ANALİZİ")
print("=" * 80)

# Lateral yük uygula
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

W_total = total_mass * g / 1000
Vte = get_Sae(T1) * W_total

for floor in floors[1:]:
    floor_nodes = pos_v9[pos_v9['floor'] == floor]['node_id'].values
    z = pos_v9[pos_v9['floor'] == floor]['z'].values[0]
    
    Fi = Vte * (z / 153.0) / len(floors)
    force_per_node = Fi / len(floor_nodes)
    
    for node in floor_nodes:
        try:
            ops.load(int(node), force_per_node, 0, 0, 0, 0, 0)
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
print(f"\n{'Kat':<6}{'δmax(mm)':<12}{'δmin(mm)':<12}{'δort(mm)':<12}{'ηbi':<8}")
print("-" * 50)

max_eta = 0
for floor in [1, 6, 11, 16, 21]:
    floor_nodes = pos_v9[pos_v9['floor'] == floor]['node_id'].values
    
    displacements = []
    for node in floor_nodes:
        try:
            ux = ops.nodeDisp(int(node), 1)
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
    print("SONUÇ: A1a 2024 Tebliğ limiti SAĞLANDI (1.2 < ηbi ≤ 1.4) ✓")
else:
    print("SONUÇ: A1a Burulma düzensizliği MEVCUT ✗")

# Göreli kat ötelemesi
print("\n" + "=" * 80)
print("GÖRELİ KAT ÖTELEMESİ")
print("=" * 80)

print(f"\n{'Kat':<6}{'δi(mm)':<12}{'δi/hi':<12}{'TBDY':<8}")
print("-" * 40)

max_drift = 0
prev_disp = 0
for floor in [5, 10, 15, 20, 25]:
    floor_nodes = pos_v9[pos_v9['floor'] == floor]['node_id'].values
    
    total_disp = 0
    for node in floor_nodes:
        try:
            ux = abs(ops.nodeDisp(int(node), 1))
            total_disp += ux
        except:
            pass
    
    avg_disp = total_disp / len(floor_nodes) if len(floor_nodes) > 0 else 0
    
    hi = 6.0
    delta_i = (avg_disp - prev_disp) * 10
    drift = abs(delta_i) / (hi * 10)
    
    if drift > max_drift:
        max_drift = drift
    
    status = "✓" if drift <= 0.008 else "✗"
    print(f"{floor:<6}{delta_i:<12.4f}{drift:<12.6f}{status:<8}")
    prev_disp = avg_disp

print("-" * 40)
print(f"Maksimum δi/hi = {max_drift:.6f}")

if max_drift <= 0.008:
    print("SONUÇ: Göreli kat ötelemesi SAĞLANDI ✓")
else:
    print("SONUÇ: Göreli kat ötelemesi AŞILDI ✗")

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
│ Toplam Ağırlık   : {v10_weight:.4f} kg {'✓' if v10_weight <= 1.4 else '✗'}                   │
│ Temel Periyot    : {T1:.4f} s                       │
│ Prototip Periyot : {T1_proto:.3f} s                        │
├────────────────────────────────────────────────────┤
│ A1a Burulma      : ηbi = {max_eta:.3f} {'✓' if max_eta <= 1.4 else '✗'}                  │
│ Drift            : δ/h = {max_drift:.6f} {'✓' if max_drift <= 0.008 else '✗'}           │
│ Ağırlık          : {v10_weight:.4f} kg {'✓' if v10_weight <= 1.4 else '✗'}                   │
└────────────────────────────────────────────────────┘
""")

# Sonuçları kaydet
results = {
    'Parametre': ['Model', 'Eleman Sayısı', 'Ağırlık (kg)', 'T1 (s)', 
                  'T1_proto (s)', 'ηbi_max', 'δ/h_max'],
    'Değer': ['V10', len(conn_v10), round(v10_weight, 4), round(T1, 4),
              round(T1_proto, 3), round(max_eta, 3), f'{max_drift:.6f}']
}
os.makedirs('results/data', exist_ok=True)
pd.DataFrame(results).to_csv('results/data/structural_design_check_v10.csv', index=False)

print("=" * 80)
print("V10 MİNİMAL ANALİZ TAMAMLANDI")
print("=" * 80)
