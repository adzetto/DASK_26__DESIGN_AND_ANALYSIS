"""
SCALE GROUND MOTION FOR 1:50 SCALE MODEL
=========================================
Scales the BOL090.AT2 ground motion by 1/sqrt(50) for shake table testing
of the 1:50 scale twin towers model.

Scale Model Similitude Theory:
- Geometric Scale: λ = 50
- Time Scale: λ_t = sqrt(λ) = sqrt(50) ≈ 7.071
- Acceleration Scale: 1/sqrt(λ) = 1/sqrt(50) ≈ 0.1414

For shake table testing, accelerations are scaled by 1/sqrt(scale) to maintain
proper dynamic similarity between prototype and model.
"""

import numpy as np
from pathlib import Path

print("=" * 70)
print("GROUND MOTION SCALING FOR 1:50 SCALE MODEL")
print("=" * 70)

# Scaling factor
SCALE = 50
SCALE_FACTOR = 1.0 / np.sqrt(SCALE)
print(f"\nScale Model: 1:{SCALE}")
print(f"Acceleration Scale Factor: 1/sqrt({SCALE}) = {SCALE_FACTOR:.6f}")

# Read original ground motion
GROUND_MOTION_DIR = Path(__file__).parent.parent / 'ground_motion'
INPUT_FILE = GROUND_MOTION_DIR / 'BOL090.AT2'
OUTPUT_FILE = GROUND_MOTION_DIR / 'BOL090_scaled_1_50.AT2'

print(f"\nReading: {INPUT_FILE.name}")

# Read the file
with open(INPUT_FILE, 'r') as f:
    lines = f.readlines()

# Parse header (first 4 lines)
header_lines = lines[:4]
data_lines = lines[4:]

# Extract metadata from header
# Line 1: Title
# Line 2: Event info
# Line 3: Units info
# Line 4: NPTS and DT
header_line4 = header_lines[3]
npts_str = header_line4.split('NPTS=')[1].split(',')[0].strip()
dt_str = header_line4.split('DT=')[1].split('SEC')[0].strip()
NPTS = int(npts_str)
DT = float(dt_str)

print(f"Original Motion Parameters:")
print(f"  NPTS: {NPTS}")
print(f"  DT: {DT} sec")
print(f"  Duration: {NPTS * DT:.2f} sec")

# Parse acceleration data (in G units)
accelerations = []
for line in data_lines:
    values = line.split()
    for val in values:
        try:
            accelerations.append(float(val))
        except ValueError:
            continue

accelerations = np.array(accelerations[:NPTS])

# Statistics of original motion
max_acc_orig = np.max(np.abs(accelerations))
pga_orig = max_acc_orig
print(f"\nOriginal Ground Motion Statistics:")
print(f"  PGA: {pga_orig:.6f} g ({pga_orig * 9.81:.3f} m/s²)")
print(f"  Max Acceleration: {max_acc_orig:.6f} g")
print(f"  Mean: {np.mean(accelerations):.6e} g")
print(f"  Std Dev: {np.std(accelerations):.6f} g")

# Scale accelerations
scaled_accelerations = accelerations * SCALE_FACTOR

# Statistics of scaled motion
max_acc_scaled = np.max(np.abs(scaled_accelerations))
pga_scaled = max_acc_scaled
print(f"\nScaled Ground Motion Statistics (1:{SCALE}):")
print(f"  PGA: {pga_scaled:.6f} g ({pga_scaled * 9.81:.3f} m/s²)")
print(f"  Max Acceleration: {max_acc_scaled:.6f} g")
print(f"  Mean: {np.mean(scaled_accelerations):.6e} g")
print(f"  Std Dev: {np.std(scaled_accelerations):.6f} g")
print(f"  Scaling Ratio: {max_acc_scaled / max_acc_orig:.6f}")

# Write scaled ground motion file
print(f"\nWriting scaled ground motion: {OUTPUT_FILE.name}")

with open(OUTPUT_FILE, 'w') as f:
    # Write modified header
    f.write(header_lines[0])  # Title
    f.write(header_lines[1])  # Event info
    # Modify line 3 to indicate scaling
    f.write("ACCELERATION TIME HISTORY IN UNITS OF G. SCALED BY 1/sqrt(50)=0.1414 FOR 1:50 MODEL\n")
    f.write(header_lines[3])  # NPTS and DT

    # Write scaled accelerations (8 values per line in scientific notation)
    for i in range(0, len(scaled_accelerations), 8):
        values = scaled_accelerations[i:i+8]
        line = ''.join([f'{val:15.7E}' for val in values])
        f.write(line + '\n')

print(f"[OK] Scaled ground motion saved successfully!")

# Also save as numpy binary for OpenSees
NPY_FILE = GROUND_MOTION_DIR / 'BOL090_scaled_1_50.npy'
np.save(NPY_FILE, scaled_accelerations)
print(f"[OK] Numpy binary saved: {NPY_FILE.name}")

# Save metadata
METADATA_FILE = GROUND_MOTION_DIR / 'BOL090_scaled_1_50_metadata.txt'
with open(METADATA_FILE, 'w') as f:
    f.write("SCALED GROUND MOTION METADATA\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Original File: BOL090.AT2\n")
    f.write(f"Scaled File: BOL090_scaled_1_50.AT2\n\n")
    f.write(f"Scale Model: 1:{SCALE}\n")
    f.write(f"Acceleration Scale Factor: 1/sqrt({SCALE}) = {SCALE_FACTOR:.6f}\n")
    f.write(f"Time Scale Factor: sqrt({SCALE}) = {np.sqrt(SCALE):.3f}\n\n")
    f.write(f"Original PGA: {pga_orig:.6f} g ({pga_orig * 9.81:.3f} m/s²)\n")
    f.write(f"Scaled PGA: {pga_scaled:.6f} g ({pga_scaled * 9.81:.3f} m/s²)\n\n")
    f.write(f"NPTS: {NPTS}\n")
    f.write(f"DT: {DT} sec\n")
    f.write(f"Duration: {NPTS * DT:.2f} sec\n")

print(f"[OK] Metadata saved: {METADATA_FILE.name}")

print("\n" + "=" * 70)
print("SCALING COMPLETE!")
print("=" * 70)
print(f"\nUse '{OUTPUT_FILE.name}' for OpenSees time history analysis")
print(f"on the 1:50 scale Model V8.")
