"""
DASK 2026 Twin Towers - Design Optimization
Based on competition rules (Proje Ön Şartnamesi 2026)

CONSTRAINTS:
- Section: 6x6 mm ONLY (cannot change)
- Shear walls: 3mm thick balsa plates allowed
- Weight limits:
  * 0-1.0 kg: No penalty
  * 1.0-1.3 kg: Cost penalty
  * >1.3 kg: DISQUALIFIED
- Current model: 1.38 kg -> MUST REDUCE!

OBJECTIVES:
1. Reduce weight to <1.0 kg (ideal) or <1.3 kg (minimum)
2. Increase Y-direction stiffness
3. Reduce drift from 24% to acceptable level
4. Maintain structural integrity
"""

import numpy as np
import pandas as pd
import os

print("=" * 70)
print("DASK 2026 - DESIGN OPTIMIZATION")
print("Competition Rules Analysis")
print("=" * 70)

# Material properties (from rules)
balsa = {
    'E_MPa': 3500,
    'rho_kg_m3': 160,
    'stick_section_mm': 6,  # FIXED - cannot change
    'stick_A_mm2': 36,
    'plate_thickness_mm': 3,  # For shear walls
}

# Current model data
current = {
    'nodes': 796,
    'elements': 2768,
    'total_length_mm': 239459,
    'weight_kg': 1.38,  # PROBLEM: Over 1.3kg limit!
}

# Weight calculation
current['calc_weight_kg'] = current['total_length_mm'] * balsa['stick_A_mm2'] * balsa['rho_kg_m3'] / 1e9

print(f"\n--- CURRENT MODEL STATUS ---")
print(f"  Total elements: {current['elements']}")
print(f"  Total length: {current['total_length_mm']:,.0f} mm")
print(f"  Weight: {current['weight_kg']:.3f} kg")
print(f"  Calculated: {current['calc_weight_kg']:.3f} kg")

# Competition weight limits
limits = {
    'optimal': 1.0,      # No penalty
    'penalty': 1.3,      # Cost penalty
    'disqualified': 1.3  # Hard limit
}

print(f"\n--- COMPETITION WEIGHT LIMITS ---")
print(f"  Optimal (no penalty): < {limits['optimal']} kg")
print(f"  With penalty: {limits['optimal']} - {limits['penalty']} kg")
print(f"  DISQUALIFIED: > {limits['penalty']} kg")
print(f"  Current: {current['weight_kg']:.3f} kg -> {'DISQUALIFIED!' if current['weight_kg'] > limits['penalty'] else 'OK'}")

# Required reduction
reduction_disq = current['weight_kg'] - limits['penalty']
reduction_optimal = current['weight_kg'] - limits['optimal']

print(f"\n  Weight to lose (avoid disqualification): {reduction_disq*1000:.0f} g")
print(f"  Weight to lose (no penalty): {reduction_optimal*1000:.0f} g")

# Element breakdown from previous analysis
elements = {
    'column': {'count': 744, 'avg_length': 65},
    'beam_x': {'count': 624, 'avg_length': 80},
    'beam_y': {'count': 520, 'avg_length': 40},
    'brace_xz': {'count': 216, 'avg_length': 100},
    'brace_yz': {'count': 64, 'avg_length': 72},
    'brace_floor': {'count': 116, 'avg_length': 56},
    'outrigger': {'count': 96, 'avg_length': 95},
    'belt_truss': {'count': 80, 'avg_length': 100},
    'brace_corner': {'count': 32, 'avg_length': 85},
    'core_wall': {'count': 80, 'avg_length': 68},
    'brace_space': {'count': 36, 'avg_length': 75},
    'bridge_total': {'count': 160, 'avg_length': 70},
}

print("\n" + "=" * 70)
print("ELEMENT WEIGHT ANALYSIS")
print("=" * 70)

print("\n{:<20} {:>8} {:>10} {:>12} {:>10}".format(
    "Element Type", "Count", "Avg Len", "Total Len", "Weight (g)"))
print("-" * 60)

total_weight_g = 0
element_weights = []

