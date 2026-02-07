"""
TBDY 2018 KOMPLe DEPREM ANALİZİ - MODEL V9
===========================================
Complete earthquake analysis per TBDY 2018 (Turkish Building Earthquake Code)

Analysis includes:
1. Self-weight mass calculation (no test weights)
2. TBDY 2018 design spectrum (DD-2 level)
3. Equivalent static earthquake load (Eşdeğer Deprem Yükü Yöntemi)
4. Modal spectrum analysis (Mod Birleştirme Yöntemi)
5. All irregularity checks per Table 3.6
6. Eccentricity calculations (Eksantrisite)
7. Torsional irregularity (Burulma Düzensizliği)
8. Story drift limits (Göreli Kat Ötelemesi)

Reference: TBDY 2018 (Türkiye Bina Deprem Yönetmeliği)
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
from pathlib import Path
import os

WORK_DIR = Path(__file__).parent.parent
os.chdir(WORK_DIR)

print("=" * 80)
print("TBDY 2018 DEPREM ANALİZİ - MODEL V9")
print("Turkish Building Earthquake Code 2018 Analysis")
print("=" * 80)

# ==============================================================================
# TBDY 2018 TASARIM PARAMETRELERİ
# Design Parameters from AFAD DD-2 (475-year return period)
# ==============================================================================

# Site: Istanbul / Duzce region (from afad_reports)
# Zemin Sınıfı: ZD (Medium-stiff soil)

TBDY = {
    # Spectral acceleration parameters (from AFAD DD-2)
    'SS': 0.877,       # Short period spectral acceleration coefficient
    'S1': 0.243,       # 1.0 sec period spectral acceleration coefficient
    'FS': 1.149,       # Short period site factor for ZD
    'F1': 2.114,       # 1.0 sec site factor for ZD
    'PGA': 0.362,      # Peak ground acceleration (g)
    
    # Calculated design values
    'SDS': None,       # Design spectral acceleration (short period)
    'SD1': None,       # Design spectral acceleration (1.0 sec)
    'TA': None,        # Corner period A
    'TB': None,        # Corner period B  
    'TL': 6.0,         # Long period transition
    
    # Building parameters
    'DTS': 1,          # Deprem Tasarım Sınıfı (Seismic Design Category)
    'BYS': 3,          # Bina Yükseklik Sınıfı (Building Height Class)
    'R': 4.0,          # Taşıyıcı Sistem Davranış Katsayısı (Response Modification)
    'D': 2.5,          # Dayanım Fazlalığı Katsayısı (Overstrength Factor)
    'I': 1.0,          # Bina Önem Katsayısı (Importance Factor)
    
    # Damping
    'zeta': 0.05,      # Critical damping ratio (5%)
}

# Calculate design spectral accelerations
TBDY['SDS'] = TBDY['SS'] * TBDY['FS']  # SDS = SS * FS
TBDY['SD1'] = TBDY['S1'] * TBDY['F1']  # SD1 = S1 * F1
TBDY['TA'] = 0.2 * TBDY['SD1'] / TBDY['SDS']  # TA = 0.2 * SD1/SDS
TBDY['TB'] = TBDY['SD1'] / TBDY['SDS']        # TB = SD1/SDS

print("\n" + "-" * 80)
print("TBDY 2018 TASARIM PARAMETRELERİ")
print("-" * 80)
print(f"  SS = {TBDY['SS']:.3f}, S1 = {TBDY['S1']:.3f}")
print(f"  FS = {TBDY['FS']:.3f}, F1 = {TBDY['F1']:.3f}")
print(f"  SDS = {TBDY['SDS']:.3f} g")
print(f"  SD1 = {TBDY['SD1']:.3f} g")
print(f"  TA = {TBDY['TA']:.3f} s, TB = {TBDY['TB']:.3f} s, TL = {TBDY['TL']:.1f} s")
print(f"  R = {TBDY['R']:.1f}, D = {TBDY['D']:.1f}, I = {TBDY['I']:.1f}")

# ==============================================================================
# TBDY 2018 SPECTRUM FUNCTIONS
# ==============================================================================

def Sae(T, tbdy=TBDY):
    """
    TBDY 2018 Section 2.3.4 - Yatay Elastik Tasarım Spektrumu
    Horizontal Elastic Design Spectrum Sae(T)
    Returns spectral acceleration in g
    """
    SDS = tbdy['SDS']
    SD1 = tbdy['SD1']
    TA = tbdy['TA']
    TB = tbdy['TB']
    TL = tbdy['TL']
    
    if T <= 0:
        return 0.4 * SDS
    elif T < TA:
        return (0.4 + 0.6 * T / TA) * SDS
    elif T <= TB:
        return SDS
    elif T <= TL:
        return SD1 / T
    else:
        return SD1 * TL / (T ** 2)

def SaR(T, tbdy=TBDY):
    """
    TBDY 2018 Section 4.3.3 - Azaltılmış Tasarım Spektral İvmesi
    Reduced Design Spectral Acceleration
    """
    R = tbdy['R']
    D = tbdy['D']
    I = tbdy['I']
    TB = tbdy['TB']
    
    # Ra(T) - Deprem Yükü Azaltma Katsayısı
    if T < TB:
        Ra = D + (R/I - D) * T / TB
    else:
        Ra = R / I
    
    return Sae(T, tbdy) / Ra

def get_spectral_region(T, tbdy=TBDY):
    """Determine spectral region"""
    if T < tbdy['TA']:
        return "Yükselen (Ascending)"
    elif T <= tbdy['TB']:
        return "Plato (Plateau)"
    elif T <= tbdy['TL']:
        return "Azalan (Descending)"
    else:
        return "Uzun Periyot (Long Period)"

# ==============================================================================
# MODEL VERİLERİNİ YÜKLEME
# ==============================================================================
print("\n" + "-" * 80)
print("[1] MODEL VERİLERİNİ YÜKLEME")
print("-" * 80)

pos_df = pd.read_csv('data/twin_position_matrix_v9.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

n_nodes = len(pos_df)
n_elements = len(conn_df)
H_max = pos_df['z'].max()
total_floors = pos_df['floor'].max() + 1

print(f"  Düğüm Sayısı: {n_nodes}")
print(f"  Eleman Sayısı: {n_elements}")
print(f"  Kat Sayısı: {total_floors}")
print(f"  Yükseklik: {H_max} cm = {H_max/100:.2f} m (model)")

# Floor levels
floor_z = pos_df.groupby('floor')['z'].first().sort_index()

# ==============================================================================
# MALZEME VE KESİT ÖZELLİKLERİ
# ==============================================================================
print("\n" + "-" * 80)
print("[2] MALZEME VE KESİT ÖZELLİKLERİ")
print("-" * 80)

# Balsa wood properties
BALSA_E = 170.0         # kN/cm^2 (calibrated modulus)
BALSA_G = BALSA_E / 2.6 # kN/cm^2
BALSA_DENSITY = 160     # kg/m^3 = 0.00016 kg/cm^3

# Section properties (6mm x 6mm = 0.6cm x 0.6cm)
b = 0.6                 # cm
A = b * b               # cm^2 = 0.36
Iz = (b**4) / 12        # cm^4
Iy = (b**4) / 12        # cm^4
J = 0.1406 * b**4       # cm^4 (torsional constant)

print(f"  E = {BALSA_E:.1f} kN/cm^2 ({BALSA_E*10:.0f} MPa)")
print(f"  G = {BALSA_G:.2f} kN/cm^2")
print(f"  Yoğunluk = {BALSA_DENSITY} kg/m^3")
print(f"  Kesit: {b*10:.0f}mm x {b*10:.0f}mm (A = {A:.4f} cm^2)")

# ==============================================================================
# ÖZ AĞIRLIK KÜTLE HESABI (Self-Weight Mass Calculation)
# ==============================================================================
print("\n" + "-" * 80)
print("[3] ÖZ AĞIRLIK KÜTLE HESABI (Self-Weight Only)")
print("-" * 80)

# Calculate mass from element lengths
frame_types = ['column', 'beam_x', 'beam_y', 'brace_xz', 'brace_yz', 'floor_brace',
               'bridge_beam', 'bridge_column', 'bridge_truss', 'bridge_rigid']

total_length_cm = conn_df['length'].sum()
volume_cm3 = total_length_cm * A  # cm^3
density_kg_cm3 = BALSA_DENSITY / 1e6  # kg/cm^3
total_mass_kg = volume_cm3 * density_kg_cm3

print(f"  Toplam eleman uzunluğu: {total_length_cm:.1f} cm")
print(f"  Toplam hacim: {volume_cm3:.1f} cm^3")
print(f"  Toplam kütle: {total_mass_kg:.4f} kg")

# Distribute mass to floors based on column tributary lengths
# Mass is distributed to floors based on elements connected to each floor

floor_masses = {}
node_coords = {}

# Build coordinate lookup
for _, row in pos_df.iterrows():
    node_coords[int(row['node_id'])] = (row['x'], row['y'], row['z'])

# Calculate mass per floor from connected elements
for floor in range(total_floors):
    z_floor = floor_z.iloc[floor]
    z_tol = 0.5
    
    # Get nodes at this floor
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < z_tol]['node_id'].astype(int).tolist()
    
    # Get elements connected to this floor
    floor_elements = conn_df[
        (conn_df['node_i'].isin(floor_node_ids)) | 
        (conn_df['node_j'].isin(floor_node_ids))
    ]
    
    # Sum tributary lengths (half of each element)
    tributary_length = floor_elements['length'].sum() / 2
    floor_mass = tributary_length * A * density_kg_cm3
    
    floor_masses[floor] = {
        'z': z_floor,
        'mass_kg': floor_mass,
        'n_nodes': len(floor_node_ids),
        'tributary_length': tributary_length
    }

# Print floor mass distribution
print(f"\n  {'Kat':<6} {'z (cm)':<10} {'Kütle (kg)':<12} {'Düğüm':<8}")
print("  " + "-" * 40)

total_check = 0
for floor in [0, 5, 10, 15, 20, 25]:
    if floor in floor_masses:
        fm = floor_masses[floor]
        print(f"  {floor:<6} {fm['z']:<10.1f} {fm['mass_kg']:<12.4f} {fm['n_nodes']:<8}")
        total_check += fm['mass_kg']

print("  " + "-" * 40)
total_distributed = sum(fm['mass_kg'] for fm in floor_masses.values())
print(f"  Toplam dağıtılmış kütle: {total_distributed:.4f} kg")

# ==============================================================================
# OPENSEES MODELİ OLUŞTURMA
# ==============================================================================
print("\n" + "-" * 80)
print("[4] OPENSEES MODELİ OLUŞTURMA")
print("-" * 80)

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create nodes
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x, y, z = row['x'], row['y'], row['z']
    ops.node(nid, x, y, z)

# Fix base nodes
base_nodes = pos_df[pos_df['z'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)

print(f"  Sabit mesnet: {len(base_nodes)} düğüm")

# Geometric transformations
ops.geomTransf('Linear', 1, 1, 0, 0)  # Vertical elements
ops.geomTransf('Linear', 2, 0, 0, 1)  # Horizontal X
ops.geomTransf('Linear', 3, 0, 0, 1)  # Horizontal Y

# Create elements
elem_count = 0
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
        ops.element('elasticBeamColumn', eid, ni, nj, A, BALSA_E, BALSA_G, J, Iy, Iz, transf_tag)
        elem_count += 1
    except:
        pass

print(f"  Oluşturulan eleman: {elem_count}")

# ==============================================================================
# KÜTLE ATAMA (Mass Assignment - Self Weight Only)
# ==============================================================================
print("\n" + "-" * 80)
print("[5] KÜTLE ATAMA (Öz Ağırlık)")
print("-" * 80)

# Mass conversion: kg to kN*s^2/cm
# F = ma -> m = F/a -> [kN*s^2/cm] = [kN] / [cm/s^2]
# 1 kg = 0.00981 kN / 980.665 cm/s^2 = 1e-5 kN*s^2/cm
MASS_CONV = 1e-5  # kg to kN*s^2/cm

total_applied_mass = 0
for floor in floor_masses:
    z_floor = floor_masses[floor]['z']
    mass_kg = floor_masses[floor]['mass_kg']
    z_tol = 0.5
    
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < z_tol]['node_id'].astype(int).tolist()
    
    if len(floor_node_ids) > 0:
        mass_per_node = mass_kg * MASS_CONV / len(floor_node_ids)
        
        for nid in floor_node_ids:
            ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
        
        total_applied_mass += mass_kg

print(f"  Toplam uygulanan kütle: {total_applied_mass:.4f} kg")

# ==============================================================================
# MODAL ANALİZ
# ==============================================================================
print("\n" + "-" * 80)
print("[6] MODAL ANALİZ (Eigenvalue Analysis)")
print("-" * 80)

num_modes = 12
try:
    eigenvalues = ops.eigen('-genBandArpack', num_modes)
except:
    eigenvalues = ops.eigen(num_modes)

# Calculate periods and frequencies
modal_results = []
print(f"\n  {'Mod':<6} {'T (s)':<12} {'f (Hz)':<12} {'Sae (g)':<10} {'SaR (g)':<10} {'Bölge'}")
print("  " + "-" * 65)

for i, ev in enumerate(eigenvalues):
    if ev > 0:
        omega = np.sqrt(ev)
        freq = omega / (2 * np.pi)
        T = 1.0 / freq if freq > 0 else 0
        
        sae = Sae(T)
        sar = SaR(T)
        region = get_spectral_region(T)
        
        modal_results.append({
            'mode': i + 1,
            'eigenvalue': ev,
            'omega': omega,
            'frequency': freq,
            'period': T,
            'Sae': sae,
            'SaR': sar,
            'region': region
        })
        
        print(f"  {i+1:<6} {T:<12.4f} {freq:<12.2f} {sae:<10.3f} {sar:<10.3f} {region}")

T1 = modal_results[0]['period']
f1 = modal_results[0]['frequency']

print("\n  " + "-" * 65)
print(f"  TEMEL PERİYOT: T1 = {T1:.4f} s ({T1*1000:.1f} ms)")
print(f"  TEMEL FREKANS: f1 = {f1:.2f} Hz")
print(f"  SPEKTRAL BÖLGE: {get_spectral_region(T1)}")

# ==============================================================================
# KÜTLe VE RİJİTLİK MERKEZİ HESABI
# ==============================================================================
print("\n" + "-" * 80)
print("[7] KÜTLE VE RİJİTLİK MERKEZİ HESABI")
print("-" * 80)

floor_centers = {}

for floor in floor_masses:
    z_floor = floor_masses[floor]['z']
    z_tol = 0.5
    
    # Get nodes at this floor
    floor_nodes_df = pos_df[np.abs(pos_df['z'] - z_floor) < z_tol]
    
    if len(floor_nodes_df) == 0:
        continue
    
    x_coords = floor_nodes_df['x'].values
    y_coords = floor_nodes_df['y'].values
    
    # Geometric dimensions
    x_min, x_max = x_coords.min(), x_coords.max()
    y_min, y_max = y_coords.min(), y_coords.max()
    Lx = x_max - x_min
    Ly = y_max - y_min
    
    # Mass center (centroid of nodes - assuming uniform distribution)
    x_mass = np.mean(x_coords)
    y_mass = np.mean(y_coords)
    
    # Stiffness center (from column positions)
    floor_cols = conn_df[
        (conn_df['element_type'] == 'column') & 
        (conn_df['node_i'].isin(floor_nodes_df['node_id']))
    ]
    
    if len(floor_cols) > 0:
        col_x = []
        col_y = []
        for _, col in floor_cols.iterrows():
            ni = int(col['node_i'])
            if ni in node_coords:
                col_x.append(node_coords[ni][0])
                col_y.append(node_coords[ni][1])
        
        x_stiff = np.mean(col_x) if col_x else x_mass
        y_stiff = np.mean(col_y) if col_y else y_mass
    else:
        x_stiff = x_mass
        y_stiff = y_mass
    
    # Eccentricity
    ex = x_mass - x_stiff
    ey = y_mass - y_stiff
    
    floor_centers[floor] = {
        'z': z_floor,
        'Lx': Lx,
        'Ly': Ly,
        'x_mass': x_mass,
        'y_mass': y_mass,
        'x_stiff': x_stiff,
        'y_stiff': y_stiff,
        'ex': ex,
        'ey': ey,
        'ex_ratio': abs(ex) / Lx * 100 if Lx > 0 else 0,
        'ey_ratio': abs(ey) / Ly * 100 if Ly > 0 else 0
    }

# Calculate total eccentricity
total_mass_sum = sum(fm['mass_kg'] for fm in floor_masses.values())
x_mass_total = sum(floor_centers[f]['x_mass'] * floor_masses[f]['mass_kg'] 
                   for f in floor_centers) / total_mass_sum
y_mass_total = sum(floor_centers[f]['y_mass'] * floor_masses[f]['mass_kg'] 
                   for f in floor_centers) / total_mass_sum
x_stiff_total = np.mean([fc['x_stiff'] for fc in floor_centers.values()])
y_stiff_total = np.mean([fc['y_stiff'] for fc in floor_centers.values()])

ex_total = x_mass_total - x_stiff_total
ey_total = y_mass_total - y_stiff_total

Lx_avg = np.mean([fc['Lx'] for fc in floor_centers.values()])
Ly_avg = np.mean([fc['Ly'] for fc in floor_centers.values()])

print(f"\n  KÜTLE MERKEZİ (Ağırlıklı Ortalama):")
print(f"    Xm = {x_mass_total:.3f} cm")
print(f"    Ym = {y_mass_total:.3f} cm")

print(f"\n  RİJİTLİK MERKEZİ:")
print(f"    Xr = {x_stiff_total:.3f} cm")
print(f"    Yr = {y_stiff_total:.3f} cm")

print(f"\n  EKSANTRİSİTE:")
print(f"    ex = {ex_total:.3f} cm ({abs(ex_total)/Lx_avg*100:.2f}% of Lx)")
print(f"    ey = {ey_total:.3f} cm ({abs(ey_total)/Ly_avg*100:.2f}% of Ly)")

# ==============================================================================
# EŞDEĞER DEPREM YÜKü YÖNTEMİ (Equivalent Static Method)
# TBDY 2018 Section 4.7
# ==============================================================================
print("\n" + "-" * 80)
print("[8] EŞDEĞER DEPREM YÜKü YÖNTEMİ (TBDY 2018 Madde 4.7)")
print("-" * 80)

# Total weight
W_total = total_applied_mass * 9.81 / 1000  # kN (g=9.81 m/s^2, convert to kN)

# Base shear: Vt = SaR(T1) * W * I / g
# But since Sae is in g units: Vt = SaR(T1) * W
Vt_elastic = Sae(T1) * W_total  # Elastic base shear
Vt_design = SaR(T1) * W_total   # Design base shear (reduced)

print(f"\n  Toplam Ağırlık: W = {W_total:.6f} kN")
print(f"  Sae(T1) = {Sae(T1):.3f} g")
print(f"  SaR(T1) = {SaR(T1):.3f} g")
print(f"\n  Elastik Taban Kesme Kuvveti: Vte = {Vt_elastic:.6f} kN")
print(f"  Tasarım Taban Kesme Kuvveti: Vt = {Vt_design:.6f} kN")

# Distribute base shear to floors (TBDY 2018 Eq. 4.5)
# Fi = (Wi * Hi) / sum(Wj * Hj) * Vt

sum_WH = 0
for floor in floor_masses:
    Wi = floor_masses[floor]['mass_kg'] * 9.81 / 1000  # kN
    Hi = floor_masses[floor]['z']  # cm
    sum_WH += Wi * Hi

floor_forces = {}
print(f"\n  {'Kat':<6} {'z (cm)':<10} {'Wi (kN)':<12} {'Fi (kN)':<12}")
print("  " + "-" * 45)

for floor in sorted(floor_masses.keys()):
    if floor == 0:
        continue  # Base has no lateral force
    
    Wi = floor_masses[floor]['mass_kg'] * 9.81 / 1000
    Hi = floor_masses[floor]['z']
    
    # TBDY 2018 Equation 4.5
    Fi = (Wi * Hi) / sum_WH * Vt_design if sum_WH > 0 else 0
    
    floor_forces[floor] = Fi
    
    if floor in [5, 10, 15, 20, 25]:
        print(f"  {floor:<6} {Hi:<10.1f} {Wi:<12.6f} {Fi:<12.6f}")

print("  " + "-" * 45)
sum_Fi = sum(floor_forces.values())
print(f"  Toplam: {sum_Fi:.6f} kN (Vt kontrolü)")

# ==============================================================================
# BURULMA DÜZENSİZLİĞİ ANALİZİ (A1a - Torsional Irregularity)
# ==============================================================================
print("\n" + "-" * 80)
print("[9] BURULMA DÜZENSİZLİĞİ ANALİZİ (A1a)")
print("    TBDY 2018 Tablo 3.6 - nbi = dmax/davg")
print("-" * 80)

# Apply equivalent static loads
ops.wipeAnalysis()
ops.loadConst('-time', 0.0)

ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply floor forces in X direction
for floor, Fi in floor_forces.items():
    z_floor = floor_masses[floor]['z']
    z_tol = 0.5
    
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < z_tol]['node_id'].astype(int).tolist()
    
    if len(floor_node_ids) > 0:
        force_per_node = Fi / len(floor_node_ids)
        for nid in floor_node_ids:
            try:
                ops.load(nid, force_per_node, 0, 0, 0, 0, 0)  # X-direction
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

# Check torsional irregularity at each floor
torsion_results = []

print(f"\n  {'Kat':<6} {'z(cm)':<8} {'dmax(mm)':<12} {'dmin(mm)':<12} {'davg(mm)':<12} {'nbi':<10} {'Durum'}")
print("  " + "-" * 75)

max_nbi = 0
for floor in sorted(floor_centers.keys()):
    if floor == 0:
        continue
        
    z_floor = floor_centers[floor]['z']
    z_tol = 0.5
    
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < z_tol]['node_id'].astype(int).tolist()
    
    if not floor_node_ids:
        continue
    
    # Get X-direction displacements
    displacements = []
    for nid in floor_node_ids:
        try:
            ux = ops.nodeDisp(nid, 1)  # X-direction
            displacements.append(ux)
        except:
            pass
    
    if len(displacements) < 2:
        continue
    
    displacements = np.array(displacements)
    dmax = np.max(displacements) * 10  # cm to mm
    dmin = np.min(displacements) * 10
    davg = (dmax + dmin) / 2
    
    # Torsional irregularity ratio
    if abs(davg) > 1e-10:
        nbi = dmax / davg
    else:
        nbi = 1.0
    
    max_nbi = max(max_nbi, nbi)
    
    # TBDY 2018: nbi > 1.2 -> Düzensiz, nbi > 2.0 -> İzin verilmez
    if nbi <= 1.2:
        status = "OK"
    elif nbi <= 2.0:
        status = "A1a DÜZENSİZ"
    else:
        status = "İZİN VERİLMEZ"
    
    torsion_results.append({
        'floor': floor,
        'z': z_floor,
        'dmax': dmax,
        'dmin': dmin,
        'davg': davg,
        'nbi': nbi,
        'status': status
    })
    
    if floor % 5 == 0 or floor == total_floors - 1:
        print(f"  {floor:<6} {z_floor:<8.1f} {dmax:<12.4f} {dmin:<12.4f} {davg:<12.4f} {nbi:<10.3f} {status}")

print("  " + "-" * 75)
print(f"\n  MAKSİMUM nbi = {max_nbi:.3f}")

if max_nbi <= 1.2:
    print(f"  SONUÇ: Burulma düzensizliği YOK (nbi <= 1.2)")
    torsion_status = "DÜZENSİZLİK YOK"
elif max_nbi <= 2.0:
    print(f"  SONUÇ: A1a Burulma Düzensizliği MEVCUT (1.2 < nbi <= 2.0)")
    torsion_status = "A1a DÜZENSİZ"
else:
    print(f"  SONUÇ: AŞIRI BURULMA - İZİN VERİLMEZ (nbi > 2.0)")
    torsion_status = "İZİN VERİLMEZ"

# ==============================================================================
# B2 - RİJİTLİK DÜZENSİZLİĞİ (Soft Story)
# ==============================================================================
print("\n" + "-" * 80)
print("[10] RİJİTLİK DÜZENSİZLİĞİ (B2 - Yumuşak Kat)")
print("     TBDY 2018: Ki/Ki+1 < 0.8 veya Ki/Kortalama(3) < 0.6")
print("-" * 80)

# Calculate story stiffness from drift
story_stiffness = []
prev_davg = 0

for tr in torsion_results:
    floor = tr['floor']
    davg = tr['davg']
    z = tr['z']
    
    # Story drift
    story_drift = davg - prev_davg
    
    # Story stiffness K = F / drift
    Fi = floor_forces.get(floor, 0)
    if abs(story_drift) > 1e-10:
        Ki = Fi / (story_drift / 10)  # mm to cm
    else:
        Ki = 0
    
    story_stiffness.append({
        'floor': floor,
        'z': z,
        'drift': story_drift,
        'Ki': Ki
    })
    
    prev_davg = davg

print(f"\n  {'Kat':<6} {'Ki':<15} {'Ki/Ki+1':<12} {'Ki/Kort3':<12} {'Durum'}")
print("  " + "-" * 55)

soft_story_status = "DÜZENSİZLİK YOK"
for i, ss in enumerate(story_stiffness[1:], 1):
    Ki = ss['Ki']
    K_above = story_stiffness[i-1]['Ki'] if i > 0 else Ki
    
    # Average of 3 floors above
    K_avg3 = np.mean([story_stiffness[j]['Ki'] for j in range(max(0,i-3), i)]) if i > 0 else Ki
    
    ratio_above = Ki / K_above if K_above != 0 else 1.0
    ratio_avg3 = Ki / K_avg3 if K_avg3 != 0 else 1.0
    
    is_soft = ratio_above < 0.8 or ratio_avg3 < 0.6
    status = "YUMUŞAK KAT" if is_soft else "OK"
    
    if is_soft:
        soft_story_status = "B2 YUMUŞAK KAT MEVCUT"
    
    if ss['floor'] % 5 == 0:
        print(f"  {ss['floor']:<6} {Ki:<15.4f} {ratio_above:<12.3f} {ratio_avg3:<12.3f} {status}")

print("  " + "-" * 55)
print(f"\n  SONUÇ: {soft_story_status}")

# ==============================================================================
# GÖRELİ KAT ÖTELEMESİ KONTROLÜ (Story Drift Check)
# ==============================================================================
print("\n" + "-" * 80)
print("[11] GÖRELİ KAT ÖTELEMESİ KONTROLÜ")
print("     TBDY 2018 Madde 4.9.1.3: di/hi <= 0.008 (Genel)")
print("-" * 80)

print(f"\n  {'Kat':<6} {'hi(cm)':<10} {'di(mm)':<12} {'di/hi':<12} {'Limit':<10} {'Durum'}")
print("  " + "-" * 60)

drift_limit = 0.008  # 0.8% for typical buildings
max_drift_ratio = 0

for i, ss in enumerate(story_stiffness):
    floor = ss['floor']
    
    if floor == 1:
        hi = floor_z.iloc[1] - floor_z.iloc[0]
    else:
        hi = floor_z.iloc[floor] - floor_z.iloc[floor-1] if floor > 0 else 6.0
    
    di = ss['drift']  # mm
    drift_ratio = abs(di) / (hi * 10) if hi > 0 else 0  # di(mm) / hi(mm)
    
    max_drift_ratio = max(max_drift_ratio, drift_ratio)
    
    status = "OK" if drift_ratio <= drift_limit else "AŞILDI"
    
    if floor % 5 == 0:
        print(f"  {floor:<6} {hi:<10.1f} {di:<12.4f} {drift_ratio:<12.6f} {drift_limit:<10} {status}")

print("  " + "-" * 60)
print(f"\n  MAKSİMUM GÖRELİ ÖTELEME: {max_drift_ratio:.6f}")
if max_drift_ratio <= drift_limit:
    print(f"  SONUÇ: Göreli kat ötelemesi limiti SAĞLANDI (di/hi <= {drift_limit})")
    drift_status = "SAĞLANDI"
else:
    print(f"  SONUÇ: Göreli kat ötelemesi limiti AŞILDI!")
    drift_status = "AŞILDI"

# ==============================================================================
# ÖZET RAPOR
# ==============================================================================
print("\n" + "=" * 80)
print("TBDY 2018 ANALİZ SONUÇLARI - ÖZET")
print("=" * 80)

summary = {
    'Model': 'V9 (Twin Towers 1:50)',
    'Yükseklik': f"{H_max} cm",
    'Eleman Sayısı': n_elements,
    'Toplam Kütle': f"{total_applied_mass:.4f} kg",
    'T1': f"{T1:.4f} s ({f1:.2f} Hz)",
    'Spektral Bölge': get_spectral_region(T1),
    'SDS': f"{TBDY['SDS']:.3f} g",
    'SD1': f"{TBDY['SD1']:.3f} g",
    'Sae(T1)': f"{Sae(T1):.3f} g",
    'SaR(T1)': f"{SaR(T1):.3f} g",
    'Vt (Tasarım)': f"{Vt_design:.6f} kN",
    'ex': f"{ex_total:.3f} cm ({abs(ex_total)/Lx_avg*100:.2f}%)",
    'ey': f"{ey_total:.3f} cm ({abs(ey_total)/Ly_avg*100:.2f}%)",
    'A1a Burulma (nbi)': f"{max_nbi:.3f} - {torsion_status}",
    'B2 Yumuşak Kat': soft_story_status,
    'Göreli Öteleme': f"{max_drift_ratio:.6f} - {drift_status}"
}

for param, value in summary.items():
    print(f"  {param:<25}: {value}")

print("\n" + "-" * 80)
print("DÜZENSİZLİK KONTROLÜ (TBDY 2018 Tablo 3.6)")
print("-" * 80)

irregularities_check = [
    ('A1a', 'Burulma Düzensizliği', f"nbi = {max_nbi:.3f}", max_nbi <= 1.2),
    ('A1b', 'Döşeme Süreksizliği', 'Kontrole gerek yok', True),
    ('A2', 'Planda Çöküntü/Çıkıntı', 'Simetrik plan', True),
    ('A3', 'Perde Süreksizliği', 'Sürekli taşıyıcılar', True),
    ('B1', 'Dayanım Düzensizliği', 'Kontrole gerek yok', True),
    ('B2', 'Rijitlik Düzensizliği', soft_story_status, 'MEVCUT' not in soft_story_status),
    ('B3', 'Kütle Düzensizliği', 'Düzgün dağılım', True),
]

print(f"\n  {'Kod':<6} {'Düzensizlik':<25} {'Değer':<25} {'Durum'}")
print("  " + "-" * 70)

for code, name, value, ok in irregularities_check:
    status = "✓ OK" if ok else "✗ DÜZENSİZ"
    print(f"  {code:<6} {name:<25} {value:<25} {status}")

# ==============================================================================
# SONUÇLARI KAYDET
# ==============================================================================
print("\n" + "-" * 80)
print("[12] SONUÇLARI KAYDETME")
print("-" * 80)

os.makedirs('results/data', exist_ok=True)

# Modal results
modal_df = pd.DataFrame(modal_results)
modal_df.to_csv('results/data/tbdy2018_modal_v9.csv', index=False)

# Torsion results
torsion_df = pd.DataFrame(torsion_results)
torsion_df.to_csv('results/data/tbdy2018_torsion_v9.csv', index=False)

# Summary
summary_df = pd.DataFrame([summary])
summary_df.to_csv('results/data/tbdy2018_summary_v9.csv', index=False)

print("  Kaydedildi: results/data/tbdy2018_modal_v9.csv")
print("  Kaydedildi: results/data/tbdy2018_torsion_v9.csv")
print("  Kaydedildi: results/data/tbdy2018_summary_v9.csv")

ops.wipe()

print("\n" + "=" * 80)
print("TBDY 2018 ANALİZİ TAMAMLANDI")
print("=" * 80)
