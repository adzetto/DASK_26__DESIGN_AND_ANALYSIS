#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TBDY 2018 A1a Burulma Düzensizliği Analizi
==========================================
TBDY 2018 Madde 3.6.2.1 ve 4.7.4'e göre:
- η_bi = (Δ_i^(X))_max / (Δ_i^(X))_ort > 1.2 ise A1a burulma düzensizliği
- 1.2 < η_bi ≤ 2.0 durumunda D_bi = (η_bi / 1.2)² büyütme faktörü uygulanır
- ±%5 ek dışmerkezlik etkileri gözönüne alınarak hesap yapılır

DİYAFRAM CONSTRAINT KULLANILMADAN nodal yer değiştirmelerden η_bi hesaplanır.

Author: DASK 2026 Analysis Pipeline
Date: 2026-02
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import json
import os
from pathlib import Path

# =============================================================================
# TBDY 2018 SPECTRUM PARAMETERS (DD-2, ZD Soil, Istanbul)
# =============================================================================
SPECTRUM_PARAMS = {
    'SDS': 1.008,      # g
    'SD1': 0.514,      # g
    'TA': 0.102,       # s
    'TB': 0.51,        # s
    'TL': 6.0,         # s
    'PGA': 0.362,      # g
    'I': 1.0,          # Bina önem katsayısı
    'R': 4.0,          # Taşıyıcı sistem davranış katsayısı (çelik çerçeve)
    'D': 2.5,          # Dayanım fazlalığı katsayısı
}

# Material properties (1:50 scale model)
MATERIAL_PROPS = {
    'E_kN_cm2': 170.0,       # Elastisite modülü
    'G_kN_cm2': 65.385,      # Kayma modülü
    'nu': 0.3,               # Poisson oranı
    'rho_kg_cm3': 7.85e-6,   # Çelik yoğunluğu
    'section_cm': 0.6,       # Kare kesit kenarı (6mm)
}


def get_Sae(T, params):
    """TBDY 2018 Denk. 2.2 - Elastik tasarım spektral ivmesi"""
    SDS, SD1, TA, TB, TL = params['SDS'], params['SD1'], params['TA'], params['TB'], params['TL']

    if T < TA:
        Sae = (0.4 + 0.6 * T / TA) * SDS
    elif T <= TB:
        Sae = SDS
    elif T <= TL:
        Sae = SD1 / T
    else:
        Sae = SD1 * TL / (T * T)

    return Sae


def get_SaR(T, params):
    """TBDY 2018 Denk. 4.8 - Azaltılmış tasarım spektral ivmesi"""
    Sae = get_Sae(T, params)
    Ra = get_Ra(T, params)
    return Sae / Ra


def get_Ra(T, params):
    """TBDY 2018 Denk. 4.1 - Deprem yükü azaltma katsayısı"""
    R, D, TB = params['R'], params['D'], params['TB']

    if T > TB:
        Ra = R / params['I']
    else:
        Ra = D + (R / params['I'] - D) * T / TB

    return Ra