for etype, data in elements.items():
    total_len = data['count'] * data['avg_length']
    weight_g = total_len * balsa['stick_A_mm2'] * balsa['rho_kg_m3'] / 1e6
    total_weight_g += weight_g
    element_weights.append({
        'type': etype,
        'count': data['count'],
        'total_length': total_len,
        'weight_g': weight_g
    })
    print("{:<20} {:>8} {:>10} {:>12} {:>10.1f}".format(
        etype, data['count'], data['avg_length'], total_len, weight_g))

print("-" * 60)
print("{:<20} {:>8} {:>10} {:>12} {:>10.1f}".format(
    "TOTAL", sum(e['count'] for e in element_weights), "",
    sum(e['total_length'] for e in element_weights), total_weight_g))

# Sort by weight
element_weights.sort(key=lambda x: x['weight_g'], reverse=True)

print("\n" + "=" * 70)
print("OPTIMIZATION STRATEGIES")
print("=" * 70)

print("\n--- STRATEGY 1: REDUCE NON-CRITICAL BRACING ---")
print("Target: Remove ~100g of bracing while maintaining stiffness")

# Floor braces can be reduced
floor_brace_reduction = {
    'remove_count': 60,  # Remove 60 of 116 floor braces
    'length_saved': 60 * 56,
    'weight_saved_g': 60 * 56 * 36 * 160 / 1e6
}
print(f"  a) Reduce floor braces: -{floor_brace_reduction['remove_count']} elements")
print(f"     Weight saved: {floor_brace_reduction['weight_saved_g']:.1f} g")

# Space braces can be removed
space_brace_reduction = {
    'remove_count': 36,  # Remove all space braces
    'length_saved': 36 * 75,
    'weight_saved_g': 36 * 75 * 36 * 160 / 1e6
}
print(f"  b) Remove space braces: -{space_brace_reduction['remove_count']} elements")
print(f"     Weight saved: {space_brace_reduction['weight_saved_g']:.1f} g")

# Reduce XZ braces (dama pattern more aggressive)
xz_brace_reduction = {
    'remove_count': 80,  # Keep only essential XZ braces
    'length_saved': 80 * 100,
    'weight_saved_g': 80 * 100 * 36 * 160 / 1e6
}
print(f"  c) Reduce XZ braces: -{xz_brace_reduction['remove_count']} elements")
print(f"     Weight saved: {xz_brace_reduction['weight_saved_g']:.1f} g")

strategy1_total = (floor_brace_reduction['weight_saved_g'] + 
                   space_brace_reduction['weight_saved_g'] +
                   xz_brace_reduction['weight_saved_g'])
print(f"\n  Strategy 1 Total: -{strategy1_total:.0f} g")

print("\n--- STRATEGY 2: USE SHEAR WALLS (3mm plates) ---")
print("Replace braces with MORE EFFICIENT 3mm balsa plates")

# Shear wall efficiency: plate vs X-brace
# X-brace diagonal: 2 x 100mm x 6x6mm = 2 x 100 x 36 = 7200 mm³
# Plate (same bay): 100mm x 60mm x 3mm = 18000 mm³ but much stiffer!

# Actually, let's calculate properly
# For a 100x60mm bay:
# - X-brace option: 2 diagonals ~116mm each = 232mm total * 36mm² = 8352 mm³
# - Plate option: 100*60*3 = 18000 mm³ (heavier but MUCH stiffer)

# Better approach: smaller plates at key locations
shear_wall_strategy = {
    'location': 'Core Y-faces (both towers)',
    'per_tower_per_floor': 2,  # 2 faces
    'floors_with_plates': [1, 2, 3, 4, 5],  # Lower floors only
    'plate_size_mm': (40, 60, 3),  # width x height x thickness
}

plate_volume = shear_wall_strategy['plate_size_mm'][0] * shear_wall_strategy['plate_size_mm'][1] * shear_wall_strategy['plate_size_mm'][2]
total_plates = shear_wall_strategy['per_tower_per_floor'] * len(shear_wall_strategy['floors_with_plates']) * 2  # 2 towers
shear_wall_weight_g = total_plates * plate_volume * balsa['rho_kg_m3'] / 1e6

