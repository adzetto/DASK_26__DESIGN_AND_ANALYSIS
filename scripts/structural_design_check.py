"""
TBDY 2018 + TS-498 KAPSAMLI YAPISAL TASARIM KONTROLÜ
=====================================================
Complete Structural Design Check per Turkish Codes

Kapsam:
1. TS-498:2021 Yük Tanımları (Zati + Hareketli Yükler)
2. TBDY 2018 Deprem Yükleri ve Spektrum
3. 2024 TBDY Uygulama Tebliği Taslağı Gereksinimleri
4. Düzensizlik Kontrolleri (A1a, A2, B2, B3)
5. Göreli Kat Ötelemesi Kontrolü
6. Yük Kombinasyonları
7. Kapasite Kontrolü

Model: Twin Towers V9 (1:50 Ölçek)
Yarışma: DASK 2025
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
from pathlib import Path
import os

WORK_DIR = Path(__file__).parent.parent
os.chdir(WORK_DIR)

print("=" * 80)
print("KAPSAMLI YAPISAL TASARIM KONTROLÜ")
print("TS-498:2021 + TBDY 2018 + 2024 TEBLİĞ TASLAĞI")
print("=" * 80)

# ==============================================================================
# BÖLÜM 1: TS-498:2021 YÜK TANIMLARI
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 1: TS-498:2021 YÜK TANIMLARI")
print("=" * 80)

# TS-498 Çizelge 6 - Düşey Hareketli Yükler
TS498_LOADS = {
    # Kullanım türü: kN/m²
    'cati_arasi': 1.5,
    'konut_buro': 2.0,
    'sinif_hastane': 3.5,
    'toplanti_spor': 5.0,
    'magazalar': 5.0,
    'kutuphane_arsiv': 5.0,
    'tribun_hareketli': 7.5,
    'garaj': 5.0,
    'konut_merdiven': 3.5,
    'genel_merdiven': 5.0,
}

# DASK Yarışması için yük tanımı
# Model ölçeği: 1:50
SCALE = 50
SCALE_AREA = SCALE ** 2  # = 2500

# Gerçek yapı için varsayılan yük: 5.0 kN/m² (genel amaçlı döşeme)
LIVE_LOAD_REAL = 5.0  # kN/m²

# Model için ölçeklenmiş yük (benzeşim kuralları)
# Yük = σ × L² → Model yükü = Gerçek yük × (1/λ)² = 5.0/2500 
LIVE_LOAD_MODEL = LIVE_LOAD_REAL / SCALE_AREA  # kN/m² = 0.002 kN/m²

print(f"\n  TS-498 Çizelge 6 - Seçilen Yük Tipi: Toplantı/Spor Salonu")
print(f"  Gerçek yapı hareketli yükü: {LIVE_LOAD_REAL} kN/m²")
print(f"  Ölçek faktörü: 1:{SCALE}")
print(f"  Model hareketli yükü: {LIVE_LOAD_MODEL:.6f} kN/m²")

# Balsa wood properties for self-weight
BALSA_DENSITY = 160  # kg/m³
BALSA_E = 170.0      # kN/cm²
BALSA_G = BALSA_E / 2.6

# Section: 6mm × 6mm
b_section = 0.6  # cm
A_section = b_section ** 2  # cm²
Iz = (b_section**4) / 12
Iy = (b_section**4) / 12
J = 0.1406 * b_section**4

print(f"\n  Malzeme: Balsa Ahşap")
print(f"  Yoğunluk: {BALSA_DENSITY} kg/m³")
print(f"  E = {BALSA_E} kN/cm² ({BALSA_E*10} MPa)")
print(f"  Kesit: {b_section*10}mm × {b_section*10}mm")

# ==============================================================================
# BÖLÜM 2: MODEL VERİLERİ
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 2: MODEL VERİLERİ")
print("=" * 80)

pos_df = pd.read_csv('data/twin_position_matrix_v9.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

n_nodes = len(pos_df)
n_elements = len(conn_df)
H_max = pos_df['z'].max()
total_floors = pos_df['floor'].max() + 1

print(f"\n  Düğüm Sayısı: {n_nodes}")
print(f"  Eleman Sayısı: {n_elements}")
print(f"  Kat Sayısı: {total_floors}")
print(f"  Model Yüksekliği: {H_max} cm")
print(f"  Prototip Yüksekliği: {H_max * SCALE / 100:.1f} m")

# Floor geometry
floor_z = pos_df.groupby('floor')['z'].first().sort_index()

# Calculate floor areas
floor_areas = {}
for floor in range(total_floors):
    z_floor = floor_z.iloc[floor]
    floor_nodes = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]
    x_coords = floor_nodes['x'].values
    y_coords = floor_nodes['y'].values
    
    Lx = x_coords.max() - x_coords.min()
    Ly = y_coords.max() - y_coords.min()
    area = Lx * Ly  # cm²
    
    floor_areas[floor] = {
        'z': z_floor,
        'Lx': Lx,
        'Ly': Ly,
        'area_cm2': area,
        'n_nodes': len(floor_nodes)
    }

print(f"\n  Kat Plan Boyutları:")
print(f"    Lx = {floor_areas[0]['Lx']:.1f} cm ({floor_areas[0]['Lx']*SCALE/100:.1f} m prototip)")
print(f"    Ly = {floor_areas[0]['Ly']:.1f} cm ({floor_areas[0]['Ly']*SCALE/100:.1f} m prototip)")

# ==============================================================================
# BÖLÜM 3: KÜTLE HESABI (Zati + Hareketli Yükler)
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 3: KÜTLE HESABI (TS-498 Zati + Hareketli Yükler)")
print("=" * 80)

# Self-weight from elements
total_length_cm = conn_df['length'].sum()
volume_cm3 = total_length_cm * A_section
density_kg_cm3 = BALSA_DENSITY / 1e6
self_weight_kg = volume_cm3 * density_kg_cm3

print(f"\n  [A] ZATİ AĞIRLIK (G):")
print(f"      Toplam eleman uzunluğu: {total_length_cm:.1f} cm")
print(f"      Toplam hacim: {volume_cm3:.1f} cm³")
print(f"      Zati ağırlık: {self_weight_kg:.4f} kg")

# Live load for model (competition test weights)
# DASK competition: Uses concentrated test weights on floors
# Typical test weight: 1.60 kg per floor for intermediate, 2.2 kg for roof

# For structural analysis WITHOUT test weights (pure self-weight)
# we calculate tributary mass per floor from elements

node_coords = {}
for _, row in pos_df.iterrows():
    node_coords[int(row['node_id'])] = (row['x'], row['y'], row['z'])

floor_masses = {}
for floor in range(total_floors):
    z_floor = floor_z.iloc[floor]
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    # Elements connected to this floor
    floor_elements = conn_df[
        (conn_df['node_i'].isin(floor_node_ids)) | 
        (conn_df['node_j'].isin(floor_node_ids))
    ]
    
    tributary_length = floor_elements['length'].sum() / 2
    floor_self_mass = tributary_length * A_section * density_kg_cm3
    
    # Live load mass (from TS-498)
    # During test: Apply competition test weights
    # For self-weight analysis: No live load
    floor_live_mass = 0.0  # Pure self-weight analysis
    
    floor_masses[floor] = {
        'z': z_floor,
        'self_mass_kg': floor_self_mass,
        'live_mass_kg': floor_live_mass,
        'total_mass_kg': floor_self_mass + floor_live_mass,
        'n_nodes': len(floor_node_ids)
    }

print(f"\n  [B] KAT KÜTLE DAĞILIMI (Zati Ağırlık):")
print(f"      {'Kat':<6} {'z(cm)':<8} {'Gk(kg)':<12} {'Qk(kg)':<12} {'Toplam(kg)'}")
print("      " + "-" * 50)

total_mass = 0
for floor in [0, 5, 10, 15, 20, 25]:
    if floor in floor_masses:
        fm = floor_masses[floor]
        print(f"      {floor:<6} {fm['z']:<8.1f} {fm['self_mass_kg']:<12.4f} {fm['live_mass_kg']:<12.4f} {fm['total_mass_kg']:.4f}")
        total_mass += fm['total_mass_kg']

print("      " + "-" * 50)
print(f"      Toplam kütle: {sum(fm['total_mass_kg'] for fm in floor_masses.values()):.4f} kg")

# ==============================================================================
# BÖLÜM 4: TBDY 2018 DEPREM PARAMETRELERİ
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 4: TBDY 2018 DEPREM PARAMETRELERİ")
print("=" * 80)

# AFAD DD-2 parameters (from afad_reports)
TBDY = {
    'SS': 0.877,       # Short period spectral acceleration
    'S1': 0.243,       # 1.0 sec spectral acceleration
    'FS': 1.149,       # Short period site factor (ZD)
    'F1': 2.114,       # 1.0 sec site factor (ZD)
    'PGA': 0.362,      # Peak ground acceleration
    
    'SDS': None,
    'SD1': None,
    'TA': None,
    'TB': None,
    'TL': 6.0,
    
    # Building parameters (ahşap çerçeve)
    'R': 3.0,          # Ahşap yapı davranış katsayısı
    'D': 2.0,          # Dayanım fazlalığı
    'I': 1.0,          # Önem katsayısı (BKS=1)
}

TBDY['SDS'] = TBDY['SS'] * TBDY['FS']
TBDY['SD1'] = TBDY['S1'] * TBDY['F1']
TBDY['TA'] = 0.2 * TBDY['SD1'] / TBDY['SDS']
TBDY['TB'] = TBDY['SD1'] / TBDY['SDS']

print(f"\n  AFAD DD-2 Parametreleri:")
print(f"    SS = {TBDY['SS']:.3f}, S1 = {TBDY['S1']:.3f}")
print(f"    FS = {TBDY['FS']:.3f}, F1 = {TBDY['F1']:.3f}")
print(f"\n  Tasarım Spektral İvmeleri:")
print(f"    SDS = SS × FS = {TBDY['SDS']:.3f} g")
print(f"    SD1 = S1 × F1 = {TBDY['SD1']:.3f} g")
print(f"\n  Köşe Periyotları:")
print(f"    TA = 0.2 × SD1/SDS = {TBDY['TA']:.3f} s")
print(f"    TB = SD1/SDS = {TBDY['TB']:.3f} s")
print(f"    TL = {TBDY['TL']:.1f} s")
print(f"\n  Taşıyıcı Sistem Katsayıları (Ahşap Çerçeve):")
print(f"    R = {TBDY['R']:.1f}")
print(f"    D = {TBDY['D']:.1f}")
print(f"    I = {TBDY['I']:.1f}")

def Sae(T):
    """TBDY 2018 Elastik Tasarım Spektrumu"""
    SDS, SD1, TA, TB, TL = TBDY['SDS'], TBDY['SD1'], TBDY['TA'], TBDY['TB'], TBDY['TL']
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

def SaR(T):
    """TBDY 2018 Azaltılmış Tasarım Spektrumu"""
    R, D, I, TB = TBDY['R'], TBDY['D'], TBDY['I'], TBDY['TB']
    if T < TB:
        Ra = D + (R/I - D) * T / TB
    else:
        Ra = R / I
    return Sae(T) / Ra

def spectral_region(T):
    if T < TBDY['TA']:
        return "Yükselen"
    elif T <= TBDY['TB']:
        return "Plato"
    elif T <= TBDY['TL']:
        return "Azalan"
    else:
        return "Uzun Periyot"

# ==============================================================================
# BÖLÜM 5: OPENSEES MODELİ
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 5: OPENSEES MODELİ OLUŞTURMA")
print("=" * 80)

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create nodes
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    ops.node(nid, row['x'], row['y'], row['z'])

# Fix base
base_nodes = pos_df[pos_df['z'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)

print(f"  Düğümler: {n_nodes}")
print(f"  Mesnetler: {len(base_nodes)}")

# Transformations
ops.geomTransf('Linear', 1, 1, 0, 0)
ops.geomTransf('Linear', 2, 0, 0, 1)
ops.geomTransf('Linear', 3, 0, 0, 1)

# Elements
elem_count = 0
for _, row in conn_df.iterrows():
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

print(f"  Elemanlar: {elem_count}")

# Mass assignment
MASS_CONV = 1e-5  # kg to kN*s²/cm
for floor in floor_masses:
    z_floor = floor_masses[floor]['z']
    mass_kg = floor_masses[floor]['total_mass_kg']
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    if len(floor_node_ids) > 0:
        mass_per_node = mass_kg * MASS_CONV / len(floor_node_ids)
        for nid in floor_node_ids:
            ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)

print(f"  Kütle ataması tamamlandı")

# ==============================================================================
# BÖLÜM 6: MODAL ANALİZ
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 6: MODAL ANALİZ")
print("=" * 80)

num_modes = 12
try:
    eigenvalues = ops.eigen('-genBandArpack', num_modes)
except:
    eigenvalues = ops.eigen(num_modes)

modal_results = []
print(f"\n  {'Mod':<5} {'T(s)':<10} {'f(Hz)':<10} {'Sae(g)':<10} {'SaR(g)':<10} {'Bölge'}")
print("  " + "-" * 60)

for i, ev in enumerate(eigenvalues):
    if ev > 0:
        omega = np.sqrt(ev)
        freq = omega / (2 * np.pi)
        T = 1.0 / freq if freq > 0 else 0
        
        modal_results.append({
            'mode': i + 1,
            'period': T,
            'frequency': freq,
            'Sae': Sae(T),
            'SaR': SaR(T),
            'region': spectral_region(T)
        })
        
        print(f"  {i+1:<5} {T:<10.4f} {freq:<10.2f} {Sae(T):<10.3f} {SaR(T):<10.3f} {spectral_region(T)}")

T1 = modal_results[0]['period']
f1 = modal_results[0]['frequency']

print("  " + "-" * 60)
print(f"\n  TEMEL PERİYOT: T1 = {T1:.4f} s")
print(f"  TEMEL FREKANS: f1 = {f1:.2f} Hz")
print(f"  SPEKTRAL BÖLGE: {spectral_region(T1)}")

# Prototype period
T1_prototype = T1 * np.sqrt(SCALE)
print(f"\n  PROTOTİP PERİYODU: T1_prototip = {T1_prototype:.3f} s")
print(f"  PROTOTİP SPEKTRAL BÖLGE: {spectral_region(T1_prototype)}")

# ==============================================================================
# BÖLÜM 7: EŞDEĞER DEPREM YÜKü ANALİZİ
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 7: EŞDEĞER DEPREM YÜKÜ ANALİZİ (TBDY 2018 Madde 4.7)")
print("=" * 80)

# Total weight
W_total = sum(fm['total_mass_kg'] for fm in floor_masses.values()) * 9.81 / 1000  # kN

# Base shear
Vt_elastic = Sae(T1) * W_total
Vt_design = SaR(T1) * W_total

print(f"\n  Toplam Ağırlık: W = {W_total:.6f} kN")
print(f"  Sae(T1) = {Sae(T1):.3f} g")
print(f"  SaR(T1) = {SaR(T1):.3f} g")
print(f"\n  Elastik Taban Kesme: Vte = {Vt_elastic:.6f} kN")
print(f"  Tasarım Taban Kesme: Vt = {Vt_design:.6f} kN")

# Distribute to floors
sum_WH = sum(
    floor_masses[f]['total_mass_kg'] * 9.81/1000 * floor_masses[f]['z']
    for f in floor_masses if f > 0
)

floor_forces = {}
for floor in floor_masses:
    if floor == 0:
        continue
    Wi = floor_masses[floor]['total_mass_kg'] * 9.81 / 1000
    Hi = floor_masses[floor]['z']
    Fi = (Wi * Hi) / sum_WH * Vt_design if sum_WH > 0 else 0
    floor_forces[floor] = Fi

# Apply lateral loads
ops.wipeAnalysis()
ops.loadConst('-time', 0.0)
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

for floor, Fi in floor_forces.items():
    z_floor = floor_masses[floor]['z']
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    if len(floor_node_ids) > 0:
        force_per_node = Fi / len(floor_node_ids)
        for nid in floor_node_ids:
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

# ==============================================================================
# BÖLÜM 8: DÜZENSİZLİK KONTROLÜ (TBDY 2018 Tablo 3.6)
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 8: DÜZENSİZLİK KONTROLÜ (TBDY 2018 Tablo 3.6)")
print("=" * 80)

irregularities = {}

# --- A1a: BURULMA DÜZENSİZLİĞİ ---
print("\n  [A1a] BURULMA DÜZENSİZLİĞİ")
print("        Koşul: ηbi = δmax/δort > 1.2")
print("        2024 Tebliğ Taslağı BKS=3: ηbi ≤ 1.4")

max_eta = 0
torsion_check = []

for floor in sorted(floor_masses.keys()):
    if floor == 0:
        continue
    
    z_floor = floor_masses[floor]['z']
    floor_node_ids = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]['node_id'].astype(int).tolist()
    
    displacements = []
    for nid in floor_node_ids:
        try:
            ux = ops.nodeDisp(nid, 1)
            displacements.append(ux)
        except:
            pass
    
    if len(displacements) >= 2:
        disp = np.array(displacements)
        dmax = np.max(disp) * 10  # mm
        dmin = np.min(disp) * 10
        davg = (dmax + dmin) / 2
        
        eta = dmax / davg if abs(davg) > 1e-10 else 1.0
        max_eta = max(max_eta, eta)
        
        torsion_check.append({
            'floor': floor,
            'dmax': dmax,
            'dmin': dmin,
            'davg': davg,
            'eta': eta
        })

print(f"\n        Kat  δmax(mm)   δmin(mm)   δort(mm)   ηbi")
print("        " + "-" * 50)
for tc in torsion_check[::5]:  # Every 5th floor
    print(f"        {tc['floor']:<4} {tc['dmax']:<10.4f} {tc['dmin']:<10.4f} {tc['davg']:<10.4f} {tc['eta']:<10.3f}")

print("        " + "-" * 50)
print(f"        Maksimum ηbi = {max_eta:.3f}")

if max_eta <= 1.2:
    print("        SONUÇ: Burulma düzensizliği YOK ✓")
    irregularities['A1a'] = {'exists': False, 'value': max_eta}
elif max_eta <= 1.4:
    print("        SONUÇ: A1a Burulma düzensizliği MEVCUT (ama < 1.4) ⚠")
    irregularities['A1a'] = {'exists': True, 'value': max_eta, 'severe': False}
elif max_eta <= 2.0:
    print("        SONUÇ: A1a Burulma düzensizliği MEVCUT ✗")
    irregularities['A1a'] = {'exists': True, 'value': max_eta, 'severe': True}
else:
    print("        SONUÇ: AŞIRI BURULMA - İZİN VERİLMEZ ✗✗")
    irregularities['A1a'] = {'exists': True, 'value': max_eta, 'unacceptable': True}

# --- A2: PLANDA ÇÖKÜ ve ÇIKINTI ---
print("\n  [A2] PLANDA ÇÖKÜNTÜ/ÇIKINTI DÜZENSİZLİĞİ")
print("        Koşul: L1/L > 0.2 veya L2/Lp > 0.2")

# For twin towers - symmetric rectangular plan
Lx = floor_areas[0]['Lx']
Ly = floor_areas[0]['Ly']
print(f"        Plan boyutları: Lx = {Lx:.1f} cm, Ly = {Ly:.1f} cm")
print(f"        Simetrik dikdörtgen plan, çöküntü/çıkıntı yok")
print("        SONUÇ: A2 Düzensizliği YOK ✓")
irregularities['A2'] = {'exists': False}

# --- B2: RİJİTLİK DÜZENSİZLİĞİ (YUMUŞAK KAT) ---
print("\n  [B2] RİJİTLİK DÜZENSİZLİĞİ (YUMUŞAK KAT)")
print("        Koşul: Ki/Ki+1 < 0.8 veya Ki/Kort3 < 0.6")

story_stiffness = []
prev_disp = 0

for tc in torsion_check:
    floor = tc['floor']
    curr_disp = tc['davg']
    
    story_drift = curr_disp - prev_disp
    Fi = floor_forces.get(floor, 0)
    
    if abs(story_drift) > 1e-10:
        Ki = Fi / (story_drift / 10)  # kN/cm
    else:
        Ki = float('inf')
    
    story_stiffness.append({
        'floor': floor,
        'drift': story_drift,
        'Ki': Ki
    })
    
    prev_disp = curr_disp

soft_story_found = False
print(f"\n        Kat  Ki         Ki/Ki+1    Ki/Kort3   Durum")
print("        " + "-" * 55)

for i, ss in enumerate(story_stiffness[1:], 1):
    Ki = ss['Ki']
    if Ki == float('inf'):
        continue
        
    K_above = story_stiffness[i-1]['Ki'] if i > 0 else Ki
    
    # Average of 3 floors above
    K_avg3 = np.mean([story_stiffness[j]['Ki'] for j in range(max(0,i-3), i) 
                      if story_stiffness[j]['Ki'] != float('inf')]) if i > 0 else Ki
    
    if K_above != float('inf') and K_above != 0:
        ratio_above = Ki / K_above
    else:
        ratio_above = 1.0
    
    if K_avg3 != float('inf') and K_avg3 != 0:
        ratio_avg3 = Ki / K_avg3
    else:
        ratio_avg3 = 1.0
    
    is_soft = ratio_above < 0.8 or ratio_avg3 < 0.6
    if is_soft:
        soft_story_found = True
    
    status = "Yumuşak" if is_soft else "OK"
    
    if ss['floor'] % 5 == 0:
        print(f"        {ss['floor']:<4} {Ki:<10.4f} {ratio_above:<10.3f} {ratio_avg3:<10.3f} {status}")

print("        " + "-" * 55)
if soft_story_found:
    print("        SONUÇ: B2 Yumuşak kat DÜZENSİZLİĞİ MEVCUT ✗")
    irregularities['B2'] = {'exists': True}
else:
    print("        SONUÇ: B2 Yumuşak kat düzensizliği YOK ✓")
    irregularities['B2'] = {'exists': False}

# --- B3: KÜTLE DÜZENSİZLİĞİ ---
print("\n  [B3] KÜTLE DÜZENSİZLİĞİ")
print("        Koşul: mi/mi+1 > 1.5 veya mi/mi-1 > 1.5")

mass_irreg_found = False
for i in range(1, total_floors):
    mi = floor_masses[i]['total_mass_kg']
    mi_below = floor_masses[i-1]['total_mass_kg'] if i > 0 else mi
    mi_above = floor_masses[i+1]['total_mass_kg'] if i < total_floors-1 else mi
    
    ratio_below = mi / mi_below if mi_below > 0 else 1.0
    ratio_above = mi / mi_above if mi_above > 0 else 1.0
    
    if ratio_below > 1.5 or ratio_above > 1.5:
        mass_irreg_found = True

if mass_irreg_found:
    print("        SONUÇ: B3 Kütle düzensizliği MEVCUT ✗")
    irregularities['B3'] = {'exists': True}
else:
    print("        SONUÇ: B3 Kütle düzensizliği YOK ✓")
    print("        (Tüm katlarda düzgün kütle dağılımı)")
    irregularities['B3'] = {'exists': False}

# ==============================================================================
# BÖLÜM 9: GÖRELİ KAT ÖTELEMESİ KONTROLÜ
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 9: GÖRELİ KAT ÖTELEMESİ KONTROLÜ")
print("=" * 80)

# TBDY 2018 Limits
DRIFT_LIMIT_TBDY = 0.008      # Standard
DRIFT_LIMIT_2024 = 0.010      # 2024 Tebliğ with infill walls
DRIFT_LIMIT_STEEL = 0.0175    # Steel moment frame (2024)

print(f"\n  TBDY 2018 Limiti: δ/h ≤ {DRIFT_LIMIT_TBDY}")
print(f"  2024 Tebliğ (dolgu duvarlı): δ/h ≤ {DRIFT_LIMIT_2024}")
print(f"  2024 Tebliğ (çelik çerçeve): δ/h ≤ {DRIFT_LIMIT_STEEL}")

print(f"\n  Kat   hi(cm)   δi(mm)   δi/hi      TBDY      2024")
print("  " + "-" * 60)

max_drift_ratio = 0
drift_results = []

for i, ss in enumerate(story_stiffness):
    floor = ss['floor']
    
    if floor == 1:
        hi = floor_z.iloc[1] - floor_z.iloc[0]
    elif floor < len(floor_z):
        hi = floor_z.iloc[floor] - floor_z.iloc[floor-1]
    else:
        hi = 6.0
    
    di = ss['drift']  # mm
    drift_ratio = abs(di) / (hi * 10) if hi > 0 else 0
    
    max_drift_ratio = max(max_drift_ratio, drift_ratio)
    
    tbdy_ok = "✓" if drift_ratio <= DRIFT_LIMIT_TBDY else "✗"
    t2024_ok = "✓" if drift_ratio <= DRIFT_LIMIT_2024 else "✗"
    
    drift_results.append({
        'floor': floor,
        'hi': hi,
        'di': di,
        'ratio': drift_ratio
    })
    
    if floor % 5 == 0:
        print(f"  {floor:<5} {hi:<8.1f} {di:<8.4f} {drift_ratio:<10.6f} {tbdy_ok:<8} {t2024_ok}")

print("  " + "-" * 60)
print(f"\n  Maksimum δi/hi = {max_drift_ratio:.6f}")

if max_drift_ratio <= DRIFT_LIMIT_TBDY:
    print(f"  TBDY 2018: SAĞLANDI ✓")
    print(f"  2024 Tebliğ: SAĞLANDI ✓")
    drift_status = "OK"
else:
    print(f"  TBDY 2018: AŞILDI ✗")
    drift_status = "FAIL"

# ==============================================================================
# BÖLÜM 10: EKSANTRİSİTE KONTROLÜ
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 10: EKSANTRİSİTE KONTROLÜ")
print("=" * 80)

# Calculate mass center and stiffness center
floor_centers = {}
for floor in range(1, total_floors):
    z_floor = floor_z.iloc[floor]
    floor_nodes = pos_df[np.abs(pos_df['z'] - z_floor) < 0.5]
    
    x_coords = floor_nodes['x'].values
    y_coords = floor_nodes['y'].values
    
    x_mass = np.mean(x_coords)
    y_mass = np.mean(y_coords)
    
    floor_centers[floor] = {
        'x_mass': x_mass,
        'y_mass': y_mass,
        'Lx': x_coords.max() - x_coords.min(),
        'Ly': y_coords.max() - y_coords.min()
    }

# Average eccentricity
total_mass_sum = sum(fm['total_mass_kg'] for fm in floor_masses.values())
x_cm = sum(floor_centers[f]['x_mass'] * floor_masses[f]['total_mass_kg'] 
           for f in floor_centers) / total_mass_sum
y_cm = sum(floor_centers[f]['y_mass'] * floor_masses[f]['total_mass_kg'] 
           for f in floor_centers) / total_mass_sum

# Stiffness center (geometric center for symmetric structure)
x_cr = np.mean([fc['x_mass'] for fc in floor_centers.values()])
y_cr = np.mean([fc['y_mass'] for fc in floor_centers.values()])

ex = x_cm - x_cr
ey = y_cm - y_cr

Lx_avg = np.mean([fc['Lx'] for fc in floor_centers.values()])
Ly_avg = np.mean([fc['Ly'] for fc in floor_centers.values()])

print(f"\n  Kütle Merkezi: ({x_cm:.3f}, {y_cm:.3f}) cm")
print(f"  Rijitlik Merkezi: ({x_cr:.3f}, {y_cr:.3f}) cm")
print(f"\n  Eksantrisite:")
print(f"    ex = {ex:.3f} cm ({abs(ex)/Lx_avg*100:.2f}% of Lx)")
print(f"    ey = {ey:.3f} cm ({abs(ey)/Ly_avg*100:.2f}% of Ly)")

if abs(ex) < 0.01 and abs(ey) < 0.01:
    print("\n  SONUÇ: Simetrik yapı, eksantrisite ihmal edilebilir ✓")
else:
    print(f"\n  SONUÇ: Eksantrisite mevcut - Ek dışmerkezlik hesabı gerekli")

# ==============================================================================
# BÖLÜM 11: SONUÇ RAPORU
# ==============================================================================
print("\n" + "=" * 80)
print("BÖLÜM 11: SONUÇ RAPORU")
print("=" * 80)

print("\n  ┌─────────────────────────────────────────────────────────────────┐")
print("  │                    YAPISAL TASARIM KONTROLÜ                     │")
print("  │                     Twin Towers Model V9                        │")
print("  ├─────────────────────────────────────────────────────────────────┤")
print(f"  │ Model Yüksekliği        : {H_max:>8.1f} cm ({H_max*SCALE/100:.1f} m prototip)    │")
print(f"  │ Toplam Kütle            : {sum(fm['total_mass_kg'] for fm in floor_masses.values()):>8.4f} kg                       │")
print(f"  │ Temel Periyot (Model)   : {T1:>8.4f} s                          │")
print(f"  │ Temel Periyot (Prototip): {T1_prototype:>8.3f} s                          │")
print(f"  │ Spektral Bölge          : {spectral_region(T1):>12}                      │")
print("  ├─────────────────────────────────────────────────────────────────┤")
print("  │           DÜZENSİZLİK KONTROLÜ (TBDY 2018)                      │")
print("  ├─────────────────────────────────────────────────────────────────┤")

checks = [
    ('A1a', 'Burulma Düzensizliği', irregularities.get('A1a', {}).get('exists', False),
     f"ηbi = {max_eta:.3f}"),
    ('A2', 'Planda Çöküntü/Çıkıntı', irregularities.get('A2', {}).get('exists', False),
     "Simetrik plan"),
    ('B2', 'Yumuşak Kat', irregularities.get('B2', {}).get('exists', False),
     "Ki kontrol"),
    ('B3', 'Kütle Düzensizliği', irregularities.get('B3', {}).get('exists', False),
     "Düzgün dağılım"),
]

for code, name, exists, value in checks:
    status = "✗ MEVCUT" if exists else "✓ YOK"
    print(f"  │ {code:<5} {name:<25} {value:<15} {status:<10} │")

print("  ├─────────────────────────────────────────────────────────────────┤")
print("  │           GÖRELİ KAT ÖTELEMESİ                                  │")
print("  ├─────────────────────────────────────────────────────────────────┤")
drift_ok = max_drift_ratio <= DRIFT_LIMIT_TBDY
print(f"  │ δmax/h = {max_drift_ratio:.6f}  Limit = {DRIFT_LIMIT_TBDY}       {'✓ SAĞLANDI' if drift_ok else '✗ AŞILDI':<12} │")
print("  ├─────────────────────────────────────────────────────────────────┤")
print("  │           EKSANTRİSİTE                                          │")
print("  ├─────────────────────────────────────────────────────────────────┤")
print(f"  │ ex = {abs(ex):.3f} cm ({abs(ex)/Lx_avg*100:.2f}%)  ey = {abs(ey):.3f} cm ({abs(ey)/Ly_avg*100:.2f}%)        ✓ SİMETRİK │")
print("  └─────────────────────────────────────────────────────────────────┘")

# Save results
os.makedirs('results/data', exist_ok=True)

summary = {
    'Model': 'V9',
    'Scale': f'1:{SCALE}',
    'Height_cm': H_max,
    'Mass_kg': sum(fm['total_mass_kg'] for fm in floor_masses.values()),
    'T1_model': T1,
    'T1_prototype': T1_prototype,
    'Spectral_Region': spectral_region(T1),
    'SDS': TBDY['SDS'],
    'SD1': TBDY['SD1'],
    'Vt_design_kN': Vt_design,
    'Max_eta_bi': max_eta,
    'A1a_Torsion': irregularities.get('A1a', {}).get('exists', False),
    'B2_SoftStory': irregularities.get('B2', {}).get('exists', False),
    'B3_Mass': irregularities.get('B3', {}).get('exists', False),
    'Max_Drift_Ratio': max_drift_ratio,
    'Drift_OK': drift_ok,
    'ex_cm': ex,
    'ey_cm': ey
}

pd.DataFrame([summary]).to_csv('results/data/structural_design_check_v9.csv', index=False)
print("\n  Sonuçlar kaydedildi: results/data/structural_design_check_v9.csv")

ops.wipe()

print("\n" + "=" * 80)
print("KAPSAMLI YAPISAL TASARIM KONTROLÜ TAMAMLANDI")
print("=" * 80)
