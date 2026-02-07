#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TBDY 2018 A1a Burulma Düzensizliği Analizi - Basitleştirilmiş Versiyon
======================================================================
Mevcut modal analiz sonuçlarını kullanarak burulma düzensizliği hesabı.

TBDY 2018 Madde 3.6.2.1 ve 4.7.4:
- η_bi = (Δ_i^(X))_max / (Δ_i^(X))_ort > 1.2 ise A1a burulma düzensizliği
- 1.2 < η_bi ≤ 2.0 durumunda D_bi = (η_bi / 1.2)² büyütme faktörü

Author: DASK 2026 Analysis Pipeline
Date: 2026-02
"""

import numpy as np
import pandas as pd
import json
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# =============================================================================
# TBDY 2018 SPECTRUM PARAMETERS (DD-2, ZD Soil, Istanbul)
# =============================================================================
SPECTRUM_PARAMS = {
    'SDS': 1.008,
    'SD1': 0.514,
    'TA': 0.102,
    'TB': 0.51,
    'TL': 6.0,
    'PGA': 0.362,
    'I': 1.0,
    'R': 4.0,
    'D': 2.5,
}

# Material properties (1:50 scale model)
MATERIAL_PROPS = {
    'E_kN_cm2': 170.0,
    'G_kN_cm2': 65.385,
    'section_cm': 0.6,
}


def get_Sae(T, params):
    """TBDY 2018 Denk. 2.2"""
    SDS, SD1, TA, TB, TL = params['SDS'], params['SD1'], params['TA'], params['TB'], params['TL']
    if T < TA:
        return (0.4 + 0.6 * T / TA) * SDS
    elif T <= TB:
        return SDS
    elif T <= TL:
        return SD1 / T
    else:
        return SD1 * TL / (T * T)


def get_SaR(T, params):
    """TBDY 2018 Denk. 4.8"""
    Sae = get_Sae(T, params)
    R, D, TB, I = params['R'], params['D'], params['TB'], params['I']
    Ra = R / I if T > TB else D + (R / I - D) * T / TB
    return Sae / Ra


class SimpleTorsionAnalyzer:
    """Basitleştirilmiş burulma düzensizliği analizi"""

    def __init__(self, position_file, output_dir):
        self.nodes_df = pd.read_csv(position_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Floor info
        self.floors = sorted(self.nodes_df['floor'].unique())
        self.floor_heights = {}
        self.floor_geometry = {}

        # Calibrated T1 from previous analysis
        self.T1 = 0.048  # From modal_analysis_calibrated.json

        self._calculate_floor_geometry()

    def _calculate_floor_geometry(self):
        """Her kat için geometri bilgileri"""
        for floor in self.floors:
            floor_nodes = self.nodes_df[self.nodes_df['floor'] == floor]

            if len(floor_nodes) == 0:
                continue

            x_coords = floor_nodes['x'].values
            y_coords = floor_nodes['y'].values
            z = floor_nodes['z'].values[0]

            # Kat boyutları
            Lx = x_coords.max() - x_coords.min()
            Ly = y_coords.max() - y_coords.min()

            # Geometrik merkez
            cm_x = (x_coords.max() + x_coords.min()) / 2
            cm_y = (y_coords.max() + y_coords.min()) / 2

            # %5 ek dışmerkezlik
            ex_5 = 0.05 * Lx
            ey_5 = 0.05 * Ly

            self.floor_heights[floor] = z
            self.floor_geometry[floor] = {
                'Lx': Lx,
                'Ly': Ly,
                'cm_x': cm_x,
                'cm_y': cm_y,
                'ex_5': ex_5,
                'ey_5': ey_5,
                'x_min': x_coords.min(),
                'x_max': x_coords.max(),
                'y_min': y_coords.min(),
                'y_max': y_coords.max(),
            }

    def calculate_equivalent_lateral_forces(self):
        """TBDY 2018 Eşdeğer Deprem Yükü Yöntemi"""
        # Kat kütleleri (her tower için)
        floor_mass = 1.6  # kg per floor
        roof_mass = 2.22  # kg for roof

        # Toplam kütle
        n_floors = len([f for f in self.floors if f > 0])
        m_t = floor_mass * (n_floors - 1) + roof_mass

        # Tasarım spektral ivmesi
        SaR = get_SaR(self.T1, SPECTRUM_PARAMS)
        g = 981.0  # cm/s²

        # Toplam taban kesme kuvveti (TBDY 2018 Denk. 4.19)
        Vt = m_t * SaR * g / 1000  # kN
        Vt_min = 0.04 * m_t * SPECTRUM_PARAMS['I'] * SPECTRUM_PARAMS['SDS'] * g / 1000
        Vt = max(Vt, Vt_min)

        # ΔF_NE (TBDY 2018 Denk. 4.22)
        N = max(self.floors)
        dF_NE = 0.0075 * N * Vt

        # ∑(m_i * H_i)
        sum_mH = 0
        floor_masses = {}
        for floor in self.floors:
            if floor == 0:
                continue
            if floor == max(self.floors):
                floor_masses[floor] = roof_mass
            else:
                floor_masses[floor] = floor_mass
            sum_mH += floor_masses[floor] * self.floor_heights[floor]

        # Kat kuvvetleri (TBDY 2018 Denk. 4.23)
        floor_forces = {}
        for floor in floor_masses:
            Fi = (Vt - dF_NE) * (floor_masses[floor] * self.floor_heights[floor]) / sum_mH
            if floor == max(self.floors):
                Fi += dF_NE
            floor_forces[floor] = Fi

        return Vt, floor_forces, floor_masses

    def estimate_floor_displacements(self, direction='X', ecc_sign=1):
        """
        Basitleştirilmiş deplasman tahmini.
        Rijitlik merkezi ile kütle merkezi arasındaki eksantrisiteye dayalı.
        """
        Vt, floor_forces, floor_masses = self.calculate_equivalent_lateral_forces()

        # Elastisite ve kesit özellikleri
        E = MATERIAL_PROPS['E_kN_cm2']
        I = (MATERIAL_PROPS['section_cm'] ** 4) / 12

        # Basitleştirilmiş rijitlik tahmini (moment frame + braces)
        # Her katta 64 kolon var (32 per tower, 8x4 grid)
        n_columns = 64
        h_story = 6.0  # cm (ortalama kat yüksekliği)

        # Kolon rijitliği (12EI/L³ konsol formülü)
        k_column = 12 * E * I / (h_story ** 3)  # kN/cm per column
        k_story = k_column * n_columns  # Total story stiffness

        # Çapraz elemanlardan ek rijitlik (yaklaşık 3x artış)
        k_story_total = k_story * 3

        floor_displacements = {}

        for floor in sorted(self.floors):
            if floor == 0:
                continue

            geom = self.floor_geometry[floor]

            # Toplam yatay yük (bu kat ve üstü)
            V_floor = sum([floor_forces[f] for f in floor_forces if f >= floor])

            # Ortalama deplasman
            delta_avg = V_floor / k_story_total

            # Burulma etkisi - ek dışmerkezlikten
            if direction == 'X':
                e = ecc_sign * geom['ey_5']  # Y yönünde dışmerkezlik
                L_torsion = geom['Ly']
            else:
                e = ecc_sign * geom['ex_5']  # X yönünde dışmerkezlik
                L_torsion = geom['Lx']

            # Burulma momenti
            M_torsion = V_floor * abs(e)

            # Burulma rijitliği (yaklaşık)
            # J_polar ≈ Ix + Iy for the floor plate
            J_polar = (geom['Lx']**2 + geom['Ly']**2) / 12  # Approximate
            k_torsion = k_story_total * J_polar / 10  # Simplified torsional stiffness

            # Burulma açısı
            theta = M_torsion / k_torsion if k_torsion > 0 else 0

            # Uç deplasmanları
            delta_torsion = theta * (L_torsion / 2)

            # Max ve min deplasmanlar
            delta_max = abs(delta_avg) + abs(delta_torsion)
            delta_min = abs(delta_avg) - abs(delta_torsion)
            delta_min = max(delta_min, delta_avg * 0.5)  # Alt sınır

            floor_displacements[floor] = {
                'delta_avg': delta_avg,
                'delta_max': delta_max,
                'delta_min': delta_min,
                'V_floor': V_floor,
                'theta': theta,
            }

        return floor_displacements

    def calculate_eta_bi(self, floor_disp, floor):
        """
        TBDY 2018 Denk. 3.6 - Burulma düzensizliği katsayısı
        η_bi = (Δ_i)_max / (Δ_i)_ort
        (Δ_i)_ort = 0.5 * [(Δ_i)_max + (Δ_i)_min]
        """
        data = floor_disp[floor]
        delta_max = data['delta_max']
        delta_min = data['delta_min']

        delta_ort = 0.5 * (delta_max + delta_min)

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
        D_bi = (η_bi / 1.2)² for 1.2 < η_bi ≤ 2.0
        """
        if eta_bi <= 1.2:
            return 1.0
        else:
            return (eta_bi / 1.2) ** 2

    def run_analysis(self):
        """Tam analizi çalıştır"""
        print("=" * 60)
        print("TBDY 2018 A1a BURULMA DÜZENSİZLİĞİ ANALİZİ")
        print("Basitleştirilmiş Hesap Yöntemi")
        print("=" * 60)

        # Eşdeğer deprem yükü
        Vt, floor_forces, _ = self.calculate_equivalent_lateral_forces()
        print(f"\nHakim periyot T1 = {self.T1:.4f} s")
        print(f"Toplam taban kesme kuvveti Vt = {Vt:.6f} kN")

        results = {}

        for direction in ['X', 'Y']:
            results[direction] = {}

            for ecc_sign in [+1, -1]:
                ecc_label = f"+5%" if ecc_sign > 0 else f"-5%"

                # Deplasman hesabı
                floor_disp = self.estimate_floor_displacements(direction, ecc_sign)

                print(f"\n{direction} Doğrultusu, {ecc_label} Dışmerkezlik:")
                print(f"{'Kat':>4} {'δ_max':>12} {'δ_min':>12} {'δ_ort':>12} {'η_bi':>8} {'D_bi':>8} {'Durum':>18}")
                print("-" * 85)

                floor_results = {}
                for floor in sorted(self.floors):
                    if floor == 0:
                        continue

                    eta_result = self.calculate_eta_bi(floor_disp, floor)
                    D_bi = self.calculate_D_bi(eta_result['eta_bi'])

                    eta = eta_result['eta_bi']
                    if eta <= 1.2:
                        status = "DÜZENLI"
                    elif eta <= 2.0:
                        status = f"A1a DÜZENSIZ (D={D_bi:.2f})"
                    else:
                        status = "RUHSAT VERILEMEZ!"

                    floor_results[floor] = {
                        **eta_result,
                        'D_bi': D_bi,
                        'status': status,
                    }

                    print(f"{floor:>4} {eta_result['delta_max']:>12.8f} {eta_result['delta_min']:>12.8f} "
                          f"{eta_result['delta_ort']:>12.8f} {eta:>8.4f} {D_bi:>8.4f} {status:>18}")

                results[direction][ecc_label] = floor_results

        self.results = results
        return results

    def get_critical_results(self):
        """Her kat için kritik η_bi değeri"""
        critical = {}

        for floor in self.floors:
            if floor == 0:
                continue

            max_eta = 0
            critical_case = None

            for direction in self.results:
                for ecc_label in self.results[direction]:
                    if floor in self.results[direction][ecc_label]:
                        eta = self.results[direction][ecc_label][floor]['eta_bi']
                        if eta > max_eta:
                            max_eta = eta
                            critical_case = f"{direction}, {ecc_label}"

            D_bi = self.calculate_D_bi(max_eta)

            critical[floor] = {
                'eta_bi_max': float(max_eta),
                'D_bi': float(D_bi),
                'critical_case': critical_case,
                'is_irregular': bool(max_eta > 1.2),
                'exceeds_limit': bool(max_eta > 2.0),
            }

        return critical

    def save_results(self):
        """Sonuçları kaydet"""
        critical = self.get_critical_results()

        # CSV
        summary_data = []
        for floor in sorted(critical.keys()):
            data = critical[floor]
            summary_data.append({
                'Kat': floor,
                'eta_bi_max': data['eta_bi_max'],
                'D_bi': data['D_bi'],
                'Kritik_Durum': data['critical_case'],
                'A1a_Duzensiz': 'EVET' if data['is_irregular'] else 'HAYIR',
                'Sinir_Asimi': 'EVET' if data['exceeds_limit'] else 'HAYIR',
            })

        summary_df = pd.DataFrame(summary_data)
        csv_file = self.output_dir / 'torsion_irregularity_results.csv'
        summary_df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        # JSON
        json_results = {
            'analysis_info': {
                'code': 'TBDY 2018',
                'sections': ['3.6.2.1', '4.7.4'],
                'method': 'Simplified Equivalent Lateral Force',
                'T1': self.T1,
            },
            'spectrum_params': SPECTRUM_PARAMS,
            'critical_results': {str(k): v for k, v in critical.items()},
        }

        json_file = self.output_dir / 'torsion_analysis_results.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)

        print(f"\nSonuçlar kaydedildi:")
        print(f"  - {csv_file}")
        print(f"  - {json_file}")

        return summary_df, critical

    def print_summary(self):
        """Özet rapor"""
        critical = self.get_critical_results()

        print("\n" + "=" * 60)
        print("ÖZET RAPOR")
        print("=" * 60)

        max_eta = max([critical[f]['eta_bi_max'] for f in critical])
        irregular_floors = [f for f in critical if critical[f]['is_irregular']]

        print(f"\nMaksimum η_bi (tüm katlar): {max_eta:.4f}")
        print(f"A1a düzensiz kat sayısı: {len(irregular_floors)}")

        if irregular_floors:
            print(f"Düzensiz katlar: {irregular_floors}")
            print("\nD_bi Büyütme Faktörleri:")
            for f in irregular_floors:
                print(f"  Kat {f}: D_bi = {critical[f]['D_bi']:.4f}")

        if max_eta <= 1.2:
            print("\n✓ Yapı A1a burulma düzensizliği açısından DÜZENLİ")
        elif max_eta <= 2.0:
            print(f"\n⚠ Yapı A1a burulma düzensiz (1.2 < η ≤ 2.0)")
            print("  Ek dışmerkezlik D_bi ile büyütülmelidir.")
        else:
            print(f"\n✗ η_bi > 2.0! TBDY 2018'e göre ruhsat verilemez!")

        print("=" * 60)


def main():
    base_dir = Path(__file__).parent
    position_file = base_dir / 'twin_position_matrix_v9.csv'
    output_dir = base_dir / 'results'

    analyzer = SimpleTorsionAnalyzer(
        position_file=str(position_file),
        output_dir=str(output_dir)
    )

    analyzer.run_analysis()
    analyzer.save_results()
    analyzer.print_summary()

    print("\n✓ Analiz tamamlandı.")


if __name__ == '__main__':
    main()