print(f"  Add shear wall plates at core (lower 5 floors)")
print(f"  Plate size: {shear_wall_strategy['plate_size_mm']} mm")
print(f"  Total plates: {total_plates}")
print(f"  Added weight: +{shear_wall_weight_g:.1f} g")
print(f"  Benefit: MAJOR Y-direction stiffness increase")

# Braces replaced by these plates
braces_replaced = len(shear_wall_strategy['floors_with_plates']) * 4 * 2  # 4 diagonals per floor, 2 towers
brace_weight_saved = braces_replaced * 72 * 36 * 160 / 1e6
print(f"  Braces replaced: {braces_replaced}")
print(f"  Weight saved from braces: -{brace_weight_saved:.1f} g")
print(f"  Net weight change: {shear_wall_weight_g - brace_weight_saved:.1f} g")

print("\n--- STRATEGY 3: OPTIMIZE BEAM LAYOUT ---")
# Beam optimization
beam_reduction = {
    'remove_intermediate_x': 150,  # Remove every other internal beam
    'avg_length': 80,
    'weight_saved_g': 150 * 80 * 36 * 160 / 1e6
}
print(f"  Remove intermediate X-beams: -{beam_reduction['remove_intermediate_x']} elements")
print(f"  Weight saved: {beam_reduction['weight_saved_g']:.1f} g")

print("\n--- STRATEGY 4: REDUCE FLOORS ---")
# Currently 26 floors = 90 + 25*60 = 1590mm (but we said 1530mm = 26 floors)
# Minimum is 20 floors
# Each floor removed saves: columns + beams + braces

floor_reduction = {
    'current_floors': 26,
    'new_floors': 22,  # Still above minimum 20
    'floors_removed': 4,
}

# Estimate weight per floor
columns_per_floor = 744 / 26  # ~28.6
beams_per_floor = (624 + 520) / 26  # ~44
braces_per_floor = (216 + 64) / 26  # ~10.8

weight_per_floor_g = (
    columns_per_floor * 60 * 36 * 160 / 1e6 +  # columns (60mm height)
    beams_per_floor * 60 * 36 * 160 / 1e6 +    # beams (avg 60mm)
    braces_per_floor * 85 * 36 * 160 / 1e6     # braces (avg diagonal)
)

floor_reduction['weight_saved_g'] = floor_reduction['floors_removed'] * weight_per_floor_g
floor_reduction['new_height_mm'] = 90 + (floor_reduction['new_floors'] - 1) * 60

print(f"  Reduce floors: {floor_reduction['current_floors']} -> {floor_reduction['new_floors']}")
print(f"  New height: {floor_reduction['new_height_mm']} mm")
print(f"  Weight saved: {floor_reduction['weight_saved_g']:.1f} g")
print(f"  Trade-off: Less rental income (lower NYK)")

print("\n" + "=" * 70)
print("RECOMMENDED OPTIMIZATION PLAN")
print("=" * 70)

# Combined strategy
print("\n--- PHASE 1: WEIGHT REDUCTION (to <1.0 kg) ---")
phase1_savings = strategy1_total + beam_reduction['weight_saved_g']
new_weight_phase1 = current['weight_kg'] * 1000 - phase1_savings

print(f"  1. Reduce floor braces (strategic only): -{floor_brace_reduction['weight_saved_g']:.0f} g")
print(f"  2. Remove space braces: -{space_brace_reduction['weight_saved_g']:.0f} g")
print(f"  3. Aggressive dama pattern on XZ: -{xz_brace_reduction['weight_saved_g']:.0f} g")
print(f"  4. Remove intermediate beams: -{beam_reduction['weight_saved_g']:.0f} g")
print(f"  ---------------------------------")
print(f"  Phase 1 savings: {phase1_savings:.0f} g")
print(f"  New weight: {new_weight_phase1:.0f} g ({new_weight_phase1/1000:.3f} kg)")

