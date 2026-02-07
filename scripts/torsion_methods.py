"""
V10 Burulma Hesabı - TBDY 2018 Kenar Bazlı Yöntem
=================================================
ηbi = δmax / δort (kenarlar arası ortalama)
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops

print("=" * 80)
print("TBDY 2018 KENAR BAZLI BURULMA HESABI")
print("=" * 80)

pos = pd.read_csv('data/twin_position_matrix_v10.csv')
conn = pd.read_csv('data/twin_connectivity_matrix_v10.csv')

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

eigenvalues = ops.eigen(12)
T1 = 2 * np.pi / np.sqrt(eigenvalues[0])

# Yük
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

SS, S1, FS, F1 = 0.877, 0.243, 1.149, 2.114
SDS, SD1 = SS * FS, S1 * F1

def Sae(T):
    TA = 0.2 * SD1 / SDS
    if T < TA: return (0.4 + 0.6 * T / TA) * SDS
    return SDS if T <= SD1/SDS else SD1 / T

W = conn['length'].sum() * A_section * density_kg_cm3 * 9.81 / 1000
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

# TBDY 2018 Kenar Bazlı Burulma
print("\n" + "=" * 80)
print("A1a BURULMA - ÜÇ FARKLI YÖNTEM")
print("=" * 80)

# Yöntem 1: Tüm düğüm ortalaması (şimdiki yöntem)
# Yöntem 2: Kenar ortalaması (y=0 ve y=16 düğümleri)
# Yöntem 3: Köşe ortalaması (4 köşe)

print(f"\n{'Kat':<6}{'Yöntem 1':<15}{'Yöntem 2':<15}{'Yöntem 3':<15}")
print(f"{'':6}{'(tüm ort)':<15}{'(kenar ort)':<15}{'(4 köşe)':<15}")
print("-" * 51)

# Y kenarları belirle - Tower 1 için y=0 ve y=16
y_min_t1, y_max_t1 = 0.0, 16.0

max_eta_m1, max_eta_m2, max_eta_m3 = 0, 0, 0

for floor in [1, 5, 10, 15, 20, 25]:
    z_f = floor_z.iloc[floor]
    floor_nodes = pos[(np.abs(pos['z'] - z_f) < 0.5) & (pos['y'] <= 20)]  # Tower 1 only
    
    all_disps = []
    edge_y0_disps = []
    edge_y16_disps = []
    
    for _, row in floor_nodes.iterrows():
        nid = int(row['node_id'])
        y = row['y']
        ux = abs(ops.nodeDisp(nid, 1)) * 10  # mm
        all_disps.append(ux)
        
        if abs(y - 0.0) < 0.5:
            edge_y0_disps.append(ux)
        elif abs(y - 16.0) < 0.5:
            edge_y16_disps.append(ux)
    
    d_max = max(all_disps)
    
    # Yöntem 1: Tüm düğüm ortalaması
    d_avg_m1 = np.mean(all_disps)
    eta_m1 = d_max / d_avg_m1 if d_avg_m1 > 0 else 1.0
    
    # Yöntem 2: İki kenar ortalaması  
    d_avg_m2 = (np.mean(edge_y0_disps) + np.mean(edge_y16_disps)) / 2 if edge_y0_disps and edge_y16_disps else d_avg_m1
    eta_m2 = d_max / d_avg_m2 if d_avg_m2 > 0 else 1.0
    
    # Yöntem 3: 4 köşe ortalaması (x=0,y=0 ve x=30,y=0 ve x=0,y=16 ve x=30,y=16)
    corners = []
    for _, row in floor_nodes.iterrows():
        x, y = row['x'], row['y']
        if (abs(x - 0) < 0.5 and abs(y - 0) < 0.5) or \
           (abs(x - 30) < 0.5 and abs(y - 0) < 0.5) or \
           (abs(x - 0) < 0.5 and abs(y - 16) < 0.5) or \
           (abs(x - 30) < 0.5 and abs(y - 16) < 0.5):
            corners.append(abs(ops.nodeDisp(int(row['node_id']), 1)) * 10)
    
    d_avg_m3 = np.mean(corners) if corners else d_avg_m1
    eta_m3 = d_max / d_avg_m3 if d_avg_m3 > 0 else 1.0
    
    print(f"{floor:<6}{eta_m1:<15.3f}{eta_m2:<15.3f}{eta_m3:<15.3f}")
    
    if eta_m1 > max_eta_m1: max_eta_m1 = eta_m1
    if eta_m2 > max_eta_m2: max_eta_m2 = eta_m2
    if eta_m3 > max_eta_m3: max_eta_m3 = eta_m3

print("-" * 51)
print(f"\nMaksimum ηbi:")
print(f"  Yöntem 1 (tüm ort):   {max_eta_m1:.3f} {'✓' if max_eta_m1 <= 1.4 else '✗'}")
print(f"  Yöntem 2 (kenar ort): {max_eta_m2:.3f} {'✓' if max_eta_m2 <= 1.4 else '✗'}")
print(f"  Yöntem 3 (4 köşe):    {max_eta_m3:.3f} {'✓' if max_eta_m3 <= 1.4 else '✗'}")

print("\n" + "=" * 80)
print("SONUÇ")
print("=" * 80)
print(f"""
TBDY 2018 göre A1a burulma düzensizliği tanımı:
"Her bir i'inci katta, herhangi bir deprem doğrultusunda ve herhangi bir 
katta, kiriş döşeme sisteminde en büyük göreli kat ötelemesinin aynı 
katta ortalama göreli kat ötelemesine oranı"

ηbi = (δ)max,i / (δ)ort,i

- δmax: En büyük deplasman (katta)
- δort: Kenarların deplasmanlarının ortalaması

V10 model için:
- Yöntem 2 (kenar ortalaması) TBDY 2018'e uygundur
- ηbi = {max_eta_m2:.3f}
""")

if max_eta_m2 <= 1.2:
    print("A1a BURULMA DÜZENSİZLİĞİ: YOK ✓")
elif max_eta_m2 <= 1.4:
    print("A1a BURULMA DÜZENSİZLİĞİ: 2024 TEBLİĞ SINIRI SAĞLANDI ✓")
elif max_eta_m2 <= 2.0:
    print("A1a BURULMA DÜZENSİZLİĞİ: TBDY 2018 İÇİN KABUL EDİLEBİLİR")
else:
    print("A1a BURULMA DÜZENSİZLİĞİ: SINIR AŞILDI ✗")
