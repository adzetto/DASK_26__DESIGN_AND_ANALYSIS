"""
Eksantirisite Hesabı - TBDY 2018
================================
ex/Lx < 0.5 ve ey/Ly < 0.5 kontrolü
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops

print("=" * 80)
print("EKSANTİRİSİTE HESABI - TBDY 2018")
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

print("\n" + "=" * 80)
print("KAT BAZLI EKSANTİRİSİTE HESABI")
print("=" * 80)

print("""
Tanımlar:
---------
- Kütle Merkezi (CM): Kat kütlesinin ağırlık merkezi
- Rijitlik Merkezi (CR): Kat rijitliğinin merkezi
- Eksantirisite (e): CM ve CR arasındaki mesafe
- ex/Lx ve ey/Ly: Eksantirisite oranları (< 0.5 olmalı)
""")

# Tower 1 plan boyutları
Lx_t1 = 30.0  # x yönü (0 - 30)
Ly_t1 = 16.0  # y yönü (0 - 16)

# Tower 2 plan boyutları  
Lx_t2 = 30.0  # x yönü (0 - 30)
Ly_t2 = 16.0  # y yönü (24 - 40)

print(f"\nPlan Boyutları:")
print(f"  Tower 1: Lx = {Lx_t1} cm, Ly = {Ly_t1} cm")
print(f"  Tower 2: Lx = {Lx_t2} cm, Ly = {Ly_t2} cm")

print(f"\n{'Kat':<6}{'CM_x':<10}{'CM_y':<10}{'CR_x':<10}{'CR_y':<10}{'ex':<8}{'ey':<8}{'ex/Lx':<8}{'ey/Ly':<8}{'Durum':<10}")
print("-" * 88)

max_ex_ratio = 0
max_ey_ratio = 0
critical_floor = 0

for floor in range(1, 26):
    z_f = floor_z.iloc[floor]
    
    # Tower 1 düğümleri (y <= 16)
    floor_t1 = pos[(np.abs(pos['z'] - z_f) < 0.5) & (pos['y'] <= 17)]
    
    if len(floor_t1) == 0:
        continue
    
    # Kütle Merkezi (CM) hesabı
    # Her düğümün kütlesi, bağlı elemanların toplam uzunluğuna orantılı
    node_masses = {}
    for _, row in floor_t1.iterrows():
        nid = int(row['node_id'])
        # Bu düğüme bağlı elemanlar
        node_elems = conn[(conn['node_i'] == nid) | (conn['node_j'] == nid)]
        mass = node_elems['length'].sum() / 2 * A_section * density_kg_cm3
        node_masses[nid] = mass
    
    total_mass = sum(node_masses.values())
    
    cm_x = sum(node_coords[n][0] * m for n, m in node_masses.items()) / total_mass
    cm_y = sum(node_coords[n][1] * m for n, m in node_masses.items()) / total_mass
    
    # Rijitlik Merkezi (CR) hesabı
    # Kolon rijitliklerinin ağırlıklı ortalaması (I/L³ orantılı)
    # Basitleştirilmiş: Tüm kolonlar aynı kesitte, CR ≈ geometrik merkez
    
    # Kolon düğümlerini bul (z yönünde bağlantısı olan)
    column_nodes = []
    for _, row in floor_t1.iterrows():
        nid = int(row['node_id'])
        x, y, z = node_coords[nid]
        
        # Bu düğümün altındaki düğümü bul
        for nid2, (x2, y2, z2) in node_coords.items():
            if abs(x - x2) < 0.5 and abs(y - y2) < 0.5 and abs(z - z2 - 6) < 0.5:
                column_nodes.append((nid, x, y))
                break
    
    if column_nodes:
        # Her kolonun rijitliği 12EI/L³
        # Tüm kolonlar aynı kesitte olduğundan, rijitlik merkezi = kolon konumlarının ortalaması
        cr_x = np.mean([x for _, x, y in column_nodes])
        cr_y = np.mean([y for _, x, y in column_nodes])
    else:
        cr_x, cr_y = cm_x, cm_y
    
    # Eksantirisite
    ex = abs(cm_x - cr_x)
    ey = abs(cm_y - cr_y)
    
    # Oranlar (Tower 1 için)
    ex_ratio = ex / Lx_t1
    ey_ratio = ey / Ly_t1
    
    status = "✓" if ex_ratio < 0.5 and ey_ratio < 0.5 else "✗"
    
    print(f"{floor:<6}{cm_x:<10.2f}{cm_y:<10.2f}{cr_x:<10.2f}{cr_y:<10.2f}{ex:<8.2f}{ey:<8.2f}{ex_ratio:<8.3f}{ey_ratio:<8.3f}{status:<10}")
    
    if ex_ratio > max_ex_ratio:
        max_ex_ratio = ex_ratio
        critical_floor = floor
    if ey_ratio > max_ey_ratio:
        max_ey_ratio = ey_ratio

print("-" * 88)
print(f"\nMaksimum Eksantirisite Oranları:")
print(f"  ex/Lx = {max_ex_ratio:.3f} {'< 0.5 ✓' if max_ex_ratio < 0.5 else '>= 0.5 ✗'}")
print(f"  ey/Ly = {max_ey_ratio:.3f} {'< 0.5 ✓' if max_ey_ratio < 0.5 else '>= 0.5 ✗'}")

print("\n" + "=" * 80)
print("SONUÇ")
print("=" * 80)

if max_ex_ratio < 0.5 and max_ey_ratio < 0.5:
    print(f"""
┌────────────────────────────────────────────────────────┐
│                    SONUÇ                               │
├────────────────────────────────────────────────────────┤
│  Maksimum ex/Lx = {max_ex_ratio:.3f} < 0.5                        │
│  Maksimum ey/Ly = {max_ey_ratio:.3f} < 0.5                        │
│                                                        │
│  EKSANTİRİSİTE KONTROLÜ: SAĞLANDI ✓                   │
└────────────────────────────────────────────────────────┘
""")
else:
    print(f"""
┌────────────────────────────────────────────────────────┐
│                    UYARI                               │
├────────────────────────────────────────────────────────┤
│  Maksimum ex/Lx = {max_ex_ratio:.3f}                              │
│  Maksimum ey/Ly = {max_ey_ratio:.3f}                              │
│                                                        │
│  EKSANTİRİSİTE KONTROLÜ: AŞIM VAR ✗                   │
│  Kritik Kat: {critical_floor}                                      │
└────────────────────────────────────────────────────────┘
""")

# Sonuçları kaydet
results = pd.DataFrame({
    'Parametre': ['ex_max', 'ey_max', 'Lx', 'Ly', 'ex/Lx', 'ey/Ly', 'Kontrol'],
    'Değer': [f'{max_ex_ratio * Lx_t1:.2f}', f'{max_ey_ratio * Ly_t1:.2f}', 
              str(Lx_t1), str(Ly_t1),
              f'{max_ex_ratio:.3f}', f'{max_ey_ratio:.3f}',
              'SAĞLANDI' if max_ex_ratio < 0.5 and max_ey_ratio < 0.5 else 'AŞIM']
})
results.to_csv('results/data/eccentricity_check_v9.csv', index=False)

print("Eksantirisite hesabı tamamlandı.")