print("\n--- PHASE 2: ADD STIFFNESS (Y-DIRECTION) ---")
print(f"  1. Add shear wall plates at core (lower floors): +{shear_wall_weight_g:.0f} g")
print(f"  2. Add continuous Y-braces on short faces")
print(f"     (fewer but strategic placement)")

# Y-braces - optimized count
y_braces_optimized = {
    'floors': [1, 2, 3, 6, 12, 18, 24, 25],  # Key floors only
    'per_floor_per_tower': 2,
    'length': 72,
}
y_braces_count = len(y_braces_optimized['floors']) * y_braces_optimized['per_floor_per_tower'] * 2
y_braces_weight = y_braces_count * y_braces_optimized['length'] * 36 * 160 / 1e6
print(f"  Added Y-braces: {y_braces_count} at key floors")
print(f"  Added weight: +{y_braces_weight:.1f} g")

phase2_addition = shear_wall_weight_g + y_braces_weight - brace_weight_saved
print(f"\n  Phase 2 net addition: +{phase2_addition:.0f} g")

final_weight = new_weight_phase1 + phase2_addition
print(f"\n  FINAL WEIGHT: {final_weight:.0f} g ({final_weight/1000:.3f} kg)")
print(f"  Target: < 1000 g (no penalty) or < 1300 g (with penalty)")

if final_weight < 1000:
    print(f"  STATUS: OPTIMAL (no weight penalty)")
elif final_weight < 1300:
    print(f"  STATUS: ACCEPTABLE (weight penalty applies)")
else:
    print(f"  STATUS: NEEDS MORE REDUCTION")

print("\n" + "=" * 70)
print("KEY DESIGN CHANGES SUMMARY")
print("=" * 70)

print("""
1. BRACING OPTIMIZATION:
   - Floor braces: Keep only at stairs/core, remove from typical bays
   - XZ braces: More aggressive dama (every 4th instead of 3rd)
   - Remove all space braces (replaced by shear walls)

2. ADD SHEAR WALLS (3mm plates):
   - Core Y-faces, floors 1-5 (where Y-stiffness is most needed)
   - Small plates (40x60mm) at strategic locations
   - Much more efficient than equivalent braces

3. BEAM REDUCTION:
   - Remove intermediate floor beams
   - Keep perimeter and core beams only
   - Floor diaphragm via braces + plates

4. MAINTAIN:
   - All columns (essential for gravity)
   - Outriggers at 6, 12, 18, 24 (core to stiffness)
   - Belt trusses at 12, 24
   - Corner braces (critical for stability)
   - All 4 bridges (mandatory)

5. Y-DIRECTION STIFFNESS:
   - Shear wall plates at core
   - Y-braces at key floors (1,2,3,6,12,18,24,25)
   - Stiffer bridges (mandatory 2-story at top)
""")

# Save optimization plan
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results', 'data')
os.makedirs(output_dir, exist_ok=True)

optimization_plan = {
    'action': [
        'Reduce floor braces',
        'Remove space braces', 
        'Aggressive XZ dama',
        'Remove intermediate beams',
        'Add shear wall plates',
        'Add strategic Y-braces'
    ],
    'weight_change_g': [
        -floor_brace_reduction['weight_saved_g'],
        -space_brace_reduction['weight_saved_g'],
        -xz_brace_reduction['weight_saved_g'],
        -beam_reduction['weight_saved_g'],
        shear_wall_weight_g - brace_weight_saved,
        y_braces_weight
    ],
    'stiffness_effect': [
        'Minor decrease',
        'Replaced by plates',
        'Minor decrease X',
        'Diaphragm via braces',
        'MAJOR Y increase',
        'Moderate Y increase'
    ],
    'priority': [1, 1, 1, 2, 1, 1]
}

df = pd.DataFrame(optimization_plan)
df['cumulative_weight_g'] = current['weight_kg'] * 1000 + df['weight_change_g'].cumsum()
df.to_csv(os.path.join(output_dir, 'optimization_plan.csv'), index=False)

print(f"\nOptimization plan saved to: optimization_plan.csv")
print(f"\nTarget weight after optimization: {final_weight:.0f} g")
