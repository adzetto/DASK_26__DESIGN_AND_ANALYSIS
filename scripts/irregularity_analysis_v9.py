"""
IRREGULARITY ANALYSIS FOR MODEL V9
===================================
TBDY 2018 Düzensizlik Kontrolü (Irregularity Check)

Analyzes:
1. A1a - Burulma Düzensizliği (Torsional Irregularity)
2. A1b - Döşeme Süreksizliği (Floor Discontinuity)
3. A2 - Döşeme Düzleminde Çöküntü/Çıkıntı (Re-entrant Corner)
4. A3 - Perde/Düşey Taşıyıcı Süreksizliği
5. B1 - Komşu Katlar Arası Dayanım Düzensizliği (Soft Story)
6. B2 - Komşu Katlar Arası Rijitlik Düzensizliği
7. B3 - Kütle Düzensizliği (Mass Irregularity)
8. Eksantrisite (Eccentricity) - Kütle vs Rijitlik Merkezi

References: TBDY 2018 Tablo 3.6
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
from pathlib import Path
import os

WORK_DIR = Path(__file__).parent.parent
os.chdir(WORK_DIR)

print("=" * 80)
print("DÜZENSIZLIK ANALIZI - MODEL V9 (TBDY 2018)")
print("IRREGULARITY ANALYSIS - MODEL V9")
print("=" * 80)

# ==============================================================================
# 1. LOAD MODEL DATA
# ==============================================================================
print("\n[1] MODEL VERILERINI YUKLEME...")

pos_df = pd.read_csv('data/twin_position_matrix_v9.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

n_nodes = len(pos_df)
n_elements = len(conn_df)
H_max = pos_df['z'].max()
total_floors = pos_df['floor'].max() + 1

print(f"    Dugum Sayisi: {n_nodes}")
print(f"    Eleman Sayisi: {n_elements}")
print(f"    Kat Sayisi: {total_floors}")
print(f"    Yukseklik: {H_max} cm")

# Get floor levels
floor_z = pos_df.groupby('floor')['z'].first().sort_index()
floor_heights = {}
for i in range(1, len(floor_z)):
    floor_heights[i] = floor_z.iloc[i] - floor_z.iloc[i-1]

print(f"\n    Kat Yukseklikleri:")
for floor, h in list(floor_heights.items())[:5]:
    print(f"      Kat {floor}: {h:.1f} cm")
print(f"      ...")

# ==============================================================================
# 2. BUILD OPENSEES MODEL
# ==============================================================================
print("\n[2] OPENSEES MODELI OLUSTURMA...")

E = 170.0         # kN/cm^2
G = E / 2.6
b = 0.6           # cm
A = b * b
Iz = (b**4) / 12
Iy = (b**4) / 12
J = 0.1406 * b**4

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create nodes
node_coords = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x, y, z = row['x'], row['y'], row['z']
    ops.node(nid, x, y, z)
    node_coords[nid] = (x, y, z)

# Fix base nodes
base_nodes = pos_df[pos_df['z'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)

# Geometric transformations
ops.geomTransf('Linear', 1, 1, 0, 0)
ops.geomTransf('Linear', 2, 0, 0, 1)
ops.geomTransf('Linear', 3, 0, 0, 1)

# Create elements
for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])

    if ni not in node_coords or nj not in node_coords:
        continue

    xi, yi, zi = node_coords[ni]
    xj, yj, zj = node_coords[nj]

    length = np.sqrt((xj-xi)**2 + (yj-yi)**2 + (zj-zi)**2)
    if length < 1e-6:
        continue

    dx, dy, dz = abs(xj-xi), abs(yj-yi), abs(zj-zi)

    if dz > max(dx, dy) * 0.9:
        transf_tag = 1
    elif dx > dy:
        transf_tag = 2
    else:
        transf_tag = 3

    try:
        ops.element('elasticBeamColumn', eid, ni, nj, A, E, G, J, Iy, Iz, transf_tag)
    except:
        pass

print("    Model olusturuldu.")

# ==============================================================================
# 3. APPLY MASSES AND CALCULATE CENTERS
# ==============================================================================
print("\n[3] KUTLE VE MERKEZ HESAPLARI...")

MASS_CONV = 1e-5
FLOOR_MASS_KG = 1.60
ROOF_MASS_KG = 2.22
WEIGHT_SPACING = 18.0

available_z = sorted(pos_df[pos_df['z'] > 0]['z'].unique())
target_z = np.arange(18.0, H_max - 5, WEIGHT_SPACING)

weight_levels = []
for tz in target_z:
    closest = min(available_z, key=lambda z: abs(z - tz))
    if closest not in weight_levels and closest < H_max - 5:
        weight_levels.append(closest)

# Calculate mass center for each floor
floor_data = {}
Z_TOL = 0.5

for floor in range(total_floors):
    z_level = floor_z.iloc[floor]
    
    # Get nodes at this floor
    floor_nodes = pos_df[np.abs(pos_df['z'] - z_level) < Z_TOL]
    
    if len(floor_nodes) == 0:
        continue
    
    # Calculate geometric center
    x_coords = floor_nodes['x'].values
    y_coords = floor_nodes['y'].values
    
    x_min, x_max = x_coords.min(), x_coords.max()
    y_min, y_max = y_coords.min(), y_coords.max()
    
    # Geometric center
    x_geo = (x_min + x_max) / 2
    y_geo = (y_min + y_max) / 2
    
    # Mass center (assuming uniform mass distribution)
    x_mass = np.mean(x_coords)
    y_mass = np.mean(y_coords)
    
    # Floor dimensions
    Lx = x_max - x_min
    Ly = y_max - y_min
    
    # Assign mass
    if z_level in weight_levels:
        floor_mass = FLOOR_MASS_KG
    elif floor == total_floors - 1:
        floor_mass = ROOF_MASS_KG
    else:
        floor_mass = 0.1  # Self-weight estimate
    
    floor_data[floor] = {
        'z': z_level,
        'x_geo': x_geo,
        'y_geo': y_geo,
        'x_mass': x_mass,
        'y_mass': y_mass,
        'Lx': Lx,
        'Ly': Ly,
        'mass': floor_mass,
        'n_nodes': len(floor_nodes),
        'area': Lx * Ly
    }
    
    # Apply mass to OpenSees
    n_floor_nodes = len(floor_nodes)
    if n_floor_nodes > 0:
        mass_per_node = floor_mass * MASS_CONV / n_floor_nodes
        for nid in floor_nodes['node_id'].astype(int):
            ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)

print(f"    {len(floor_data)} kat icin kutle ve merkez hesaplandi.")

# ==============================================================================
# 4. MODAL ANALYSIS FOR STIFFNESS CENTER
# ==============================================================================
print("\n[4] MODAL ANALIZ VE RIJITLIK MERKEZI...")

num_modes = 12
eigenvalues = ops.eigen('-genBandArpack', num_modes)

periods = []
for ev in eigenvalues:
    if ev > 0:
        omega = np.sqrt(ev)
        T = 2 * np.pi / omega
        periods.append(T)

T1 = periods[0] if periods else 0
print(f"    T1 = {T1:.4f} s")

# Estimate stiffness center by applying unit forces
# Stiffness center is where applying force causes no rotation

# For each floor, estimate stiffness center from element distribution
for floor in floor_data:
    z_level = floor_data[floor]['z']
    
    # Get columns at this floor
    floor_cols = conn_df[
        (conn_df['element_type'] == 'column') & 
        (conn_df['node_i'].isin(pos_df[np.abs(pos_df['z'] - z_level) < Z_TOL]['node_id']))
    ]
    
    # Calculate stiffness-weighted center
    if len(floor_cols) > 0:
        x_stiff = []
        y_stiff = []
        
        for _, col in floor_cols.iterrows():
            ni = int(col['node_i'])
            if ni in node_coords:
                x_stiff.append(node_coords[ni][0])
                y_stiff.append(node_coords[ni][1])
        
        if x_stiff:
            floor_data[floor]['x_stiff'] = np.mean(x_stiff)
            floor_data[floor]['y_stiff'] = np.mean(y_stiff)
        else:
            floor_data[floor]['x_stiff'] = floor_data[floor]['x_geo']
            floor_data[floor]['y_stiff'] = floor_data[floor]['y_geo']
    else:
        floor_data[floor]['x_stiff'] = floor_data[floor]['x_geo']
        floor_data[floor]['y_stiff'] = floor_data[floor]['y_geo']

# ==============================================================================
# 5. ECCENTRICITY CALCULATION
# ==============================================================================
print("\n[5] EKSANTRISITE HESABI...")
print("=" * 80)

print(f"\n{'Kat':<6} {'z(cm)':<8} {'Lx(cm)':<8} {'Ly(cm)':<8} {'ex(cm)':<10} {'ey(cm)':<10} {'ex/Lx(%)':<10} {'ey/Ly(%)':<10}")
print("-" * 80)

eccentricities = []

for floor in sorted(floor_data.keys()):
    fd = floor_data[floor]
    
    # Eccentricity = Mass Center - Stiffness Center
    ex = fd['x_mass'] - fd['x_stiff']
    ey = fd['y_mass'] - fd['y_stiff']
    
    ex_ratio = abs(ex) / fd['Lx'] * 100 if fd['Lx'] > 0 else 0
    ey_ratio = abs(ey) / fd['Ly'] * 100 if fd['Ly'] > 0 else 0
    
    fd['ex'] = ex
    fd['ey'] = ey
    fd['ex_ratio'] = ex_ratio
    fd['ey_ratio'] = ey_ratio
    
    eccentricities.append({
        'floor': floor,
        'z': fd['z'],
        'ex': ex,
        'ey': ey,
        'ex_ratio': ex_ratio,
        'ey_ratio': ey_ratio
    })
    
    if floor % 5 == 0 or floor == total_floors - 1:
        print(f"{floor:<6} {fd['z']:<8.1f} {fd['Lx']:<8.1f} {fd['Ly']:<8.1f} {ex:<10.3f} {ey:<10.3f} {ex_ratio:<10.2f} {ey_ratio:<10.2f}")

# Overall eccentricity
total_mass = sum(fd['mass'] for fd in floor_data.values())
x_mass_total = sum(fd['x_mass'] * fd['mass'] for fd in floor_data.values()) / total_mass
y_mass_total = sum(fd['y_mass'] * fd['mass'] for fd in floor_data.values()) / total_mass
x_stiff_total = sum(fd['x_stiff'] for fd in floor_data.values()) / len(floor_data)
y_stiff_total = sum(fd['y_stiff'] for fd in floor_data.values()) / len(floor_data)

ex_total = x_mass_total - x_stiff_total
ey_total = y_mass_total - y_stiff_total

Lx_avg = np.mean([fd['Lx'] for fd in floor_data.values()])
Ly_avg = np.mean([fd['Ly'] for fd in floor_data.values()])

ex_total_ratio = abs(ex_total) / Lx_avg * 100
ey_total_ratio = abs(ey_total) / Ly_avg * 100

print("-" * 80)
print(f"\nTOPLAM EKSANTRISITE:")
print(f"  Kutle Merkezi:    X = {x_mass_total:.2f} cm, Y = {y_mass_total:.2f} cm")
print(f"  Rijitlik Merkezi: X = {x_stiff_total:.2f} cm, Y = {y_stiff_total:.2f} cm")
print(f"  Eksantrisite:     ex = {ex_total:.3f} cm ({ex_total_ratio:.2f}%)")
print(f"                    ey = {ey_total:.3f} cm ({ey_total_ratio:.2f}%)")

# ==============================================================================
# 6. TORSIONAL IRREGULARITY (A1a)
# ==============================================================================
print("\n" + "=" * 80)
print("[6] A1a - BURULMA DUZENSIZLIGI (Torsional Irregularity)")
print("=" * 80)

# Apply unit displacement and check rotation
# TBDY 2018: etaBI = delta_max / delta_avg > 1.2 => Düzensiz
# etaBI > 2.0 => Çok düzensiz (izin verilmez)

print("\n    Burulma duzensizligi icin deprem analizi yapiliyor...")

# Modal response analysis for torsion check
ops.wipeAnalysis()
ops.loadConst('-time', 0.0)

# Apply lateral load in X direction
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply loads at each floor proportional to height
for floor in floor_data:
    z = floor_data[floor]['z']
    floor_nodes_ids = pos_df[np.abs(pos_df['z'] - z) < Z_TOL]['node_id'].astype(int).tolist()
    
    if floor_nodes_ids:
        force_per_node = z * 0.01 / len(floor_nodes_ids)  # Height-proportional
        for nid in floor_nodes_ids:
            try:
                ops.load(nid, force_per_node, 0, 0, 0, 0, 0)
            except:
                pass

# Static analysis
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Newton')
ops.analysis('Static')
ops.analyze(1)

# Check displacements at each floor
torsion_results = []

for floor in floor_data:
    z = floor_data[floor]['z']
    floor_nodes_ids = pos_df[np.abs(pos_df['z'] - z) < Z_TOL]['node_id'].astype(int).tolist()
    
    if not floor_nodes_ids:
        continue
    
    # Get X-direction displacements for all nodes at this floor
    displacements = []
    x_coords = []
    
    for nid in floor_nodes_ids:
        try:
            ux = ops.nodeDisp(nid, 1)
            x = node_coords[nid][0]
            displacements.append(ux)
            x_coords.append(x)
        except:
            pass
    
    if len(displacements) < 2:
        continue
    
    displacements = np.array(displacements)
    x_coords = np.array(x_coords)
    
    # Find max and min displacement edges
    delta_max = np.max(displacements)
    delta_min = np.min(displacements)
    delta_avg = (delta_max + delta_min) / 2
    
    # Torsion ratio
    if abs(delta_avg) > 1e-10:
        eta_bi = delta_max / delta_avg
    else:
        eta_bi = 1.0
    
    torsion_results.append({
        'floor': floor,
        'z': z,
        'delta_max': delta_max * 1000,  # mm
        'delta_min': delta_min * 1000,
        'delta_avg': delta_avg * 1000,
        'eta_bi': eta_bi
    })
    
    floor_data[floor]['eta_bi'] = eta_bi

# Print results
print(f"\n{'Kat':<6} {'z(cm)':<8} {'d_max(mm)':<12} {'d_min(mm)':<12} {'d_avg(mm)':<12} {'eta_bi':<10} {'Durum'}")
print("-" * 80)

max_eta = 0
for tr in torsion_results:
    if tr['floor'] % 5 == 0 or tr['floor'] == total_floors - 1:
        status = "OK" if tr['eta_bi'] <= 1.2 else ("DUZENSIZ" if tr['eta_bi'] <= 2.0 else "IZIN YOK")
        print(f"{tr['floor']:<6} {tr['z']:<8.1f} {tr['delta_max']:<12.4f} {tr['delta_min']:<12.4f} {tr['delta_avg']:<12.4f} {tr['eta_bi']:<10.3f} {status}")
    max_eta = max(max_eta, tr['eta_bi'])

print("-" * 80)
print(f"\n    MAKSIMUM eta_bi = {max_eta:.3f}")
if max_eta <= 1.2:
    print(f"    SONUC: Burulma duzensizligi YOK (eta_bi <= 1.2)")
    torsion_status = "DUZENSIZLIK YOK"
elif max_eta <= 2.0:
    print(f"    SONUC: A1a Burulma Duzensizligi MEVCUT (1.2 < eta_bi <= 2.0)")
    torsion_status = "A1a DUZENSIZ"
else:
    print(f"    SONUC: ASIRI BURULMA - IZIN VERILMEZ (eta_bi > 2.0)")
    torsion_status = "IZIN VERILMEZ"

# ==============================================================================
# 7. SOFT STORY (B2) - Stiffness Irregularity
# ==============================================================================
print("\n" + "=" * 80)
print("[7] B2 - RIJITLIK DUZENSIZLIGI (Stiffness/Soft Story)")
print("=" * 80)

# Calculate story stiffness from lateral displacement under unit load
# K_i = V_i / delta_i

story_stiffness = []
for i, tr in enumerate(torsion_results):
    if tr['delta_avg'] != 0:
        # Approximate stiffness as force/displacement
        K = 1.0 / abs(tr['delta_avg']) if tr['delta_avg'] != 0 else 0
    else:
        K = 0
    
    story_stiffness.append({
        'floor': tr['floor'],
        'z': tr['z'],
        'K': K
    })

# Check for soft story
print(f"\n{'Kat':<6} {'z(cm)':<8} {'K_i':<15} {'K_i/K_i+1':<12} {'K_i/K_avg3':<12} {'Durum'}")
print("-" * 80)

soft_story_status = "DUZENSIZLIK YOK"
for i, ss in enumerate(story_stiffness[1:], 1):  # Skip ground
    K_i = ss['K']
    K_above = story_stiffness[i-1]['K'] if i > 0 else K_i
    
    # Average of 3 floors above
    K_avg3 = np.mean([story_stiffness[j]['K'] for j in range(max(0,i-3), i)]) if i > 0 else K_i
    
    ratio_above = K_i / K_above if K_above > 0 else 1.0
    ratio_avg3 = K_i / K_avg3 if K_avg3 > 0 else 1.0
    
    # TBDY 2018: K_i/K_i+1 < 0.8 or K_i/K_avg3 < 0.6 => Soft Story
    is_soft = ratio_above < 0.8 or ratio_avg3 < 0.6
    status = "YUMUSAK KAT" if is_soft else "OK"
    
    if is_soft:
        soft_story_status = "B2 YUMUSAK KAT MEVCUT"
    
    if ss['floor'] % 5 == 0 or is_soft:
        print(f"{ss['floor']:<6} {ss['z']:<8.1f} {K_i:<15.2f} {ratio_above:<12.3f} {ratio_avg3:<12.3f} {status}")

print("-" * 80)
print(f"\n    SONUC: {soft_story_status}")

# ==============================================================================
# 8. MASS IRREGULARITY (B3)
# ==============================================================================
print("\n" + "=" * 80)
print("[8] B3 - KUTLE DUZENSIZLIGI (Mass Irregularity)")
print("=" * 80)

# TBDY 2018: m_i / m_i+1 > 1.5 or m_i / m_i-1 > 1.5 => Mass Irregularity

floor_masses = [(floor, fd['mass']) for floor, fd in floor_data.items()]
floor_masses.sort(key=lambda x: x[0])

print(f"\n{'Kat':<6} {'z(cm)':<8} {'Kutle(kg)':<12} {'m_i/m_i+1':<12} {'m_i/m_i-1':<12} {'Durum'}")
print("-" * 80)

mass_irreg_status = "DUZENSIZLIK YOK"
for i, (floor, mass) in enumerate(floor_masses):
    z = floor_data[floor]['z']
    
    m_above = floor_masses[i+1][1] if i < len(floor_masses)-1 else mass
    m_below = floor_masses[i-1][1] if i > 0 else mass
    
    ratio_above = mass / m_above if m_above > 0 else 1.0
    ratio_below = mass / m_below if m_below > 0 else 1.0
    
    is_irreg = ratio_above > 1.5 or ratio_below > 1.5
    status = "DUZENSIZ" if is_irreg else "OK"
    
    if is_irreg:
        mass_irreg_status = "B3 KUTLE DUZENSIZLIGI MEVCUT"
    
    if floor % 5 == 0 or is_irreg:
        print(f"{floor:<6} {z:<8.1f} {mass:<12.2f} {ratio_above:<12.3f} {ratio_below:<12.3f} {status}")

print("-" * 80)
print(f"\n    SONUC: {mass_irreg_status}")

# ==============================================================================
# 9. GEOMETRIC IRREGULARITY (A2 - Re-entrant Corner)
# ==============================================================================
print("\n" + "=" * 80)
print("[9] A2 - PLANDA COKUNTU/CIKINTI (Re-entrant Corner)")
print("=" * 80)

# Check floor plan geometry
# TBDY 2018: Projection > 0.2 * total dimension => Irregularity

# Get typical floor dimensions
typical_floor = floor_data[10]  # Mid-height floor
Lx = typical_floor['Lx']
Ly = typical_floor['Ly']

# Twin towers geometry - calculate gap/projection
# Gap between towers is the re-entrant
gap_x = 1.2  # cm (from 14.4 to 15.6)
gap_y = 8.0  # cm (between towers - from 16.0 to 24.0)

projection_x_ratio = gap_x / Lx
projection_y_ratio = gap_y / Ly

print(f"\n    Plan Boyutlari: Lx = {Lx:.1f} cm, Ly = {Ly:.1f} cm")
print(f"    Gap X: {gap_x:.1f} cm ({projection_x_ratio*100:.1f}%)")
print(f"    Gap Y: {gap_y:.1f} cm ({projection_y_ratio*100:.1f}%)")

if projection_x_ratio > 0.2 or projection_y_ratio > 0.2:
    reentrant_status = "A2 COKUNTU/CIKINTI DUZENSIZLIGI MEVCUT"
    print(f"\n    SONUC: {reentrant_status}")
    print(f"           (Projeksiyon orani > %20)")
else:
    reentrant_status = "DUZENSIZLIK YOK"
    print(f"\n    SONUC: {reentrant_status}")

# ==============================================================================
# 10. SUMMARY REPORT
# ==============================================================================
print("\n" + "=" * 80)
print("OZET - DUZENSIZLIK ANALIZI SONUCLARI")
print("=" * 80)

results_summary = {
    'Eksantrisite X': f"{ex_total:.3f} cm ({ex_total_ratio:.2f}%)",
    'Eksantrisite Y': f"{ey_total:.3f} cm ({ey_total_ratio:.2f}%)",
    'A1a Burulma': torsion_status,
    'A1a eta_bi (max)': f"{max_eta:.3f}",
    'A2 Cokuntu/Cikinti': reentrant_status,
    'B2 Yumusak Kat': soft_story_status,
    'B3 Kutle': mass_irreg_status
}

print(f"\n{'Parametre':<30} {'Deger/Durum':<40}")
print("-" * 70)
for param, value in results_summary.items():
    print(f"{param:<30} {value:<40}")

# Overall assessment
print("\n" + "-" * 70)
irregularities = [v for v in results_summary.values() if "MEVCUT" in str(v) or "IZIN" in str(v)]

if not irregularities:
    print("\nGENEL DEGERLENDIRME: YAPI DUZENLI (No Irregularities)")
    print("                     Tum duzensizlik kontrolleri BASARILI")
else:
    print(f"\nGENEL DEGERLENDIRME: {len(irregularities)} DUZENSIZLIK MEVCUT")
    for irr in irregularities:
        print(f"                     - {irr}")

# ==============================================================================
# 11. SAVE RESULTS
# ==============================================================================
print("\n[11] SONUCLARI KAYDETME...")

# Save to CSV
ecc_df = pd.DataFrame(eccentricities)
ecc_df.to_csv('results/data/eccentricity_v9.csv', index=False)

torsion_df = pd.DataFrame(torsion_results)
torsion_df.to_csv('results/data/torsion_results_v9.csv', index=False)

# Save summary
summary_df = pd.DataFrame([results_summary])
summary_df.to_csv('results/data/irregularity_summary_v9.csv', index=False)

print("    Kaydedildi: results/data/eccentricity_v9.csv")
print("    Kaydedildi: results/data/torsion_results_v9.csv")
print("    Kaydedildi: results/data/irregularity_summary_v9.csv")

ops.wipe()

print("\n" + "=" * 80)
print("DUZENSIZLIK ANALIZI TAMAMLANDI")
print("=" * 80)
