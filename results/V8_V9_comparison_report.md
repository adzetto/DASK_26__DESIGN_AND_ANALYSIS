# MODEL V8 vs V9 COMPARISON REPORT
## DASK 2026 Twin Towers - 1:50 Scale Model

---

## EXECUTIVE SUMMARY

| Parameter | V8 | V9 (Stiffened) | Change |
|-----------|-----|----------------|--------|
| **Weight** | 1.389 kg | 1.398 kg | +9g |
| **T1 (Period)** | 0.200 s | 0.198 s | -1.0% |
| **f1 (Frequency)** | 5.00 Hz | 5.05 Hz | +1.0% |
| **Spectral Region** | Plateau | Plateau | Same |
| **Sae(T1) DD-2** | 1.008 g | 1.008 g | Same |

---

## MODEL CONFIGURATIONS

### V8 (Original)
- Shear walls: Up to floor 6
- Y-bracing: 64 elements (strategic locations)
- Floor bracing: Every 12 floors
- Beams: Standard configuration

### V9 (Stiffened)
- Shear walls: Up to floor 6 (same)
- Y-bracing: 80 elements at floors [0, 6, 12, 18, 24]
- Floor bracing: At floors 0, 12, 24 only
- Beams: Same as V8

---

## MODAL ANALYSIS RESULTS

### V8 Periods
| Mode | Period (s) | Freq (Hz) | Region (DD-2) |
|------|------------|-----------|---------------|
| 1 | 0.1999 | 5.00 | **Plateau** |
| 2 | 0.1471 | 6.80 | Plateau |
| 3 | 0.1348 | 7.42 | Plateau |
| 4 | 0.0643 | 15.54 | Ascending |

### V9 Periods
| Mode | Period (s) | Freq (Hz) | Region (DD-2) |
|------|------------|-----------|---------------|
| 1 | 0.1979 | 5.05 | **Plateau** |
| 2 | 0.1468 | 6.81 | Plateau |
| 3 | 0.1329 | 7.53 | Plateau |
| 4 | 0.0630 | 15.86 | Ascending |

---

## AFAD SPECTRUM ANALYSIS

### Corner Periods (TBDY 2018)
| DD Level | TA (s) | TB (s) | Required T1 for Ascending |
|----------|--------|--------|---------------------------|
| DD-1 | 0.104 | 0.518 | T < 0.104 s |
| DD-2 | 0.102 | 0.510 | T < 0.102 s |
| DD-3 | 0.088 | 0.438 | T < 0.088 s |
| DD-4 | 0.083 | 0.412 | T < 0.083 s |

### Current Status
- **V8 T1 = 0.200 s** → In Plateau (Maximum spectral demand)
- **V9 T1 = 0.198 s** → In Plateau (Maximum spectral demand)

---

## STIFFNESS REQUIREMENTS FOR ASCENDING REGION

To reach the **Ascending region** (T < TA), the period must be reduced significantly:

| Target | Required T1 | Current T1 | Reduction | Stiffness Increase |
|--------|-------------|------------|-----------|-------------------|
| DD-2 (TA = 0.102s) | < 0.100 s | 0.200 s | 50% | **4.0x** |
| DD-4 (TA = 0.083s) | < 0.080 s | 0.200 s | 60% | **6.25x** |

### Physical Interpretation
Since **T ∝ 1/√K** (period is inversely proportional to square root of stiffness):

- To halve the period: Need 4x the stiffness
- This would require significantly more bracing
- Weight increases proportionally with added bracing

### Weight Constraint Analysis
| Scenario | Weight | Feasibility |
|----------|--------|-------------|
| V8 (Current) | 1.389 kg | ✓ OK |
| V9 (Max bracing within limit) | 1.398 kg | ✓ OK |
| Ascending Target (4x stiffness) | ~2.5-3.0 kg | ✗ Exceeds 1.4 kg limit |

---

## CONCLUSION

**It is NOT possible to reach the Ascending spectral region while staying within the 1.4 kg weight limit.**

The fundamental physics:
1. Current model period T1 ≈ 0.20 s (5 Hz)
2. Ascending region requires T1 < 0.10 s (>10 Hz)
3. This needs ~4x stiffness increase
4. 4x stiffness would require ~2x weight increase
5. Weight limit prevents this

### Recommendations

1. **Accept Plateau Region**: The model will experience maximum spectral acceleration (Sae = SDS = 1.008g for DD-2). Design structural elements accordingly.

2. **Alternative: Reduce Mass**: If test weights could be reduced, the period would decrease:
   - Current mass: 15.02 kg (test loads)
   - T ∝ √(m/k), so reducing mass by 4x could halve the period
   - But this defeats the purpose of load testing

3. **Focus on Capacity**: Ensure the model can resist Sae = 1.008g at the plateau level rather than trying to reduce demand.

---

## GROUND MOTION SCALING

The scaled ground motion file has been prepared:
- **File**: `ground_motion/BOL090_scaled_1_50.AT2`
- **Scale Factor**: 1/√50 = 0.1414
- **Original PGA**: 0.822 g
- **Scaled PGA**: 0.116 g

---

## FILES GENERATED

1. `scripts/scale_ground_motion.py` - Ground motion scaling
2. `scripts/modal_analysis_v8_afad.py` - V8 modal analysis
3. `scripts/modal_analysis_v9_afad.py` - V9 modal analysis
4. `scripts/regenerate_twin_model_v9b.py` - V9 model generator
5. `ground_motion/BOL090_scaled_1_50.AT2` - Scaled ground motion
6. `results/data/modal_results_v8_afad.csv` - V8 results
7. `results/data/modal_results_v9_afad.csv` - V9 results
8. `exports/twin_towers_v9b_stiffened.dxf` - V9 DXF export

---

*Report generated: February 4, 2026*
*DASK 2026 Competition - Seismic Model Analysis*