class TorsionalIrregularityAnalyzer:
    """
    TBDY 2018 A1a Burulma Düzensizliği Analizi
    Diyafram constraint kullanmadan nodal yer değiştirmelerden hesaplama
    """

    def __init__(self, position_file, connectivity_file, output_dir):
        self.position_file = position_file
        self.connectivity_file = connectivity_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load data
        self.nodes_df = pd.read_csv(position_file)
        self.elements_df = pd.read_csv(connectivity_file)

        # Floor information
        self.floors = sorted(self.nodes_df['floor'].unique())
        self.n_floors = len(self.floors) - 1  # Exclude base (floor 0)

        # Model properties
        self.E = MATERIAL_PROPS['E_kN_cm2']
        self.G = MATERIAL_PROPS['G_kN_cm2']
        self.nu = MATERIAL_PROPS['nu']
        self.section = MATERIAL_PROPS['section_cm']
        self.A = self.section ** 2
        self.Iz = self.section ** 4 / 12
        self.Iy = self.Iz
        self.J = 2.25 * (self.section / 2) ** 4  # Torsional constant for square section

        # Results storage
        self.modal_results = {}
        self.torsion_results = {}
        self.floor_displacements = {}

    def build_model(self):
        """OpenSees modelini oluştur - DİYAFRAM CONSTRAINT YOK"""
        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)

        print("=" * 60)
        print("TBDY 2018 A1a Burulma Düzensizliği Analizi")
        print("DİYAFRAM CONSTRAINT KULLANILMIYOR")
        print("=" * 60)

        # Create nodes
        print(f"\nDüğüm noktaları oluşturuluyor ({len(self.nodes_df)} adet)...")
        for _, row in self.nodes_df.iterrows():
            node_id = int(row['node_id'])
            x, y, z = row['x'], row['y'], row['z']
            ops.node(node_id, x, y, z)

        # Fix base nodes (floor 0)
        base_nodes = self.nodes_df[self.nodes_df['floor'] == 0]['node_id'].values
        print(f"Ankastre mesnetler oluşturuluyor ({len(base_nodes)} adet)...")
        for node_id in base_nodes:
            ops.fix(int(node_id), 1, 1, 1, 1, 1, 1)

        # Define material and sections
        mat_tag = 1
        ops.uniaxialMaterial('Elastic', mat_tag, self.E)

        # Geometric transformation
        col_transf_tag = 1  # Column (vertical)
        beam_x_transf_tag = 2  # Beam in X direction
        beam_y_transf_tag = 3  # Beam in Y direction

        ops.geomTransf('Linear', col_transf_tag, 1, 0, 0)
        ops.geomTransf('Linear', beam_x_transf_tag, 0, 0, 1)
        ops.geomTransf('Linear', beam_y_transf_tag, 0, 0, 1)

        # Create elements with dynamic transformation for braces
        print(f"Elemanlar oluşturuluyor ({len(self.elements_df)} adet)...")
        brace_transf_counter = 100  # Start brace transformations from 100

        for _, row in self.elements_df.iterrows():
            elem_id = int(row['element_id'])
            node_i = int(row['node_i'])
            node_j = int(row['node_j'])
            elem_type = row['element_type']

            # Select appropriate transformation
            if elem_type == 'column':
                transf_tag = col_transf_tag
            elif elem_type == 'beam_x':
                transf_tag = beam_x_transf_tag
            elif elem_type == 'beam_y':
                transf_tag = beam_y_transf_tag
            else:  # braces - need unique transformation based on element orientation
                # Get node coordinates
                node_i_data = self.nodes_df[self.nodes_df['node_id'] == node_i].iloc[0]
                node_j_data = self.nodes_df[self.nodes_df['node_id'] == node_j].iloc[0]

                xi, yi, zi = node_i_data['x'], node_i_data['y'], node_i_data['z']
                xj, yj, zj = node_j_data['x'], node_j_data['y'], node_j_data['z']

                # Element direction vector
                dx = xj - xi
                dy = yj - yi
                dz = zj - zi

                # Find appropriate vecxz (perpendicular to element axis)
                # For braces, use a vector that's not parallel to the element
                if abs(dz) > 1e-6:  # Element has vertical component
                    vecxz = (0, 1, 0)  # Use Y-axis
                elif abs(dy) > 1e-6:  # Element in XY plane with Y component
                    vecxz = (0, 0, 1)  # Use Z-axis
                else:  # Element along X-axis
                    vecxz = (0, 0, 1)  # Use Z-axis

                # Create unique transformation for this brace
                transf_tag = brace_transf_counter
                ops.geomTransf('Linear', transf_tag, *vecxz)
                brace_transf_counter += 1

            # Elastic beam-column element
            ops.element('elasticBeamColumn', elem_id, node_i, node_j,
                       self.A, self.E, self.G, self.J, self.Iy, self.Iz, transf_tag)

        # Add mass to floor nodes (excluding base)
        print("Kütle ataması yapılıyor...")
        floor_mass_kg = 1.6  # kg per floor per tower
        roof_mass_kg = 2.22  # kg for roof

        for floor in self.floors:
            if floor == 0:
                continue

            floor_nodes = self.nodes_df[self.nodes_df['floor'] == floor]['node_id'].values
            n_nodes = len(floor_nodes)

            # Check if it's roof (max floor)
            if floor == max(self.floors):
                mass_per_node = roof_mass_kg / n_nodes
            else:
                mass_per_node = floor_mass_kg / n_nodes

            for node_id in floor_nodes:
                # Mass in X, Y, Z and rotational inertia
                ops.mass(int(node_id), mass_per_node, mass_per_node, mass_per_node / 10,
                        mass_per_node * 0.01, mass_per_node * 0.01, mass_per_node * 0.01)

        print("Model oluşturuldu.\n")

    def run_modal_analysis(self, n_modes=12):
        """Modal analiz - Eigenvalue analysis"""
        print("Modal analiz yapılıyor...")

        eigenvalues = ops.eigen('-fullGenLapack', n_modes)

        self.modal_results['eigenvalues'] = eigenvalues
        self.modal_results['periods'] = []
        self.modal_results['frequencies'] = []

        print(f"\n{'Mode':>4} {'Periyot (s)':>12} {'Frekans (Hz)':>14} {'Sae (g)':>10} {'Bölge':>15}")
        print("-" * 60)

        for i, eigenvalue in enumerate(eigenvalues):
            omega = np.sqrt(eigenvalue)
            freq = omega / (2 * np.pi)
            period = 1 / freq if freq > 0 else 0
            Sae = get_Sae(period, SPECTRUM_PARAMS)

            if period < SPECTRUM_PARAMS['TA']:
                region = "Yükselen"
            elif period <= SPECTRUM_PARAMS['TB']:
                region = "Plato"
            else:
                region = "Azalan"

            self.modal_results['periods'].append(period)
            self.modal_results['frequencies'].append(freq)

            print(f"{i+1:>4} {period:>12.6f} {freq:>14.4f} {Sae:>10.4f} {region:>15}")

        self.T1 = self.modal_results['periods'][0]
        print(f"\nHakim doğal titreşim periyodu T1 = {self.T1:.4f} s")

    def calculate_floor_geometry(self):
        """Her kat için geometri bilgilerini hesapla"""
        self.floor_geometry = {}

        for floor in self.floors:
            if floor == 0:
                continue

            floor_nodes = self.nodes_df[self.nodes_df['floor'] == floor]

            # Kat sınırları
            x_coords = floor_nodes['x'].values
            y_coords = floor_nodes['y'].values

            Lx = x_coords.max() - x_coords.min()
            Ly = y_coords.max() - y_coords.min()

            # Kütle merkezi (geometrik merkez varsayımı)
            cm_x = (x_coords.max() + x_coords.min()) / 2
            cm_y = (y_coords.max() + y_coords.min()) / 2

            # %5 ek dışmerkezlik
            ex_5 = 0.05 * Lx
            ey_5 = 0.05 * Ly

            self.floor_geometry[floor] = {
                'Lx': Lx,
                'Ly': Ly,
                'cm_x': cm_x,
                'cm_y': cm_y,
                'ex_5': ex_5,
                'ey_5': ey_5,
                'node_ids': floor_nodes['node_id'].values,
                'x_coords': x_coords,
                'y_coords': y_coords,
            }

    def apply_lateral_load_with_eccentricity(self, direction='X', ecc_sign=1):
        """
        TBDY 2018 Eşdeğer Deprem Yükü Yöntemi ile yatay yük uygula
        ±%5 ek dışmerkezlik dahil

        direction: 'X' veya 'Y' deprem doğrultusu
        ecc_sign: +1 veya -1 (dışmerkezlik işareti)
        """
        # Toplam kütle
        m_t = sum([1.6 for f in self.floors if f > 0 and f < max(self.floors)]) + 2.22

        # Tasarım spektral ivmesi
        SaR = get_SaR(self.T1, SPECTRUM_PARAMS)

        # Toplam taban kesme kuvveti (TBDY 2018 Denk. 4.19)
        g = 981.0  # cm/s²
        Vt = m_t * SaR * g / 1000  # kN

        # Minimum taban kesme kontrolü
        Vt_min = 0.04 * m_t * SPECTRUM_PARAMS['I'] * SPECTRUM_PARAMS['SDS'] * g / 1000
        if Vt < Vt_min:
            Vt = Vt_min

        print(f"\nDeprem doğrultusu: {direction}, Dışmerkezlik: {'+' if ecc_sign > 0 else '-'}%5")
        print(f"Toplam taban kesme kuvveti Vt = {Vt:.4f} kN")

        # Kat yükseklikleri ve kütleleri
        floor_heights = {}
        floor_masses = {}

        for floor in self.floors:
            if floor == 0:
                continue
            floor_nodes = self.nodes_df[self.nodes_df['floor'] == floor]
            z = floor_nodes['z'].values[0]
            floor_heights[floor] = z

            if floor == max(self.floors):
                floor_masses[floor] = 2.22
            else:
                floor_masses[floor] = 1.6

        # ΔF_NE - Tepeye ek eşdeğer deprem yükü (TBDY 2018 Denk. 4.22)
        N = max(self.floors)
        dF_NE = 0.0075 * N * Vt

        # Katlara dağıtılan kuvvetler (TBDY 2018 Denk. 4.23)
        sum_mH = sum([floor_masses[f] * floor_heights[f] for f in floor_masses])

        floor_forces = {}
        for floor in floor_masses:
            Fi = (Vt - dF_NE) * (floor_masses[floor] * floor_heights[floor]) / sum_mH
            if floor == max(self.floors):
                Fi += dF_NE
            floor_forces[floor] = Fi

        # Yükleri uygula - ek dışmerkezlik dahil
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)

        for floor in floor_forces:
            floor_nodes = self.nodes_df[self.nodes_df['floor'] == floor]['node_id'].values
            n_nodes = len(floor_nodes)
            force_per_node = floor_forces[floor] / n_nodes

            # Ek dışmerkezlik için burulma momenti (TBDY 2018 Denk. 4.17)
            geom = self.floor_geometry[floor]

            if direction == 'X':
                # X yönünde kuvvet, Y yönünde dışmerkezlik
                e = ecc_sign * geom['ey_5']
                M_torsion = floor_forces[floor] * e  # ek kat burulma momenti

                for node_id in floor_nodes:
                    ops.load(int(node_id), force_per_node, 0.0, 0.0, 0.0, 0.0, M_torsion / n_nodes)
            else:
                # Y yönünde kuvvet, X yönünde dışmerkezlik
                e = ecc_sign * geom['ex_5']
                M_torsion = floor_forces[floor] * e

                for node_id in floor_nodes:
                    ops.load(int(node_id), 0.0, force_per_node, 0.0, 0.0, 0.0, M_torsion / n_nodes)

        return floor_forces

    def run_static_analysis(self):
        """Statik analiz"""
        ops.system('BandSPD')
        ops.numberer('RCM')
        ops.constraints('Plain')
        ops.integrator('LoadControl', 1.0)
        ops.algorithm('Linear')
        ops.analysis('Static')

        ok = ops.analyze(1)

        if ok != 0:
            print("UYARI: Statik analiz yakınsamadı!")

        return ok == 0

    def get_floor_displacements(self, direction='X'):
        """
        Kat düğümlerindeki yer değiştirmeleri al
        DİYAFRAM YOK - her düğümün bireysel deplasmanı
        """
        floor_disp = {}

        for floor in self.floors:
            if floor == 0:
                continue

            floor_nodes = self.nodes_df[self.nodes_df['floor'] == floor]
            displacements = []

            for _, row in floor_nodes.iterrows():
                node_id = int(row['node_id'])
                x, y = row['x'], row['y']

                # Düğüm deplasmanını al
                disp = ops.nodeDisp(node_id)

                if direction == 'X':
                    d = disp[0]  # X yönü deplasmanı
                else:
                    d = disp[1]  # Y yönü deplasmanı

                displacements.append({
                    'node_id': node_id,
                    'x': x,
                    'y': y,
                    'disp': d,
                    'abs_disp': abs(d)
                })

            floor_disp[floor] = pd.DataFrame(displacements)

        return floor_disp

    def calculate_eta_bi(self, floor_disp, floor, direction='X'):
        """
        TBDY 2018 Denk. 3.6 - Burulma düzensizliği katsayısı

        η_bi = (Δ_i)_max / (Δ_i)_ort
        (Δ_i)_ort = 0.5 * [(Δ_i)_max + (Δ_i)_min]

        DİYAFRAM OLMADAN: Her düğümün deplasmanı ayrı ayrı
        """
        df = floor_disp[floor]

        # X veya Y yönündeki deplasmanlar
        disps = df['disp'].values

        # Deprem doğrultusuna dik yöndeki uç düğümler
        geom = self.floor_geometry[floor]

        if direction == 'X':
            # Y yönündeki uçlardaki deplasmanlar (burulma etkisini görmek için)
            y_min = df['y'].min()
            y_max = df['y'].max()

            disp_at_y_min = df[df['y'] == y_min]['disp'].values
            disp_at_y_max = df[df['y'] == y_max]['disp'].values

            # Maksimum ve minimum uç deplasmanları
            delta_max = max(abs(disp_at_y_min).max(), abs(disp_at_y_max).max())
            delta_min = min(abs(disp_at_y_min).min(), abs(disp_at_y_max).min())
        else:
            # X yönündeki uçlardaki deplasmanlar
            x_min = df['x'].min()
            x_max = df['x'].max()

            disp_at_x_min = df[df['x'] == x_min]['disp'].values
            disp_at_x_max = df[df['x'] == x_max]['disp'].values

            delta_max = max(abs(disp_at_x_min).max(), abs(disp_at_x_max).max())
            delta_min = min(abs(disp_at_x_min).min(), abs(disp_at_x_max).min())

        # Ortalama deplasman
        delta_ort = 0.5 * (delta_max + delta_min)

        # Burulma düzensizliği katsayısı
        if delta_ort > 1e-10:
            eta_bi = delta_max / delta_ort
        else:
            eta_bi = 1.0

        return {
            'delta_max': delta_max,
            'delta_min': delta_min,
            'delta_ort': delta_ort,
            'eta_bi': eta_bi,
        }

    def calculate_D_bi(self, eta_bi):
        """
        TBDY 2018 Denk. 4.29 - Ek dışmerkezlik büyütme katsayısı

        1.2 < η_bi ≤ 2.0 durumunda:
        D_bi = (η_bi / 1.2)²
        """
        if eta_bi <= 1.2:
            return 1.0
        elif eta_bi <= 2.0:
            return (eta_bi / 1.2) ** 2
        else:
            # η_bi > 2.0 durumunda yapı ruhsat alamaz (TBDY 2018)
            return (eta_bi / 1.2) ** 2  # Yine de hesapla, uyarı verilecek

    def run_full_torsion_analysis(self):
        """
        Tam burulma düzensizliği analizi
        Her iki doğrultu (X, Y) ve her iki dışmerkezlik işareti (+, -)
        """
        print("\n" + "=" * 60)
        print("A1a BURULMA DÜZENSİZLİĞİ ANALİZİ")
        print("TBDY 2018 Madde 3.6.2.1 ve 4.7.4")
        print("=" * 60)

        # Geometri hesapla
        self.calculate_floor_geometry()

        results = {}

        for direction in ['X', 'Y']:
            results[direction] = {}

            for ecc_sign in [+1, -1]:
                ecc_label = f"+{int(abs(ecc_sign)*5)}%" if ecc_sign > 0 else f"-{int(abs(ecc_sign)*5)}%"

                # Modeli yeniden oluştur
                self.build_model()

                # Modal analiz
                self.run_modal_analysis()

                # Yatay yük uygula
                self.apply_lateral_load_with_eccentricity(direction, ecc_sign)

                # Statik analiz
                success = self.run_static_analysis()

                if not success:
                    print(f"UYARI: {direction} yönü, {ecc_label} dışmerkezlik analizi başarısız!")
                    continue

                # Kat deplasmanlarını al
                floor_disp = self.get_floor_displacements(direction)

                # Her kat için η_bi hesapla
                floor_results = {}

                print(f"\n{direction} Doğrultusu, {ecc_label} Dışmerkezlik:")
                print(f"{'Kat':>4} {'δ_max (cm)':>12} {'δ_min (cm)':>12} {'δ_ort (cm)':>12} {'η_bi':>8} {'D_bi':>8} {'Durum':>15}")
                print("-" * 80)

                for floor in sorted(self.floors):
                    if floor == 0:
                        continue

                    eta_result = self.calculate_eta_bi(floor_disp, floor, direction)
                    D_bi = self.calculate_D_bi(eta_result['eta_bi'])

                    # Durum belirleme
                    eta = eta_result['eta_bi']
                    if eta <= 1.2:
                        status = "DÜZENLI"
                    elif eta <= 2.0:
                        status = f"A1a DÜZENSİZ (D={D_bi:.2f})"
                    else:
                        status = "RUHSAT VERİLEMEZ!"

                    floor_results[floor] = {
                        **eta_result,
                        'D_bi': D_bi,
                        'status': status,
                    }

                    print(f"{floor:>4} {eta_result['delta_max']:>12.6f} {eta_result['delta_min']:>12.6f} "
                          f"{eta_result['delta_ort']:>12.6f} {eta:>8.4f} {D_bi:>8.4f} {status:>15}")

                results[direction][ecc_label] = floor_results

                # Model temizle
                ops.wipe()

        self.torsion_results = results
        return results

    def get_critical_eta(self):
        """Her kat için kritik (maksimum) η_bi değerini bul"""
        critical = {}

        for floor in self.floors:
            if floor == 0:
                continue

            max_eta = 0
            critical_case = None

            for direction in self.torsion_results:
                for ecc_label in self.torsion_results[direction]:
                    if floor in self.torsion_results[direction][ecc_label]:
                        eta = self.torsion_results[direction][ecc_label][floor]['eta_bi']
                        if eta > max_eta:
                            max_eta = eta
                            critical_case = f"{direction}, {ecc_label}"

            D_bi = self.calculate_D_bi(max_eta)

            critical[floor] = {
                'eta_bi_max': max_eta,
                'D_bi': D_bi,
                'critical_case': critical_case,
                'is_irregular': max_eta > 1.2,
                'exceeds_limit': max_eta > 2.0,
            }

        return critical

    def save_results(self):
        """Sonuçları kaydet"""
        # Critical results
        critical = self.get_critical_eta()

        # Summary DataFrame
        summary_data = []
        for floor in sorted(critical.keys()):
            data = critical[floor]
            summary_data.append({
                'Kat': floor,
                'η_bi_max': data['eta_bi_max'],
                'D_bi': data['D_bi'],
                'Kritik Durum': data['critical_case'],
                'A1a Düzensiz': 'EVET' if data['is_irregular'] else 'HAYIR',
                'Sınır Aşımı (>2.0)': 'EVET' if data['exceeds_limit'] else 'HAYIR',
            })

        summary_df = pd.DataFrame(summary_data)
        summary_file = self.output_dir / 'torsion_irregularity_results.csv'
        summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')

        # Full results JSON
        json_results = {
            'analysis_info': {
                'code': 'TBDY 2018',
                'sections': ['3.6.2.1', '4.7.4'],
                'method': 'Eşdeğer Deprem Yükü Yöntemi',
                'diaphragm_constraint': False,
                'eccentricity': '±5%',
            },
            'spectrum_params': SPECTRUM_PARAMS,
            'material_props': MATERIAL_PROPS,
            'modal_results': {
                'T1': self.T1,
                'periods': self.modal_results['periods'][:6],
            },
            'critical_torsion_results': {
                str(k): v for k, v in critical.items()
            },
        }

        json_file = self.output_dir / 'torsion_analysis_full.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)

        print(f"\nSonuçlar kaydedildi:")
        print(f"  - {summary_file}")
        print(f"  - {json_file}")

        return summary_df, critical

    def print_final_summary(self, critical):
        """Final özet raporu"""
        print("\n" + "=" * 60)
        print("A1a BURULMA DÜZENSİZLİĞİ ANALİZİ - ÖZET")
        print("=" * 60)

        max_eta_all = max([critical[f]['eta_bi_max'] for f in critical])
        irregular_floors = [f for f in critical if critical[f]['is_irregular']]
        exceeds_limit_floors = [f for f in critical if critical[f]['exceeds_limit']]

        print(f"\nMaksimum η_bi (tüm katlar): {max_eta_all:.4f}")
        print(f"A1a düzensiz kat sayısı (η > 1.2): {len(irregular_floors)}")

        if irregular_floors:
            print(f"Düzensiz katlar: {irregular_floors}")

            # D_bi büyütme faktörleri
            print("\nEk Dışmerkezlik Büyütme Faktörleri (D_bi):")
            for floor in irregular_floors:
                D_bi = critical[floor]['D_bi']
                print(f"  Kat {floor}: D_bi = {D_bi:.4f}")

        if exceeds_limit_floors:
            print(f"\n⚠️  UYARI: η_bi > 2.0 olan katlar mevcut!")
            print(f"   Katlar: {exceeds_limit_floors}")
            print("   TBDY 2018'e göre bu yapıya ruhsat verilemez!")
        else:
            if max_eta_all <= 1.2:
                print("\n✓ Yapı A1a burulma düzensizliği açısından DÜZENLİ")
            else:
                print(f"\n⚠️  Yapı A1a burulma düzensiz (1.2 < η ≤ 2.0)")
                print("   Ek dışmerkezlik D_bi ile büyütülmelidir.")

        print("\n" + "=" * 60)


def main():
    """Ana fonksiyon"""
    # Paths
    base_dir = Path(__file__).parent
    position_file = base_dir / 'twin_position_matrix_v9.csv'
    connectivity_file = base_dir / 'twin_connectivity_matrix_v9.csv'
    output_dir = base_dir / 'results'

    # Analyzer
    analyzer = TorsionalIrregularityAnalyzer(
        position_file=str(position_file),
        connectivity_file=str(connectivity_file),
        output_dir=str(output_dir)
    )

    # Full analysis
    results = analyzer.run_full_torsion_analysis()

    # Get critical values
    critical = analyzer.get_critical_eta()

    # Save results
    summary_df, critical = analyzer.save_results()

    # Print final summary
    analyzer.print_final_summary(critical)

    print("\n✓ Analiz tamamlandı.")

    return analyzer, results, critical


if __name__ == '__main__':
    analyzer, results, critical = main()
