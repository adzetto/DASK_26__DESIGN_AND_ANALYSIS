# ============================================================================
# TBDY 2018 A1a TORSIONAL IRREGULARITY ANALYSIS
# OpenSees Tcl Script - Twin Towers Model V9
# ============================================================================
# Generated: 2026-02-05 13:37:31
# Model: 1:50 Scale Twin Towers with Sky Bridges
# Code: TBDY 2018 (Turkish Building Seismic Code)
# Sections: 3.6.2.1 (A1a Torsional Irregularity), 4.7.4 (Eccentricity Amplification)
# ============================================================================

puts "============================================================"
puts "  TBDY 2018 A1a TORSIONAL IRREGULARITY ANALYSIS"
puts "  OpenSees Tcl Script - Twin Towers Model V9"
puts "============================================================"
puts ""
puts ">>> Starting analysis..."
puts ""

# ============================================================================
# CLEAR ANY PREVIOUS MODEL
# ============================================================================
wipe
puts ">>> Previous model cleared"

# ============================================================================
# MODEL PARAMETERS
# ============================================================================
puts ""
puts "============================================================"
puts "  MODEL PARAMETERS"
puts "============================================================"

# Material Properties (1:50 scale model)
set E 170.0              ;# Elastic modulus (kN/cm2)
set G 65.385           ;# Shear modulus (kN/cm2)
set nu 0.3              ;# Poisson's ratio

# Section Properties (6mm x 6mm square section)
set section 0.6           ;# Section dimension (cm)
set A 0.36            ;# Cross-sectional area (cm2)
set Iz 0.010799999999999999  ;# Moment of inertia about z-axis (cm4)
set Iy $Iz             ;# Moment of inertia about y-axis (cm4)
set J 0.018224999999999998  ;# Torsional constant (cm4)

puts "  E  = $E kN/cm2"
puts "  G  = $G kN/cm2"
puts "  A  = $A cm2"
puts "  Iz = $Iz cm4"
puts "  J  = $J cm4"

# TBDY 2018 Spectrum Parameters (DD-2, ZD Soil, Istanbul)
set SDS 1.008             ;# Short period design spectral acceleration (g)
set SD1 0.514             ;# 1-sec period design spectral acceleration (g)
set TA 0.102             ;# Spectrum corner period TA (s)
set TB 0.51              ;# Spectrum corner period TB (s)
set R 4.0               ;# Response modification factor
set D 2.5               ;# Overstrength factor
set I 1.0               ;# Importance factor

puts ""
puts "  TBDY 2018 Spectrum Parameters:"
puts "  SDS = $SDS g"
puts "  SD1 = $SD1 g"
puts "  TA  = $TA s"
puts "  TB  = $TB s"
puts "  R   = $R"
puts "  D   = $D"

# ============================================================================
# MODEL DEFINITION
# ============================================================================
puts ""
puts "============================================================"
puts "  CREATING 3D MODEL"
puts "============================================================"

model BasicBuilder -ndm 3 -ndf 6
puts ">>> 3D model with 6 DOF per node created"

# ============================================================================
# NODE DEFINITIONS
# ============================================================================
puts ""
puts ">>> Defining nodes..."

set numNodes 1680
set numFloors 25

# Node definitions: node nodeTag x y z
node 0 0.000000 0.000000 0.000000  ;# Floor 0, Tower 1
node 1 0.000000 7.400000 0.000000  ;# Floor 0, Tower 1
node 2 0.000000 8.600000 0.000000  ;# Floor 0, Tower 1
node 3 0.000000 16.000000 0.000000  ;# Floor 0, Tower 1
node 4 3.000000 0.000000 0.000000  ;# Floor 0, Tower 1
node 5 3.000000 7.400000 0.000000  ;# Floor 0, Tower 1
node 6 3.000000 8.600000 0.000000  ;# Floor 0, Tower 1
node 7 3.000000 16.000000 0.000000  ;# Floor 0, Tower 1
node 8 11.000000 0.000000 0.000000  ;# Floor 0, Tower 1
node 9 11.000000 7.400000 0.000000  ;# Floor 0, Tower 1
node 10 11.000000 8.600000 0.000000  ;# Floor 0, Tower 1
node 11 11.000000 16.000000 0.000000  ;# Floor 0, Tower 1
node 12 14.400000 0.000000 0.000000  ;# Floor 0, Tower 1
node 13 14.400000 7.400000 0.000000  ;# Floor 0, Tower 1
node 14 14.400000 8.600000 0.000000  ;# Floor 0, Tower 1
node 15 14.400000 16.000000 0.000000  ;# Floor 0, Tower 1
node 16 15.600000 0.000000 0.000000  ;# Floor 0, Tower 1
node 17 15.600000 7.400000 0.000000  ;# Floor 0, Tower 1
node 18 15.600000 8.600000 0.000000  ;# Floor 0, Tower 1
node 19 15.600000 16.000000 0.000000  ;# Floor 0, Tower 1
node 20 19.000000 0.000000 0.000000  ;# Floor 0, Tower 1
node 21 19.000000 7.400000 0.000000  ;# Floor 0, Tower 1
node 22 19.000000 8.600000 0.000000  ;# Floor 0, Tower 1
node 23 19.000000 16.000000 0.000000  ;# Floor 0, Tower 1
node 24 27.000000 0.000000 0.000000  ;# Floor 0, Tower 1
node 25 27.000000 7.400000 0.000000  ;# Floor 0, Tower 1
node 26 27.000000 8.600000 0.000000  ;# Floor 0, Tower 1
node 27 27.000000 16.000000 0.000000  ;# Floor 0, Tower 1
node 28 30.000000 0.000000 0.000000  ;# Floor 0, Tower 1
node 29 30.000000 7.400000 0.000000  ;# Floor 0, Tower 1
node 30 30.000000 8.600000 0.000000  ;# Floor 0, Tower 1
node 31 30.000000 16.000000 0.000000  ;# Floor 0, Tower 1
node 32 0.000000 0.000000 9.000000  ;# Floor 1, Tower 1
node 33 0.000000 7.400000 9.000000  ;# Floor 1, Tower 1
node 34 0.000000 8.600000 9.000000  ;# Floor 1, Tower 1
node 35 0.000000 16.000000 9.000000  ;# Floor 1, Tower 1
node 36 3.000000 0.000000 9.000000  ;# Floor 1, Tower 1
node 37 3.000000 7.400000 9.000000  ;# Floor 1, Tower 1
node 38 3.000000 8.600000 9.000000  ;# Floor 1, Tower 1
node 39 3.000000 16.000000 9.000000  ;# Floor 1, Tower 1
node 40 11.000000 0.000000 9.000000  ;# Floor 1, Tower 1
node 41 11.000000 7.400000 9.000000  ;# Floor 1, Tower 1
node 42 11.000000 8.600000 9.000000  ;# Floor 1, Tower 1
node 43 11.000000 16.000000 9.000000  ;# Floor 1, Tower 1
node 44 14.400000 0.000000 9.000000  ;# Floor 1, Tower 1
node 45 14.400000 7.400000 9.000000  ;# Floor 1, Tower 1
node 46 14.400000 8.600000 9.000000  ;# Floor 1, Tower 1
node 47 14.400000 16.000000 9.000000  ;# Floor 1, Tower 1
node 48 15.600000 0.000000 9.000000  ;# Floor 1, Tower 1
node 49 15.600000 7.400000 9.000000  ;# Floor 1, Tower 1
node 50 15.600000 8.600000 9.000000  ;# Floor 1, Tower 1
node 51 15.600000 16.000000 9.000000  ;# Floor 1, Tower 1
node 52 19.000000 0.000000 9.000000  ;# Floor 1, Tower 1
node 53 19.000000 7.400000 9.000000  ;# Floor 1, Tower 1
node 54 19.000000 8.600000 9.000000  ;# Floor 1, Tower 1
node 55 19.000000 16.000000 9.000000  ;# Floor 1, Tower 1
node 56 27.000000 0.000000 9.000000  ;# Floor 1, Tower 1
node 57 27.000000 7.400000 9.000000  ;# Floor 1, Tower 1
node 58 27.000000 8.600000 9.000000  ;# Floor 1, Tower 1
node 59 27.000000 16.000000 9.000000  ;# Floor 1, Tower 1
node 60 30.000000 0.000000 9.000000  ;# Floor 1, Tower 1
node 61 30.000000 7.400000 9.000000  ;# Floor 1, Tower 1
node 62 30.000000 8.600000 9.000000  ;# Floor 1, Tower 1
node 63 30.000000 16.000000 9.000000  ;# Floor 1, Tower 1
node 64 0.000000 0.000000 15.000000  ;# Floor 2, Tower 1
node 65 0.000000 7.400000 15.000000  ;# Floor 2, Tower 1
node 66 0.000000 8.600000 15.000000  ;# Floor 2, Tower 1
node 67 0.000000 16.000000 15.000000  ;# Floor 2, Tower 1
node 68 3.000000 0.000000 15.000000  ;# Floor 2, Tower 1
node 69 3.000000 7.400000 15.000000  ;# Floor 2, Tower 1
node 70 3.000000 8.600000 15.000000  ;# Floor 2, Tower 1
node 71 3.000000 16.000000 15.000000  ;# Floor 2, Tower 1
node 72 11.000000 0.000000 15.000000  ;# Floor 2, Tower 1
node 73 11.000000 7.400000 15.000000  ;# Floor 2, Tower 1
node 74 11.000000 8.600000 15.000000  ;# Floor 2, Tower 1
node 75 11.000000 16.000000 15.000000  ;# Floor 2, Tower 1
node 76 14.400000 0.000000 15.000000  ;# Floor 2, Tower 1
node 77 14.400000 7.400000 15.000000  ;# Floor 2, Tower 1
node 78 14.400000 8.600000 15.000000  ;# Floor 2, Tower 1
node 79 14.400000 16.000000 15.000000  ;# Floor 2, Tower 1
node 80 15.600000 0.000000 15.000000  ;# Floor 2, Tower 1
node 81 15.600000 7.400000 15.000000  ;# Floor 2, Tower 1
node 82 15.600000 8.600000 15.000000  ;# Floor 2, Tower 1
node 83 15.600000 16.000000 15.000000  ;# Floor 2, Tower 1
node 84 19.000000 0.000000 15.000000  ;# Floor 2, Tower 1
node 85 19.000000 7.400000 15.000000  ;# Floor 2, Tower 1
node 86 19.000000 8.600000 15.000000  ;# Floor 2, Tower 1
node 87 19.000000 16.000000 15.000000  ;# Floor 2, Tower 1
node 88 27.000000 0.000000 15.000000  ;# Floor 2, Tower 1
node 89 27.000000 7.400000 15.000000  ;# Floor 2, Tower 1
node 90 27.000000 8.600000 15.000000  ;# Floor 2, Tower 1
node 91 27.000000 16.000000 15.000000  ;# Floor 2, Tower 1
node 92 30.000000 0.000000 15.000000  ;# Floor 2, Tower 1
node 93 30.000000 7.400000 15.000000  ;# Floor 2, Tower 1
node 94 30.000000 8.600000 15.000000  ;# Floor 2, Tower 1
node 95 30.000000 16.000000 15.000000  ;# Floor 2, Tower 1
node 96 0.000000 0.000000 21.000000  ;# Floor 3, Tower 1
node 97 0.000000 7.400000 21.000000  ;# Floor 3, Tower 1
node 98 0.000000 8.600000 21.000000  ;# Floor 3, Tower 1
node 99 0.000000 16.000000 21.000000  ;# Floor 3, Tower 1
node 100 3.000000 0.000000 21.000000  ;# Floor 3, Tower 1
node 101 3.000000 7.400000 21.000000  ;# Floor 3, Tower 1
node 102 3.000000 8.600000 21.000000  ;# Floor 3, Tower 1
node 103 3.000000 16.000000 21.000000  ;# Floor 3, Tower 1
node 104 11.000000 0.000000 21.000000  ;# Floor 3, Tower 1
node 105 11.000000 7.400000 21.000000  ;# Floor 3, Tower 1
node 106 11.000000 8.600000 21.000000  ;# Floor 3, Tower 1
node 107 11.000000 16.000000 21.000000  ;# Floor 3, Tower 1
node 108 14.400000 0.000000 21.000000  ;# Floor 3, Tower 1
node 109 14.400000 7.400000 21.000000  ;# Floor 3, Tower 1
node 110 14.400000 8.600000 21.000000  ;# Floor 3, Tower 1
node 111 14.400000 16.000000 21.000000  ;# Floor 3, Tower 1
node 112 15.600000 0.000000 21.000000  ;# Floor 3, Tower 1
node 113 15.600000 7.400000 21.000000  ;# Floor 3, Tower 1
node 114 15.600000 8.600000 21.000000  ;# Floor 3, Tower 1
node 115 15.600000 16.000000 21.000000  ;# Floor 3, Tower 1
node 116 19.000000 0.000000 21.000000  ;# Floor 3, Tower 1
node 117 19.000000 7.400000 21.000000  ;# Floor 3, Tower 1
node 118 19.000000 8.600000 21.000000  ;# Floor 3, Tower 1
node 119 19.000000 16.000000 21.000000  ;# Floor 3, Tower 1
node 120 27.000000 0.000000 21.000000  ;# Floor 3, Tower 1
node 121 27.000000 7.400000 21.000000  ;# Floor 3, Tower 1
node 122 27.000000 8.600000 21.000000  ;# Floor 3, Tower 1
node 123 27.000000 16.000000 21.000000  ;# Floor 3, Tower 1
node 124 30.000000 0.000000 21.000000  ;# Floor 3, Tower 1
node 125 30.000000 7.400000 21.000000  ;# Floor 3, Tower 1
node 126 30.000000 8.600000 21.000000  ;# Floor 3, Tower 1
node 127 30.000000 16.000000 21.000000  ;# Floor 3, Tower 1
node 128 0.000000 0.000000 27.000000  ;# Floor 4, Tower 1
node 129 0.000000 7.400000 27.000000  ;# Floor 4, Tower 1
node 130 0.000000 8.600000 27.000000  ;# Floor 4, Tower 1
node 131 0.000000 16.000000 27.000000  ;# Floor 4, Tower 1
node 132 3.000000 0.000000 27.000000  ;# Floor 4, Tower 1
node 133 3.000000 7.400000 27.000000  ;# Floor 4, Tower 1
node 134 3.000000 8.600000 27.000000  ;# Floor 4, Tower 1
node 135 3.000000 16.000000 27.000000  ;# Floor 4, Tower 1
node 136 11.000000 0.000000 27.000000  ;# Floor 4, Tower 1
node 137 11.000000 7.400000 27.000000  ;# Floor 4, Tower 1
node 138 11.000000 8.600000 27.000000  ;# Floor 4, Tower 1
node 139 11.000000 16.000000 27.000000  ;# Floor 4, Tower 1
node 140 14.400000 0.000000 27.000000  ;# Floor 4, Tower 1
node 141 14.400000 7.400000 27.000000  ;# Floor 4, Tower 1
node 142 14.400000 8.600000 27.000000  ;# Floor 4, Tower 1
node 143 14.400000 16.000000 27.000000  ;# Floor 4, Tower 1
node 144 15.600000 0.000000 27.000000  ;# Floor 4, Tower 1
node 145 15.600000 7.400000 27.000000  ;# Floor 4, Tower 1
node 146 15.600000 8.600000 27.000000  ;# Floor 4, Tower 1
node 147 15.600000 16.000000 27.000000  ;# Floor 4, Tower 1
node 148 19.000000 0.000000 27.000000  ;# Floor 4, Tower 1
node 149 19.000000 7.400000 27.000000  ;# Floor 4, Tower 1
node 150 19.000000 8.600000 27.000000  ;# Floor 4, Tower 1
node 151 19.000000 16.000000 27.000000  ;# Floor 4, Tower 1
node 152 27.000000 0.000000 27.000000  ;# Floor 4, Tower 1
node 153 27.000000 7.400000 27.000000  ;# Floor 4, Tower 1
node 154 27.000000 8.600000 27.000000  ;# Floor 4, Tower 1
node 155 27.000000 16.000000 27.000000  ;# Floor 4, Tower 1
node 156 30.000000 0.000000 27.000000  ;# Floor 4, Tower 1
node 157 30.000000 7.400000 27.000000  ;# Floor 4, Tower 1
node 158 30.000000 8.600000 27.000000  ;# Floor 4, Tower 1
node 159 30.000000 16.000000 27.000000  ;# Floor 4, Tower 1
node 160 0.000000 0.000000 33.000000  ;# Floor 5, Tower 1
node 161 0.000000 7.400000 33.000000  ;# Floor 5, Tower 1
node 162 0.000000 8.600000 33.000000  ;# Floor 5, Tower 1
node 163 0.000000 16.000000 33.000000  ;# Floor 5, Tower 1
node 164 3.000000 0.000000 33.000000  ;# Floor 5, Tower 1
node 165 3.000000 7.400000 33.000000  ;# Floor 5, Tower 1
node 166 3.000000 8.600000 33.000000  ;# Floor 5, Tower 1
node 167 3.000000 16.000000 33.000000  ;# Floor 5, Tower 1
node 168 11.000000 0.000000 33.000000  ;# Floor 5, Tower 1
node 169 11.000000 7.400000 33.000000  ;# Floor 5, Tower 1
node 170 11.000000 8.600000 33.000000  ;# Floor 5, Tower 1
node 171 11.000000 16.000000 33.000000  ;# Floor 5, Tower 1
node 172 14.400000 0.000000 33.000000  ;# Floor 5, Tower 1
node 173 14.400000 7.400000 33.000000  ;# Floor 5, Tower 1
node 174 14.400000 8.600000 33.000000  ;# Floor 5, Tower 1
node 175 14.400000 16.000000 33.000000  ;# Floor 5, Tower 1
node 176 15.600000 0.000000 33.000000  ;# Floor 5, Tower 1
node 177 15.600000 7.400000 33.000000  ;# Floor 5, Tower 1
node 178 15.600000 8.600000 33.000000  ;# Floor 5, Tower 1
node 179 15.600000 16.000000 33.000000  ;# Floor 5, Tower 1
node 180 19.000000 0.000000 33.000000  ;# Floor 5, Tower 1
node 181 19.000000 7.400000 33.000000  ;# Floor 5, Tower 1
node 182 19.000000 8.600000 33.000000  ;# Floor 5, Tower 1
node 183 19.000000 16.000000 33.000000  ;# Floor 5, Tower 1
node 184 27.000000 0.000000 33.000000  ;# Floor 5, Tower 1
node 185 27.000000 7.400000 33.000000  ;# Floor 5, Tower 1
node 186 27.000000 8.600000 33.000000  ;# Floor 5, Tower 1
node 187 27.000000 16.000000 33.000000  ;# Floor 5, Tower 1
node 188 30.000000 0.000000 33.000000  ;# Floor 5, Tower 1
node 189 30.000000 7.400000 33.000000  ;# Floor 5, Tower 1
node 190 30.000000 8.600000 33.000000  ;# Floor 5, Tower 1
node 191 30.000000 16.000000 33.000000  ;# Floor 5, Tower 1
node 192 0.000000 0.000000 39.000000  ;# Floor 6, Tower 1
node 193 0.000000 7.400000 39.000000  ;# Floor 6, Tower 1
node 194 0.000000 8.600000 39.000000  ;# Floor 6, Tower 1
node 195 0.000000 16.000000 39.000000  ;# Floor 6, Tower 1
node 196 3.000000 0.000000 39.000000  ;# Floor 6, Tower 1
node 197 3.000000 7.400000 39.000000  ;# Floor 6, Tower 1
node 198 3.000000 8.600000 39.000000  ;# Floor 6, Tower 1
node 199 3.000000 16.000000 39.000000  ;# Floor 6, Tower 1
node 200 11.000000 0.000000 39.000000  ;# Floor 6, Tower 1
node 201 11.000000 7.400000 39.000000  ;# Floor 6, Tower 1
node 202 11.000000 8.600000 39.000000  ;# Floor 6, Tower 1
node 203 11.000000 16.000000 39.000000  ;# Floor 6, Tower 1
node 204 14.400000 0.000000 39.000000  ;# Floor 6, Tower 1
node 205 14.400000 7.400000 39.000000  ;# Floor 6, Tower 1
node 206 14.400000 8.600000 39.000000  ;# Floor 6, Tower 1
node 207 14.400000 16.000000 39.000000  ;# Floor 6, Tower 1
node 208 15.600000 0.000000 39.000000  ;# Floor 6, Tower 1
node 209 15.600000 7.400000 39.000000  ;# Floor 6, Tower 1
node 210 15.600000 8.600000 39.000000  ;# Floor 6, Tower 1
node 211 15.600000 16.000000 39.000000  ;# Floor 6, Tower 1
node 212 19.000000 0.000000 39.000000  ;# Floor 6, Tower 1
node 213 19.000000 7.400000 39.000000  ;# Floor 6, Tower 1
node 214 19.000000 8.600000 39.000000  ;# Floor 6, Tower 1
node 215 19.000000 16.000000 39.000000  ;# Floor 6, Tower 1
node 216 27.000000 0.000000 39.000000  ;# Floor 6, Tower 1
node 217 27.000000 7.400000 39.000000  ;# Floor 6, Tower 1
node 218 27.000000 8.600000 39.000000  ;# Floor 6, Tower 1
node 219 27.000000 16.000000 39.000000  ;# Floor 6, Tower 1
node 220 30.000000 0.000000 39.000000  ;# Floor 6, Tower 1
node 221 30.000000 7.400000 39.000000  ;# Floor 6, Tower 1
node 222 30.000000 8.600000 39.000000  ;# Floor 6, Tower 1
node 223 30.000000 16.000000 39.000000  ;# Floor 6, Tower 1
node 224 0.000000 0.000000 45.000000  ;# Floor 7, Tower 1
node 225 0.000000 7.400000 45.000000  ;# Floor 7, Tower 1
node 226 0.000000 8.600000 45.000000  ;# Floor 7, Tower 1
node 227 0.000000 16.000000 45.000000  ;# Floor 7, Tower 1
node 228 3.000000 0.000000 45.000000  ;# Floor 7, Tower 1
node 229 3.000000 7.400000 45.000000  ;# Floor 7, Tower 1
node 230 3.000000 8.600000 45.000000  ;# Floor 7, Tower 1
node 231 3.000000 16.000000 45.000000  ;# Floor 7, Tower 1
node 232 11.000000 0.000000 45.000000  ;# Floor 7, Tower 1
node 233 11.000000 7.400000 45.000000  ;# Floor 7, Tower 1
node 234 11.000000 8.600000 45.000000  ;# Floor 7, Tower 1
node 235 11.000000 16.000000 45.000000  ;# Floor 7, Tower 1
node 236 14.400000 0.000000 45.000000  ;# Floor 7, Tower 1
node 237 14.400000 7.400000 45.000000  ;# Floor 7, Tower 1
node 238 14.400000 8.600000 45.000000  ;# Floor 7, Tower 1
node 239 14.400000 16.000000 45.000000  ;# Floor 7, Tower 1
node 240 15.600000 0.000000 45.000000  ;# Floor 7, Tower 1
node 241 15.600000 7.400000 45.000000  ;# Floor 7, Tower 1
node 242 15.600000 8.600000 45.000000  ;# Floor 7, Tower 1
node 243 15.600000 16.000000 45.000000  ;# Floor 7, Tower 1
node 244 19.000000 0.000000 45.000000  ;# Floor 7, Tower 1
node 245 19.000000 7.400000 45.000000  ;# Floor 7, Tower 1
node 246 19.000000 8.600000 45.000000  ;# Floor 7, Tower 1
node 247 19.000000 16.000000 45.000000  ;# Floor 7, Tower 1
node 248 27.000000 0.000000 45.000000  ;# Floor 7, Tower 1
node 249 27.000000 7.400000 45.000000  ;# Floor 7, Tower 1
node 250 27.000000 8.600000 45.000000  ;# Floor 7, Tower 1
node 251 27.000000 16.000000 45.000000  ;# Floor 7, Tower 1
node 252 30.000000 0.000000 45.000000  ;# Floor 7, Tower 1
node 253 30.000000 7.400000 45.000000  ;# Floor 7, Tower 1
node 254 30.000000 8.600000 45.000000  ;# Floor 7, Tower 1
node 255 30.000000 16.000000 45.000000  ;# Floor 7, Tower 1
node 256 0.000000 0.000000 51.000000  ;# Floor 8, Tower 1
node 257 0.000000 7.400000 51.000000  ;# Floor 8, Tower 1
node 258 0.000000 8.600000 51.000000  ;# Floor 8, Tower 1
node 259 0.000000 16.000000 51.000000  ;# Floor 8, Tower 1
node 260 3.000000 0.000000 51.000000  ;# Floor 8, Tower 1
node 261 3.000000 7.400000 51.000000  ;# Floor 8, Tower 1
node 262 3.000000 8.600000 51.000000  ;# Floor 8, Tower 1
node 263 3.000000 16.000000 51.000000  ;# Floor 8, Tower 1
node 264 11.000000 0.000000 51.000000  ;# Floor 8, Tower 1
node 265 11.000000 7.400000 51.000000  ;# Floor 8, Tower 1
node 266 11.000000 8.600000 51.000000  ;# Floor 8, Tower 1
node 267 11.000000 16.000000 51.000000  ;# Floor 8, Tower 1
node 268 14.400000 0.000000 51.000000  ;# Floor 8, Tower 1
node 269 14.400000 7.400000 51.000000  ;# Floor 8, Tower 1
node 270 14.400000 8.600000 51.000000  ;# Floor 8, Tower 1
node 271 14.400000 16.000000 51.000000  ;# Floor 8, Tower 1
node 272 15.600000 0.000000 51.000000  ;# Floor 8, Tower 1
node 273 15.600000 7.400000 51.000000  ;# Floor 8, Tower 1
node 274 15.600000 8.600000 51.000000  ;# Floor 8, Tower 1
node 275 15.600000 16.000000 51.000000  ;# Floor 8, Tower 1
node 276 19.000000 0.000000 51.000000  ;# Floor 8, Tower 1
node 277 19.000000 7.400000 51.000000  ;# Floor 8, Tower 1
node 278 19.000000 8.600000 51.000000  ;# Floor 8, Tower 1
node 279 19.000000 16.000000 51.000000  ;# Floor 8, Tower 1
node 280 27.000000 0.000000 51.000000  ;# Floor 8, Tower 1
node 281 27.000000 7.400000 51.000000  ;# Floor 8, Tower 1
node 282 27.000000 8.600000 51.000000  ;# Floor 8, Tower 1
node 283 27.000000 16.000000 51.000000  ;# Floor 8, Tower 1
node 284 30.000000 0.000000 51.000000  ;# Floor 8, Tower 1
node 285 30.000000 7.400000 51.000000  ;# Floor 8, Tower 1
node 286 30.000000 8.600000 51.000000  ;# Floor 8, Tower 1
node 287 30.000000 16.000000 51.000000  ;# Floor 8, Tower 1
node 288 0.000000 0.000000 57.000000  ;# Floor 9, Tower 1
node 289 0.000000 7.400000 57.000000  ;# Floor 9, Tower 1
node 290 0.000000 8.600000 57.000000  ;# Floor 9, Tower 1
node 291 0.000000 16.000000 57.000000  ;# Floor 9, Tower 1
node 292 3.000000 0.000000 57.000000  ;# Floor 9, Tower 1
node 293 3.000000 7.400000 57.000000  ;# Floor 9, Tower 1
node 294 3.000000 8.600000 57.000000  ;# Floor 9, Tower 1
node 295 3.000000 16.000000 57.000000  ;# Floor 9, Tower 1
node 296 11.000000 0.000000 57.000000  ;# Floor 9, Tower 1
node 297 11.000000 7.400000 57.000000  ;# Floor 9, Tower 1
node 298 11.000000 8.600000 57.000000  ;# Floor 9, Tower 1
node 299 11.000000 16.000000 57.000000  ;# Floor 9, Tower 1
node 300 14.400000 0.000000 57.000000  ;# Floor 9, Tower 1
node 301 14.400000 7.400000 57.000000  ;# Floor 9, Tower 1
node 302 14.400000 8.600000 57.000000  ;# Floor 9, Tower 1
node 303 14.400000 16.000000 57.000000  ;# Floor 9, Tower 1
node 304 15.600000 0.000000 57.000000  ;# Floor 9, Tower 1
node 305 15.600000 7.400000 57.000000  ;# Floor 9, Tower 1
node 306 15.600000 8.600000 57.000000  ;# Floor 9, Tower 1
node 307 15.600000 16.000000 57.000000  ;# Floor 9, Tower 1
node 308 19.000000 0.000000 57.000000  ;# Floor 9, Tower 1
node 309 19.000000 7.400000 57.000000  ;# Floor 9, Tower 1
node 310 19.000000 8.600000 57.000000  ;# Floor 9, Tower 1
node 311 19.000000 16.000000 57.000000  ;# Floor 9, Tower 1
node 312 27.000000 0.000000 57.000000  ;# Floor 9, Tower 1
node 313 27.000000 7.400000 57.000000  ;# Floor 9, Tower 1
node 314 27.000000 8.600000 57.000000  ;# Floor 9, Tower 1
node 315 27.000000 16.000000 57.000000  ;# Floor 9, Tower 1
node 316 30.000000 0.000000 57.000000  ;# Floor 9, Tower 1
node 317 30.000000 7.400000 57.000000  ;# Floor 9, Tower 1
node 318 30.000000 8.600000 57.000000  ;# Floor 9, Tower 1
node 319 30.000000 16.000000 57.000000  ;# Floor 9, Tower 1
node 320 0.000000 0.000000 63.000000  ;# Floor 10, Tower 1
node 321 0.000000 7.400000 63.000000  ;# Floor 10, Tower 1
node 322 0.000000 8.600000 63.000000  ;# Floor 10, Tower 1
node 323 0.000000 16.000000 63.000000  ;# Floor 10, Tower 1
node 324 3.000000 0.000000 63.000000  ;# Floor 10, Tower 1
node 325 3.000000 7.400000 63.000000  ;# Floor 10, Tower 1
node 326 3.000000 8.600000 63.000000  ;# Floor 10, Tower 1
node 327 3.000000 16.000000 63.000000  ;# Floor 10, Tower 1
node 328 11.000000 0.000000 63.000000  ;# Floor 10, Tower 1
node 329 11.000000 7.400000 63.000000  ;# Floor 10, Tower 1
node 330 11.000000 8.600000 63.000000  ;# Floor 10, Tower 1
node 331 11.000000 16.000000 63.000000  ;# Floor 10, Tower 1
node 332 14.400000 0.000000 63.000000  ;# Floor 10, Tower 1
node 333 14.400000 7.400000 63.000000  ;# Floor 10, Tower 1
node 334 14.400000 8.600000 63.000000  ;# Floor 10, Tower 1
node 335 14.400000 16.000000 63.000000  ;# Floor 10, Tower 1
node 336 15.600000 0.000000 63.000000  ;# Floor 10, Tower 1
node 337 15.600000 7.400000 63.000000  ;# Floor 10, Tower 1
node 338 15.600000 8.600000 63.000000  ;# Floor 10, Tower 1
node 339 15.600000 16.000000 63.000000  ;# Floor 10, Tower 1
node 340 19.000000 0.000000 63.000000  ;# Floor 10, Tower 1
node 341 19.000000 7.400000 63.000000  ;# Floor 10, Tower 1
node 342 19.000000 8.600000 63.000000  ;# Floor 10, Tower 1
node 343 19.000000 16.000000 63.000000  ;# Floor 10, Tower 1
node 344 27.000000 0.000000 63.000000  ;# Floor 10, Tower 1
node 345 27.000000 7.400000 63.000000  ;# Floor 10, Tower 1
node 346 27.000000 8.600000 63.000000  ;# Floor 10, Tower 1
node 347 27.000000 16.000000 63.000000  ;# Floor 10, Tower 1
node 348 30.000000 0.000000 63.000000  ;# Floor 10, Tower 1
node 349 30.000000 7.400000 63.000000  ;# Floor 10, Tower 1
node 350 30.000000 8.600000 63.000000  ;# Floor 10, Tower 1
node 351 30.000000 16.000000 63.000000  ;# Floor 10, Tower 1
node 352 0.000000 0.000000 69.000000  ;# Floor 11, Tower 1
node 353 0.000000 7.400000 69.000000  ;# Floor 11, Tower 1
node 354 0.000000 8.600000 69.000000  ;# Floor 11, Tower 1
node 355 0.000000 16.000000 69.000000  ;# Floor 11, Tower 1
node 356 3.000000 0.000000 69.000000  ;# Floor 11, Tower 1
node 357 3.000000 7.400000 69.000000  ;# Floor 11, Tower 1
node 358 3.000000 8.600000 69.000000  ;# Floor 11, Tower 1
node 359 3.000000 16.000000 69.000000  ;# Floor 11, Tower 1
node 360 11.000000 0.000000 69.000000  ;# Floor 11, Tower 1
node 361 11.000000 7.400000 69.000000  ;# Floor 11, Tower 1
node 362 11.000000 8.600000 69.000000  ;# Floor 11, Tower 1
node 363 11.000000 16.000000 69.000000  ;# Floor 11, Tower 1
node 364 14.400000 0.000000 69.000000  ;# Floor 11, Tower 1
node 365 14.400000 7.400000 69.000000  ;# Floor 11, Tower 1
node 366 14.400000 8.600000 69.000000  ;# Floor 11, Tower 1
node 367 14.400000 16.000000 69.000000  ;# Floor 11, Tower 1
node 368 15.600000 0.000000 69.000000  ;# Floor 11, Tower 1
node 369 15.600000 7.400000 69.000000  ;# Floor 11, Tower 1
node 370 15.600000 8.600000 69.000000  ;# Floor 11, Tower 1
node 371 15.600000 16.000000 69.000000  ;# Floor 11, Tower 1
node 372 19.000000 0.000000 69.000000  ;# Floor 11, Tower 1
node 373 19.000000 7.400000 69.000000  ;# Floor 11, Tower 1
node 374 19.000000 8.600000 69.000000  ;# Floor 11, Tower 1
node 375 19.000000 16.000000 69.000000  ;# Floor 11, Tower 1
node 376 27.000000 0.000000 69.000000  ;# Floor 11, Tower 1
node 377 27.000000 7.400000 69.000000  ;# Floor 11, Tower 1
node 378 27.000000 8.600000 69.000000  ;# Floor 11, Tower 1
node 379 27.000000 16.000000 69.000000  ;# Floor 11, Tower 1
node 380 30.000000 0.000000 69.000000  ;# Floor 11, Tower 1
node 381 30.000000 7.400000 69.000000  ;# Floor 11, Tower 1
node 382 30.000000 8.600000 69.000000  ;# Floor 11, Tower 1
node 383 30.000000 16.000000 69.000000  ;# Floor 11, Tower 1
node 384 0.000000 0.000000 75.000000  ;# Floor 12, Tower 1
node 385 0.000000 7.400000 75.000000  ;# Floor 12, Tower 1
node 386 0.000000 8.600000 75.000000  ;# Floor 12, Tower 1
node 387 0.000000 16.000000 75.000000  ;# Floor 12, Tower 1
node 388 3.000000 0.000000 75.000000  ;# Floor 12, Tower 1
node 389 3.000000 7.400000 75.000000  ;# Floor 12, Tower 1
node 390 3.000000 8.600000 75.000000  ;# Floor 12, Tower 1
node 391 3.000000 16.000000 75.000000  ;# Floor 12, Tower 1
node 392 11.000000 0.000000 75.000000  ;# Floor 12, Tower 1
node 393 11.000000 7.400000 75.000000  ;# Floor 12, Tower 1
node 394 11.000000 8.600000 75.000000  ;# Floor 12, Tower 1
node 395 11.000000 16.000000 75.000000  ;# Floor 12, Tower 1
node 396 14.400000 0.000000 75.000000  ;# Floor 12, Tower 1
node 397 14.400000 7.400000 75.000000  ;# Floor 12, Tower 1
node 398 14.400000 8.600000 75.000000  ;# Floor 12, Tower 1
node 399 14.400000 16.000000 75.000000  ;# Floor 12, Tower 1
node 400 15.600000 0.000000 75.000000  ;# Floor 12, Tower 1
node 401 15.600000 7.400000 75.000000  ;# Floor 12, Tower 1
node 402 15.600000 8.600000 75.000000  ;# Floor 12, Tower 1
node 403 15.600000 16.000000 75.000000  ;# Floor 12, Tower 1
node 404 19.000000 0.000000 75.000000  ;# Floor 12, Tower 1
node 405 19.000000 7.400000 75.000000  ;# Floor 12, Tower 1
node 406 19.000000 8.600000 75.000000  ;# Floor 12, Tower 1
node 407 19.000000 16.000000 75.000000  ;# Floor 12, Tower 1
node 408 27.000000 0.000000 75.000000  ;# Floor 12, Tower 1
node 409 27.000000 7.400000 75.000000  ;# Floor 12, Tower 1
node 410 27.000000 8.600000 75.000000  ;# Floor 12, Tower 1
node 411 27.000000 16.000000 75.000000  ;# Floor 12, Tower 1
node 412 30.000000 0.000000 75.000000  ;# Floor 12, Tower 1
node 413 30.000000 7.400000 75.000000  ;# Floor 12, Tower 1
node 414 30.000000 8.600000 75.000000  ;# Floor 12, Tower 1
node 415 30.000000 16.000000 75.000000  ;# Floor 12, Tower 1
node 416 0.000000 0.000000 81.000000  ;# Floor 13, Tower 1
node 417 0.000000 7.400000 81.000000  ;# Floor 13, Tower 1
node 418 0.000000 8.600000 81.000000  ;# Floor 13, Tower 1
node 419 0.000000 16.000000 81.000000  ;# Floor 13, Tower 1
node 420 3.000000 0.000000 81.000000  ;# Floor 13, Tower 1
node 421 3.000000 7.400000 81.000000  ;# Floor 13, Tower 1
node 422 3.000000 8.600000 81.000000  ;# Floor 13, Tower 1
node 423 3.000000 16.000000 81.000000  ;# Floor 13, Tower 1
node 424 11.000000 0.000000 81.000000  ;# Floor 13, Tower 1
node 425 11.000000 7.400000 81.000000  ;# Floor 13, Tower 1
node 426 11.000000 8.600000 81.000000  ;# Floor 13, Tower 1
node 427 11.000000 16.000000 81.000000  ;# Floor 13, Tower 1
node 428 14.400000 0.000000 81.000000  ;# Floor 13, Tower 1
node 429 14.400000 7.400000 81.000000  ;# Floor 13, Tower 1
node 430 14.400000 8.600000 81.000000  ;# Floor 13, Tower 1
node 431 14.400000 16.000000 81.000000  ;# Floor 13, Tower 1
node 432 15.600000 0.000000 81.000000  ;# Floor 13, Tower 1
node 433 15.600000 7.400000 81.000000  ;# Floor 13, Tower 1
node 434 15.600000 8.600000 81.000000  ;# Floor 13, Tower 1
node 435 15.600000 16.000000 81.000000  ;# Floor 13, Tower 1
node 436 19.000000 0.000000 81.000000  ;# Floor 13, Tower 1
node 437 19.000000 7.400000 81.000000  ;# Floor 13, Tower 1
node 438 19.000000 8.600000 81.000000  ;# Floor 13, Tower 1
node 439 19.000000 16.000000 81.000000  ;# Floor 13, Tower 1
node 440 27.000000 0.000000 81.000000  ;# Floor 13, Tower 1
node 441 27.000000 7.400000 81.000000  ;# Floor 13, Tower 1
node 442 27.000000 8.600000 81.000000  ;# Floor 13, Tower 1
node 443 27.000000 16.000000 81.000000  ;# Floor 13, Tower 1
node 444 30.000000 0.000000 81.000000  ;# Floor 13, Tower 1
node 445 30.000000 7.400000 81.000000  ;# Floor 13, Tower 1
node 446 30.000000 8.600000 81.000000  ;# Floor 13, Tower 1
node 447 30.000000 16.000000 81.000000  ;# Floor 13, Tower 1
node 448 0.000000 0.000000 87.000000  ;# Floor 14, Tower 1
node 449 0.000000 7.400000 87.000000  ;# Floor 14, Tower 1
node 450 0.000000 8.600000 87.000000  ;# Floor 14, Tower 1
node 451 0.000000 16.000000 87.000000  ;# Floor 14, Tower 1
node 452 3.000000 0.000000 87.000000  ;# Floor 14, Tower 1
node 453 3.000000 7.400000 87.000000  ;# Floor 14, Tower 1
node 454 3.000000 8.600000 87.000000  ;# Floor 14, Tower 1
node 455 3.000000 16.000000 87.000000  ;# Floor 14, Tower 1
node 456 11.000000 0.000000 87.000000  ;# Floor 14, Tower 1
node 457 11.000000 7.400000 87.000000  ;# Floor 14, Tower 1
node 458 11.000000 8.600000 87.000000  ;# Floor 14, Tower 1
node 459 11.000000 16.000000 87.000000  ;# Floor 14, Tower 1
node 460 14.400000 0.000000 87.000000  ;# Floor 14, Tower 1
node 461 14.400000 7.400000 87.000000  ;# Floor 14, Tower 1
node 462 14.400000 8.600000 87.000000  ;# Floor 14, Tower 1
node 463 14.400000 16.000000 87.000000  ;# Floor 14, Tower 1
node 464 15.600000 0.000000 87.000000  ;# Floor 14, Tower 1
node 465 15.600000 7.400000 87.000000  ;# Floor 14, Tower 1
node 466 15.600000 8.600000 87.000000  ;# Floor 14, Tower 1
node 467 15.600000 16.000000 87.000000  ;# Floor 14, Tower 1
node 468 19.000000 0.000000 87.000000  ;# Floor 14, Tower 1
node 469 19.000000 7.400000 87.000000  ;# Floor 14, Tower 1
node 470 19.000000 8.600000 87.000000  ;# Floor 14, Tower 1
node 471 19.000000 16.000000 87.000000  ;# Floor 14, Tower 1
node 472 27.000000 0.000000 87.000000  ;# Floor 14, Tower 1
node 473 27.000000 7.400000 87.000000  ;# Floor 14, Tower 1
node 474 27.000000 8.600000 87.000000  ;# Floor 14, Tower 1
node 475 27.000000 16.000000 87.000000  ;# Floor 14, Tower 1
node 476 30.000000 0.000000 87.000000  ;# Floor 14, Tower 1
node 477 30.000000 7.400000 87.000000  ;# Floor 14, Tower 1
node 478 30.000000 8.600000 87.000000  ;# Floor 14, Tower 1
node 479 30.000000 16.000000 87.000000  ;# Floor 14, Tower 1
node 480 0.000000 0.000000 93.000000  ;# Floor 15, Tower 1
node 481 0.000000 7.400000 93.000000  ;# Floor 15, Tower 1
node 482 0.000000 8.600000 93.000000  ;# Floor 15, Tower 1
node 483 0.000000 16.000000 93.000000  ;# Floor 15, Tower 1
node 484 3.000000 0.000000 93.000000  ;# Floor 15, Tower 1
node 485 3.000000 7.400000 93.000000  ;# Floor 15, Tower 1
node 486 3.000000 8.600000 93.000000  ;# Floor 15, Tower 1
node 487 3.000000 16.000000 93.000000  ;# Floor 15, Tower 1
node 488 11.000000 0.000000 93.000000  ;# Floor 15, Tower 1
node 489 11.000000 7.400000 93.000000  ;# Floor 15, Tower 1
node 490 11.000000 8.600000 93.000000  ;# Floor 15, Tower 1
node 491 11.000000 16.000000 93.000000  ;# Floor 15, Tower 1
node 492 14.400000 0.000000 93.000000  ;# Floor 15, Tower 1
node 493 14.400000 7.400000 93.000000  ;# Floor 15, Tower 1
node 494 14.400000 8.600000 93.000000  ;# Floor 15, Tower 1
node 495 14.400000 16.000000 93.000000  ;# Floor 15, Tower 1
node 496 15.600000 0.000000 93.000000  ;# Floor 15, Tower 1
node 497 15.600000 7.400000 93.000000  ;# Floor 15, Tower 1
node 498 15.600000 8.600000 93.000000  ;# Floor 15, Tower 1
node 499 15.600000 16.000000 93.000000  ;# Floor 15, Tower 1
node 500 19.000000 0.000000 93.000000  ;# Floor 15, Tower 1
node 501 19.000000 7.400000 93.000000  ;# Floor 15, Tower 1
node 502 19.000000 8.600000 93.000000  ;# Floor 15, Tower 1
node 503 19.000000 16.000000 93.000000  ;# Floor 15, Tower 1
node 504 27.000000 0.000000 93.000000  ;# Floor 15, Tower 1
node 505 27.000000 7.400000 93.000000  ;# Floor 15, Tower 1
node 506 27.000000 8.600000 93.000000  ;# Floor 15, Tower 1
node 507 27.000000 16.000000 93.000000  ;# Floor 15, Tower 1
node 508 30.000000 0.000000 93.000000  ;# Floor 15, Tower 1
node 509 30.000000 7.400000 93.000000  ;# Floor 15, Tower 1
node 510 30.000000 8.600000 93.000000  ;# Floor 15, Tower 1
node 511 30.000000 16.000000 93.000000  ;# Floor 15, Tower 1
node 512 0.000000 0.000000 99.000000  ;# Floor 16, Tower 1
node 513 0.000000 7.400000 99.000000  ;# Floor 16, Tower 1
node 514 0.000000 8.600000 99.000000  ;# Floor 16, Tower 1
node 515 0.000000 16.000000 99.000000  ;# Floor 16, Tower 1
node 516 3.000000 0.000000 99.000000  ;# Floor 16, Tower 1
node 517 3.000000 7.400000 99.000000  ;# Floor 16, Tower 1
node 518 3.000000 8.600000 99.000000  ;# Floor 16, Tower 1
node 519 3.000000 16.000000 99.000000  ;# Floor 16, Tower 1
node 520 11.000000 0.000000 99.000000  ;# Floor 16, Tower 1
node 521 11.000000 7.400000 99.000000  ;# Floor 16, Tower 1
node 522 11.000000 8.600000 99.000000  ;# Floor 16, Tower 1
node 523 11.000000 16.000000 99.000000  ;# Floor 16, Tower 1
node 524 14.400000 0.000000 99.000000  ;# Floor 16, Tower 1
node 525 14.400000 7.400000 99.000000  ;# Floor 16, Tower 1
node 526 14.400000 8.600000 99.000000  ;# Floor 16, Tower 1
node 527 14.400000 16.000000 99.000000  ;# Floor 16, Tower 1
node 528 15.600000 0.000000 99.000000  ;# Floor 16, Tower 1
node 529 15.600000 7.400000 99.000000  ;# Floor 16, Tower 1
node 530 15.600000 8.600000 99.000000  ;# Floor 16, Tower 1
node 531 15.600000 16.000000 99.000000  ;# Floor 16, Tower 1
node 532 19.000000 0.000000 99.000000  ;# Floor 16, Tower 1
node 533 19.000000 7.400000 99.000000  ;# Floor 16, Tower 1
node 534 19.000000 8.600000 99.000000  ;# Floor 16, Tower 1
node 535 19.000000 16.000000 99.000000  ;# Floor 16, Tower 1
node 536 27.000000 0.000000 99.000000  ;# Floor 16, Tower 1
node 537 27.000000 7.400000 99.000000  ;# Floor 16, Tower 1
node 538 27.000000 8.600000 99.000000  ;# Floor 16, Tower 1
node 539 27.000000 16.000000 99.000000  ;# Floor 16, Tower 1
node 540 30.000000 0.000000 99.000000  ;# Floor 16, Tower 1
node 541 30.000000 7.400000 99.000000  ;# Floor 16, Tower 1
node 542 30.000000 8.600000 99.000000  ;# Floor 16, Tower 1
node 543 30.000000 16.000000 99.000000  ;# Floor 16, Tower 1
node 544 0.000000 0.000000 105.000000  ;# Floor 17, Tower 1
node 545 0.000000 7.400000 105.000000  ;# Floor 17, Tower 1
node 546 0.000000 8.600000 105.000000  ;# Floor 17, Tower 1
node 547 0.000000 16.000000 105.000000  ;# Floor 17, Tower 1
node 548 3.000000 0.000000 105.000000  ;# Floor 17, Tower 1
node 549 3.000000 7.400000 105.000000  ;# Floor 17, Tower 1
node 550 3.000000 8.600000 105.000000  ;# Floor 17, Tower 1
node 551 3.000000 16.000000 105.000000  ;# Floor 17, Tower 1
node 552 11.000000 0.000000 105.000000  ;# Floor 17, Tower 1
node 553 11.000000 7.400000 105.000000  ;# Floor 17, Tower 1
node 554 11.000000 8.600000 105.000000  ;# Floor 17, Tower 1
node 555 11.000000 16.000000 105.000000  ;# Floor 17, Tower 1
node 556 14.400000 0.000000 105.000000  ;# Floor 17, Tower 1
node 557 14.400000 7.400000 105.000000  ;# Floor 17, Tower 1
node 558 14.400000 8.600000 105.000000  ;# Floor 17, Tower 1
node 559 14.400000 16.000000 105.000000  ;# Floor 17, Tower 1
node 560 15.600000 0.000000 105.000000  ;# Floor 17, Tower 1
node 561 15.600000 7.400000 105.000000  ;# Floor 17, Tower 1
node 562 15.600000 8.600000 105.000000  ;# Floor 17, Tower 1
node 563 15.600000 16.000000 105.000000  ;# Floor 17, Tower 1
node 564 19.000000 0.000000 105.000000  ;# Floor 17, Tower 1
node 565 19.000000 7.400000 105.000000  ;# Floor 17, Tower 1
node 566 19.000000 8.600000 105.000000  ;# Floor 17, Tower 1
node 567 19.000000 16.000000 105.000000  ;# Floor 17, Tower 1
node 568 27.000000 0.000000 105.000000  ;# Floor 17, Tower 1
node 569 27.000000 7.400000 105.000000  ;# Floor 17, Tower 1
node 570 27.000000 8.600000 105.000000  ;# Floor 17, Tower 1
node 571 27.000000 16.000000 105.000000  ;# Floor 17, Tower 1
node 572 30.000000 0.000000 105.000000  ;# Floor 17, Tower 1
node 573 30.000000 7.400000 105.000000  ;# Floor 17, Tower 1
node 574 30.000000 8.600000 105.000000  ;# Floor 17, Tower 1
node 575 30.000000 16.000000 105.000000  ;# Floor 17, Tower 1
node 576 0.000000 0.000000 111.000000  ;# Floor 18, Tower 1
node 577 0.000000 7.400000 111.000000  ;# Floor 18, Tower 1
node 578 0.000000 8.600000 111.000000  ;# Floor 18, Tower 1
node 579 0.000000 16.000000 111.000000  ;# Floor 18, Tower 1
node 580 3.000000 0.000000 111.000000  ;# Floor 18, Tower 1
node 581 3.000000 7.400000 111.000000  ;# Floor 18, Tower 1
node 582 3.000000 8.600000 111.000000  ;# Floor 18, Tower 1
node 583 3.000000 16.000000 111.000000  ;# Floor 18, Tower 1
node 584 11.000000 0.000000 111.000000  ;# Floor 18, Tower 1
node 585 11.000000 7.400000 111.000000  ;# Floor 18, Tower 1
node 586 11.000000 8.600000 111.000000  ;# Floor 18, Tower 1
node 587 11.000000 16.000000 111.000000  ;# Floor 18, Tower 1
node 588 14.400000 0.000000 111.000000  ;# Floor 18, Tower 1
node 589 14.400000 7.400000 111.000000  ;# Floor 18, Tower 1
node 590 14.400000 8.600000 111.000000  ;# Floor 18, Tower 1
node 591 14.400000 16.000000 111.000000  ;# Floor 18, Tower 1
node 592 15.600000 0.000000 111.000000  ;# Floor 18, Tower 1
node 593 15.600000 7.400000 111.000000  ;# Floor 18, Tower 1
node 594 15.600000 8.600000 111.000000  ;# Floor 18, Tower 1
node 595 15.600000 16.000000 111.000000  ;# Floor 18, Tower 1
node 596 19.000000 0.000000 111.000000  ;# Floor 18, Tower 1
node 597 19.000000 7.400000 111.000000  ;# Floor 18, Tower 1
node 598 19.000000 8.600000 111.000000  ;# Floor 18, Tower 1
node 599 19.000000 16.000000 111.000000  ;# Floor 18, Tower 1
node 600 27.000000 0.000000 111.000000  ;# Floor 18, Tower 1
node 601 27.000000 7.400000 111.000000  ;# Floor 18, Tower 1
node 602 27.000000 8.600000 111.000000  ;# Floor 18, Tower 1
node 603 27.000000 16.000000 111.000000  ;# Floor 18, Tower 1
node 604 30.000000 0.000000 111.000000  ;# Floor 18, Tower 1
node 605 30.000000 7.400000 111.000000  ;# Floor 18, Tower 1
node 606 30.000000 8.600000 111.000000  ;# Floor 18, Tower 1
node 607 30.000000 16.000000 111.000000  ;# Floor 18, Tower 1
node 608 0.000000 0.000000 117.000000  ;# Floor 19, Tower 1
node 609 0.000000 7.400000 117.000000  ;# Floor 19, Tower 1
node 610 0.000000 8.600000 117.000000  ;# Floor 19, Tower 1
node 611 0.000000 16.000000 117.000000  ;# Floor 19, Tower 1
node 612 3.000000 0.000000 117.000000  ;# Floor 19, Tower 1
node 613 3.000000 7.400000 117.000000  ;# Floor 19, Tower 1
node 614 3.000000 8.600000 117.000000  ;# Floor 19, Tower 1
node 615 3.000000 16.000000 117.000000  ;# Floor 19, Tower 1
node 616 11.000000 0.000000 117.000000  ;# Floor 19, Tower 1
node 617 11.000000 7.400000 117.000000  ;# Floor 19, Tower 1
node 618 11.000000 8.600000 117.000000  ;# Floor 19, Tower 1
node 619 11.000000 16.000000 117.000000  ;# Floor 19, Tower 1
node 620 14.400000 0.000000 117.000000  ;# Floor 19, Tower 1
node 621 14.400000 7.400000 117.000000  ;# Floor 19, Tower 1
node 622 14.400000 8.600000 117.000000  ;# Floor 19, Tower 1
node 623 14.400000 16.000000 117.000000  ;# Floor 19, Tower 1
node 624 15.600000 0.000000 117.000000  ;# Floor 19, Tower 1
node 625 15.600000 7.400000 117.000000  ;# Floor 19, Tower 1
node 626 15.600000 8.600000 117.000000  ;# Floor 19, Tower 1
node 627 15.600000 16.000000 117.000000  ;# Floor 19, Tower 1
node 628 19.000000 0.000000 117.000000  ;# Floor 19, Tower 1
node 629 19.000000 7.400000 117.000000  ;# Floor 19, Tower 1
node 630 19.000000 8.600000 117.000000  ;# Floor 19, Tower 1
node 631 19.000000 16.000000 117.000000  ;# Floor 19, Tower 1
node 632 27.000000 0.000000 117.000000  ;# Floor 19, Tower 1
node 633 27.000000 7.400000 117.000000  ;# Floor 19, Tower 1
node 634 27.000000 8.600000 117.000000  ;# Floor 19, Tower 1
node 635 27.000000 16.000000 117.000000  ;# Floor 19, Tower 1
node 636 30.000000 0.000000 117.000000  ;# Floor 19, Tower 1
node 637 30.000000 7.400000 117.000000  ;# Floor 19, Tower 1
node 638 30.000000 8.600000 117.000000  ;# Floor 19, Tower 1
node 639 30.000000 16.000000 117.000000  ;# Floor 19, Tower 1
node 640 0.000000 0.000000 123.000000  ;# Floor 20, Tower 1
node 641 0.000000 7.400000 123.000000  ;# Floor 20, Tower 1
node 642 0.000000 8.600000 123.000000  ;# Floor 20, Tower 1
node 643 0.000000 16.000000 123.000000  ;# Floor 20, Tower 1
node 644 3.000000 0.000000 123.000000  ;# Floor 20, Tower 1
node 645 3.000000 7.400000 123.000000  ;# Floor 20, Tower 1
node 646 3.000000 8.600000 123.000000  ;# Floor 20, Tower 1
node 647 3.000000 16.000000 123.000000  ;# Floor 20, Tower 1
node 648 11.000000 0.000000 123.000000  ;# Floor 20, Tower 1
node 649 11.000000 7.400000 123.000000  ;# Floor 20, Tower 1
node 650 11.000000 8.600000 123.000000  ;# Floor 20, Tower 1
node 651 11.000000 16.000000 123.000000  ;# Floor 20, Tower 1
node 652 14.400000 0.000000 123.000000  ;# Floor 20, Tower 1
node 653 14.400000 7.400000 123.000000  ;# Floor 20, Tower 1
node 654 14.400000 8.600000 123.000000  ;# Floor 20, Tower 1
node 655 14.400000 16.000000 123.000000  ;# Floor 20, Tower 1
node 656 15.600000 0.000000 123.000000  ;# Floor 20, Tower 1
node 657 15.600000 7.400000 123.000000  ;# Floor 20, Tower 1
node 658 15.600000 8.600000 123.000000  ;# Floor 20, Tower 1
node 659 15.600000 16.000000 123.000000  ;# Floor 20, Tower 1
node 660 19.000000 0.000000 123.000000  ;# Floor 20, Tower 1
node 661 19.000000 7.400000 123.000000  ;# Floor 20, Tower 1
node 662 19.000000 8.600000 123.000000  ;# Floor 20, Tower 1
node 663 19.000000 16.000000 123.000000  ;# Floor 20, Tower 1
node 664 27.000000 0.000000 123.000000  ;# Floor 20, Tower 1
node 665 27.000000 7.400000 123.000000  ;# Floor 20, Tower 1
node 666 27.000000 8.600000 123.000000  ;# Floor 20, Tower 1
node 667 27.000000 16.000000 123.000000  ;# Floor 20, Tower 1
node 668 30.000000 0.000000 123.000000  ;# Floor 20, Tower 1
node 669 30.000000 7.400000 123.000000  ;# Floor 20, Tower 1
node 670 30.000000 8.600000 123.000000  ;# Floor 20, Tower 1
node 671 30.000000 16.000000 123.000000  ;# Floor 20, Tower 1
node 672 0.000000 0.000000 129.000000  ;# Floor 21, Tower 1
node 673 0.000000 7.400000 129.000000  ;# Floor 21, Tower 1
node 674 0.000000 8.600000 129.000000  ;# Floor 21, Tower 1
node 675 0.000000 16.000000 129.000000  ;# Floor 21, Tower 1
node 676 3.000000 0.000000 129.000000  ;# Floor 21, Tower 1
node 677 3.000000 7.400000 129.000000  ;# Floor 21, Tower 1
node 678 3.000000 8.600000 129.000000  ;# Floor 21, Tower 1
node 679 3.000000 16.000000 129.000000  ;# Floor 21, Tower 1
node 680 11.000000 0.000000 129.000000  ;# Floor 21, Tower 1
node 681 11.000000 7.400000 129.000000  ;# Floor 21, Tower 1
node 682 11.000000 8.600000 129.000000  ;# Floor 21, Tower 1
node 683 11.000000 16.000000 129.000000  ;# Floor 21, Tower 1
node 684 14.400000 0.000000 129.000000  ;# Floor 21, Tower 1
node 685 14.400000 7.400000 129.000000  ;# Floor 21, Tower 1
node 686 14.400000 8.600000 129.000000  ;# Floor 21, Tower 1
node 687 14.400000 16.000000 129.000000  ;# Floor 21, Tower 1
node 688 15.600000 0.000000 129.000000  ;# Floor 21, Tower 1
node 689 15.600000 7.400000 129.000000  ;# Floor 21, Tower 1
node 690 15.600000 8.600000 129.000000  ;# Floor 21, Tower 1
node 691 15.600000 16.000000 129.000000  ;# Floor 21, Tower 1
node 692 19.000000 0.000000 129.000000  ;# Floor 21, Tower 1
node 693 19.000000 7.400000 129.000000  ;# Floor 21, Tower 1
node 694 19.000000 8.600000 129.000000  ;# Floor 21, Tower 1
node 695 19.000000 16.000000 129.000000  ;# Floor 21, Tower 1
node 696 27.000000 0.000000 129.000000  ;# Floor 21, Tower 1
node 697 27.000000 7.400000 129.000000  ;# Floor 21, Tower 1
node 698 27.000000 8.600000 129.000000  ;# Floor 21, Tower 1
node 699 27.000000 16.000000 129.000000  ;# Floor 21, Tower 1
node 700 30.000000 0.000000 129.000000  ;# Floor 21, Tower 1
node 701 30.000000 7.400000 129.000000  ;# Floor 21, Tower 1
node 702 30.000000 8.600000 129.000000  ;# Floor 21, Tower 1
node 703 30.000000 16.000000 129.000000  ;# Floor 21, Tower 1
node 704 0.000000 0.000000 135.000000  ;# Floor 22, Tower 1
node 705 0.000000 7.400000 135.000000  ;# Floor 22, Tower 1
node 706 0.000000 8.600000 135.000000  ;# Floor 22, Tower 1
node 707 0.000000 16.000000 135.000000  ;# Floor 22, Tower 1
node 708 3.000000 0.000000 135.000000  ;# Floor 22, Tower 1
node 709 3.000000 7.400000 135.000000  ;# Floor 22, Tower 1
node 710 3.000000 8.600000 135.000000  ;# Floor 22, Tower 1
node 711 3.000000 16.000000 135.000000  ;# Floor 22, Tower 1
node 712 11.000000 0.000000 135.000000  ;# Floor 22, Tower 1
node 713 11.000000 7.400000 135.000000  ;# Floor 22, Tower 1
node 714 11.000000 8.600000 135.000000  ;# Floor 22, Tower 1
node 715 11.000000 16.000000 135.000000  ;# Floor 22, Tower 1
node 716 14.400000 0.000000 135.000000  ;# Floor 22, Tower 1
node 717 14.400000 7.400000 135.000000  ;# Floor 22, Tower 1
node 718 14.400000 8.600000 135.000000  ;# Floor 22, Tower 1
node 719 14.400000 16.000000 135.000000  ;# Floor 22, Tower 1
node 720 15.600000 0.000000 135.000000  ;# Floor 22, Tower 1
node 721 15.600000 7.400000 135.000000  ;# Floor 22, Tower 1
node 722 15.600000 8.600000 135.000000  ;# Floor 22, Tower 1
node 723 15.600000 16.000000 135.000000  ;# Floor 22, Tower 1
node 724 19.000000 0.000000 135.000000  ;# Floor 22, Tower 1
node 725 19.000000 7.400000 135.000000  ;# Floor 22, Tower 1
node 726 19.000000 8.600000 135.000000  ;# Floor 22, Tower 1
node 727 19.000000 16.000000 135.000000  ;# Floor 22, Tower 1
node 728 27.000000 0.000000 135.000000  ;# Floor 22, Tower 1
node 729 27.000000 7.400000 135.000000  ;# Floor 22, Tower 1
node 730 27.000000 8.600000 135.000000  ;# Floor 22, Tower 1
node 731 27.000000 16.000000 135.000000  ;# Floor 22, Tower 1
node 732 30.000000 0.000000 135.000000  ;# Floor 22, Tower 1
node 733 30.000000 7.400000 135.000000  ;# Floor 22, Tower 1
node 734 30.000000 8.600000 135.000000  ;# Floor 22, Tower 1
node 735 30.000000 16.000000 135.000000  ;# Floor 22, Tower 1
node 736 0.000000 0.000000 141.000000  ;# Floor 23, Tower 1
node 737 0.000000 7.400000 141.000000  ;# Floor 23, Tower 1
node 738 0.000000 8.600000 141.000000  ;# Floor 23, Tower 1
node 739 0.000000 16.000000 141.000000  ;# Floor 23, Tower 1
node 740 3.000000 0.000000 141.000000  ;# Floor 23, Tower 1
node 741 3.000000 7.400000 141.000000  ;# Floor 23, Tower 1
node 742 3.000000 8.600000 141.000000  ;# Floor 23, Tower 1
node 743 3.000000 16.000000 141.000000  ;# Floor 23, Tower 1
node 744 11.000000 0.000000 141.000000  ;# Floor 23, Tower 1
node 745 11.000000 7.400000 141.000000  ;# Floor 23, Tower 1
node 746 11.000000 8.600000 141.000000  ;# Floor 23, Tower 1
node 747 11.000000 16.000000 141.000000  ;# Floor 23, Tower 1
node 748 14.400000 0.000000 141.000000  ;# Floor 23, Tower 1
node 749 14.400000 7.400000 141.000000  ;# Floor 23, Tower 1
node 750 14.400000 8.600000 141.000000  ;# Floor 23, Tower 1
node 751 14.400000 16.000000 141.000000  ;# Floor 23, Tower 1
node 752 15.600000 0.000000 141.000000  ;# Floor 23, Tower 1
node 753 15.600000 7.400000 141.000000  ;# Floor 23, Tower 1
node 754 15.600000 8.600000 141.000000  ;# Floor 23, Tower 1
node 755 15.600000 16.000000 141.000000  ;# Floor 23, Tower 1
node 756 19.000000 0.000000 141.000000  ;# Floor 23, Tower 1
node 757 19.000000 7.400000 141.000000  ;# Floor 23, Tower 1
node 758 19.000000 8.600000 141.000000  ;# Floor 23, Tower 1
node 759 19.000000 16.000000 141.000000  ;# Floor 23, Tower 1
node 760 27.000000 0.000000 141.000000  ;# Floor 23, Tower 1
node 761 27.000000 7.400000 141.000000  ;# Floor 23, Tower 1
node 762 27.000000 8.600000 141.000000  ;# Floor 23, Tower 1
node 763 27.000000 16.000000 141.000000  ;# Floor 23, Tower 1
node 764 30.000000 0.000000 141.000000  ;# Floor 23, Tower 1
node 765 30.000000 7.400000 141.000000  ;# Floor 23, Tower 1
node 766 30.000000 8.600000 141.000000  ;# Floor 23, Tower 1
node 767 30.000000 16.000000 141.000000  ;# Floor 23, Tower 1
node 768 0.000000 0.000000 147.000000  ;# Floor 24, Tower 1
node 769 0.000000 7.400000 147.000000  ;# Floor 24, Tower 1
node 770 0.000000 8.600000 147.000000  ;# Floor 24, Tower 1
node 771 0.000000 16.000000 147.000000  ;# Floor 24, Tower 1
node 772 3.000000 0.000000 147.000000  ;# Floor 24, Tower 1
node 773 3.000000 7.400000 147.000000  ;# Floor 24, Tower 1
node 774 3.000000 8.600000 147.000000  ;# Floor 24, Tower 1
node 775 3.000000 16.000000 147.000000  ;# Floor 24, Tower 1
node 776 11.000000 0.000000 147.000000  ;# Floor 24, Tower 1
node 777 11.000000 7.400000 147.000000  ;# Floor 24, Tower 1
node 778 11.000000 8.600000 147.000000  ;# Floor 24, Tower 1
node 779 11.000000 16.000000 147.000000  ;# Floor 24, Tower 1
node 780 14.400000 0.000000 147.000000  ;# Floor 24, Tower 1
node 781 14.400000 7.400000 147.000000  ;# Floor 24, Tower 1
node 782 14.400000 8.600000 147.000000  ;# Floor 24, Tower 1
node 783 14.400000 16.000000 147.000000  ;# Floor 24, Tower 1
node 784 15.600000 0.000000 147.000000  ;# Floor 24, Tower 1
node 785 15.600000 7.400000 147.000000  ;# Floor 24, Tower 1
node 786 15.600000 8.600000 147.000000  ;# Floor 24, Tower 1
node 787 15.600000 16.000000 147.000000  ;# Floor 24, Tower 1
node 788 19.000000 0.000000 147.000000  ;# Floor 24, Tower 1
node 789 19.000000 7.400000 147.000000  ;# Floor 24, Tower 1
node 790 19.000000 8.600000 147.000000  ;# Floor 24, Tower 1
node 791 19.000000 16.000000 147.000000  ;# Floor 24, Tower 1
node 792 27.000000 0.000000 147.000000  ;# Floor 24, Tower 1
node 793 27.000000 7.400000 147.000000  ;# Floor 24, Tower 1
node 794 27.000000 8.600000 147.000000  ;# Floor 24, Tower 1
node 795 27.000000 16.000000 147.000000  ;# Floor 24, Tower 1
node 796 30.000000 0.000000 147.000000  ;# Floor 24, Tower 1
node 797 30.000000 7.400000 147.000000  ;# Floor 24, Tower 1
node 798 30.000000 8.600000 147.000000  ;# Floor 24, Tower 1
node 799 30.000000 16.000000 147.000000  ;# Floor 24, Tower 1
node 800 0.000000 0.000000 153.000000  ;# Floor 25, Tower 1
node 801 0.000000 7.400000 153.000000  ;# Floor 25, Tower 1
node 802 0.000000 8.600000 153.000000  ;# Floor 25, Tower 1
node 803 0.000000 16.000000 153.000000  ;# Floor 25, Tower 1
node 804 3.000000 0.000000 153.000000  ;# Floor 25, Tower 1
node 805 3.000000 7.400000 153.000000  ;# Floor 25, Tower 1
node 806 3.000000 8.600000 153.000000  ;# Floor 25, Tower 1
node 807 3.000000 16.000000 153.000000  ;# Floor 25, Tower 1
node 808 11.000000 0.000000 153.000000  ;# Floor 25, Tower 1
node 809 11.000000 7.400000 153.000000  ;# Floor 25, Tower 1
node 810 11.000000 8.600000 153.000000  ;# Floor 25, Tower 1
node 811 11.000000 16.000000 153.000000  ;# Floor 25, Tower 1
node 812 14.400000 0.000000 153.000000  ;# Floor 25, Tower 1
node 813 14.400000 7.400000 153.000000  ;# Floor 25, Tower 1
node 814 14.400000 8.600000 153.000000  ;# Floor 25, Tower 1
node 815 14.400000 16.000000 153.000000  ;# Floor 25, Tower 1
node 816 15.600000 0.000000 153.000000  ;# Floor 25, Tower 1
node 817 15.600000 7.400000 153.000000  ;# Floor 25, Tower 1
node 818 15.600000 8.600000 153.000000  ;# Floor 25, Tower 1
node 819 15.600000 16.000000 153.000000  ;# Floor 25, Tower 1
node 820 19.000000 0.000000 153.000000  ;# Floor 25, Tower 1
node 821 19.000000 7.400000 153.000000  ;# Floor 25, Tower 1
node 822 19.000000 8.600000 153.000000  ;# Floor 25, Tower 1
node 823 19.000000 16.000000 153.000000  ;# Floor 25, Tower 1
node 824 27.000000 0.000000 153.000000  ;# Floor 25, Tower 1
node 825 27.000000 7.400000 153.000000  ;# Floor 25, Tower 1
node 826 27.000000 8.600000 153.000000  ;# Floor 25, Tower 1
node 827 27.000000 16.000000 153.000000  ;# Floor 25, Tower 1
node 828 30.000000 0.000000 153.000000  ;# Floor 25, Tower 1
node 829 30.000000 7.400000 153.000000  ;# Floor 25, Tower 1
node 830 30.000000 8.600000 153.000000  ;# Floor 25, Tower 1
node 831 30.000000 16.000000 153.000000  ;# Floor 25, Tower 1
node 832 0.000000 24.000000 0.000000  ;# Floor 0, Tower 2
node 833 0.000000 31.400000 0.000000  ;# Floor 0, Tower 2
node 834 0.000000 32.600000 0.000000  ;# Floor 0, Tower 2
node 835 0.000000 40.000000 0.000000  ;# Floor 0, Tower 2
node 836 3.000000 24.000000 0.000000  ;# Floor 0, Tower 2
node 837 3.000000 31.400000 0.000000  ;# Floor 0, Tower 2
node 838 3.000000 32.600000 0.000000  ;# Floor 0, Tower 2
node 839 3.000000 40.000000 0.000000  ;# Floor 0, Tower 2
node 840 11.000000 24.000000 0.000000  ;# Floor 0, Tower 2
node 841 11.000000 31.400000 0.000000  ;# Floor 0, Tower 2
node 842 11.000000 32.600000 0.000000  ;# Floor 0, Tower 2
node 843 11.000000 40.000000 0.000000  ;# Floor 0, Tower 2
node 844 14.400000 24.000000 0.000000  ;# Floor 0, Tower 2
node 845 14.400000 31.400000 0.000000  ;# Floor 0, Tower 2
node 846 14.400000 32.600000 0.000000  ;# Floor 0, Tower 2
node 847 14.400000 40.000000 0.000000  ;# Floor 0, Tower 2
node 848 15.600000 24.000000 0.000000  ;# Floor 0, Tower 2
node 849 15.600000 31.400000 0.000000  ;# Floor 0, Tower 2
node 850 15.600000 32.600000 0.000000  ;# Floor 0, Tower 2
node 851 15.600000 40.000000 0.000000  ;# Floor 0, Tower 2
node 852 19.000000 24.000000 0.000000  ;# Floor 0, Tower 2
node 853 19.000000 31.400000 0.000000  ;# Floor 0, Tower 2
node 854 19.000000 32.600000 0.000000  ;# Floor 0, Tower 2
node 855 19.000000 40.000000 0.000000  ;# Floor 0, Tower 2
node 856 27.000000 24.000000 0.000000  ;# Floor 0, Tower 2
node 857 27.000000 31.400000 0.000000  ;# Floor 0, Tower 2
node 858 27.000000 32.600000 0.000000  ;# Floor 0, Tower 2
node 859 27.000000 40.000000 0.000000  ;# Floor 0, Tower 2
node 860 30.000000 24.000000 0.000000  ;# Floor 0, Tower 2
node 861 30.000000 31.400000 0.000000  ;# Floor 0, Tower 2
node 862 30.000000 32.600000 0.000000  ;# Floor 0, Tower 2
node 863 30.000000 40.000000 0.000000  ;# Floor 0, Tower 2
node 864 0.000000 24.000000 9.000000  ;# Floor 1, Tower 2
node 865 0.000000 31.400000 9.000000  ;# Floor 1, Tower 2
node 866 0.000000 32.600000 9.000000  ;# Floor 1, Tower 2
node 867 0.000000 40.000000 9.000000  ;# Floor 1, Tower 2
node 868 3.000000 24.000000 9.000000  ;# Floor 1, Tower 2
node 869 3.000000 31.400000 9.000000  ;# Floor 1, Tower 2
node 870 3.000000 32.600000 9.000000  ;# Floor 1, Tower 2
node 871 3.000000 40.000000 9.000000  ;# Floor 1, Tower 2
node 872 11.000000 24.000000 9.000000  ;# Floor 1, Tower 2
node 873 11.000000 31.400000 9.000000  ;# Floor 1, Tower 2
node 874 11.000000 32.600000 9.000000  ;# Floor 1, Tower 2
node 875 11.000000 40.000000 9.000000  ;# Floor 1, Tower 2
node 876 14.400000 24.000000 9.000000  ;# Floor 1, Tower 2
node 877 14.400000 31.400000 9.000000  ;# Floor 1, Tower 2
node 878 14.400000 32.600000 9.000000  ;# Floor 1, Tower 2
node 879 14.400000 40.000000 9.000000  ;# Floor 1, Tower 2
node 880 15.600000 24.000000 9.000000  ;# Floor 1, Tower 2
node 881 15.600000 31.400000 9.000000  ;# Floor 1, Tower 2
node 882 15.600000 32.600000 9.000000  ;# Floor 1, Tower 2
node 883 15.600000 40.000000 9.000000  ;# Floor 1, Tower 2
node 884 19.000000 24.000000 9.000000  ;# Floor 1, Tower 2
node 885 19.000000 31.400000 9.000000  ;# Floor 1, Tower 2
node 886 19.000000 32.600000 9.000000  ;# Floor 1, Tower 2
node 887 19.000000 40.000000 9.000000  ;# Floor 1, Tower 2
node 888 27.000000 24.000000 9.000000  ;# Floor 1, Tower 2
node 889 27.000000 31.400000 9.000000  ;# Floor 1, Tower 2
node 890 27.000000 32.600000 9.000000  ;# Floor 1, Tower 2
node 891 27.000000 40.000000 9.000000  ;# Floor 1, Tower 2
node 892 30.000000 24.000000 9.000000  ;# Floor 1, Tower 2
node 893 30.000000 31.400000 9.000000  ;# Floor 1, Tower 2
node 894 30.000000 32.600000 9.000000  ;# Floor 1, Tower 2
node 895 30.000000 40.000000 9.000000  ;# Floor 1, Tower 2
node 896 0.000000 24.000000 15.000000  ;# Floor 2, Tower 2
node 897 0.000000 31.400000 15.000000  ;# Floor 2, Tower 2
node 898 0.000000 32.600000 15.000000  ;# Floor 2, Tower 2
node 899 0.000000 40.000000 15.000000  ;# Floor 2, Tower 2
node 900 3.000000 24.000000 15.000000  ;# Floor 2, Tower 2
node 901 3.000000 31.400000 15.000000  ;# Floor 2, Tower 2
node 902 3.000000 32.600000 15.000000  ;# Floor 2, Tower 2
node 903 3.000000 40.000000 15.000000  ;# Floor 2, Tower 2
node 904 11.000000 24.000000 15.000000  ;# Floor 2, Tower 2
node 905 11.000000 31.400000 15.000000  ;# Floor 2, Tower 2
node 906 11.000000 32.600000 15.000000  ;# Floor 2, Tower 2
node 907 11.000000 40.000000 15.000000  ;# Floor 2, Tower 2
node 908 14.400000 24.000000 15.000000  ;# Floor 2, Tower 2
node 909 14.400000 31.400000 15.000000  ;# Floor 2, Tower 2
node 910 14.400000 32.600000 15.000000  ;# Floor 2, Tower 2
node 911 14.400000 40.000000 15.000000  ;# Floor 2, Tower 2
node 912 15.600000 24.000000 15.000000  ;# Floor 2, Tower 2
node 913 15.600000 31.400000 15.000000  ;# Floor 2, Tower 2
node 914 15.600000 32.600000 15.000000  ;# Floor 2, Tower 2
node 915 15.600000 40.000000 15.000000  ;# Floor 2, Tower 2
node 916 19.000000 24.000000 15.000000  ;# Floor 2, Tower 2
node 917 19.000000 31.400000 15.000000  ;# Floor 2, Tower 2
node 918 19.000000 32.600000 15.000000  ;# Floor 2, Tower 2
node 919 19.000000 40.000000 15.000000  ;# Floor 2, Tower 2
node 920 27.000000 24.000000 15.000000  ;# Floor 2, Tower 2
node 921 27.000000 31.400000 15.000000  ;# Floor 2, Tower 2
node 922 27.000000 32.600000 15.000000  ;# Floor 2, Tower 2
node 923 27.000000 40.000000 15.000000  ;# Floor 2, Tower 2
node 924 30.000000 24.000000 15.000000  ;# Floor 2, Tower 2
node 925 30.000000 31.400000 15.000000  ;# Floor 2, Tower 2
node 926 30.000000 32.600000 15.000000  ;# Floor 2, Tower 2
node 927 30.000000 40.000000 15.000000  ;# Floor 2, Tower 2
node 928 0.000000 24.000000 21.000000  ;# Floor 3, Tower 2
node 929 0.000000 31.400000 21.000000  ;# Floor 3, Tower 2
node 930 0.000000 32.600000 21.000000  ;# Floor 3, Tower 2
node 931 0.000000 40.000000 21.000000  ;# Floor 3, Tower 2
node 932 3.000000 24.000000 21.000000  ;# Floor 3, Tower 2
node 933 3.000000 31.400000 21.000000  ;# Floor 3, Tower 2
node 934 3.000000 32.600000 21.000000  ;# Floor 3, Tower 2
node 935 3.000000 40.000000 21.000000  ;# Floor 3, Tower 2
node 936 11.000000 24.000000 21.000000  ;# Floor 3, Tower 2
node 937 11.000000 31.400000 21.000000  ;# Floor 3, Tower 2
node 938 11.000000 32.600000 21.000000  ;# Floor 3, Tower 2
node 939 11.000000 40.000000 21.000000  ;# Floor 3, Tower 2
node 940 14.400000 24.000000 21.000000  ;# Floor 3, Tower 2
node 941 14.400000 31.400000 21.000000  ;# Floor 3, Tower 2
node 942 14.400000 32.600000 21.000000  ;# Floor 3, Tower 2
node 943 14.400000 40.000000 21.000000  ;# Floor 3, Tower 2
node 944 15.600000 24.000000 21.000000  ;# Floor 3, Tower 2
node 945 15.600000 31.400000 21.000000  ;# Floor 3, Tower 2
node 946 15.600000 32.600000 21.000000  ;# Floor 3, Tower 2
node 947 15.600000 40.000000 21.000000  ;# Floor 3, Tower 2
node 948 19.000000 24.000000 21.000000  ;# Floor 3, Tower 2
node 949 19.000000 31.400000 21.000000  ;# Floor 3, Tower 2
node 950 19.000000 32.600000 21.000000  ;# Floor 3, Tower 2
node 951 19.000000 40.000000 21.000000  ;# Floor 3, Tower 2
node 952 27.000000 24.000000 21.000000  ;# Floor 3, Tower 2
node 953 27.000000 31.400000 21.000000  ;# Floor 3, Tower 2
node 954 27.000000 32.600000 21.000000  ;# Floor 3, Tower 2
node 955 27.000000 40.000000 21.000000  ;# Floor 3, Tower 2
node 956 30.000000 24.000000 21.000000  ;# Floor 3, Tower 2
node 957 30.000000 31.400000 21.000000  ;# Floor 3, Tower 2
node 958 30.000000 32.600000 21.000000  ;# Floor 3, Tower 2
node 959 30.000000 40.000000 21.000000  ;# Floor 3, Tower 2
node 960 0.000000 24.000000 27.000000  ;# Floor 4, Tower 2
node 961 0.000000 31.400000 27.000000  ;# Floor 4, Tower 2
node 962 0.000000 32.600000 27.000000  ;# Floor 4, Tower 2
node 963 0.000000 40.000000 27.000000  ;# Floor 4, Tower 2
node 964 3.000000 24.000000 27.000000  ;# Floor 4, Tower 2
node 965 3.000000 31.400000 27.000000  ;# Floor 4, Tower 2
node 966 3.000000 32.600000 27.000000  ;# Floor 4, Tower 2
node 967 3.000000 40.000000 27.000000  ;# Floor 4, Tower 2
node 968 11.000000 24.000000 27.000000  ;# Floor 4, Tower 2
node 969 11.000000 31.400000 27.000000  ;# Floor 4, Tower 2
node 970 11.000000 32.600000 27.000000  ;# Floor 4, Tower 2
node 971 11.000000 40.000000 27.000000  ;# Floor 4, Tower 2
node 972 14.400000 24.000000 27.000000  ;# Floor 4, Tower 2
node 973 14.400000 31.400000 27.000000  ;# Floor 4, Tower 2
node 974 14.400000 32.600000 27.000000  ;# Floor 4, Tower 2
node 975 14.400000 40.000000 27.000000  ;# Floor 4, Tower 2
node 976 15.600000 24.000000 27.000000  ;# Floor 4, Tower 2
node 977 15.600000 31.400000 27.000000  ;# Floor 4, Tower 2
node 978 15.600000 32.600000 27.000000  ;# Floor 4, Tower 2
node 979 15.600000 40.000000 27.000000  ;# Floor 4, Tower 2
node 980 19.000000 24.000000 27.000000  ;# Floor 4, Tower 2
node 981 19.000000 31.400000 27.000000  ;# Floor 4, Tower 2
node 982 19.000000 32.600000 27.000000  ;# Floor 4, Tower 2
node 983 19.000000 40.000000 27.000000  ;# Floor 4, Tower 2
node 984 27.000000 24.000000 27.000000  ;# Floor 4, Tower 2
node 985 27.000000 31.400000 27.000000  ;# Floor 4, Tower 2
node 986 27.000000 32.600000 27.000000  ;# Floor 4, Tower 2
node 987 27.000000 40.000000 27.000000  ;# Floor 4, Tower 2
node 988 30.000000 24.000000 27.000000  ;# Floor 4, Tower 2
node 989 30.000000 31.400000 27.000000  ;# Floor 4, Tower 2
node 990 30.000000 32.600000 27.000000  ;# Floor 4, Tower 2
node 991 30.000000 40.000000 27.000000  ;# Floor 4, Tower 2
node 992 0.000000 24.000000 33.000000  ;# Floor 5, Tower 2
node 993 0.000000 31.400000 33.000000  ;# Floor 5, Tower 2
node 994 0.000000 32.600000 33.000000  ;# Floor 5, Tower 2
node 995 0.000000 40.000000 33.000000  ;# Floor 5, Tower 2
node 996 3.000000 24.000000 33.000000  ;# Floor 5, Tower 2
node 997 3.000000 31.400000 33.000000  ;# Floor 5, Tower 2
node 998 3.000000 32.600000 33.000000  ;# Floor 5, Tower 2
node 999 3.000000 40.000000 33.000000  ;# Floor 5, Tower 2
node 1000 11.000000 24.000000 33.000000  ;# Floor 5, Tower 2
node 1001 11.000000 31.400000 33.000000  ;# Floor 5, Tower 2
node 1002 11.000000 32.600000 33.000000  ;# Floor 5, Tower 2
node 1003 11.000000 40.000000 33.000000  ;# Floor 5, Tower 2
node 1004 14.400000 24.000000 33.000000  ;# Floor 5, Tower 2
node 1005 14.400000 31.400000 33.000000  ;# Floor 5, Tower 2
node 1006 14.400000 32.600000 33.000000  ;# Floor 5, Tower 2
node 1007 14.400000 40.000000 33.000000  ;# Floor 5, Tower 2
node 1008 15.600000 24.000000 33.000000  ;# Floor 5, Tower 2
node 1009 15.600000 31.400000 33.000000  ;# Floor 5, Tower 2
node 1010 15.600000 32.600000 33.000000  ;# Floor 5, Tower 2
node 1011 15.600000 40.000000 33.000000  ;# Floor 5, Tower 2
node 1012 19.000000 24.000000 33.000000  ;# Floor 5, Tower 2
node 1013 19.000000 31.400000 33.000000  ;# Floor 5, Tower 2
node 1014 19.000000 32.600000 33.000000  ;# Floor 5, Tower 2
node 1015 19.000000 40.000000 33.000000  ;# Floor 5, Tower 2
node 1016 27.000000 24.000000 33.000000  ;# Floor 5, Tower 2
node 1017 27.000000 31.400000 33.000000  ;# Floor 5, Tower 2
node 1018 27.000000 32.600000 33.000000  ;# Floor 5, Tower 2
node 1019 27.000000 40.000000 33.000000  ;# Floor 5, Tower 2
node 1020 30.000000 24.000000 33.000000  ;# Floor 5, Tower 2
node 1021 30.000000 31.400000 33.000000  ;# Floor 5, Tower 2
node 1022 30.000000 32.600000 33.000000  ;# Floor 5, Tower 2
node 1023 30.000000 40.000000 33.000000  ;# Floor 5, Tower 2
node 1024 0.000000 24.000000 39.000000  ;# Floor 6, Tower 2
node 1025 0.000000 31.400000 39.000000  ;# Floor 6, Tower 2
node 1026 0.000000 32.600000 39.000000  ;# Floor 6, Tower 2
node 1027 0.000000 40.000000 39.000000  ;# Floor 6, Tower 2
node 1028 3.000000 24.000000 39.000000  ;# Floor 6, Tower 2
node 1029 3.000000 31.400000 39.000000  ;# Floor 6, Tower 2
node 1030 3.000000 32.600000 39.000000  ;# Floor 6, Tower 2
node 1031 3.000000 40.000000 39.000000  ;# Floor 6, Tower 2
node 1032 11.000000 24.000000 39.000000  ;# Floor 6, Tower 2
node 1033 11.000000 31.400000 39.000000  ;# Floor 6, Tower 2
node 1034 11.000000 32.600000 39.000000  ;# Floor 6, Tower 2
node 1035 11.000000 40.000000 39.000000  ;# Floor 6, Tower 2
node 1036 14.400000 24.000000 39.000000  ;# Floor 6, Tower 2
node 1037 14.400000 31.400000 39.000000  ;# Floor 6, Tower 2
node 1038 14.400000 32.600000 39.000000  ;# Floor 6, Tower 2
node 1039 14.400000 40.000000 39.000000  ;# Floor 6, Tower 2
node 1040 15.600000 24.000000 39.000000  ;# Floor 6, Tower 2
node 1041 15.600000 31.400000 39.000000  ;# Floor 6, Tower 2
node 1042 15.600000 32.600000 39.000000  ;# Floor 6, Tower 2
node 1043 15.600000 40.000000 39.000000  ;# Floor 6, Tower 2
node 1044 19.000000 24.000000 39.000000  ;# Floor 6, Tower 2
node 1045 19.000000 31.400000 39.000000  ;# Floor 6, Tower 2
node 1046 19.000000 32.600000 39.000000  ;# Floor 6, Tower 2
node 1047 19.000000 40.000000 39.000000  ;# Floor 6, Tower 2
node 1048 27.000000 24.000000 39.000000  ;# Floor 6, Tower 2
node 1049 27.000000 31.400000 39.000000  ;# Floor 6, Tower 2
node 1050 27.000000 32.600000 39.000000  ;# Floor 6, Tower 2
node 1051 27.000000 40.000000 39.000000  ;# Floor 6, Tower 2
node 1052 30.000000 24.000000 39.000000  ;# Floor 6, Tower 2
node 1053 30.000000 31.400000 39.000000  ;# Floor 6, Tower 2
node 1054 30.000000 32.600000 39.000000  ;# Floor 6, Tower 2
node 1055 30.000000 40.000000 39.000000  ;# Floor 6, Tower 2
node 1056 0.000000 24.000000 45.000000  ;# Floor 7, Tower 2
node 1057 0.000000 31.400000 45.000000  ;# Floor 7, Tower 2
node 1058 0.000000 32.600000 45.000000  ;# Floor 7, Tower 2
node 1059 0.000000 40.000000 45.000000  ;# Floor 7, Tower 2
node 1060 3.000000 24.000000 45.000000  ;# Floor 7, Tower 2
node 1061 3.000000 31.400000 45.000000  ;# Floor 7, Tower 2
node 1062 3.000000 32.600000 45.000000  ;# Floor 7, Tower 2
node 1063 3.000000 40.000000 45.000000  ;# Floor 7, Tower 2
node 1064 11.000000 24.000000 45.000000  ;# Floor 7, Tower 2
node 1065 11.000000 31.400000 45.000000  ;# Floor 7, Tower 2
node 1066 11.000000 32.600000 45.000000  ;# Floor 7, Tower 2
node 1067 11.000000 40.000000 45.000000  ;# Floor 7, Tower 2
node 1068 14.400000 24.000000 45.000000  ;# Floor 7, Tower 2
node 1069 14.400000 31.400000 45.000000  ;# Floor 7, Tower 2
node 1070 14.400000 32.600000 45.000000  ;# Floor 7, Tower 2
node 1071 14.400000 40.000000 45.000000  ;# Floor 7, Tower 2
node 1072 15.600000 24.000000 45.000000  ;# Floor 7, Tower 2
node 1073 15.600000 31.400000 45.000000  ;# Floor 7, Tower 2
node 1074 15.600000 32.600000 45.000000  ;# Floor 7, Tower 2
node 1075 15.600000 40.000000 45.000000  ;# Floor 7, Tower 2
node 1076 19.000000 24.000000 45.000000  ;# Floor 7, Tower 2
node 1077 19.000000 31.400000 45.000000  ;# Floor 7, Tower 2
node 1078 19.000000 32.600000 45.000000  ;# Floor 7, Tower 2
node 1079 19.000000 40.000000 45.000000  ;# Floor 7, Tower 2
node 1080 27.000000 24.000000 45.000000  ;# Floor 7, Tower 2
node 1081 27.000000 31.400000 45.000000  ;# Floor 7, Tower 2
node 1082 27.000000 32.600000 45.000000  ;# Floor 7, Tower 2
node 1083 27.000000 40.000000 45.000000  ;# Floor 7, Tower 2
node 1084 30.000000 24.000000 45.000000  ;# Floor 7, Tower 2
node 1085 30.000000 31.400000 45.000000  ;# Floor 7, Tower 2
node 1086 30.000000 32.600000 45.000000  ;# Floor 7, Tower 2
node 1087 30.000000 40.000000 45.000000  ;# Floor 7, Tower 2
node 1088 0.000000 24.000000 51.000000  ;# Floor 8, Tower 2
node 1089 0.000000 31.400000 51.000000  ;# Floor 8, Tower 2
node 1090 0.000000 32.600000 51.000000  ;# Floor 8, Tower 2
node 1091 0.000000 40.000000 51.000000  ;# Floor 8, Tower 2
node 1092 3.000000 24.000000 51.000000  ;# Floor 8, Tower 2
node 1093 3.000000 31.400000 51.000000  ;# Floor 8, Tower 2
node 1094 3.000000 32.600000 51.000000  ;# Floor 8, Tower 2
node 1095 3.000000 40.000000 51.000000  ;# Floor 8, Tower 2
node 1096 11.000000 24.000000 51.000000  ;# Floor 8, Tower 2
node 1097 11.000000 31.400000 51.000000  ;# Floor 8, Tower 2
node 1098 11.000000 32.600000 51.000000  ;# Floor 8, Tower 2
node 1099 11.000000 40.000000 51.000000  ;# Floor 8, Tower 2
node 1100 14.400000 24.000000 51.000000  ;# Floor 8, Tower 2
node 1101 14.400000 31.400000 51.000000  ;# Floor 8, Tower 2
node 1102 14.400000 32.600000 51.000000  ;# Floor 8, Tower 2
node 1103 14.400000 40.000000 51.000000  ;# Floor 8, Tower 2
node 1104 15.600000 24.000000 51.000000  ;# Floor 8, Tower 2
node 1105 15.600000 31.400000 51.000000  ;# Floor 8, Tower 2
node 1106 15.600000 32.600000 51.000000  ;# Floor 8, Tower 2
node 1107 15.600000 40.000000 51.000000  ;# Floor 8, Tower 2
node 1108 19.000000 24.000000 51.000000  ;# Floor 8, Tower 2
node 1109 19.000000 31.400000 51.000000  ;# Floor 8, Tower 2
node 1110 19.000000 32.600000 51.000000  ;# Floor 8, Tower 2
node 1111 19.000000 40.000000 51.000000  ;# Floor 8, Tower 2
node 1112 27.000000 24.000000 51.000000  ;# Floor 8, Tower 2
node 1113 27.000000 31.400000 51.000000  ;# Floor 8, Tower 2
node 1114 27.000000 32.600000 51.000000  ;# Floor 8, Tower 2
node 1115 27.000000 40.000000 51.000000  ;# Floor 8, Tower 2
node 1116 30.000000 24.000000 51.000000  ;# Floor 8, Tower 2
node 1117 30.000000 31.400000 51.000000  ;# Floor 8, Tower 2
node 1118 30.000000 32.600000 51.000000  ;# Floor 8, Tower 2
node 1119 30.000000 40.000000 51.000000  ;# Floor 8, Tower 2
node 1120 0.000000 24.000000 57.000000  ;# Floor 9, Tower 2
node 1121 0.000000 31.400000 57.000000  ;# Floor 9, Tower 2
node 1122 0.000000 32.600000 57.000000  ;# Floor 9, Tower 2
node 1123 0.000000 40.000000 57.000000  ;# Floor 9, Tower 2
node 1124 3.000000 24.000000 57.000000  ;# Floor 9, Tower 2
node 1125 3.000000 31.400000 57.000000  ;# Floor 9, Tower 2
node 1126 3.000000 32.600000 57.000000  ;# Floor 9, Tower 2
node 1127 3.000000 40.000000 57.000000  ;# Floor 9, Tower 2
node 1128 11.000000 24.000000 57.000000  ;# Floor 9, Tower 2
node 1129 11.000000 31.400000 57.000000  ;# Floor 9, Tower 2
node 1130 11.000000 32.600000 57.000000  ;# Floor 9, Tower 2
node 1131 11.000000 40.000000 57.000000  ;# Floor 9, Tower 2
node 1132 14.400000 24.000000 57.000000  ;# Floor 9, Tower 2
node 1133 14.400000 31.400000 57.000000  ;# Floor 9, Tower 2
node 1134 14.400000 32.600000 57.000000  ;# Floor 9, Tower 2
node 1135 14.400000 40.000000 57.000000  ;# Floor 9, Tower 2
node 1136 15.600000 24.000000 57.000000  ;# Floor 9, Tower 2
node 1137 15.600000 31.400000 57.000000  ;# Floor 9, Tower 2
node 1138 15.600000 32.600000 57.000000  ;# Floor 9, Tower 2
node 1139 15.600000 40.000000 57.000000  ;# Floor 9, Tower 2
node 1140 19.000000 24.000000 57.000000  ;# Floor 9, Tower 2
node 1141 19.000000 31.400000 57.000000  ;# Floor 9, Tower 2
node 1142 19.000000 32.600000 57.000000  ;# Floor 9, Tower 2
node 1143 19.000000 40.000000 57.000000  ;# Floor 9, Tower 2
node 1144 27.000000 24.000000 57.000000  ;# Floor 9, Tower 2
node 1145 27.000000 31.400000 57.000000  ;# Floor 9, Tower 2
node 1146 27.000000 32.600000 57.000000  ;# Floor 9, Tower 2
node 1147 27.000000 40.000000 57.000000  ;# Floor 9, Tower 2
node 1148 30.000000 24.000000 57.000000  ;# Floor 9, Tower 2
node 1149 30.000000 31.400000 57.000000  ;# Floor 9, Tower 2
node 1150 30.000000 32.600000 57.000000  ;# Floor 9, Tower 2
node 1151 30.000000 40.000000 57.000000  ;# Floor 9, Tower 2
node 1152 0.000000 24.000000 63.000000  ;# Floor 10, Tower 2
node 1153 0.000000 31.400000 63.000000  ;# Floor 10, Tower 2
node 1154 0.000000 32.600000 63.000000  ;# Floor 10, Tower 2
node 1155 0.000000 40.000000 63.000000  ;# Floor 10, Tower 2
node 1156 3.000000 24.000000 63.000000  ;# Floor 10, Tower 2
node 1157 3.000000 31.400000 63.000000  ;# Floor 10, Tower 2
node 1158 3.000000 32.600000 63.000000  ;# Floor 10, Tower 2
node 1159 3.000000 40.000000 63.000000  ;# Floor 10, Tower 2
node 1160 11.000000 24.000000 63.000000  ;# Floor 10, Tower 2
node 1161 11.000000 31.400000 63.000000  ;# Floor 10, Tower 2
node 1162 11.000000 32.600000 63.000000  ;# Floor 10, Tower 2
node 1163 11.000000 40.000000 63.000000  ;# Floor 10, Tower 2
node 1164 14.400000 24.000000 63.000000  ;# Floor 10, Tower 2
node 1165 14.400000 31.400000 63.000000  ;# Floor 10, Tower 2
node 1166 14.400000 32.600000 63.000000  ;# Floor 10, Tower 2
node 1167 14.400000 40.000000 63.000000  ;# Floor 10, Tower 2
node 1168 15.600000 24.000000 63.000000  ;# Floor 10, Tower 2
node 1169 15.600000 31.400000 63.000000  ;# Floor 10, Tower 2
node 1170 15.600000 32.600000 63.000000  ;# Floor 10, Tower 2
node 1171 15.600000 40.000000 63.000000  ;# Floor 10, Tower 2
node 1172 19.000000 24.000000 63.000000  ;# Floor 10, Tower 2
node 1173 19.000000 31.400000 63.000000  ;# Floor 10, Tower 2
node 1174 19.000000 32.600000 63.000000  ;# Floor 10, Tower 2
node 1175 19.000000 40.000000 63.000000  ;# Floor 10, Tower 2
node 1176 27.000000 24.000000 63.000000  ;# Floor 10, Tower 2
node 1177 27.000000 31.400000 63.000000  ;# Floor 10, Tower 2
node 1178 27.000000 32.600000 63.000000  ;# Floor 10, Tower 2
node 1179 27.000000 40.000000 63.000000  ;# Floor 10, Tower 2
node 1180 30.000000 24.000000 63.000000  ;# Floor 10, Tower 2
node 1181 30.000000 31.400000 63.000000  ;# Floor 10, Tower 2
node 1182 30.000000 32.600000 63.000000  ;# Floor 10, Tower 2
node 1183 30.000000 40.000000 63.000000  ;# Floor 10, Tower 2
node 1184 0.000000 24.000000 69.000000  ;# Floor 11, Tower 2
node 1185 0.000000 31.400000 69.000000  ;# Floor 11, Tower 2
node 1186 0.000000 32.600000 69.000000  ;# Floor 11, Tower 2
node 1187 0.000000 40.000000 69.000000  ;# Floor 11, Tower 2
node 1188 3.000000 24.000000 69.000000  ;# Floor 11, Tower 2
node 1189 3.000000 31.400000 69.000000  ;# Floor 11, Tower 2
node 1190 3.000000 32.600000 69.000000  ;# Floor 11, Tower 2
node 1191 3.000000 40.000000 69.000000  ;# Floor 11, Tower 2
node 1192 11.000000 24.000000 69.000000  ;# Floor 11, Tower 2
node 1193 11.000000 31.400000 69.000000  ;# Floor 11, Tower 2
node 1194 11.000000 32.600000 69.000000  ;# Floor 11, Tower 2
node 1195 11.000000 40.000000 69.000000  ;# Floor 11, Tower 2
node 1196 14.400000 24.000000 69.000000  ;# Floor 11, Tower 2
node 1197 14.400000 31.400000 69.000000  ;# Floor 11, Tower 2
node 1198 14.400000 32.600000 69.000000  ;# Floor 11, Tower 2
node 1199 14.400000 40.000000 69.000000  ;# Floor 11, Tower 2
node 1200 15.600000 24.000000 69.000000  ;# Floor 11, Tower 2
node 1201 15.600000 31.400000 69.000000  ;# Floor 11, Tower 2
node 1202 15.600000 32.600000 69.000000  ;# Floor 11, Tower 2
node 1203 15.600000 40.000000 69.000000  ;# Floor 11, Tower 2
node 1204 19.000000 24.000000 69.000000  ;# Floor 11, Tower 2
node 1205 19.000000 31.400000 69.000000  ;# Floor 11, Tower 2
node 1206 19.000000 32.600000 69.000000  ;# Floor 11, Tower 2
node 1207 19.000000 40.000000 69.000000  ;# Floor 11, Tower 2
node 1208 27.000000 24.000000 69.000000  ;# Floor 11, Tower 2
node 1209 27.000000 31.400000 69.000000  ;# Floor 11, Tower 2
node 1210 27.000000 32.600000 69.000000  ;# Floor 11, Tower 2
node 1211 27.000000 40.000000 69.000000  ;# Floor 11, Tower 2
node 1212 30.000000 24.000000 69.000000  ;# Floor 11, Tower 2
node 1213 30.000000 31.400000 69.000000  ;# Floor 11, Tower 2
node 1214 30.000000 32.600000 69.000000  ;# Floor 11, Tower 2
node 1215 30.000000 40.000000 69.000000  ;# Floor 11, Tower 2
node 1216 0.000000 24.000000 75.000000  ;# Floor 12, Tower 2
node 1217 0.000000 31.400000 75.000000  ;# Floor 12, Tower 2
node 1218 0.000000 32.600000 75.000000  ;# Floor 12, Tower 2
node 1219 0.000000 40.000000 75.000000  ;# Floor 12, Tower 2
node 1220 3.000000 24.000000 75.000000  ;# Floor 12, Tower 2
node 1221 3.000000 31.400000 75.000000  ;# Floor 12, Tower 2
node 1222 3.000000 32.600000 75.000000  ;# Floor 12, Tower 2
node 1223 3.000000 40.000000 75.000000  ;# Floor 12, Tower 2
node 1224 11.000000 24.000000 75.000000  ;# Floor 12, Tower 2
node 1225 11.000000 31.400000 75.000000  ;# Floor 12, Tower 2
node 1226 11.000000 32.600000 75.000000  ;# Floor 12, Tower 2
node 1227 11.000000 40.000000 75.000000  ;# Floor 12, Tower 2
node 1228 14.400000 24.000000 75.000000  ;# Floor 12, Tower 2
node 1229 14.400000 31.400000 75.000000  ;# Floor 12, Tower 2
node 1230 14.400000 32.600000 75.000000  ;# Floor 12, Tower 2
node 1231 14.400000 40.000000 75.000000  ;# Floor 12, Tower 2
node 1232 15.600000 24.000000 75.000000  ;# Floor 12, Tower 2
node 1233 15.600000 31.400000 75.000000  ;# Floor 12, Tower 2
node 1234 15.600000 32.600000 75.000000  ;# Floor 12, Tower 2
node 1235 15.600000 40.000000 75.000000  ;# Floor 12, Tower 2
node 1236 19.000000 24.000000 75.000000  ;# Floor 12, Tower 2
node 1237 19.000000 31.400000 75.000000  ;# Floor 12, Tower 2
node 1238 19.000000 32.600000 75.000000  ;# Floor 12, Tower 2
node 1239 19.000000 40.000000 75.000000  ;# Floor 12, Tower 2
node 1240 27.000000 24.000000 75.000000  ;# Floor 12, Tower 2
node 1241 27.000000 31.400000 75.000000  ;# Floor 12, Tower 2
node 1242 27.000000 32.600000 75.000000  ;# Floor 12, Tower 2
node 1243 27.000000 40.000000 75.000000  ;# Floor 12, Tower 2
node 1244 30.000000 24.000000 75.000000  ;# Floor 12, Tower 2
node 1245 30.000000 31.400000 75.000000  ;# Floor 12, Tower 2
node 1246 30.000000 32.600000 75.000000  ;# Floor 12, Tower 2
node 1247 30.000000 40.000000 75.000000  ;# Floor 12, Tower 2
node 1248 0.000000 24.000000 81.000000  ;# Floor 13, Tower 2
node 1249 0.000000 31.400000 81.000000  ;# Floor 13, Tower 2
node 1250 0.000000 32.600000 81.000000  ;# Floor 13, Tower 2
node 1251 0.000000 40.000000 81.000000  ;# Floor 13, Tower 2
node 1252 3.000000 24.000000 81.000000  ;# Floor 13, Tower 2
node 1253 3.000000 31.400000 81.000000  ;# Floor 13, Tower 2
node 1254 3.000000 32.600000 81.000000  ;# Floor 13, Tower 2
node 1255 3.000000 40.000000 81.000000  ;# Floor 13, Tower 2
node 1256 11.000000 24.000000 81.000000  ;# Floor 13, Tower 2
node 1257 11.000000 31.400000 81.000000  ;# Floor 13, Tower 2
node 1258 11.000000 32.600000 81.000000  ;# Floor 13, Tower 2
node 1259 11.000000 40.000000 81.000000  ;# Floor 13, Tower 2
node 1260 14.400000 24.000000 81.000000  ;# Floor 13, Tower 2
node 1261 14.400000 31.400000 81.000000  ;# Floor 13, Tower 2
node 1262 14.400000 32.600000 81.000000  ;# Floor 13, Tower 2
node 1263 14.400000 40.000000 81.000000  ;# Floor 13, Tower 2
node 1264 15.600000 24.000000 81.000000  ;# Floor 13, Tower 2
node 1265 15.600000 31.400000 81.000000  ;# Floor 13, Tower 2
node 1266 15.600000 32.600000 81.000000  ;# Floor 13, Tower 2
node 1267 15.600000 40.000000 81.000000  ;# Floor 13, Tower 2
node 1268 19.000000 24.000000 81.000000  ;# Floor 13, Tower 2
node 1269 19.000000 31.400000 81.000000  ;# Floor 13, Tower 2
node 1270 19.000000 32.600000 81.000000  ;# Floor 13, Tower 2
node 1271 19.000000 40.000000 81.000000  ;# Floor 13, Tower 2
node 1272 27.000000 24.000000 81.000000  ;# Floor 13, Tower 2
node 1273 27.000000 31.400000 81.000000  ;# Floor 13, Tower 2
node 1274 27.000000 32.600000 81.000000  ;# Floor 13, Tower 2
node 1275 27.000000 40.000000 81.000000  ;# Floor 13, Tower 2
node 1276 30.000000 24.000000 81.000000  ;# Floor 13, Tower 2
node 1277 30.000000 31.400000 81.000000  ;# Floor 13, Tower 2
node 1278 30.000000 32.600000 81.000000  ;# Floor 13, Tower 2
node 1279 30.000000 40.000000 81.000000  ;# Floor 13, Tower 2
node 1280 0.000000 24.000000 87.000000  ;# Floor 14, Tower 2
node 1281 0.000000 31.400000 87.000000  ;# Floor 14, Tower 2
node 1282 0.000000 32.600000 87.000000  ;# Floor 14, Tower 2
node 1283 0.000000 40.000000 87.000000  ;# Floor 14, Tower 2
node 1284 3.000000 24.000000 87.000000  ;# Floor 14, Tower 2
node 1285 3.000000 31.400000 87.000000  ;# Floor 14, Tower 2
node 1286 3.000000 32.600000 87.000000  ;# Floor 14, Tower 2
node 1287 3.000000 40.000000 87.000000  ;# Floor 14, Tower 2
node 1288 11.000000 24.000000 87.000000  ;# Floor 14, Tower 2
node 1289 11.000000 31.400000 87.000000  ;# Floor 14, Tower 2
node 1290 11.000000 32.600000 87.000000  ;# Floor 14, Tower 2
node 1291 11.000000 40.000000 87.000000  ;# Floor 14, Tower 2
node 1292 14.400000 24.000000 87.000000  ;# Floor 14, Tower 2
node 1293 14.400000 31.400000 87.000000  ;# Floor 14, Tower 2
node 1294 14.400000 32.600000 87.000000  ;# Floor 14, Tower 2
node 1295 14.400000 40.000000 87.000000  ;# Floor 14, Tower 2
node 1296 15.600000 24.000000 87.000000  ;# Floor 14, Tower 2
node 1297 15.600000 31.400000 87.000000  ;# Floor 14, Tower 2
node 1298 15.600000 32.600000 87.000000  ;# Floor 14, Tower 2
node 1299 15.600000 40.000000 87.000000  ;# Floor 14, Tower 2
node 1300 19.000000 24.000000 87.000000  ;# Floor 14, Tower 2
node 1301 19.000000 31.400000 87.000000  ;# Floor 14, Tower 2
node 1302 19.000000 32.600000 87.000000  ;# Floor 14, Tower 2
node 1303 19.000000 40.000000 87.000000  ;# Floor 14, Tower 2
node 1304 27.000000 24.000000 87.000000  ;# Floor 14, Tower 2
node 1305 27.000000 31.400000 87.000000  ;# Floor 14, Tower 2
node 1306 27.000000 32.600000 87.000000  ;# Floor 14, Tower 2
node 1307 27.000000 40.000000 87.000000  ;# Floor 14, Tower 2
node 1308 30.000000 24.000000 87.000000  ;# Floor 14, Tower 2
node 1309 30.000000 31.400000 87.000000  ;# Floor 14, Tower 2
node 1310 30.000000 32.600000 87.000000  ;# Floor 14, Tower 2
node 1311 30.000000 40.000000 87.000000  ;# Floor 14, Tower 2
node 1312 0.000000 24.000000 93.000000  ;# Floor 15, Tower 2
node 1313 0.000000 31.400000 93.000000  ;# Floor 15, Tower 2
node 1314 0.000000 32.600000 93.000000  ;# Floor 15, Tower 2
node 1315 0.000000 40.000000 93.000000  ;# Floor 15, Tower 2
node 1316 3.000000 24.000000 93.000000  ;# Floor 15, Tower 2
node 1317 3.000000 31.400000 93.000000  ;# Floor 15, Tower 2
node 1318 3.000000 32.600000 93.000000  ;# Floor 15, Tower 2
node 1319 3.000000 40.000000 93.000000  ;# Floor 15, Tower 2
node 1320 11.000000 24.000000 93.000000  ;# Floor 15, Tower 2
node 1321 11.000000 31.400000 93.000000  ;# Floor 15, Tower 2
node 1322 11.000000 32.600000 93.000000  ;# Floor 15, Tower 2
node 1323 11.000000 40.000000 93.000000  ;# Floor 15, Tower 2
node 1324 14.400000 24.000000 93.000000  ;# Floor 15, Tower 2
node 1325 14.400000 31.400000 93.000000  ;# Floor 15, Tower 2
node 1326 14.400000 32.600000 93.000000  ;# Floor 15, Tower 2
node 1327 14.400000 40.000000 93.000000  ;# Floor 15, Tower 2
node 1328 15.600000 24.000000 93.000000  ;# Floor 15, Tower 2
node 1329 15.600000 31.400000 93.000000  ;# Floor 15, Tower 2
node 1330 15.600000 32.600000 93.000000  ;# Floor 15, Tower 2
node 1331 15.600000 40.000000 93.000000  ;# Floor 15, Tower 2
node 1332 19.000000 24.000000 93.000000  ;# Floor 15, Tower 2
node 1333 19.000000 31.400000 93.000000  ;# Floor 15, Tower 2
node 1334 19.000000 32.600000 93.000000  ;# Floor 15, Tower 2
node 1335 19.000000 40.000000 93.000000  ;# Floor 15, Tower 2
node 1336 27.000000 24.000000 93.000000  ;# Floor 15, Tower 2
node 1337 27.000000 31.400000 93.000000  ;# Floor 15, Tower 2
node 1338 27.000000 32.600000 93.000000  ;# Floor 15, Tower 2
node 1339 27.000000 40.000000 93.000000  ;# Floor 15, Tower 2
node 1340 30.000000 24.000000 93.000000  ;# Floor 15, Tower 2
node 1341 30.000000 31.400000 93.000000  ;# Floor 15, Tower 2
node 1342 30.000000 32.600000 93.000000  ;# Floor 15, Tower 2
node 1343 30.000000 40.000000 93.000000  ;# Floor 15, Tower 2
node 1344 0.000000 24.000000 99.000000  ;# Floor 16, Tower 2
node 1345 0.000000 31.400000 99.000000  ;# Floor 16, Tower 2
node 1346 0.000000 32.600000 99.000000  ;# Floor 16, Tower 2
node 1347 0.000000 40.000000 99.000000  ;# Floor 16, Tower 2
node 1348 3.000000 24.000000 99.000000  ;# Floor 16, Tower 2
node 1349 3.000000 31.400000 99.000000  ;# Floor 16, Tower 2
node 1350 3.000000 32.600000 99.000000  ;# Floor 16, Tower 2
node 1351 3.000000 40.000000 99.000000  ;# Floor 16, Tower 2
node 1352 11.000000 24.000000 99.000000  ;# Floor 16, Tower 2
node 1353 11.000000 31.400000 99.000000  ;# Floor 16, Tower 2
node 1354 11.000000 32.600000 99.000000  ;# Floor 16, Tower 2
node 1355 11.000000 40.000000 99.000000  ;# Floor 16, Tower 2
node 1356 14.400000 24.000000 99.000000  ;# Floor 16, Tower 2
node 1357 14.400000 31.400000 99.000000  ;# Floor 16, Tower 2
node 1358 14.400000 32.600000 99.000000  ;# Floor 16, Tower 2
node 1359 14.400000 40.000000 99.000000  ;# Floor 16, Tower 2
node 1360 15.600000 24.000000 99.000000  ;# Floor 16, Tower 2
node 1361 15.600000 31.400000 99.000000  ;# Floor 16, Tower 2
node 1362 15.600000 32.600000 99.000000  ;# Floor 16, Tower 2
node 1363 15.600000 40.000000 99.000000  ;# Floor 16, Tower 2
node 1364 19.000000 24.000000 99.000000  ;# Floor 16, Tower 2
node 1365 19.000000 31.400000 99.000000  ;# Floor 16, Tower 2
node 1366 19.000000 32.600000 99.000000  ;# Floor 16, Tower 2
node 1367 19.000000 40.000000 99.000000  ;# Floor 16, Tower 2
node 1368 27.000000 24.000000 99.000000  ;# Floor 16, Tower 2
node 1369 27.000000 31.400000 99.000000  ;# Floor 16, Tower 2
node 1370 27.000000 32.600000 99.000000  ;# Floor 16, Tower 2
node 1371 27.000000 40.000000 99.000000  ;# Floor 16, Tower 2
node 1372 30.000000 24.000000 99.000000  ;# Floor 16, Tower 2
node 1373 30.000000 31.400000 99.000000  ;# Floor 16, Tower 2
node 1374 30.000000 32.600000 99.000000  ;# Floor 16, Tower 2
node 1375 30.000000 40.000000 99.000000  ;# Floor 16, Tower 2
node 1376 0.000000 24.000000 105.000000  ;# Floor 17, Tower 2
node 1377 0.000000 31.400000 105.000000  ;# Floor 17, Tower 2
node 1378 0.000000 32.600000 105.000000  ;# Floor 17, Tower 2
node 1379 0.000000 40.000000 105.000000  ;# Floor 17, Tower 2
node 1380 3.000000 24.000000 105.000000  ;# Floor 17, Tower 2
node 1381 3.000000 31.400000 105.000000  ;# Floor 17, Tower 2
node 1382 3.000000 32.600000 105.000000  ;# Floor 17, Tower 2
node 1383 3.000000 40.000000 105.000000  ;# Floor 17, Tower 2
node 1384 11.000000 24.000000 105.000000  ;# Floor 17, Tower 2
node 1385 11.000000 31.400000 105.000000  ;# Floor 17, Tower 2
node 1386 11.000000 32.600000 105.000000  ;# Floor 17, Tower 2
node 1387 11.000000 40.000000 105.000000  ;# Floor 17, Tower 2
node 1388 14.400000 24.000000 105.000000  ;# Floor 17, Tower 2
node 1389 14.400000 31.400000 105.000000  ;# Floor 17, Tower 2
node 1390 14.400000 32.600000 105.000000  ;# Floor 17, Tower 2
node 1391 14.400000 40.000000 105.000000  ;# Floor 17, Tower 2
node 1392 15.600000 24.000000 105.000000  ;# Floor 17, Tower 2
node 1393 15.600000 31.400000 105.000000  ;# Floor 17, Tower 2
node 1394 15.600000 32.600000 105.000000  ;# Floor 17, Tower 2
node 1395 15.600000 40.000000 105.000000  ;# Floor 17, Tower 2
node 1396 19.000000 24.000000 105.000000  ;# Floor 17, Tower 2
node 1397 19.000000 31.400000 105.000000  ;# Floor 17, Tower 2
node 1398 19.000000 32.600000 105.000000  ;# Floor 17, Tower 2
node 1399 19.000000 40.000000 105.000000  ;# Floor 17, Tower 2
node 1400 27.000000 24.000000 105.000000  ;# Floor 17, Tower 2
node 1401 27.000000 31.400000 105.000000  ;# Floor 17, Tower 2
node 1402 27.000000 32.600000 105.000000  ;# Floor 17, Tower 2
node 1403 27.000000 40.000000 105.000000  ;# Floor 17, Tower 2
node 1404 30.000000 24.000000 105.000000  ;# Floor 17, Tower 2
node 1405 30.000000 31.400000 105.000000  ;# Floor 17, Tower 2
node 1406 30.000000 32.600000 105.000000  ;# Floor 17, Tower 2
node 1407 30.000000 40.000000 105.000000  ;# Floor 17, Tower 2
node 1408 0.000000 24.000000 111.000000  ;# Floor 18, Tower 2
node 1409 0.000000 31.400000 111.000000  ;# Floor 18, Tower 2
node 1410 0.000000 32.600000 111.000000  ;# Floor 18, Tower 2
node 1411 0.000000 40.000000 111.000000  ;# Floor 18, Tower 2
node 1412 3.000000 24.000000 111.000000  ;# Floor 18, Tower 2
node 1413 3.000000 31.400000 111.000000  ;# Floor 18, Tower 2
node 1414 3.000000 32.600000 111.000000  ;# Floor 18, Tower 2
node 1415 3.000000 40.000000 111.000000  ;# Floor 18, Tower 2
node 1416 11.000000 24.000000 111.000000  ;# Floor 18, Tower 2
node 1417 11.000000 31.400000 111.000000  ;# Floor 18, Tower 2
node 1418 11.000000 32.600000 111.000000  ;# Floor 18, Tower 2
node 1419 11.000000 40.000000 111.000000  ;# Floor 18, Tower 2
node 1420 14.400000 24.000000 111.000000  ;# Floor 18, Tower 2
node 1421 14.400000 31.400000 111.000000  ;# Floor 18, Tower 2
node 1422 14.400000 32.600000 111.000000  ;# Floor 18, Tower 2
node 1423 14.400000 40.000000 111.000000  ;# Floor 18, Tower 2
node 1424 15.600000 24.000000 111.000000  ;# Floor 18, Tower 2
node 1425 15.600000 31.400000 111.000000  ;# Floor 18, Tower 2
node 1426 15.600000 32.600000 111.000000  ;# Floor 18, Tower 2
node 1427 15.600000 40.000000 111.000000  ;# Floor 18, Tower 2
node 1428 19.000000 24.000000 111.000000  ;# Floor 18, Tower 2
node 1429 19.000000 31.400000 111.000000  ;# Floor 18, Tower 2
node 1430 19.000000 32.600000 111.000000  ;# Floor 18, Tower 2
node 1431 19.000000 40.000000 111.000000  ;# Floor 18, Tower 2
node 1432 27.000000 24.000000 111.000000  ;# Floor 18, Tower 2
node 1433 27.000000 31.400000 111.000000  ;# Floor 18, Tower 2
node 1434 27.000000 32.600000 111.000000  ;# Floor 18, Tower 2
node 1435 27.000000 40.000000 111.000000  ;# Floor 18, Tower 2
node 1436 30.000000 24.000000 111.000000  ;# Floor 18, Tower 2
node 1437 30.000000 31.400000 111.000000  ;# Floor 18, Tower 2
node 1438 30.000000 32.600000 111.000000  ;# Floor 18, Tower 2
node 1439 30.000000 40.000000 111.000000  ;# Floor 18, Tower 2
node 1440 0.000000 24.000000 117.000000  ;# Floor 19, Tower 2
node 1441 0.000000 31.400000 117.000000  ;# Floor 19, Tower 2
node 1442 0.000000 32.600000 117.000000  ;# Floor 19, Tower 2
node 1443 0.000000 40.000000 117.000000  ;# Floor 19, Tower 2
node 1444 3.000000 24.000000 117.000000  ;# Floor 19, Tower 2
node 1445 3.000000 31.400000 117.000000  ;# Floor 19, Tower 2
node 1446 3.000000 32.600000 117.000000  ;# Floor 19, Tower 2
node 1447 3.000000 40.000000 117.000000  ;# Floor 19, Tower 2
node 1448 11.000000 24.000000 117.000000  ;# Floor 19, Tower 2
node 1449 11.000000 31.400000 117.000000  ;# Floor 19, Tower 2
node 1450 11.000000 32.600000 117.000000  ;# Floor 19, Tower 2
node 1451 11.000000 40.000000 117.000000  ;# Floor 19, Tower 2
node 1452 14.400000 24.000000 117.000000  ;# Floor 19, Tower 2
node 1453 14.400000 31.400000 117.000000  ;# Floor 19, Tower 2
node 1454 14.400000 32.600000 117.000000  ;# Floor 19, Tower 2
node 1455 14.400000 40.000000 117.000000  ;# Floor 19, Tower 2
node 1456 15.600000 24.000000 117.000000  ;# Floor 19, Tower 2
node 1457 15.600000 31.400000 117.000000  ;# Floor 19, Tower 2
node 1458 15.600000 32.600000 117.000000  ;# Floor 19, Tower 2
node 1459 15.600000 40.000000 117.000000  ;# Floor 19, Tower 2
node 1460 19.000000 24.000000 117.000000  ;# Floor 19, Tower 2
node 1461 19.000000 31.400000 117.000000  ;# Floor 19, Tower 2
node 1462 19.000000 32.600000 117.000000  ;# Floor 19, Tower 2
node 1463 19.000000 40.000000 117.000000  ;# Floor 19, Tower 2
node 1464 27.000000 24.000000 117.000000  ;# Floor 19, Tower 2
node 1465 27.000000 31.400000 117.000000  ;# Floor 19, Tower 2
node 1466 27.000000 32.600000 117.000000  ;# Floor 19, Tower 2
node 1467 27.000000 40.000000 117.000000  ;# Floor 19, Tower 2
node 1468 30.000000 24.000000 117.000000  ;# Floor 19, Tower 2
node 1469 30.000000 31.400000 117.000000  ;# Floor 19, Tower 2
node 1470 30.000000 32.600000 117.000000  ;# Floor 19, Tower 2
node 1471 30.000000 40.000000 117.000000  ;# Floor 19, Tower 2
node 1472 0.000000 24.000000 123.000000  ;# Floor 20, Tower 2
node 1473 0.000000 31.400000 123.000000  ;# Floor 20, Tower 2
node 1474 0.000000 32.600000 123.000000  ;# Floor 20, Tower 2
node 1475 0.000000 40.000000 123.000000  ;# Floor 20, Tower 2
node 1476 3.000000 24.000000 123.000000  ;# Floor 20, Tower 2
node 1477 3.000000 31.400000 123.000000  ;# Floor 20, Tower 2
node 1478 3.000000 32.600000 123.000000  ;# Floor 20, Tower 2
node 1479 3.000000 40.000000 123.000000  ;# Floor 20, Tower 2
node 1480 11.000000 24.000000 123.000000  ;# Floor 20, Tower 2
node 1481 11.000000 31.400000 123.000000  ;# Floor 20, Tower 2
node 1482 11.000000 32.600000 123.000000  ;# Floor 20, Tower 2
node 1483 11.000000 40.000000 123.000000  ;# Floor 20, Tower 2
node 1484 14.400000 24.000000 123.000000  ;# Floor 20, Tower 2
node 1485 14.400000 31.400000 123.000000  ;# Floor 20, Tower 2
node 1486 14.400000 32.600000 123.000000  ;# Floor 20, Tower 2
node 1487 14.400000 40.000000 123.000000  ;# Floor 20, Tower 2
node 1488 15.600000 24.000000 123.000000  ;# Floor 20, Tower 2
node 1489 15.600000 31.400000 123.000000  ;# Floor 20, Tower 2
node 1490 15.600000 32.600000 123.000000  ;# Floor 20, Tower 2
node 1491 15.600000 40.000000 123.000000  ;# Floor 20, Tower 2
node 1492 19.000000 24.000000 123.000000  ;# Floor 20, Tower 2
node 1493 19.000000 31.400000 123.000000  ;# Floor 20, Tower 2
node 1494 19.000000 32.600000 123.000000  ;# Floor 20, Tower 2
node 1495 19.000000 40.000000 123.000000  ;# Floor 20, Tower 2
node 1496 27.000000 24.000000 123.000000  ;# Floor 20, Tower 2
node 1497 27.000000 31.400000 123.000000  ;# Floor 20, Tower 2
node 1498 27.000000 32.600000 123.000000  ;# Floor 20, Tower 2
node 1499 27.000000 40.000000 123.000000  ;# Floor 20, Tower 2
node 1500 30.000000 24.000000 123.000000  ;# Floor 20, Tower 2
node 1501 30.000000 31.400000 123.000000  ;# Floor 20, Tower 2
node 1502 30.000000 32.600000 123.000000  ;# Floor 20, Tower 2
node 1503 30.000000 40.000000 123.000000  ;# Floor 20, Tower 2
node 1504 0.000000 24.000000 129.000000  ;# Floor 21, Tower 2
node 1505 0.000000 31.400000 129.000000  ;# Floor 21, Tower 2
node 1506 0.000000 32.600000 129.000000  ;# Floor 21, Tower 2
node 1507 0.000000 40.000000 129.000000  ;# Floor 21, Tower 2
node 1508 3.000000 24.000000 129.000000  ;# Floor 21, Tower 2
node 1509 3.000000 31.400000 129.000000  ;# Floor 21, Tower 2
node 1510 3.000000 32.600000 129.000000  ;# Floor 21, Tower 2
node 1511 3.000000 40.000000 129.000000  ;# Floor 21, Tower 2
node 1512 11.000000 24.000000 129.000000  ;# Floor 21, Tower 2
node 1513 11.000000 31.400000 129.000000  ;# Floor 21, Tower 2
node 1514 11.000000 32.600000 129.000000  ;# Floor 21, Tower 2
node 1515 11.000000 40.000000 129.000000  ;# Floor 21, Tower 2
node 1516 14.400000 24.000000 129.000000  ;# Floor 21, Tower 2
node 1517 14.400000 31.400000 129.000000  ;# Floor 21, Tower 2
node 1518 14.400000 32.600000 129.000000  ;# Floor 21, Tower 2
node 1519 14.400000 40.000000 129.000000  ;# Floor 21, Tower 2
node 1520 15.600000 24.000000 129.000000  ;# Floor 21, Tower 2
node 1521 15.600000 31.400000 129.000000  ;# Floor 21, Tower 2
node 1522 15.600000 32.600000 129.000000  ;# Floor 21, Tower 2
node 1523 15.600000 40.000000 129.000000  ;# Floor 21, Tower 2
node 1524 19.000000 24.000000 129.000000  ;# Floor 21, Tower 2
node 1525 19.000000 31.400000 129.000000  ;# Floor 21, Tower 2
node 1526 19.000000 32.600000 129.000000  ;# Floor 21, Tower 2
node 1527 19.000000 40.000000 129.000000  ;# Floor 21, Tower 2
node 1528 27.000000 24.000000 129.000000  ;# Floor 21, Tower 2
node 1529 27.000000 31.400000 129.000000  ;# Floor 21, Tower 2
node 1530 27.000000 32.600000 129.000000  ;# Floor 21, Tower 2
node 1531 27.000000 40.000000 129.000000  ;# Floor 21, Tower 2
node 1532 30.000000 24.000000 129.000000  ;# Floor 21, Tower 2
node 1533 30.000000 31.400000 129.000000  ;# Floor 21, Tower 2
node 1534 30.000000 32.600000 129.000000  ;# Floor 21, Tower 2
node 1535 30.000000 40.000000 129.000000  ;# Floor 21, Tower 2
node 1536 0.000000 24.000000 135.000000  ;# Floor 22, Tower 2
node 1537 0.000000 31.400000 135.000000  ;# Floor 22, Tower 2
node 1538 0.000000 32.600000 135.000000  ;# Floor 22, Tower 2
node 1539 0.000000 40.000000 135.000000  ;# Floor 22, Tower 2
node 1540 3.000000 24.000000 135.000000  ;# Floor 22, Tower 2
node 1541 3.000000 31.400000 135.000000  ;# Floor 22, Tower 2
node 1542 3.000000 32.600000 135.000000  ;# Floor 22, Tower 2
node 1543 3.000000 40.000000 135.000000  ;# Floor 22, Tower 2
node 1544 11.000000 24.000000 135.000000  ;# Floor 22, Tower 2
node 1545 11.000000 31.400000 135.000000  ;# Floor 22, Tower 2
node 1546 11.000000 32.600000 135.000000  ;# Floor 22, Tower 2
node 1547 11.000000 40.000000 135.000000  ;# Floor 22, Tower 2
node 1548 14.400000 24.000000 135.000000  ;# Floor 22, Tower 2
node 1549 14.400000 31.400000 135.000000  ;# Floor 22, Tower 2
node 1550 14.400000 32.600000 135.000000  ;# Floor 22, Tower 2
node 1551 14.400000 40.000000 135.000000  ;# Floor 22, Tower 2
node 1552 15.600000 24.000000 135.000000  ;# Floor 22, Tower 2
node 1553 15.600000 31.400000 135.000000  ;# Floor 22, Tower 2
node 1554 15.600000 32.600000 135.000000  ;# Floor 22, Tower 2
node 1555 15.600000 40.000000 135.000000  ;# Floor 22, Tower 2
node 1556 19.000000 24.000000 135.000000  ;# Floor 22, Tower 2
node 1557 19.000000 31.400000 135.000000  ;# Floor 22, Tower 2
node 1558 19.000000 32.600000 135.000000  ;# Floor 22, Tower 2
node 1559 19.000000 40.000000 135.000000  ;# Floor 22, Tower 2
node 1560 27.000000 24.000000 135.000000  ;# Floor 22, Tower 2
node 1561 27.000000 31.400000 135.000000  ;# Floor 22, Tower 2
node 1562 27.000000 32.600000 135.000000  ;# Floor 22, Tower 2
node 1563 27.000000 40.000000 135.000000  ;# Floor 22, Tower 2
node 1564 30.000000 24.000000 135.000000  ;# Floor 22, Tower 2
node 1565 30.000000 31.400000 135.000000  ;# Floor 22, Tower 2
node 1566 30.000000 32.600000 135.000000  ;# Floor 22, Tower 2
node 1567 30.000000 40.000000 135.000000  ;# Floor 22, Tower 2
node 1568 0.000000 24.000000 141.000000  ;# Floor 23, Tower 2
node 1569 0.000000 31.400000 141.000000  ;# Floor 23, Tower 2
node 1570 0.000000 32.600000 141.000000  ;# Floor 23, Tower 2
node 1571 0.000000 40.000000 141.000000  ;# Floor 23, Tower 2
node 1572 3.000000 24.000000 141.000000  ;# Floor 23, Tower 2
node 1573 3.000000 31.400000 141.000000  ;# Floor 23, Tower 2
node 1574 3.000000 32.600000 141.000000  ;# Floor 23, Tower 2
node 1575 3.000000 40.000000 141.000000  ;# Floor 23, Tower 2
node 1576 11.000000 24.000000 141.000000  ;# Floor 23, Tower 2
node 1577 11.000000 31.400000 141.000000  ;# Floor 23, Tower 2
node 1578 11.000000 32.600000 141.000000  ;# Floor 23, Tower 2
node 1579 11.000000 40.000000 141.000000  ;# Floor 23, Tower 2
node 1580 14.400000 24.000000 141.000000  ;# Floor 23, Tower 2
node 1581 14.400000 31.400000 141.000000  ;# Floor 23, Tower 2
node 1582 14.400000 32.600000 141.000000  ;# Floor 23, Tower 2
node 1583 14.400000 40.000000 141.000000  ;# Floor 23, Tower 2
node 1584 15.600000 24.000000 141.000000  ;# Floor 23, Tower 2
node 1585 15.600000 31.400000 141.000000  ;# Floor 23, Tower 2
node 1586 15.600000 32.600000 141.000000  ;# Floor 23, Tower 2
node 1587 15.600000 40.000000 141.000000  ;# Floor 23, Tower 2
node 1588 19.000000 24.000000 141.000000  ;# Floor 23, Tower 2
node 1589 19.000000 31.400000 141.000000  ;# Floor 23, Tower 2
node 1590 19.000000 32.600000 141.000000  ;# Floor 23, Tower 2
node 1591 19.000000 40.000000 141.000000  ;# Floor 23, Tower 2
node 1592 27.000000 24.000000 141.000000  ;# Floor 23, Tower 2
node 1593 27.000000 31.400000 141.000000  ;# Floor 23, Tower 2
node 1594 27.000000 32.600000 141.000000  ;# Floor 23, Tower 2
node 1595 27.000000 40.000000 141.000000  ;# Floor 23, Tower 2
node 1596 30.000000 24.000000 141.000000  ;# Floor 23, Tower 2
node 1597 30.000000 31.400000 141.000000  ;# Floor 23, Tower 2
node 1598 30.000000 32.600000 141.000000  ;# Floor 23, Tower 2
node 1599 30.000000 40.000000 141.000000  ;# Floor 23, Tower 2
node 1600 0.000000 24.000000 147.000000  ;# Floor 24, Tower 2
node 1601 0.000000 31.400000 147.000000  ;# Floor 24, Tower 2
node 1602 0.000000 32.600000 147.000000  ;# Floor 24, Tower 2
node 1603 0.000000 40.000000 147.000000  ;# Floor 24, Tower 2
node 1604 3.000000 24.000000 147.000000  ;# Floor 24, Tower 2
node 1605 3.000000 31.400000 147.000000  ;# Floor 24, Tower 2
node 1606 3.000000 32.600000 147.000000  ;# Floor 24, Tower 2
node 1607 3.000000 40.000000 147.000000  ;# Floor 24, Tower 2
node 1608 11.000000 24.000000 147.000000  ;# Floor 24, Tower 2
node 1609 11.000000 31.400000 147.000000  ;# Floor 24, Tower 2
node 1610 11.000000 32.600000 147.000000  ;# Floor 24, Tower 2
node 1611 11.000000 40.000000 147.000000  ;# Floor 24, Tower 2
node 1612 14.400000 24.000000 147.000000  ;# Floor 24, Tower 2
node 1613 14.400000 31.400000 147.000000  ;# Floor 24, Tower 2
node 1614 14.400000 32.600000 147.000000  ;# Floor 24, Tower 2
node 1615 14.400000 40.000000 147.000000  ;# Floor 24, Tower 2
node 1616 15.600000 24.000000 147.000000  ;# Floor 24, Tower 2
node 1617 15.600000 31.400000 147.000000  ;# Floor 24, Tower 2
node 1618 15.600000 32.600000 147.000000  ;# Floor 24, Tower 2
node 1619 15.600000 40.000000 147.000000  ;# Floor 24, Tower 2
node 1620 19.000000 24.000000 147.000000  ;# Floor 24, Tower 2
node 1621 19.000000 31.400000 147.000000  ;# Floor 24, Tower 2
node 1622 19.000000 32.600000 147.000000  ;# Floor 24, Tower 2
node 1623 19.000000 40.000000 147.000000  ;# Floor 24, Tower 2
node 1624 27.000000 24.000000 147.000000  ;# Floor 24, Tower 2
node 1625 27.000000 31.400000 147.000000  ;# Floor 24, Tower 2
node 1626 27.000000 32.600000 147.000000  ;# Floor 24, Tower 2
node 1627 27.000000 40.000000 147.000000  ;# Floor 24, Tower 2
node 1628 30.000000 24.000000 147.000000  ;# Floor 24, Tower 2
node 1629 30.000000 31.400000 147.000000  ;# Floor 24, Tower 2
node 1630 30.000000 32.600000 147.000000  ;# Floor 24, Tower 2
node 1631 30.000000 40.000000 147.000000  ;# Floor 24, Tower 2
node 1632 0.000000 24.000000 153.000000  ;# Floor 25, Tower 2
node 1633 0.000000 31.400000 153.000000  ;# Floor 25, Tower 2
node 1634 0.000000 32.600000 153.000000  ;# Floor 25, Tower 2
node 1635 0.000000 40.000000 153.000000  ;# Floor 25, Tower 2
node 1636 3.000000 24.000000 153.000000  ;# Floor 25, Tower 2
node 1637 3.000000 31.400000 153.000000  ;# Floor 25, Tower 2
node 1638 3.000000 32.600000 153.000000  ;# Floor 25, Tower 2
node 1639 3.000000 40.000000 153.000000  ;# Floor 25, Tower 2
node 1640 11.000000 24.000000 153.000000  ;# Floor 25, Tower 2
node 1641 11.000000 31.400000 153.000000  ;# Floor 25, Tower 2
node 1642 11.000000 32.600000 153.000000  ;# Floor 25, Tower 2
node 1643 11.000000 40.000000 153.000000  ;# Floor 25, Tower 2
node 1644 14.400000 24.000000 153.000000  ;# Floor 25, Tower 2
node 1645 14.400000 31.400000 153.000000  ;# Floor 25, Tower 2
node 1646 14.400000 32.600000 153.000000  ;# Floor 25, Tower 2
node 1647 14.400000 40.000000 153.000000  ;# Floor 25, Tower 2
node 1648 15.600000 24.000000 153.000000  ;# Floor 25, Tower 2
node 1649 15.600000 31.400000 153.000000  ;# Floor 25, Tower 2
node 1650 15.600000 32.600000 153.000000  ;# Floor 25, Tower 2
node 1651 15.600000 40.000000 153.000000  ;# Floor 25, Tower 2
node 1652 19.000000 24.000000 153.000000  ;# Floor 25, Tower 2
node 1653 19.000000 31.400000 153.000000  ;# Floor 25, Tower 2
node 1654 19.000000 32.600000 153.000000  ;# Floor 25, Tower 2
node 1655 19.000000 40.000000 153.000000  ;# Floor 25, Tower 2
node 1656 27.000000 24.000000 153.000000  ;# Floor 25, Tower 2
node 1657 27.000000 31.400000 153.000000  ;# Floor 25, Tower 2
node 1658 27.000000 32.600000 153.000000  ;# Floor 25, Tower 2
node 1659 27.000000 40.000000 153.000000  ;# Floor 25, Tower 2
node 1660 30.000000 24.000000 153.000000  ;# Floor 25, Tower 2
node 1661 30.000000 31.400000 153.000000  ;# Floor 25, Tower 2
node 1662 30.000000 32.600000 153.000000  ;# Floor 25, Tower 2
node 1663 30.000000 40.000000 153.000000  ;# Floor 25, Tower 2
node 1664 11.000000 20.000000 33.000000  ;# Floor 5, Tower bridge
node 1665 19.000000 20.000000 33.000000  ;# Floor 5, Tower bridge
node 1666 11.000000 20.000000 39.000000  ;# Floor 6, Tower bridge
node 1667 19.000000 20.000000 39.000000  ;# Floor 6, Tower bridge
node 1668 11.000000 20.000000 69.000000  ;# Floor 11, Tower bridge
node 1669 19.000000 20.000000 69.000000  ;# Floor 11, Tower bridge
node 1670 11.000000 20.000000 75.000000  ;# Floor 12, Tower bridge
node 1671 19.000000 20.000000 75.000000  ;# Floor 12, Tower bridge
node 1672 11.000000 20.000000 105.000000  ;# Floor 17, Tower bridge
node 1673 19.000000 20.000000 105.000000  ;# Floor 17, Tower bridge
node 1674 11.000000 20.000000 111.000000  ;# Floor 18, Tower bridge
node 1675 19.000000 20.000000 111.000000  ;# Floor 18, Tower bridge
node 1676 11.000000 20.000000 141.000000  ;# Floor 23, Tower bridge
node 1677 19.000000 20.000000 141.000000  ;# Floor 23, Tower bridge
node 1678 11.000000 20.000000 153.000000  ;# Floor 25, Tower bridge
node 1679 19.000000 20.000000 153.000000  ;# Floor 25, Tower bridge

puts ">>> $numNodes nodes defined"

# ============================================================================
# BOUNDARY CONDITIONS (Fixed Base)
# ============================================================================
puts ""
puts ">>> Applying boundary conditions..."

set numFixed 0

# Fix base nodes (Floor 0): fix nodeTag Dx Dy Dz Rx Ry Rz
fix 0 1 1 1 1 1 1
incr numFixed
fix 1 1 1 1 1 1 1
incr numFixed
fix 2 1 1 1 1 1 1
incr numFixed
fix 3 1 1 1 1 1 1
incr numFixed
fix 4 1 1 1 1 1 1
incr numFixed
fix 5 1 1 1 1 1 1
incr numFixed
fix 6 1 1 1 1 1 1
incr numFixed
fix 7 1 1 1 1 1 1
incr numFixed
fix 8 1 1 1 1 1 1
incr numFixed
fix 9 1 1 1 1 1 1
incr numFixed
fix 10 1 1 1 1 1 1
incr numFixed
fix 11 1 1 1 1 1 1
incr numFixed
fix 12 1 1 1 1 1 1
incr numFixed
fix 13 1 1 1 1 1 1
incr numFixed
fix 14 1 1 1 1 1 1
incr numFixed
fix 15 1 1 1 1 1 1
incr numFixed
fix 16 1 1 1 1 1 1
incr numFixed
fix 17 1 1 1 1 1 1
incr numFixed
fix 18 1 1 1 1 1 1
incr numFixed
fix 19 1 1 1 1 1 1
incr numFixed
fix 20 1 1 1 1 1 1
incr numFixed
fix 21 1 1 1 1 1 1
incr numFixed
fix 22 1 1 1 1 1 1
incr numFixed
fix 23 1 1 1 1 1 1
incr numFixed
fix 24 1 1 1 1 1 1
incr numFixed
fix 25 1 1 1 1 1 1
incr numFixed
fix 26 1 1 1 1 1 1
incr numFixed
fix 27 1 1 1 1 1 1
incr numFixed
fix 28 1 1 1 1 1 1
incr numFixed
fix 29 1 1 1 1 1 1
incr numFixed
fix 30 1 1 1 1 1 1
incr numFixed
fix 31 1 1 1 1 1 1
incr numFixed
fix 832 1 1 1 1 1 1
incr numFixed
fix 833 1 1 1 1 1 1
incr numFixed
fix 834 1 1 1 1 1 1
incr numFixed
fix 835 1 1 1 1 1 1
incr numFixed
fix 836 1 1 1 1 1 1
incr numFixed
fix 837 1 1 1 1 1 1
incr numFixed
fix 838 1 1 1 1 1 1
incr numFixed
fix 839 1 1 1 1 1 1
incr numFixed
fix 840 1 1 1 1 1 1
incr numFixed
fix 841 1 1 1 1 1 1
incr numFixed
fix 842 1 1 1 1 1 1
incr numFixed
fix 843 1 1 1 1 1 1
incr numFixed
fix 844 1 1 1 1 1 1
incr numFixed
fix 845 1 1 1 1 1 1
incr numFixed
fix 846 1 1 1 1 1 1
incr numFixed
fix 847 1 1 1 1 1 1
incr numFixed
fix 848 1 1 1 1 1 1
incr numFixed
fix 849 1 1 1 1 1 1
incr numFixed
fix 850 1 1 1 1 1 1
incr numFixed
fix 851 1 1 1 1 1 1
incr numFixed
fix 852 1 1 1 1 1 1
incr numFixed
fix 853 1 1 1 1 1 1
incr numFixed
fix 854 1 1 1 1 1 1
incr numFixed
fix 855 1 1 1 1 1 1
incr numFixed
fix 856 1 1 1 1 1 1
incr numFixed
fix 857 1 1 1 1 1 1
incr numFixed
fix 858 1 1 1 1 1 1
incr numFixed
fix 859 1 1 1 1 1 1
incr numFixed
fix 860 1 1 1 1 1 1
incr numFixed
fix 861 1 1 1 1 1 1
incr numFixed
fix 862 1 1 1 1 1 1
incr numFixed
fix 863 1 1 1 1 1 1
incr numFixed

puts ">>> $numFixed base nodes fixed"

# ============================================================================
# MATERIAL DEFINITION
# ============================================================================
puts ""
puts ">>> Defining materials..."

set matTag 1
uniaxialMaterial Elastic $matTag $E
puts ">>> Elastic material defined (Tag: $matTag, E: $E kN/cm2)"

# ============================================================================
# GEOMETRIC TRANSFORMATIONS
# ============================================================================
puts ""
puts ">>> Defining geometric transformations..."

# Column transformation (vertical elements)
set colTransfTag 1
geomTransf Linear $colTransfTag 1 0 0
puts ">>> Column transformation defined (Tag: $colTransfTag)"

# Beam X transformation (beams along X-axis)
set beamXTransfTag 2
geomTransf Linear $beamXTransfTag 0 0 1
puts ">>> Beam-X transformation defined (Tag: $beamXTransfTag)"

# Beam Y transformation (beams along Y-axis)
set beamYTransfTag 3
geomTransf Linear $beamYTransfTag 0 0 1
puts ">>> Beam-Y transformation defined (Tag: $beamYTransfTag)"

# Brace transformations will be created dynamically
set braceTransfStart 100
puts ">>> Brace transformations will start from Tag: $braceTransfStart"

# ============================================================================
# ELEMENT DEFINITIONS
# ============================================================================
puts ""
puts ">>> Defining elements..."

set numElements 0
set numColumns 0
set numBeamsX 0
set numBeamsY 0
set numBraces 0
set braceTransfTag $braceTransfStart


# ===== COLUMNS =====
puts ">>> Creating columns..."
element elasticBeamColumn 0 0 32 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1 1 33 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2 2 34 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3 3 35 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4 4 36 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 5 5 37 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 6 6 38 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 7 7 39 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 8 8 40 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 9 9 41 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 10 10 42 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 11 11 43 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 12 12 44 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 13 13 45 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 14 14 46 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 15 15 47 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 16 16 48 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 17 17 49 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 18 18 50 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 19 19 51 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 20 20 52 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 21 21 53 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 22 22 54 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 23 23 55 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 24 24 56 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 25 25 57 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 26 26 58 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 27 27 59 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 28 28 60 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 29 29 61 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 30 30 62 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 31 31 63 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 108 32 64 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 109 33 65 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 110 34 66 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 111 35 67 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 112 36 68 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 113 37 69 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 114 38 70 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 115 39 71 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 116 40 72 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 117 41 73 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 118 42 74 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 119 43 75 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 120 44 76 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 121 45 77 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 122 46 78 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 123 47 79 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 124 48 80 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 125 49 81 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 126 50 82 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 127 51 83 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 128 52 84 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 129 53 85 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 130 54 86 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 131 55 87 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 132 56 88 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 133 57 89 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 134 58 90 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 135 59 91 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 136 60 92 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 137 61 93 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 138 62 94 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 139 63 95 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 188 64 96 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 189 65 97 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 190 66 98 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 191 67 99 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 192 68 100 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 193 69 101 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 194 70 102 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 195 71 103 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 196 72 104 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 197 73 105 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 198 74 106 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 199 75 107 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 200 76 108 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 201 77 109 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 202 78 110 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 203 79 111 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 204 80 112 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 205 81 113 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 206 82 114 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 207 83 115 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 208 84 116 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 209 85 117 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 210 86 118 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 211 87 119 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 212 88 120 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 213 89 121 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 214 90 122 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 215 91 123 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 216 92 124 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 217 93 125 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 218 94 126 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 219 95 127 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 268 96 128 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 269 97 129 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 270 98 130 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 271 99 131 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 272 100 132 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 273 101 133 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 274 102 134 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 275 103 135 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 276 104 136 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 277 105 137 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 278 106 138 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 279 107 139 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 280 108 140 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 281 109 141 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 282 110 142 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 283 111 143 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 284 112 144 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 285 113 145 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 286 114 146 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 287 115 147 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 288 116 148 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 289 117 149 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 290 118 150 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 291 119 151 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 292 120 152 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 293 121 153 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 294 122 154 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 295 123 155 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 296 124 156 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 297 125 157 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 298 126 158 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 299 127 159 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 348 128 160 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 349 129 161 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 350 130 162 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 351 131 163 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 352 132 164 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 353 133 165 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 354 134 166 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 355 135 167 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 356 136 168 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 357 137 169 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 358 138 170 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 359 139 171 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 360 140 172 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 361 141 173 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 362 142 174 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 363 143 175 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 364 144 176 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 365 145 177 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 366 146 178 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 367 147 179 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 368 148 180 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 369 149 181 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 370 150 182 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 371 151 183 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 372 152 184 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 373 153 185 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 374 154 186 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 375 155 187 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 376 156 188 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 377 157 189 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 378 158 190 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 379 159 191 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 428 160 192 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 429 161 193 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 430 162 194 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 431 163 195 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 432 164 196 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 433 165 197 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 434 166 198 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 435 167 199 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 436 168 200 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 437 169 201 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 438 170 202 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 439 171 203 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 440 172 204 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 441 173 205 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 442 174 206 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 443 175 207 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 444 176 208 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 445 177 209 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 446 178 210 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 447 179 211 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 448 180 212 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 449 181 213 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 450 182 214 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 451 183 215 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 452 184 216 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 453 185 217 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 454 186 218 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 455 187 219 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 456 188 220 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 457 189 221 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 458 190 222 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 459 191 223 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 508 192 224 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 509 193 225 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 510 194 226 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 511 195 227 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 512 196 228 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 513 197 229 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 514 198 230 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 515 199 231 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 516 200 232 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 517 201 233 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 518 202 234 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 519 203 235 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 520 204 236 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 521 205 237 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 522 206 238 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 523 207 239 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 524 208 240 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 525 209 241 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 526 210 242 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 527 211 243 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 528 212 244 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 529 213 245 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 530 214 246 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 531 215 247 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 532 216 248 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 533 217 249 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 534 218 250 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 535 219 251 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 536 220 252 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 537 221 253 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 538 222 254 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 539 223 255 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 596 224 256 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 597 225 257 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 598 226 258 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 599 227 259 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 600 228 260 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 601 229 261 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 602 230 262 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 603 231 263 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 604 232 264 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 605 233 265 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 606 234 266 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 607 235 267 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 608 236 268 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 609 237 269 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 610 238 270 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 611 239 271 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 612 240 272 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 613 241 273 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 614 242 274 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 615 243 275 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 616 244 276 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 617 245 277 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 618 246 278 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 619 247 279 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 620 248 280 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 621 249 281 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 622 250 282 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 623 251 283 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 624 252 284 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 625 253 285 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 626 254 286 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 627 255 287 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 668 256 288 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 669 257 289 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 670 258 290 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 671 259 291 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 672 260 292 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 673 261 293 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 674 262 294 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 675 263 295 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 676 264 296 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 677 265 297 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 678 266 298 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 679 267 299 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 680 268 300 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 681 269 301 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 682 270 302 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 683 271 303 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 684 272 304 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 685 273 305 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 686 274 306 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 687 275 307 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 688 276 308 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 689 277 309 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 690 278 310 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 691 279 311 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 692 280 312 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 693 281 313 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 694 282 314 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 695 283 315 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 696 284 316 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 697 285 317 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 698 286 318 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 699 287 319 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 756 288 320 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 757 289 321 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 758 290 322 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 759 291 323 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 760 292 324 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 761 293 325 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 762 294 326 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 763 295 327 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 764 296 328 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 765 297 329 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 766 298 330 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 767 299 331 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 768 300 332 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 769 301 333 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 770 302 334 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 771 303 335 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 772 304 336 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 773 305 337 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 774 306 338 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 775 307 339 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 776 308 340 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 777 309 341 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 778 310 342 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 779 311 343 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 780 312 344 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 781 313 345 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 782 314 346 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 783 315 347 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 784 316 348 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 785 317 349 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 786 318 350 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 787 319 351 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 828 320 352 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 829 321 353 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 830 322 354 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 831 323 355 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 832 324 356 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 833 325 357 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 834 326 358 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 835 327 359 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 836 328 360 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 837 329 361 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 838 330 362 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 839 331 363 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 840 332 364 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 841 333 365 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 842 334 366 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 843 335 367 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 844 336 368 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 845 337 369 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 846 338 370 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 847 339 371 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 848 340 372 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 849 341 373 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 850 342 374 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 851 343 375 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 852 344 376 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 853 345 377 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 854 346 378 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 855 347 379 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 856 348 380 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 857 349 381 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 858 350 382 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 859 351 383 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 908 352 384 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 909 353 385 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 910 354 386 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 911 355 387 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 912 356 388 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 913 357 389 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 914 358 390 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 915 359 391 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 916 360 392 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 917 361 393 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 918 362 394 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 919 363 395 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 920 364 396 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 921 365 397 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 922 366 398 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 923 367 399 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 924 368 400 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 925 369 401 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 926 370 402 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 927 371 403 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 928 372 404 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 929 373 405 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 930 374 406 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 931 375 407 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 932 376 408 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 933 377 409 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 934 378 410 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 935 379 411 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 936 380 412 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 937 381 413 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 938 382 414 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 939 383 415 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 980 384 416 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 981 385 417 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 982 386 418 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 983 387 419 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 984 388 420 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 985 389 421 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 986 390 422 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 987 391 423 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 988 392 424 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 989 393 425 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 990 394 426 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 991 395 427 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 992 396 428 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 993 397 429 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 994 398 430 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 995 399 431 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 996 400 432 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 997 401 433 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 998 402 434 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 999 403 435 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1000 404 436 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1001 405 437 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1002 406 438 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1003 407 439 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1004 408 440 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1005 409 441 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1006 410 442 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1007 411 443 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1008 412 444 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1009 413 445 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1010 414 446 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1011 415 447 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1080 416 448 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1081 417 449 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1082 418 450 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1083 419 451 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1084 420 452 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1085 421 453 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1086 422 454 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1087 423 455 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1088 424 456 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1089 425 457 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1090 426 458 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1091 427 459 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1092 428 460 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1093 429 461 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1094 430 462 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1095 431 463 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1096 432 464 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1097 433 465 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1098 434 466 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1099 435 467 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1100 436 468 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1101 437 469 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1102 438 470 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1103 439 471 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1104 440 472 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1105 441 473 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1106 442 474 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1107 443 475 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1108 444 476 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1109 445 477 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1110 446 478 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1111 447 479 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1152 448 480 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1153 449 481 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1154 450 482 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1155 451 483 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1156 452 484 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1157 453 485 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1158 454 486 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1159 455 487 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1160 456 488 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1161 457 489 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1162 458 490 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1163 459 491 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1164 460 492 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1165 461 493 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1166 462 494 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1167 463 495 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1168 464 496 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1169 465 497 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1170 466 498 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1171 467 499 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1172 468 500 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1173 469 501 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1174 470 502 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1175 471 503 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1176 472 504 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1177 473 505 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1178 474 506 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1179 475 507 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1180 476 508 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1181 477 509 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1182 478 510 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1183 479 511 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1232 480 512 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1233 481 513 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1234 482 514 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1235 483 515 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1236 484 516 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1237 485 517 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1238 486 518 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1239 487 519 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1240 488 520 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1241 489 521 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1242 490 522 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1243 491 523 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1244 492 524 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1245 493 525 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1246 494 526 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1247 495 527 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1248 496 528 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1249 497 529 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1250 498 530 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1251 499 531 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1252 500 532 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1253 501 533 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1254 502 534 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1255 503 535 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1256 504 536 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1257 505 537 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1258 506 538 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1259 507 539 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1260 508 540 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1261 509 541 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1262 510 542 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1263 511 543 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1304 512 544 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1305 513 545 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1306 514 546 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1307 515 547 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1308 516 548 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1309 517 549 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1310 518 550 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1311 519 551 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1312 520 552 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1313 521 553 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1314 522 554 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1315 523 555 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1316 524 556 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1317 525 557 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1318 526 558 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1319 527 559 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1320 528 560 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1321 529 561 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1322 530 562 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1323 531 563 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1324 532 564 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1325 533 565 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1326 534 566 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1327 535 567 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1328 536 568 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1329 537 569 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1330 538 570 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1331 539 571 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1332 540 572 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1333 541 573 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1334 542 574 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1335 543 575 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1392 544 576 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1393 545 577 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1394 546 578 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1395 547 579 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1396 548 580 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1397 549 581 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1398 550 582 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1399 551 583 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1400 552 584 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1401 553 585 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1402 554 586 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1403 555 587 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1404 556 588 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1405 557 589 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1406 558 590 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1407 559 591 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1408 560 592 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1409 561 593 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1410 562 594 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1411 563 595 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1412 564 596 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1413 565 597 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1414 566 598 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1415 567 599 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1416 568 600 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1417 569 601 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1418 570 602 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1419 571 603 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1420 572 604 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1421 573 605 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1422 574 606 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1423 575 607 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1464 576 608 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1465 577 609 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1466 578 610 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1467 579 611 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1468 580 612 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1469 581 613 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1470 582 614 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1471 583 615 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1472 584 616 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1473 585 617 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1474 586 618 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1475 587 619 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1476 588 620 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1477 589 621 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1478 590 622 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1479 591 623 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1480 592 624 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1481 593 625 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1482 594 626 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1483 595 627 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1484 596 628 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1485 597 629 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1486 598 630 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1487 599 631 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1488 600 632 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1489 601 633 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1490 602 634 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1491 603 635 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1492 604 636 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1493 605 637 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1494 606 638 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1495 607 639 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1552 608 640 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1553 609 641 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1554 610 642 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1555 611 643 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1556 612 644 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1557 613 645 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1558 614 646 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1559 615 647 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1560 616 648 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1561 617 649 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1562 618 650 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1563 619 651 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1564 620 652 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1565 621 653 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1566 622 654 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1567 623 655 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1568 624 656 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1569 625 657 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1570 626 658 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1571 627 659 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1572 628 660 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1573 629 661 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1574 630 662 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1575 631 663 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1576 632 664 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1577 633 665 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1578 634 666 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1579 635 667 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1580 636 668 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1581 637 669 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1582 638 670 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1583 639 671 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1624 640 672 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1625 641 673 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1626 642 674 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1627 643 675 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1628 644 676 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1629 645 677 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1630 646 678 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1631 647 679 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1632 648 680 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1633 649 681 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1634 650 682 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1635 651 683 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1636 652 684 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1637 653 685 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1638 654 686 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1639 655 687 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1640 656 688 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1641 657 689 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1642 658 690 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1643 659 691 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1644 660 692 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1645 661 693 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1646 662 694 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1647 663 695 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1648 664 696 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1649 665 697 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1650 666 698 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1651 667 699 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1652 668 700 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1653 669 701 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1654 670 702 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1655 671 703 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1704 672 704 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1705 673 705 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1706 674 706 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1707 675 707 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1708 676 708 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1709 677 709 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1710 678 710 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1711 679 711 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1712 680 712 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1713 681 713 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1714 682 714 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1715 683 715 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1716 684 716 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1717 685 717 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1718 686 718 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1719 687 719 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1720 688 720 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1721 689 721 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1722 690 722 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1723 691 723 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1724 692 724 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1725 693 725 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1726 694 726 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1727 695 727 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1728 696 728 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1729 697 729 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1730 698 730 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1731 699 731 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1732 700 732 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1733 701 733 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1734 702 734 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1735 703 735 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1776 704 736 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1777 705 737 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1778 706 738 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1779 707 739 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1780 708 740 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1781 709 741 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1782 710 742 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1783 711 743 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1784 712 744 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1785 713 745 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1786 714 746 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1787 715 747 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1788 716 748 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1789 717 749 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1790 718 750 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1791 719 751 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1792 720 752 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1793 721 753 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1794 722 754 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1795 723 755 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1796 724 756 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1797 725 757 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1798 726 758 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1799 727 759 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1800 728 760 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1801 729 761 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1802 730 762 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1803 731 763 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1804 732 764 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1805 733 765 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1806 734 766 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1807 735 767 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1856 736 768 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1857 737 769 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1858 738 770 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1859 739 771 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1860 740 772 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1861 741 773 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1862 742 774 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1863 743 775 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1864 744 776 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1865 745 777 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1866 746 778 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1867 747 779 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1868 748 780 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1869 749 781 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1870 750 782 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1871 751 783 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1872 752 784 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1873 753 785 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1874 754 786 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1875 755 787 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1876 756 788 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1877 757 789 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1878 758 790 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1879 759 791 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1880 760 792 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1881 761 793 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1882 762 794 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1883 763 795 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1884 764 796 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1885 765 797 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1886 766 798 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1887 767 799 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1928 768 800 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1929 769 801 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1930 770 802 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1931 771 803 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1932 772 804 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1933 773 805 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1934 774 806 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1935 775 807 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1936 776 808 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1937 777 809 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1938 778 810 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1939 779 811 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1940 780 812 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1941 781 813 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1942 782 814 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1943 783 815 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1944 784 816 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1945 785 817 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1946 786 818 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1947 787 819 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1948 788 820 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1949 789 821 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1950 790 822 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1951 791 823 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1952 792 824 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1953 793 825 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1954 794 826 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1955 795 827 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1956 796 828 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1957 797 829 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1958 798 830 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 1959 799 831 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2076 832 864 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2077 833 865 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2078 834 866 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2079 835 867 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2080 836 868 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2081 837 869 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2082 838 870 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2083 839 871 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2084 840 872 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2085 841 873 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2086 842 874 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2087 843 875 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2088 844 876 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2089 845 877 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2090 846 878 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2091 847 879 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2092 848 880 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2093 849 881 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2094 850 882 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2095 851 883 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2096 852 884 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2097 853 885 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2098 854 886 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2099 855 887 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2100 856 888 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2101 857 889 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2102 858 890 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2103 859 891 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2104 860 892 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2105 861 893 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2106 862 894 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2107 863 895 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2184 864 896 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2185 865 897 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2186 866 898 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2187 867 899 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2188 868 900 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2189 869 901 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2190 870 902 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2191 871 903 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2192 872 904 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2193 873 905 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2194 874 906 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2195 875 907 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2196 876 908 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2197 877 909 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2198 878 910 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2199 879 911 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2200 880 912 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2201 881 913 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2202 882 914 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2203 883 915 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2204 884 916 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2205 885 917 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2206 886 918 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2207 887 919 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2208 888 920 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2209 889 921 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2210 890 922 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2211 891 923 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2212 892 924 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2213 893 925 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2214 894 926 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2215 895 927 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2264 896 928 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2265 897 929 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2266 898 930 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2267 899 931 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2268 900 932 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2269 901 933 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2270 902 934 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2271 903 935 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2272 904 936 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2273 905 937 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2274 906 938 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2275 907 939 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2276 908 940 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2277 909 941 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2278 910 942 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2279 911 943 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2280 912 944 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2281 913 945 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2282 914 946 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2283 915 947 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2284 916 948 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2285 917 949 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2286 918 950 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2287 919 951 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2288 920 952 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2289 921 953 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2290 922 954 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2291 923 955 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2292 924 956 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2293 925 957 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2294 926 958 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2295 927 959 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2344 928 960 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2345 929 961 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2346 930 962 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2347 931 963 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2348 932 964 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2349 933 965 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2350 934 966 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2351 935 967 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2352 936 968 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2353 937 969 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2354 938 970 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2355 939 971 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2356 940 972 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2357 941 973 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2358 942 974 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2359 943 975 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2360 944 976 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2361 945 977 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2362 946 978 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2363 947 979 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2364 948 980 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2365 949 981 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2366 950 982 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2367 951 983 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2368 952 984 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2369 953 985 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2370 954 986 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2371 955 987 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2372 956 988 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2373 957 989 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2374 958 990 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2375 959 991 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2424 960 992 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2425 961 993 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2426 962 994 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2427 963 995 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2428 964 996 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2429 965 997 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2430 966 998 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2431 967 999 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2432 968 1000 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2433 969 1001 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2434 970 1002 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2435 971 1003 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2436 972 1004 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2437 973 1005 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2438 974 1006 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2439 975 1007 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2440 976 1008 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2441 977 1009 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2442 978 1010 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2443 979 1011 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2444 980 1012 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2445 981 1013 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2446 982 1014 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2447 983 1015 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2448 984 1016 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2449 985 1017 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2450 986 1018 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2451 987 1019 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2452 988 1020 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2453 989 1021 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2454 990 1022 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2455 991 1023 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2504 992 1024 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2505 993 1025 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2506 994 1026 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2507 995 1027 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2508 996 1028 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2509 997 1029 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2510 998 1030 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2511 999 1031 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2512 1000 1032 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2513 1001 1033 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2514 1002 1034 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2515 1003 1035 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2516 1004 1036 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2517 1005 1037 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2518 1006 1038 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2519 1007 1039 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2520 1008 1040 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2521 1009 1041 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2522 1010 1042 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2523 1011 1043 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2524 1012 1044 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2525 1013 1045 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2526 1014 1046 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2527 1015 1047 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2528 1016 1048 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2529 1017 1049 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2530 1018 1050 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2531 1019 1051 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2532 1020 1052 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2533 1021 1053 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2534 1022 1054 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2535 1023 1055 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2584 1024 1056 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2585 1025 1057 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2586 1026 1058 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2587 1027 1059 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2588 1028 1060 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2589 1029 1061 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2590 1030 1062 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2591 1031 1063 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2592 1032 1064 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2593 1033 1065 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2594 1034 1066 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2595 1035 1067 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2596 1036 1068 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2597 1037 1069 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2598 1038 1070 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2599 1039 1071 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2600 1040 1072 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2601 1041 1073 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2602 1042 1074 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2603 1043 1075 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2604 1044 1076 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2605 1045 1077 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2606 1046 1078 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2607 1047 1079 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2608 1048 1080 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2609 1049 1081 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2610 1050 1082 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2611 1051 1083 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2612 1052 1084 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2613 1053 1085 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2614 1054 1086 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2615 1055 1087 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2672 1056 1088 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2673 1057 1089 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2674 1058 1090 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2675 1059 1091 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2676 1060 1092 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2677 1061 1093 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2678 1062 1094 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2679 1063 1095 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2680 1064 1096 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2681 1065 1097 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2682 1066 1098 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2683 1067 1099 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2684 1068 1100 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2685 1069 1101 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2686 1070 1102 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2687 1071 1103 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2688 1072 1104 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2689 1073 1105 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2690 1074 1106 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2691 1075 1107 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2692 1076 1108 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2693 1077 1109 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2694 1078 1110 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2695 1079 1111 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2696 1080 1112 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2697 1081 1113 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2698 1082 1114 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2699 1083 1115 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2700 1084 1116 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2701 1085 1117 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2702 1086 1118 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2703 1087 1119 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2744 1088 1120 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2745 1089 1121 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2746 1090 1122 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2747 1091 1123 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2748 1092 1124 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2749 1093 1125 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2750 1094 1126 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2751 1095 1127 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2752 1096 1128 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2753 1097 1129 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2754 1098 1130 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2755 1099 1131 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2756 1100 1132 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2757 1101 1133 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2758 1102 1134 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2759 1103 1135 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2760 1104 1136 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2761 1105 1137 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2762 1106 1138 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2763 1107 1139 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2764 1108 1140 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2765 1109 1141 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2766 1110 1142 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2767 1111 1143 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2768 1112 1144 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2769 1113 1145 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2770 1114 1146 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2771 1115 1147 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2772 1116 1148 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2773 1117 1149 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2774 1118 1150 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2775 1119 1151 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2832 1120 1152 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2833 1121 1153 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2834 1122 1154 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2835 1123 1155 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2836 1124 1156 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2837 1125 1157 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2838 1126 1158 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2839 1127 1159 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2840 1128 1160 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2841 1129 1161 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2842 1130 1162 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2843 1131 1163 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2844 1132 1164 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2845 1133 1165 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2846 1134 1166 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2847 1135 1167 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2848 1136 1168 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2849 1137 1169 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2850 1138 1170 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2851 1139 1171 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2852 1140 1172 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2853 1141 1173 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2854 1142 1174 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2855 1143 1175 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2856 1144 1176 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2857 1145 1177 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2858 1146 1178 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2859 1147 1179 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2860 1148 1180 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2861 1149 1181 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2862 1150 1182 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2863 1151 1183 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2904 1152 1184 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2905 1153 1185 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2906 1154 1186 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2907 1155 1187 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2908 1156 1188 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2909 1157 1189 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2910 1158 1190 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2911 1159 1191 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2912 1160 1192 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2913 1161 1193 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2914 1162 1194 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2915 1163 1195 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2916 1164 1196 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2917 1165 1197 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2918 1166 1198 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2919 1167 1199 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2920 1168 1200 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2921 1169 1201 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2922 1170 1202 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2923 1171 1203 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2924 1172 1204 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2925 1173 1205 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2926 1174 1206 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2927 1175 1207 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2928 1176 1208 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2929 1177 1209 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2930 1178 1210 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2931 1179 1211 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2932 1180 1212 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2933 1181 1213 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2934 1182 1214 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2935 1183 1215 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2984 1184 1216 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2985 1185 1217 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2986 1186 1218 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2987 1187 1219 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2988 1188 1220 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2989 1189 1221 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2990 1190 1222 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2991 1191 1223 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2992 1192 1224 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2993 1193 1225 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2994 1194 1226 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2995 1195 1227 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2996 1196 1228 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2997 1197 1229 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2998 1198 1230 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 2999 1199 1231 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3000 1200 1232 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3001 1201 1233 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3002 1202 1234 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3003 1203 1235 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3004 1204 1236 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3005 1205 1237 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3006 1206 1238 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3007 1207 1239 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3008 1208 1240 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3009 1209 1241 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3010 1210 1242 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3011 1211 1243 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3012 1212 1244 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3013 1213 1245 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3014 1214 1246 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3015 1215 1247 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3056 1216 1248 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3057 1217 1249 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3058 1218 1250 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3059 1219 1251 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3060 1220 1252 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3061 1221 1253 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3062 1222 1254 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3063 1223 1255 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3064 1224 1256 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3065 1225 1257 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3066 1226 1258 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3067 1227 1259 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3068 1228 1260 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3069 1229 1261 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3070 1230 1262 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3071 1231 1263 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3072 1232 1264 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3073 1233 1265 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3074 1234 1266 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3075 1235 1267 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3076 1236 1268 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3077 1237 1269 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3078 1238 1270 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3079 1239 1271 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3080 1240 1272 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3081 1241 1273 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3082 1242 1274 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3083 1243 1275 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3084 1244 1276 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3085 1245 1277 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3086 1246 1278 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3087 1247 1279 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3156 1248 1280 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3157 1249 1281 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3158 1250 1282 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3159 1251 1283 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3160 1252 1284 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3161 1253 1285 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3162 1254 1286 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3163 1255 1287 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3164 1256 1288 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3165 1257 1289 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3166 1258 1290 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3167 1259 1291 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3168 1260 1292 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3169 1261 1293 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3170 1262 1294 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3171 1263 1295 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3172 1264 1296 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3173 1265 1297 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3174 1266 1298 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3175 1267 1299 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3176 1268 1300 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3177 1269 1301 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3178 1270 1302 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3179 1271 1303 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3180 1272 1304 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3181 1273 1305 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3182 1274 1306 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3183 1275 1307 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3184 1276 1308 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3185 1277 1309 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3186 1278 1310 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3187 1279 1311 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3228 1280 1312 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3229 1281 1313 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3230 1282 1314 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3231 1283 1315 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3232 1284 1316 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3233 1285 1317 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3234 1286 1318 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3235 1287 1319 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3236 1288 1320 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3237 1289 1321 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3238 1290 1322 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3239 1291 1323 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3240 1292 1324 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3241 1293 1325 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3242 1294 1326 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3243 1295 1327 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3244 1296 1328 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3245 1297 1329 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3246 1298 1330 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3247 1299 1331 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3248 1300 1332 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3249 1301 1333 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3250 1302 1334 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3251 1303 1335 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3252 1304 1336 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3253 1305 1337 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3254 1306 1338 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3255 1307 1339 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3256 1308 1340 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3257 1309 1341 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3258 1310 1342 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3259 1311 1343 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3308 1312 1344 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3309 1313 1345 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3310 1314 1346 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3311 1315 1347 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3312 1316 1348 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3313 1317 1349 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3314 1318 1350 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3315 1319 1351 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3316 1320 1352 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3317 1321 1353 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3318 1322 1354 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3319 1323 1355 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3320 1324 1356 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3321 1325 1357 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3322 1326 1358 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3323 1327 1359 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3324 1328 1360 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3325 1329 1361 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3326 1330 1362 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3327 1331 1363 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3328 1332 1364 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3329 1333 1365 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3330 1334 1366 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3331 1335 1367 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3332 1336 1368 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3333 1337 1369 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3334 1338 1370 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3335 1339 1371 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3336 1340 1372 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3337 1341 1373 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3338 1342 1374 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3339 1343 1375 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3380 1344 1376 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3381 1345 1377 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3382 1346 1378 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3383 1347 1379 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3384 1348 1380 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3385 1349 1381 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3386 1350 1382 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3387 1351 1383 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3388 1352 1384 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3389 1353 1385 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3390 1354 1386 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3391 1355 1387 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3392 1356 1388 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3393 1357 1389 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3394 1358 1390 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3395 1359 1391 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3396 1360 1392 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3397 1361 1393 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3398 1362 1394 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3399 1363 1395 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3400 1364 1396 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3401 1365 1397 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3402 1366 1398 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3403 1367 1399 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3404 1368 1400 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3405 1369 1401 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3406 1370 1402 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3407 1371 1403 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3408 1372 1404 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3409 1373 1405 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3410 1374 1406 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3411 1375 1407 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3468 1376 1408 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3469 1377 1409 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3470 1378 1410 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3471 1379 1411 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3472 1380 1412 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3473 1381 1413 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3474 1382 1414 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3475 1383 1415 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3476 1384 1416 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3477 1385 1417 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3478 1386 1418 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3479 1387 1419 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3480 1388 1420 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3481 1389 1421 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3482 1390 1422 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3483 1391 1423 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3484 1392 1424 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3485 1393 1425 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3486 1394 1426 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3487 1395 1427 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3488 1396 1428 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3489 1397 1429 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3490 1398 1430 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3491 1399 1431 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3492 1400 1432 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3493 1401 1433 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3494 1402 1434 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3495 1403 1435 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3496 1404 1436 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3497 1405 1437 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3498 1406 1438 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3499 1407 1439 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3540 1408 1440 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3541 1409 1441 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3542 1410 1442 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3543 1411 1443 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3544 1412 1444 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3545 1413 1445 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3546 1414 1446 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3547 1415 1447 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3548 1416 1448 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3549 1417 1449 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3550 1418 1450 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3551 1419 1451 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3552 1420 1452 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3553 1421 1453 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3554 1422 1454 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3555 1423 1455 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3556 1424 1456 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3557 1425 1457 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3558 1426 1458 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3559 1427 1459 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3560 1428 1460 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3561 1429 1461 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3562 1430 1462 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3563 1431 1463 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3564 1432 1464 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3565 1433 1465 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3566 1434 1466 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3567 1435 1467 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3568 1436 1468 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3569 1437 1469 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3570 1438 1470 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3571 1439 1471 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3628 1440 1472 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3629 1441 1473 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3630 1442 1474 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3631 1443 1475 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3632 1444 1476 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3633 1445 1477 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3634 1446 1478 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3635 1447 1479 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3636 1448 1480 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3637 1449 1481 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3638 1450 1482 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3639 1451 1483 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3640 1452 1484 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3641 1453 1485 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3642 1454 1486 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3643 1455 1487 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3644 1456 1488 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3645 1457 1489 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3646 1458 1490 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3647 1459 1491 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3648 1460 1492 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3649 1461 1493 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3650 1462 1494 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3651 1463 1495 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3652 1464 1496 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3653 1465 1497 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3654 1466 1498 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3655 1467 1499 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3656 1468 1500 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3657 1469 1501 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3658 1470 1502 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3659 1471 1503 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3700 1472 1504 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3701 1473 1505 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3702 1474 1506 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3703 1475 1507 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3704 1476 1508 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3705 1477 1509 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3706 1478 1510 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3707 1479 1511 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3708 1480 1512 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3709 1481 1513 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3710 1482 1514 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3711 1483 1515 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3712 1484 1516 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3713 1485 1517 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3714 1486 1518 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3715 1487 1519 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3716 1488 1520 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3717 1489 1521 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3718 1490 1522 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3719 1491 1523 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3720 1492 1524 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3721 1493 1525 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3722 1494 1526 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3723 1495 1527 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3724 1496 1528 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3725 1497 1529 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3726 1498 1530 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3727 1499 1531 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3728 1500 1532 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3729 1501 1533 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3730 1502 1534 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3731 1503 1535 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3780 1504 1536 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3781 1505 1537 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3782 1506 1538 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3783 1507 1539 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3784 1508 1540 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3785 1509 1541 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3786 1510 1542 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3787 1511 1543 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3788 1512 1544 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3789 1513 1545 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3790 1514 1546 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3791 1515 1547 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3792 1516 1548 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3793 1517 1549 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3794 1518 1550 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3795 1519 1551 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3796 1520 1552 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3797 1521 1553 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3798 1522 1554 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3799 1523 1555 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3800 1524 1556 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3801 1525 1557 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3802 1526 1558 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3803 1527 1559 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3804 1528 1560 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3805 1529 1561 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3806 1530 1562 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3807 1531 1563 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3808 1532 1564 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3809 1533 1565 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3810 1534 1566 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3811 1535 1567 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3852 1536 1568 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3853 1537 1569 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3854 1538 1570 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3855 1539 1571 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3856 1540 1572 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3857 1541 1573 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3858 1542 1574 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3859 1543 1575 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3860 1544 1576 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3861 1545 1577 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3862 1546 1578 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3863 1547 1579 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3864 1548 1580 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3865 1549 1581 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3866 1550 1582 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3867 1551 1583 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3868 1552 1584 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3869 1553 1585 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3870 1554 1586 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3871 1555 1587 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3872 1556 1588 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3873 1557 1589 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3874 1558 1590 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3875 1559 1591 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3876 1560 1592 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3877 1561 1593 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3878 1562 1594 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3879 1563 1595 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3880 1564 1596 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3881 1565 1597 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3882 1566 1598 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3883 1567 1599 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3932 1568 1600 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3933 1569 1601 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3934 1570 1602 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3935 1571 1603 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3936 1572 1604 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3937 1573 1605 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3938 1574 1606 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3939 1575 1607 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3940 1576 1608 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3941 1577 1609 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3942 1578 1610 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3943 1579 1611 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3944 1580 1612 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3945 1581 1613 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3946 1582 1614 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3947 1583 1615 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3948 1584 1616 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3949 1585 1617 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3950 1586 1618 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3951 1587 1619 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3952 1588 1620 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3953 1589 1621 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3954 1590 1622 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3955 1591 1623 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3956 1592 1624 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3957 1593 1625 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3958 1594 1626 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3959 1595 1627 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3960 1596 1628 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3961 1597 1629 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3962 1598 1630 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 3963 1599 1631 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4004 1600 1632 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4005 1601 1633 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4006 1602 1634 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4007 1603 1635 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4008 1604 1636 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4009 1605 1637 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4010 1606 1638 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4011 1607 1639 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4012 1608 1640 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4013 1609 1641 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4014 1610 1642 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4015 1611 1643 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4016 1612 1644 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4017 1613 1645 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4018 1614 1646 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4019 1615 1647 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4020 1616 1648 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4021 1617 1649 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4022 1618 1650 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4023 1619 1651 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4024 1620 1652 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4025 1621 1653 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4026 1622 1654 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4027 1623 1655 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4028 1624 1656 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4029 1625 1657 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4030 1626 1658 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4031 1627 1659 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4032 1628 1660 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4033 1629 1661 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4034 1630 1662 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns
element elasticBeamColumn 4035 1631 1663 $A $E $G $J $Iy $Iz $colTransfTag
incr numColumns

# ===== BEAMS (X-direction) =====
puts ">>> Creating beams (X-direction)..."
element elasticBeamColumn 32 0 4 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 33 1 5 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 34 2 6 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 35 3 7 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 36 4 8 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 37 5 9 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 38 6 10 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 39 7 11 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 40 8 12 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 41 9 13 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 42 10 14 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 43 11 15 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 44 12 16 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 45 13 17 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 46 14 18 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 47 15 19 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 48 16 20 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 49 17 21 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 50 18 22 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 51 19 23 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 52 20 24 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 53 21 25 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 54 22 26 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 55 23 27 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 56 24 28 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 57 25 29 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 58 26 30 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 59 27 31 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 140 32 36 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 141 35 39 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 142 36 40 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 143 39 43 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 144 40 44 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 145 43 47 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 146 44 48 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 147 45 49 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 148 46 50 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 149 47 51 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 150 48 52 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 151 51 55 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 152 52 56 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 153 55 59 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 154 56 60 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 155 59 63 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 220 64 68 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 221 65 69 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 222 66 70 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 223 67 71 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 224 68 72 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 225 69 73 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 226 70 74 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 227 71 75 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 228 72 76 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 229 73 77 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 230 74 78 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 231 75 79 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 232 76 80 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 233 77 81 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 234 78 82 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 235 79 83 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 236 80 84 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 237 81 85 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 238 82 86 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 239 83 87 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 240 84 88 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 241 85 89 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 242 86 90 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 243 87 91 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 244 88 92 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 245 89 93 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 246 90 94 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 247 91 95 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 300 96 100 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 301 99 103 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 302 100 104 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 303 103 107 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 304 104 108 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 305 107 111 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 306 108 112 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 307 109 113 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 308 110 114 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 309 111 115 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 310 112 116 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 311 115 119 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 312 116 120 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 313 119 123 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 314 120 124 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 315 123 127 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 380 128 132 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 381 129 133 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 382 130 134 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 383 131 135 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 384 132 136 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 385 133 137 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 386 134 138 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 387 135 139 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 388 136 140 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 389 137 141 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 390 138 142 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 391 139 143 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 392 140 144 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 393 141 145 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 394 142 146 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 395 143 147 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 396 144 148 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 397 145 149 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 398 146 150 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 399 147 151 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 400 148 152 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 401 149 153 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 402 150 154 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 403 151 155 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 404 152 156 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 405 153 157 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 406 154 158 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 407 155 159 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 460 160 164 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 461 163 167 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 462 164 168 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 463 167 171 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 464 168 172 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 465 171 175 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 466 172 176 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 467 173 177 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 468 174 178 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 469 175 179 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 470 176 180 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 471 179 183 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 472 180 184 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 473 183 187 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 474 184 188 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 475 187 191 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 540 192 196 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 541 193 197 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 542 194 198 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 543 195 199 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 544 196 200 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 545 197 201 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 546 198 202 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 547 199 203 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 548 200 204 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 549 201 205 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 550 202 206 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 551 203 207 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 552 204 208 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 553 205 209 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 554 206 210 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 555 207 211 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 556 208 212 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 557 209 213 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 558 210 214 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 559 211 215 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 560 212 216 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 561 213 217 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 562 214 218 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 563 215 219 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 564 216 220 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 565 217 221 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 566 218 222 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 567 219 223 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 628 224 228 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 629 227 231 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 630 228 232 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 631 231 235 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 632 232 236 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 633 235 239 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 634 236 240 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 635 237 241 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 636 238 242 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 637 239 243 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 638 240 244 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 639 243 247 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 640 244 248 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 641 247 251 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 642 248 252 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 643 251 255 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 700 256 260 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 701 257 261 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 702 258 262 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 703 259 263 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 704 260 264 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 705 261 265 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 706 262 266 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 707 263 267 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 708 264 268 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 709 265 269 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 710 266 270 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 711 267 271 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 712 268 272 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 713 269 273 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 714 270 274 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 715 271 275 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 716 272 276 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 717 273 277 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 718 274 278 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 719 275 279 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 720 276 280 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 721 277 281 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 722 278 282 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 723 279 283 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 724 280 284 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 725 281 285 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 726 282 286 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 727 283 287 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 788 288 292 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 789 291 295 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 790 292 296 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 791 295 299 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 792 296 300 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 793 299 303 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 794 300 304 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 795 301 305 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 796 302 306 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 797 303 307 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 798 304 308 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 799 307 311 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 800 308 312 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 801 311 315 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 802 312 316 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 803 315 319 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 860 320 324 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 861 321 325 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 862 322 326 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 863 323 327 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 864 324 328 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 865 325 329 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 866 326 330 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 867 327 331 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 868 328 332 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 869 329 333 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 870 330 334 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 871 331 335 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 872 332 336 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 873 333 337 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 874 334 338 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 875 335 339 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 876 336 340 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 877 337 341 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 878 338 342 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 879 339 343 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 880 340 344 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 881 341 345 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 882 342 346 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 883 343 347 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 884 344 348 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 885 345 349 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 886 346 350 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 887 347 351 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 940 352 356 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 941 355 359 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 942 356 360 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 943 359 363 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 944 360 364 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 945 363 367 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 946 364 368 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 947 365 369 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 948 366 370 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 949 367 371 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 950 368 372 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 951 371 375 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 952 372 376 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 953 375 379 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 954 376 380 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 955 379 383 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1012 384 388 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1013 385 389 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1014 386 390 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1015 387 391 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1016 388 392 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1017 389 393 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1018 390 394 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1019 391 395 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1020 392 396 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1021 393 397 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1022 394 398 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1023 395 399 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1024 396 400 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1025 397 401 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1026 398 402 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1027 399 403 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1028 400 404 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1029 401 405 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1030 402 406 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1031 403 407 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1032 404 408 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1033 405 409 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1034 406 410 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1035 407 411 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1036 408 412 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1037 409 413 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1038 410 414 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1039 411 415 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1112 416 420 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1113 419 423 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1114 420 424 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1115 423 427 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1116 424 428 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1117 427 431 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1118 428 432 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1119 429 433 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1120 430 434 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1121 431 435 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1122 432 436 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1123 435 439 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1124 436 440 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1125 439 443 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1126 440 444 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1127 443 447 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1184 448 452 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1185 449 453 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1186 450 454 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1187 451 455 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1188 452 456 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1189 453 457 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1190 454 458 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1191 455 459 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1192 456 460 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1193 457 461 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1194 458 462 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1195 459 463 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1196 460 464 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1197 461 465 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1198 462 466 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1199 463 467 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1200 464 468 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1201 465 469 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1202 466 470 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1203 467 471 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1204 468 472 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1205 469 473 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1206 470 474 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1207 471 475 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1208 472 476 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1209 473 477 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1210 474 478 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1211 475 479 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1264 480 484 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1265 483 487 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1266 484 488 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1267 487 491 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1268 488 492 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1269 491 495 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1270 492 496 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1271 493 497 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1272 494 498 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1273 495 499 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1274 496 500 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1275 499 503 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1276 500 504 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1277 503 507 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1278 504 508 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1279 507 511 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1336 512 516 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1337 513 517 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1338 514 518 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1339 515 519 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1340 516 520 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1341 517 521 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1342 518 522 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1343 519 523 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1344 520 524 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1345 521 525 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1346 522 526 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1347 523 527 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1348 524 528 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1349 525 529 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1350 526 530 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1351 527 531 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1352 528 532 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1353 529 533 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1354 530 534 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1355 531 535 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1356 532 536 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1357 533 537 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1358 534 538 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1359 535 539 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1360 536 540 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1361 537 541 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1362 538 542 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1363 539 543 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1424 544 548 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1425 547 551 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1426 548 552 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1427 551 555 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1428 552 556 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1429 555 559 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1430 556 560 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1431 557 561 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1432 558 562 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1433 559 563 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1434 560 564 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1435 563 567 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1436 564 568 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1437 567 571 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1438 568 572 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1439 571 575 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1496 576 580 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1497 577 581 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1498 578 582 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1499 579 583 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1500 580 584 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1501 581 585 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1502 582 586 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1503 583 587 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1504 584 588 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1505 585 589 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1506 586 590 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1507 587 591 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1508 588 592 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1509 589 593 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1510 590 594 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1511 591 595 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1512 592 596 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1513 593 597 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1514 594 598 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1515 595 599 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1516 596 600 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1517 597 601 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1518 598 602 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1519 599 603 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1520 600 604 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1521 601 605 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1522 602 606 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1523 603 607 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1584 608 612 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1585 611 615 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1586 612 616 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1587 615 619 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1588 616 620 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1589 619 623 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1590 620 624 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1591 621 625 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1592 622 626 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1593 623 627 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1594 624 628 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1595 627 631 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1596 628 632 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1597 631 635 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1598 632 636 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1599 635 639 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1656 640 644 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1657 641 645 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1658 642 646 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1659 643 647 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1660 644 648 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1661 645 649 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1662 646 650 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1663 647 651 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1664 648 652 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1665 649 653 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1666 650 654 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1667 651 655 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1668 652 656 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1669 653 657 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1670 654 658 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1671 655 659 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1672 656 660 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1673 657 661 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1674 658 662 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1675 659 663 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1676 660 664 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1677 661 665 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1678 662 666 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1679 663 667 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1680 664 668 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1681 665 669 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1682 666 670 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1683 667 671 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1736 672 676 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1737 675 679 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1738 676 680 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1739 679 683 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1740 680 684 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1741 683 687 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1742 684 688 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1743 685 689 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1744 686 690 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1745 687 691 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1746 688 692 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1747 691 695 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1748 692 696 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1749 695 699 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1750 696 700 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1751 699 703 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1808 704 708 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1809 705 709 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1810 706 710 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1811 707 711 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1812 708 712 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1813 709 713 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1814 710 714 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1815 711 715 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1816 712 716 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1817 713 717 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1818 714 718 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1819 715 719 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1820 716 720 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1821 717 721 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1822 718 722 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1823 719 723 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1824 720 724 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1825 721 725 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1826 722 726 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1827 723 727 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1828 724 728 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1829 725 729 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1830 726 730 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1831 727 731 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1832 728 732 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1833 729 733 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1834 730 734 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1835 731 735 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1888 736 740 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1889 739 743 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1890 740 744 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1891 743 747 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1892 744 748 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1893 747 751 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1894 748 752 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1895 749 753 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1896 750 754 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1897 751 755 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1898 752 756 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1899 755 759 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1900 756 760 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1901 759 763 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1902 760 764 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1903 763 767 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1960 768 772 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1961 769 773 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1962 770 774 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1963 771 775 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1964 772 776 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1965 773 777 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1966 774 778 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1967 775 779 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1968 776 780 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1969 777 781 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1970 778 782 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1971 779 783 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1972 780 784 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1973 781 785 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1974 782 786 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1975 783 787 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1976 784 788 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1977 785 789 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1978 786 790 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1979 787 791 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1980 788 792 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1981 789 793 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1982 790 794 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1983 791 795 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1984 792 796 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1985 793 797 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1986 794 798 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 1987 795 799 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2036 800 804 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2037 803 807 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2038 804 808 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2039 807 811 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2040 808 812 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2041 811 815 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2042 812 816 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2043 813 817 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2044 814 818 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2045 815 819 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2046 816 820 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2047 819 823 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2048 820 824 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2049 823 827 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2050 824 828 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2051 827 831 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2108 832 836 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2109 833 837 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2110 834 838 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2111 835 839 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2112 836 840 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2113 837 841 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2114 838 842 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2115 839 843 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2116 840 844 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2117 841 845 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2118 842 846 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2119 843 847 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2120 844 848 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2121 845 849 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2122 846 850 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2123 847 851 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2124 848 852 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2125 849 853 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2126 850 854 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2127 851 855 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2128 852 856 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2129 853 857 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2130 854 858 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2131 855 859 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2132 856 860 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2133 857 861 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2134 858 862 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2135 859 863 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2216 864 868 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2217 867 871 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2218 868 872 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2219 871 875 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2220 872 876 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2221 875 879 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2222 876 880 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2223 877 881 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2224 878 882 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2225 879 883 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2226 880 884 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2227 883 887 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2228 884 888 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2229 887 891 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2230 888 892 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2231 891 895 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2296 896 900 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2297 897 901 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2298 898 902 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2299 899 903 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2300 900 904 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2301 901 905 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2302 902 906 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2303 903 907 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2304 904 908 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2305 905 909 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2306 906 910 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2307 907 911 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2308 908 912 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2309 909 913 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2310 910 914 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2311 911 915 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2312 912 916 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2313 913 917 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2314 914 918 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2315 915 919 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2316 916 920 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2317 917 921 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2318 918 922 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2319 919 923 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2320 920 924 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2321 921 925 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2322 922 926 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2323 923 927 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2376 928 932 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2377 931 935 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2378 932 936 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2379 935 939 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2380 936 940 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2381 939 943 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2382 940 944 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2383 941 945 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2384 942 946 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2385 943 947 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2386 944 948 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2387 947 951 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2388 948 952 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2389 951 955 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2390 952 956 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2391 955 959 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2456 960 964 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2457 961 965 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2458 962 966 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2459 963 967 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2460 964 968 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2461 965 969 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2462 966 970 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2463 967 971 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2464 968 972 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2465 969 973 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2466 970 974 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2467 971 975 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2468 972 976 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2469 973 977 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2470 974 978 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2471 975 979 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2472 976 980 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2473 977 981 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2474 978 982 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2475 979 983 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2476 980 984 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2477 981 985 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2478 982 986 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2479 983 987 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2480 984 988 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2481 985 989 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2482 986 990 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2483 987 991 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2536 992 996 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2537 995 999 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2538 996 1000 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2539 999 1003 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2540 1000 1004 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2541 1003 1007 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2542 1004 1008 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2543 1005 1009 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2544 1006 1010 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2545 1007 1011 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2546 1008 1012 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2547 1011 1015 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2548 1012 1016 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2549 1015 1019 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2550 1016 1020 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2551 1019 1023 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2616 1024 1028 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2617 1025 1029 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2618 1026 1030 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2619 1027 1031 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2620 1028 1032 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2621 1029 1033 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2622 1030 1034 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2623 1031 1035 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2624 1032 1036 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2625 1033 1037 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2626 1034 1038 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2627 1035 1039 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2628 1036 1040 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2629 1037 1041 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2630 1038 1042 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2631 1039 1043 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2632 1040 1044 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2633 1041 1045 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2634 1042 1046 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2635 1043 1047 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2636 1044 1048 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2637 1045 1049 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2638 1046 1050 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2639 1047 1051 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2640 1048 1052 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2641 1049 1053 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2642 1050 1054 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2643 1051 1055 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2704 1056 1060 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2705 1059 1063 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2706 1060 1064 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2707 1063 1067 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2708 1064 1068 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2709 1067 1071 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2710 1068 1072 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2711 1069 1073 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2712 1070 1074 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2713 1071 1075 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2714 1072 1076 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2715 1075 1079 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2716 1076 1080 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2717 1079 1083 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2718 1080 1084 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2719 1083 1087 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2776 1088 1092 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2777 1089 1093 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2778 1090 1094 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2779 1091 1095 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2780 1092 1096 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2781 1093 1097 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2782 1094 1098 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2783 1095 1099 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2784 1096 1100 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2785 1097 1101 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2786 1098 1102 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2787 1099 1103 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2788 1100 1104 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2789 1101 1105 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2790 1102 1106 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2791 1103 1107 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2792 1104 1108 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2793 1105 1109 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2794 1106 1110 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2795 1107 1111 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2796 1108 1112 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2797 1109 1113 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2798 1110 1114 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2799 1111 1115 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2800 1112 1116 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2801 1113 1117 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2802 1114 1118 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2803 1115 1119 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2864 1120 1124 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2865 1123 1127 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2866 1124 1128 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2867 1127 1131 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2868 1128 1132 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2869 1131 1135 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2870 1132 1136 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2871 1133 1137 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2872 1134 1138 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2873 1135 1139 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2874 1136 1140 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2875 1139 1143 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2876 1140 1144 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2877 1143 1147 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2878 1144 1148 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2879 1147 1151 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2936 1152 1156 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2937 1153 1157 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2938 1154 1158 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2939 1155 1159 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2940 1156 1160 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2941 1157 1161 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2942 1158 1162 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2943 1159 1163 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2944 1160 1164 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2945 1161 1165 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2946 1162 1166 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2947 1163 1167 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2948 1164 1168 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2949 1165 1169 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2950 1166 1170 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2951 1167 1171 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2952 1168 1172 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2953 1169 1173 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2954 1170 1174 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2955 1171 1175 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2956 1172 1176 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2957 1173 1177 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2958 1174 1178 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2959 1175 1179 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2960 1176 1180 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2961 1177 1181 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2962 1178 1182 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 2963 1179 1183 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3016 1184 1188 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3017 1187 1191 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3018 1188 1192 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3019 1191 1195 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3020 1192 1196 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3021 1195 1199 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3022 1196 1200 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3023 1197 1201 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3024 1198 1202 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3025 1199 1203 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3026 1200 1204 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3027 1203 1207 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3028 1204 1208 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3029 1207 1211 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3030 1208 1212 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3031 1211 1215 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3088 1216 1220 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3089 1217 1221 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3090 1218 1222 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3091 1219 1223 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3092 1220 1224 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3093 1221 1225 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3094 1222 1226 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3095 1223 1227 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3096 1224 1228 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3097 1225 1229 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3098 1226 1230 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3099 1227 1231 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3100 1228 1232 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3101 1229 1233 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3102 1230 1234 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3103 1231 1235 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3104 1232 1236 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3105 1233 1237 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3106 1234 1238 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3107 1235 1239 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3108 1236 1240 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3109 1237 1241 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3110 1238 1242 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3111 1239 1243 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3112 1240 1244 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3113 1241 1245 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3114 1242 1246 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3115 1243 1247 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3188 1248 1252 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3189 1251 1255 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3190 1252 1256 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3191 1255 1259 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3192 1256 1260 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3193 1259 1263 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3194 1260 1264 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3195 1261 1265 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3196 1262 1266 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3197 1263 1267 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3198 1264 1268 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3199 1267 1271 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3200 1268 1272 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3201 1271 1275 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3202 1272 1276 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3203 1275 1279 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3260 1280 1284 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3261 1281 1285 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3262 1282 1286 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3263 1283 1287 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3264 1284 1288 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3265 1285 1289 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3266 1286 1290 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3267 1287 1291 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3268 1288 1292 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3269 1289 1293 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3270 1290 1294 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3271 1291 1295 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3272 1292 1296 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3273 1293 1297 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3274 1294 1298 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3275 1295 1299 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3276 1296 1300 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3277 1297 1301 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3278 1298 1302 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3279 1299 1303 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3280 1300 1304 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3281 1301 1305 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3282 1302 1306 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3283 1303 1307 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3284 1304 1308 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3285 1305 1309 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3286 1306 1310 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3287 1307 1311 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3340 1312 1316 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3341 1315 1319 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3342 1316 1320 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3343 1319 1323 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3344 1320 1324 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3345 1323 1327 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3346 1324 1328 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3347 1325 1329 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3348 1326 1330 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3349 1327 1331 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3350 1328 1332 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3351 1331 1335 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3352 1332 1336 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3353 1335 1339 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3354 1336 1340 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3355 1339 1343 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3412 1344 1348 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3413 1345 1349 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3414 1346 1350 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3415 1347 1351 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3416 1348 1352 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3417 1349 1353 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3418 1350 1354 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3419 1351 1355 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3420 1352 1356 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3421 1353 1357 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3422 1354 1358 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3423 1355 1359 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3424 1356 1360 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3425 1357 1361 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3426 1358 1362 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3427 1359 1363 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3428 1360 1364 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3429 1361 1365 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3430 1362 1366 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3431 1363 1367 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3432 1364 1368 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3433 1365 1369 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3434 1366 1370 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3435 1367 1371 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3436 1368 1372 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3437 1369 1373 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3438 1370 1374 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3439 1371 1375 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3500 1376 1380 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3501 1379 1383 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3502 1380 1384 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3503 1383 1387 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3504 1384 1388 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3505 1387 1391 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3506 1388 1392 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3507 1389 1393 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3508 1390 1394 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3509 1391 1395 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3510 1392 1396 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3511 1395 1399 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3512 1396 1400 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3513 1399 1403 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3514 1400 1404 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3515 1403 1407 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3572 1408 1412 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3573 1409 1413 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3574 1410 1414 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3575 1411 1415 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3576 1412 1416 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3577 1413 1417 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3578 1414 1418 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3579 1415 1419 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3580 1416 1420 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3581 1417 1421 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3582 1418 1422 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3583 1419 1423 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3584 1420 1424 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3585 1421 1425 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3586 1422 1426 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3587 1423 1427 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3588 1424 1428 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3589 1425 1429 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3590 1426 1430 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3591 1427 1431 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3592 1428 1432 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3593 1429 1433 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3594 1430 1434 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3595 1431 1435 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3596 1432 1436 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3597 1433 1437 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3598 1434 1438 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3599 1435 1439 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3660 1440 1444 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3661 1443 1447 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3662 1444 1448 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3663 1447 1451 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3664 1448 1452 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3665 1451 1455 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3666 1452 1456 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3667 1453 1457 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3668 1454 1458 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3669 1455 1459 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3670 1456 1460 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3671 1459 1463 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3672 1460 1464 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3673 1463 1467 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3674 1464 1468 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3675 1467 1471 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3732 1472 1476 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3733 1473 1477 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3734 1474 1478 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3735 1475 1479 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3736 1476 1480 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3737 1477 1481 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3738 1478 1482 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3739 1479 1483 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3740 1480 1484 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3741 1481 1485 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3742 1482 1486 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3743 1483 1487 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3744 1484 1488 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3745 1485 1489 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3746 1486 1490 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3747 1487 1491 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3748 1488 1492 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3749 1489 1493 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3750 1490 1494 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3751 1491 1495 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3752 1492 1496 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3753 1493 1497 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3754 1494 1498 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3755 1495 1499 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3756 1496 1500 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3757 1497 1501 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3758 1498 1502 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3759 1499 1503 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3812 1504 1508 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3813 1507 1511 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3814 1508 1512 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3815 1511 1515 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3816 1512 1516 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3817 1515 1519 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3818 1516 1520 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3819 1517 1521 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3820 1518 1522 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3821 1519 1523 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3822 1520 1524 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3823 1523 1527 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3824 1524 1528 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3825 1527 1531 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3826 1528 1532 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3827 1531 1535 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3884 1536 1540 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3885 1537 1541 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3886 1538 1542 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3887 1539 1543 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3888 1540 1544 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3889 1541 1545 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3890 1542 1546 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3891 1543 1547 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3892 1544 1548 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3893 1545 1549 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3894 1546 1550 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3895 1547 1551 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3896 1548 1552 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3897 1549 1553 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3898 1550 1554 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3899 1551 1555 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3900 1552 1556 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3901 1553 1557 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3902 1554 1558 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3903 1555 1559 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3904 1556 1560 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3905 1557 1561 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3906 1558 1562 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3907 1559 1563 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3908 1560 1564 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3909 1561 1565 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3910 1562 1566 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3911 1563 1567 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3964 1568 1572 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3965 1571 1575 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3966 1572 1576 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3967 1575 1579 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3968 1576 1580 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3969 1579 1583 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3970 1580 1584 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3971 1581 1585 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3972 1582 1586 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3973 1583 1587 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3974 1584 1588 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3975 1587 1591 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3976 1588 1592 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3977 1591 1595 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3978 1592 1596 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 3979 1595 1599 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4036 1600 1604 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4037 1601 1605 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4038 1602 1606 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4039 1603 1607 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4040 1604 1608 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4041 1605 1609 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4042 1606 1610 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4043 1607 1611 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4044 1608 1612 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4045 1609 1613 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4046 1610 1614 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4047 1611 1615 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4048 1612 1616 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4049 1613 1617 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4050 1614 1618 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4051 1615 1619 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4052 1616 1620 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4053 1617 1621 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4054 1618 1622 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4055 1619 1623 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4056 1620 1624 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4057 1621 1625 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4058 1622 1626 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4059 1623 1627 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4060 1624 1628 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4061 1625 1629 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4062 1626 1630 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4063 1627 1631 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4112 1632 1636 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4113 1635 1639 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4114 1636 1640 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4115 1639 1643 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4116 1640 1644 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4117 1643 1647 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4118 1644 1648 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4119 1645 1649 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4120 1646 1650 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4121 1647 1651 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4122 1648 1652 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4123 1651 1655 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4124 1652 1656 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4125 1655 1659 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4126 1656 1660 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX
element elasticBeamColumn 4127 1659 1663 $A $E $G $J $Iy $Iz $beamXTransfTag
incr numBeamsX

# ===== BEAMS (Y-direction) =====
puts ">>> Creating beams (Y-direction)..."
element elasticBeamColumn 60 0 1 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 61 12 13 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 62 16 17 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 63 28 29 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 64 1 2 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 65 13 14 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 66 17 18 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 67 29 30 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 68 2 3 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 69 14 15 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 70 18 19 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 71 30 31 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 156 32 33 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 157 36 37 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 158 40 41 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 159 44 45 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 160 48 49 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 161 52 53 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 162 56 57 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 163 60 61 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 164 33 34 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 165 37 38 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 166 41 42 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 167 45 46 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 168 49 50 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 169 53 54 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 170 57 58 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 171 61 62 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 172 34 35 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 173 38 39 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 174 42 43 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 175 46 47 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 176 50 51 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 177 54 55 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 178 58 59 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 179 62 63 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 248 64 65 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 249 76 77 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 250 80 81 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 251 92 93 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 252 65 66 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 253 77 78 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 254 81 82 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 255 93 94 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 256 66 67 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 257 78 79 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 258 82 83 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 259 94 95 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 316 96 97 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 317 100 101 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 318 104 105 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 319 108 109 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 320 112 113 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 321 116 117 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 322 120 121 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 323 124 125 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 324 97 98 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 325 101 102 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 326 105 106 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 327 109 110 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 328 113 114 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 329 117 118 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 330 121 122 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 331 125 126 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 332 98 99 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 333 102 103 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 334 106 107 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 335 110 111 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 336 114 115 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 337 118 119 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 338 122 123 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 339 126 127 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 408 128 129 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 409 140 141 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 410 144 145 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 411 156 157 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 412 129 130 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 413 141 142 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 414 145 146 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 415 157 158 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 416 130 131 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 417 142 143 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 418 146 147 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 419 158 159 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 476 160 161 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 477 164 165 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 478 168 169 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 479 172 173 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 480 176 177 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 481 180 181 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 482 184 185 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 483 188 189 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 484 161 162 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 485 165 166 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 486 169 170 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 487 173 174 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 488 177 178 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 489 181 182 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 490 185 186 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 491 189 190 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 492 162 163 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 493 166 167 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 494 170 171 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 495 174 175 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 496 178 179 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 497 182 183 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 498 186 187 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 499 190 191 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 568 192 193 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 569 204 205 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 570 208 209 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 571 220 221 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 572 193 194 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 573 205 206 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 574 209 210 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 575 221 222 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 576 194 195 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 577 206 207 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 578 210 211 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 579 222 223 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 644 224 225 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 645 228 229 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 646 232 233 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 647 236 237 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 648 240 241 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 649 244 245 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 650 248 249 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 651 252 253 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 652 225 226 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 653 229 230 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 654 233 234 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 655 237 238 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 656 241 242 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 657 245 246 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 658 249 250 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 659 253 254 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 660 226 227 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 661 230 231 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 662 234 235 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 663 238 239 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 664 242 243 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 665 246 247 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 666 250 251 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 667 254 255 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 728 256 257 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 729 268 269 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 730 272 273 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 731 284 285 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 732 257 258 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 733 269 270 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 734 273 274 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 735 285 286 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 736 258 259 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 737 270 271 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 738 274 275 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 739 286 287 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 804 288 289 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 805 292 293 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 806 296 297 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 807 300 301 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 808 304 305 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 809 308 309 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 810 312 313 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 811 316 317 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 812 289 290 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 813 293 294 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 814 297 298 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 815 301 302 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 816 305 306 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 817 309 310 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 818 313 314 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 819 317 318 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 820 290 291 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 821 294 295 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 822 298 299 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 823 302 303 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 824 306 307 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 825 310 311 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 826 314 315 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 827 318 319 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 888 320 321 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 889 332 333 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 890 336 337 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 891 348 349 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 892 321 322 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 893 333 334 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 894 337 338 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 895 349 350 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 896 322 323 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 897 334 335 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 898 338 339 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 899 350 351 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 956 352 353 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 957 356 357 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 958 360 361 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 959 364 365 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 960 368 369 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 961 372 373 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 962 376 377 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 963 380 381 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 964 353 354 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 965 357 358 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 966 361 362 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 967 365 366 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 968 369 370 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 969 373 374 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 970 377 378 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 971 381 382 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 972 354 355 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 973 358 359 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 974 362 363 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 975 366 367 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 976 370 371 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 977 374 375 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 978 378 379 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 979 382 383 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1040 384 385 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1041 396 397 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1042 400 401 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1043 412 413 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1044 385 386 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1045 397 398 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1046 401 402 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1047 413 414 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1048 386 387 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1049 398 399 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1050 402 403 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1051 414 415 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1128 416 417 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1129 420 421 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1130 424 425 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1131 428 429 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1132 432 433 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1133 436 437 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1134 440 441 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1135 444 445 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1136 417 418 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1137 421 422 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1138 425 426 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1139 429 430 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1140 433 434 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1141 437 438 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1142 441 442 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1143 445 446 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1144 418 419 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1145 422 423 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1146 426 427 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1147 430 431 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1148 434 435 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1149 438 439 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1150 442 443 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1151 446 447 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1212 448 449 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1213 460 461 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1214 464 465 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1215 476 477 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1216 449 450 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1217 461 462 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1218 465 466 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1219 477 478 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1220 450 451 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1221 462 463 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1222 466 467 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1223 478 479 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1280 480 481 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1281 484 485 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1282 488 489 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1283 492 493 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1284 496 497 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1285 500 501 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1286 504 505 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1287 508 509 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1288 481 482 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1289 485 486 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1290 489 490 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1291 493 494 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1292 497 498 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1293 501 502 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1294 505 506 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1295 509 510 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1296 482 483 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1297 486 487 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1298 490 491 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1299 494 495 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1300 498 499 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1301 502 503 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1302 506 507 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1303 510 511 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1364 512 513 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1365 524 525 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1366 528 529 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1367 540 541 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1368 513 514 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1369 525 526 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1370 529 530 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1371 541 542 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1372 514 515 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1373 526 527 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1374 530 531 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1375 542 543 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1440 544 545 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1441 548 549 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1442 552 553 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1443 556 557 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1444 560 561 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1445 564 565 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1446 568 569 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1447 572 573 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1448 545 546 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1449 549 550 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1450 553 554 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1451 557 558 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1452 561 562 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1453 565 566 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1454 569 570 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1455 573 574 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1456 546 547 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1457 550 551 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1458 554 555 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1459 558 559 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1460 562 563 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1461 566 567 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1462 570 571 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1463 574 575 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1524 576 577 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1525 588 589 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1526 592 593 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1527 604 605 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1528 577 578 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1529 589 590 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1530 593 594 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1531 605 606 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1532 578 579 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1533 590 591 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1534 594 595 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1535 606 607 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1600 608 609 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1601 612 613 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1602 616 617 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1603 620 621 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1604 624 625 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1605 628 629 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1606 632 633 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1607 636 637 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1608 609 610 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1609 613 614 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1610 617 618 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1611 621 622 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1612 625 626 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1613 629 630 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1614 633 634 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1615 637 638 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1616 610 611 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1617 614 615 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1618 618 619 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1619 622 623 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1620 626 627 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1621 630 631 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1622 634 635 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1623 638 639 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1684 640 641 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1685 652 653 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1686 656 657 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1687 668 669 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1688 641 642 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1689 653 654 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1690 657 658 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1691 669 670 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1692 642 643 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1693 654 655 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1694 658 659 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1695 670 671 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1752 672 673 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1753 676 677 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1754 680 681 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1755 684 685 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1756 688 689 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1757 692 693 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1758 696 697 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1759 700 701 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1760 673 674 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1761 677 678 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1762 681 682 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1763 685 686 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1764 689 690 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1765 693 694 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1766 697 698 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1767 701 702 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1768 674 675 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1769 678 679 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1770 682 683 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1771 686 687 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1772 690 691 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1773 694 695 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1774 698 699 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1775 702 703 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1836 704 705 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1837 716 717 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1838 720 721 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1839 732 733 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1840 705 706 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1841 717 718 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1842 721 722 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1843 733 734 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1844 706 707 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1845 718 719 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1846 722 723 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1847 734 735 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1904 736 737 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1905 740 741 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1906 744 745 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1907 748 749 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1908 752 753 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1909 756 757 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1910 760 761 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1911 764 765 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1912 737 738 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1913 741 742 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1914 745 746 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1915 749 750 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1916 753 754 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1917 757 758 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1918 761 762 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1919 765 766 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1920 738 739 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1921 742 743 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1922 746 747 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1923 750 751 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1924 754 755 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1925 758 759 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1926 762 763 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1927 766 767 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1988 768 769 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1989 780 781 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1990 784 785 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1991 796 797 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1992 769 770 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1993 781 782 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1994 785 786 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1995 797 798 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1996 770 771 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1997 782 783 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1998 786 787 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 1999 798 799 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2052 800 801 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2053 804 805 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2054 808 809 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2055 812 813 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2056 816 817 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2057 820 821 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2058 824 825 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2059 828 829 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2060 801 802 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2061 805 806 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2062 809 810 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2063 813 814 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2064 817 818 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2065 821 822 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2066 825 826 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2067 829 830 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2068 802 803 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2069 806 807 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2070 810 811 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2071 814 815 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2072 818 819 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2073 822 823 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2074 826 827 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2075 830 831 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2136 832 833 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2137 844 845 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2138 848 849 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2139 860 861 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2140 833 834 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2141 845 846 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2142 849 850 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2143 861 862 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2144 834 835 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2145 846 847 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2146 850 851 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2147 862 863 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2232 864 865 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2233 868 869 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2234 872 873 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2235 876 877 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2236 880 881 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2237 884 885 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2238 888 889 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2239 892 893 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2240 865 866 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2241 869 870 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2242 873 874 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2243 877 878 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2244 881 882 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2245 885 886 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2246 889 890 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2247 893 894 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2248 866 867 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2249 870 871 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2250 874 875 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2251 878 879 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2252 882 883 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2253 886 887 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2254 890 891 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2255 894 895 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2324 896 897 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2325 908 909 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2326 912 913 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2327 924 925 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2328 897 898 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2329 909 910 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2330 913 914 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2331 925 926 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2332 898 899 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2333 910 911 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2334 914 915 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2335 926 927 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2392 928 929 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2393 932 933 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2394 936 937 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2395 940 941 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2396 944 945 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2397 948 949 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2398 952 953 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2399 956 957 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2400 929 930 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2401 933 934 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2402 937 938 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2403 941 942 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2404 945 946 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2405 949 950 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2406 953 954 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2407 957 958 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2408 930 931 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2409 934 935 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2410 938 939 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2411 942 943 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2412 946 947 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2413 950 951 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2414 954 955 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2415 958 959 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2484 960 961 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2485 972 973 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2486 976 977 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2487 988 989 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2488 961 962 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2489 973 974 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2490 977 978 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2491 989 990 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2492 962 963 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2493 974 975 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2494 978 979 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2495 990 991 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2552 992 993 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2553 996 997 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2554 1000 1001 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2555 1004 1005 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2556 1008 1009 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2557 1012 1013 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2558 1016 1017 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2559 1020 1021 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2560 993 994 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2561 997 998 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2562 1001 1002 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2563 1005 1006 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2564 1009 1010 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2565 1013 1014 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2566 1017 1018 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2567 1021 1022 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2568 994 995 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2569 998 999 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2570 1002 1003 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2571 1006 1007 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2572 1010 1011 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2573 1014 1015 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2574 1018 1019 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2575 1022 1023 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2644 1024 1025 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2645 1036 1037 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2646 1040 1041 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2647 1052 1053 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2648 1025 1026 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2649 1037 1038 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2650 1041 1042 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2651 1053 1054 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2652 1026 1027 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2653 1038 1039 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2654 1042 1043 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2655 1054 1055 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2720 1056 1057 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2721 1060 1061 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2722 1064 1065 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2723 1068 1069 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2724 1072 1073 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2725 1076 1077 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2726 1080 1081 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2727 1084 1085 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2728 1057 1058 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2729 1061 1062 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2730 1065 1066 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2731 1069 1070 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2732 1073 1074 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2733 1077 1078 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2734 1081 1082 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2735 1085 1086 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2736 1058 1059 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2737 1062 1063 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2738 1066 1067 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2739 1070 1071 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2740 1074 1075 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2741 1078 1079 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2742 1082 1083 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2743 1086 1087 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2804 1088 1089 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2805 1100 1101 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2806 1104 1105 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2807 1116 1117 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2808 1089 1090 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2809 1101 1102 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2810 1105 1106 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2811 1117 1118 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2812 1090 1091 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2813 1102 1103 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2814 1106 1107 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2815 1118 1119 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2880 1120 1121 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2881 1124 1125 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2882 1128 1129 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2883 1132 1133 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2884 1136 1137 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2885 1140 1141 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2886 1144 1145 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2887 1148 1149 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2888 1121 1122 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2889 1125 1126 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2890 1129 1130 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2891 1133 1134 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2892 1137 1138 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2893 1141 1142 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2894 1145 1146 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2895 1149 1150 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2896 1122 1123 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2897 1126 1127 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2898 1130 1131 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2899 1134 1135 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2900 1138 1139 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2901 1142 1143 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2902 1146 1147 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2903 1150 1151 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2964 1152 1153 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2965 1164 1165 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2966 1168 1169 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2967 1180 1181 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2968 1153 1154 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2969 1165 1166 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2970 1169 1170 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2971 1181 1182 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2972 1154 1155 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2973 1166 1167 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2974 1170 1171 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 2975 1182 1183 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3032 1184 1185 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3033 1188 1189 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3034 1192 1193 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3035 1196 1197 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3036 1200 1201 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3037 1204 1205 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3038 1208 1209 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3039 1212 1213 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3040 1185 1186 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3041 1189 1190 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3042 1193 1194 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3043 1197 1198 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3044 1201 1202 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3045 1205 1206 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3046 1209 1210 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3047 1213 1214 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3048 1186 1187 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3049 1190 1191 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3050 1194 1195 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3051 1198 1199 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3052 1202 1203 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3053 1206 1207 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3054 1210 1211 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3055 1214 1215 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3116 1216 1217 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3117 1228 1229 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3118 1232 1233 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3119 1244 1245 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3120 1217 1218 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3121 1229 1230 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3122 1233 1234 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3123 1245 1246 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3124 1218 1219 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3125 1230 1231 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3126 1234 1235 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3127 1246 1247 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3204 1248 1249 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3205 1252 1253 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3206 1256 1257 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3207 1260 1261 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3208 1264 1265 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3209 1268 1269 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3210 1272 1273 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3211 1276 1277 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3212 1249 1250 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3213 1253 1254 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3214 1257 1258 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3215 1261 1262 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3216 1265 1266 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3217 1269 1270 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3218 1273 1274 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3219 1277 1278 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3220 1250 1251 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3221 1254 1255 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3222 1258 1259 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3223 1262 1263 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3224 1266 1267 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3225 1270 1271 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3226 1274 1275 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3227 1278 1279 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3288 1280 1281 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3289 1292 1293 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3290 1296 1297 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3291 1308 1309 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3292 1281 1282 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3293 1293 1294 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3294 1297 1298 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3295 1309 1310 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3296 1282 1283 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3297 1294 1295 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3298 1298 1299 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3299 1310 1311 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3356 1312 1313 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3357 1316 1317 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3358 1320 1321 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3359 1324 1325 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3360 1328 1329 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3361 1332 1333 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3362 1336 1337 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3363 1340 1341 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3364 1313 1314 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3365 1317 1318 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3366 1321 1322 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3367 1325 1326 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3368 1329 1330 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3369 1333 1334 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3370 1337 1338 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3371 1341 1342 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3372 1314 1315 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3373 1318 1319 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3374 1322 1323 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3375 1326 1327 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3376 1330 1331 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3377 1334 1335 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3378 1338 1339 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3379 1342 1343 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3440 1344 1345 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3441 1356 1357 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3442 1360 1361 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3443 1372 1373 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3444 1345 1346 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3445 1357 1358 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3446 1361 1362 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3447 1373 1374 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3448 1346 1347 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3449 1358 1359 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3450 1362 1363 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3451 1374 1375 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3516 1376 1377 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3517 1380 1381 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3518 1384 1385 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3519 1388 1389 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3520 1392 1393 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3521 1396 1397 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3522 1400 1401 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3523 1404 1405 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3524 1377 1378 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3525 1381 1382 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3526 1385 1386 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3527 1389 1390 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3528 1393 1394 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3529 1397 1398 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3530 1401 1402 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3531 1405 1406 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3532 1378 1379 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3533 1382 1383 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3534 1386 1387 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3535 1390 1391 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3536 1394 1395 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3537 1398 1399 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3538 1402 1403 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3539 1406 1407 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3600 1408 1409 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3601 1420 1421 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3602 1424 1425 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3603 1436 1437 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3604 1409 1410 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3605 1421 1422 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3606 1425 1426 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3607 1437 1438 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3608 1410 1411 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3609 1422 1423 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3610 1426 1427 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3611 1438 1439 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3676 1440 1441 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3677 1444 1445 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3678 1448 1449 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3679 1452 1453 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3680 1456 1457 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3681 1460 1461 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3682 1464 1465 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3683 1468 1469 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3684 1441 1442 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3685 1445 1446 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3686 1449 1450 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3687 1453 1454 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3688 1457 1458 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3689 1461 1462 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3690 1465 1466 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3691 1469 1470 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3692 1442 1443 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3693 1446 1447 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3694 1450 1451 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3695 1454 1455 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3696 1458 1459 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3697 1462 1463 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3698 1466 1467 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3699 1470 1471 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3760 1472 1473 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3761 1484 1485 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3762 1488 1489 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3763 1500 1501 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3764 1473 1474 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3765 1485 1486 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3766 1489 1490 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3767 1501 1502 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3768 1474 1475 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3769 1486 1487 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3770 1490 1491 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3771 1502 1503 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3828 1504 1505 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3829 1508 1509 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3830 1512 1513 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3831 1516 1517 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3832 1520 1521 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3833 1524 1525 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3834 1528 1529 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3835 1532 1533 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3836 1505 1506 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3837 1509 1510 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3838 1513 1514 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3839 1517 1518 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3840 1521 1522 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3841 1525 1526 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3842 1529 1530 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3843 1533 1534 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3844 1506 1507 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3845 1510 1511 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3846 1514 1515 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3847 1518 1519 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3848 1522 1523 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3849 1526 1527 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3850 1530 1531 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3851 1534 1535 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3912 1536 1537 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3913 1548 1549 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3914 1552 1553 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3915 1564 1565 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3916 1537 1538 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3917 1549 1550 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3918 1553 1554 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3919 1565 1566 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3920 1538 1539 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3921 1550 1551 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3922 1554 1555 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3923 1566 1567 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3980 1568 1569 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3981 1572 1573 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3982 1576 1577 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3983 1580 1581 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3984 1584 1585 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3985 1588 1589 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3986 1592 1593 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3987 1596 1597 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3988 1569 1570 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3989 1573 1574 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3990 1577 1578 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3991 1581 1582 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3992 1585 1586 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3993 1589 1590 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3994 1593 1594 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3995 1597 1598 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3996 1570 1571 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3997 1574 1575 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3998 1578 1579 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 3999 1582 1583 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4000 1586 1587 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4001 1590 1591 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4002 1594 1595 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4003 1598 1599 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4064 1600 1601 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4065 1612 1613 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4066 1616 1617 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4067 1628 1629 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4068 1601 1602 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4069 1613 1614 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4070 1617 1618 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4071 1629 1630 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4072 1602 1603 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4073 1614 1615 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4074 1618 1619 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4075 1630 1631 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4128 1632 1633 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4129 1636 1637 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4130 1640 1641 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4131 1644 1645 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4132 1648 1649 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4133 1652 1653 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4134 1656 1657 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4135 1660 1661 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4136 1633 1634 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4137 1637 1638 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4138 1641 1642 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4139 1645 1646 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4140 1649 1650 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4141 1653 1654 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4142 1657 1658 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4143 1661 1662 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4144 1634 1635 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4145 1638 1639 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4146 1642 1643 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4147 1646 1647 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4148 1650 1651 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4149 1654 1655 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4150 1658 1659 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY
element elasticBeamColumn 4151 1662 1663 $A $E $G $J $Iy $Iz $beamYTransfTag
incr numBeamsY

# ===== BRACES (Diagonal Elements) =====
puts ">>> Creating braces..."
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 72 0 36 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 73 8 36 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 74 8 44 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 75 12 40 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 76 16 52 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 77 20 48 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 78 24 52 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 79 24 60 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 80 3 39 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 81 11 39 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 82 11 47 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 83 15 43 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 84 19 55 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 85 23 51 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 86 27 55 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 87 27 63 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 88 0 33 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 89 1 32 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 90 2 35 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 91 3 34 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 92 28 61 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 93 29 60 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 94 30 63 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 95 31 62 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 96 0 5 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 97 2 7 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 98 4 9 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 99 6 11 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 100 8 13 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 101 10 15 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 102 16 21 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 103 18 23 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 104 20 25 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 105 22 27 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 106 24 29 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 107 26 31 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 180 40 76 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 181 44 72 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 182 48 84 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 183 52 80 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 184 43 79 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 185 47 75 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 186 51 87 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 187 55 83 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 260 72 108 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 261 76 104 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 262 80 116 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 263 84 112 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 264 75 111 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 265 79 107 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 266 83 119 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 267 87 115 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 340 104 140 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 341 108 136 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 342 112 148 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 343 116 144 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 344 107 143 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 345 111 139 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 346 115 151 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 347 119 147 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 420 136 172 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 421 140 168 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 422 144 180 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 423 148 176 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 424 139 175 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 425 143 171 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 426 147 183 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 427 151 179 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 500 168 204 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 501 172 200 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 502 176 212 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 503 180 208 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 504 171 207 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 505 175 203 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 506 179 215 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 507 183 211 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 580 200 236 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 581 204 232 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 582 208 244 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 583 212 240 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 584 203 239 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 585 207 235 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 586 211 247 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 587 215 243 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 588 192 225 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 589 193 224 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 590 194 227 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 591 195 226 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 592 220 253 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 593 221 252 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 594 222 255 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 595 223 254 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 740 256 292 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 741 264 292 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 742 264 300 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 743 268 296 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 744 272 308 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 745 276 304 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 746 280 308 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 747 280 316 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 748 259 295 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 749 267 295 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 750 267 303 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 751 271 299 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 752 275 311 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 753 279 307 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 754 283 311 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 755 283 319 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 900 328 364 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 901 332 360 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 902 336 372 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 903 340 368 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 904 331 367 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 905 335 363 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 906 339 375 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 907 343 371 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1052 392 428 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1053 396 424 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1054 400 436 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1055 404 432 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1056 395 431 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1057 399 427 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1058 403 439 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1059 407 435 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1060 384 417 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1061 385 416 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1062 386 419 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1063 387 418 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1064 412 445 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1065 413 444 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1066 414 447 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1067 415 446 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1068 384 389 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1069 386 391 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1070 388 393 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1071 390 395 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1072 392 397 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1073 394 399 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1074 400 405 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1075 402 407 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1076 404 409 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1077 406 411 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1078 408 413 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 1079 410 415 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1224 456 492 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1225 460 488 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1226 464 500 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1227 468 496 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1228 459 495 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1229 463 491 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1230 467 503 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1231 471 499 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1376 512 548 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1377 520 548 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1378 520 556 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1379 524 552 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1380 528 564 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1381 532 560 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1382 536 564 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1383 536 572 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1384 515 551 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1385 523 551 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1386 523 559 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1387 527 555 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1388 531 567 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1389 535 563 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1390 539 567 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1391 539 575 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1536 584 620 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1537 588 616 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1538 592 628 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1539 596 624 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1540 587 623 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1541 591 619 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1542 595 631 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1543 599 627 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1544 576 609 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1545 577 608 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1546 578 611 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1547 579 610 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1548 604 637 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1549 605 636 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1550 606 639 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1551 607 638 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1696 648 684 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1697 652 680 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1698 656 692 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1699 660 688 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1700 651 687 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1701 655 683 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1702 659 695 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1703 663 691 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1848 712 748 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1849 716 744 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1850 720 756 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1851 724 752 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1852 715 751 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1853 719 747 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1854 723 759 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 1855 727 755 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2000 768 804 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2001 776 804 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2002 776 812 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2003 780 808 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2004 784 820 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2005 788 816 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2006 792 820 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2007 792 828 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2008 771 807 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2009 779 807 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2010 779 815 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2011 783 811 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2012 787 823 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2013 791 819 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2014 795 823 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2015 795 831 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2016 768 801 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2017 769 800 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2018 770 803 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2019 771 802 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2020 796 829 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2021 797 828 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2022 798 831 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2023 799 830 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2024 768 773 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2025 770 775 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2026 772 777 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2027 774 779 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2028 776 781 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2029 778 783 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2030 784 789 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2031 786 791 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2032 788 793 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2033 790 795 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2034 792 797 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2035 794 799 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2148 832 868 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2149 840 868 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2150 840 876 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2151 844 872 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2152 848 884 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2153 852 880 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2154 856 884 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2155 856 892 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2156 835 871 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2157 843 871 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2158 843 879 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2159 847 875 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2160 851 887 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2161 855 883 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2162 859 887 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2163 859 895 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2164 832 865 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2165 833 864 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2166 834 867 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2167 835 866 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2168 860 893 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2169 861 892 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2170 862 895 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2171 863 894 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2172 832 837 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2173 834 839 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2174 836 841 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2175 838 843 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2176 840 845 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2177 842 847 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2178 848 853 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2179 850 855 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2180 852 857 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2181 854 859 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2182 856 861 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 2183 858 863 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2256 872 908 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2257 876 904 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2258 880 916 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2259 884 912 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2260 875 911 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2261 879 907 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2262 883 919 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2263 887 915 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2336 904 940 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2337 908 936 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2338 912 948 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2339 916 944 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2340 907 943 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2341 911 939 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2342 915 951 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2343 919 947 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2416 936 972 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2417 940 968 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2418 944 980 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2419 948 976 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2420 939 975 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2421 943 971 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2422 947 983 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2423 951 979 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2496 968 1004 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2497 972 1000 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2498 976 1012 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2499 980 1008 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2500 971 1007 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2501 975 1003 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2502 979 1015 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2503 983 1011 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2576 1000 1036 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2577 1004 1032 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2578 1008 1044 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2579 1012 1040 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2580 1003 1039 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2581 1007 1035 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2582 1011 1047 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2583 1015 1043 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2656 1032 1068 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2657 1036 1064 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2658 1040 1076 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2659 1044 1072 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2660 1035 1071 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2661 1039 1067 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2662 1043 1079 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2663 1047 1075 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2664 1024 1057 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2665 1025 1056 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2666 1026 1059 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2667 1027 1058 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2668 1052 1085 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2669 1053 1084 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2670 1054 1087 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2671 1055 1086 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2816 1088 1124 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2817 1096 1124 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2818 1096 1132 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2819 1100 1128 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2820 1104 1140 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2821 1108 1136 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2822 1112 1140 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2823 1112 1148 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2824 1091 1127 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2825 1099 1127 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2826 1099 1135 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2827 1103 1131 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2828 1107 1143 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2829 1111 1139 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2830 1115 1143 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2831 1115 1151 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2976 1160 1196 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2977 1164 1192 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2978 1168 1204 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2979 1172 1200 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2980 1163 1199 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2981 1167 1195 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2982 1171 1207 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 2983 1175 1203 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3128 1224 1260 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3129 1228 1256 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3130 1232 1268 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3131 1236 1264 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3132 1227 1263 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3133 1231 1259 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3134 1235 1271 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3135 1239 1267 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3136 1216 1249 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3137 1217 1248 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3138 1218 1251 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3139 1219 1250 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3140 1244 1277 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3141 1245 1276 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3142 1246 1279 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3143 1247 1278 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3144 1216 1221 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3145 1218 1223 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3146 1220 1225 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3147 1222 1227 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3148 1224 1229 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3149 1226 1231 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3150 1232 1237 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3151 1234 1239 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3152 1236 1241 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3153 1238 1243 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3154 1240 1245 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 3155 1242 1247 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3300 1288 1324 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3301 1292 1320 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3302 1296 1332 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3303 1300 1328 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3304 1291 1327 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3305 1295 1323 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3306 1299 1335 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3307 1303 1331 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3452 1344 1380 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3453 1352 1380 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3454 1352 1388 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3455 1356 1384 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3456 1360 1396 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3457 1364 1392 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3458 1368 1396 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3459 1368 1404 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3460 1347 1383 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3461 1355 1383 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3462 1355 1391 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3463 1359 1387 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3464 1363 1399 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3465 1367 1395 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3466 1371 1399 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3467 1371 1407 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3612 1416 1452 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3613 1420 1448 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3614 1424 1460 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3615 1428 1456 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3616 1419 1455 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3617 1423 1451 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3618 1427 1463 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3619 1431 1459 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3620 1408 1441 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3621 1409 1440 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3622 1410 1443 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3623 1411 1442 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3624 1436 1469 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3625 1437 1468 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3626 1438 1471 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3627 1439 1470 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3772 1480 1516 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3773 1484 1512 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3774 1488 1524 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3775 1492 1520 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3776 1483 1519 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3777 1487 1515 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3778 1491 1527 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3779 1495 1523 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3924 1544 1580 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3925 1548 1576 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3926 1552 1588 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3927 1556 1584 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3928 1547 1583 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3929 1551 1579 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3930 1555 1591 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 3931 1559 1587 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4076 1600 1636 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4077 1608 1636 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4078 1608 1644 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4079 1612 1640 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4080 1616 1652 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4081 1620 1648 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4082 1624 1652 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4083 1624 1660 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4084 1603 1639 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4085 1611 1639 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4086 1611 1647 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4087 1615 1643 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4088 1619 1655 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4089 1623 1651 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4090 1627 1655 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4091 1627 1663 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4092 1600 1633 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4093 1601 1632 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4094 1602 1635 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4095 1603 1634 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4096 1628 1661 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4097 1629 1660 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4098 1630 1663 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4099 1631 1662 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4100 1600 1605 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4101 1602 1607 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4102 1604 1609 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4103 1606 1611 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4104 1608 1613 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4105 1610 1615 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4106 1616 1621 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4107 1618 1623 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4108 1620 1625 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4109 1622 1627 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4110 1624 1629 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4111 1626 1631 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4152 171 1664 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4153 183 1665 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4154 1664 1665 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4155 1664 1000 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4156 1665 1012 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4157 203 1666 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4158 215 1667 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4159 1666 1667 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4160 1666 1032 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4161 1667 1044 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4162 1664 1666 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4163 1665 1667 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4164 171 1666 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4165 1664 203 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4166 1664 1032 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4167 1000 1666 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4168 183 1667 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4169 1665 215 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4170 1665 1044 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4171 1012 1667 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4172 171 1012 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4173 1000 183 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4174 203 1044 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4175 1032 215 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4176 363 1668 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4177 375 1669 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4178 1668 1669 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4179 1668 1192 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4180 1669 1204 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4181 395 1670 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4182 407 1671 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4183 1670 1671 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4184 1670 1224 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4185 1671 1236 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4186 1668 1670 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4187 1669 1671 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4188 363 1670 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4189 1668 395 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4190 1668 1224 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4191 1192 1670 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4192 375 1671 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4193 1669 407 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4194 1669 1236 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4195 1204 1671 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4196 363 1204 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4197 1192 375 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4198 395 1236 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4199 1224 407 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4200 555 1672 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4201 567 1673 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4202 1672 1673 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4203 1672 1384 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4204 1673 1396 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4205 587 1674 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4206 599 1675 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4207 1674 1675 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4208 1674 1416 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4209 1675 1428 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4210 1672 1674 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4211 1673 1675 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4212 555 1674 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4213 1672 587 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4214 1672 1416 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4215 1384 1674 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4216 567 1675 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4217 1673 599 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4218 1673 1428 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4219 1396 1675 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4220 555 1396 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4221 1384 567 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4222 587 1428 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4223 1416 599 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4224 747 1676 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4225 759 1677 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4226 1676 1677 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4227 1676 1576 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4228 1677 1588 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4229 811 1678 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4230 823 1679 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4231 1678 1679 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4232 1678 1640 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4233 1679 1652 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4234 1676 1678 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4235 1677 1679 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4236 747 1678 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4237 1676 811 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4238 1676 1640 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4239 1576 1678 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4240 759 1679 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4241 1677 823 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4242 1677 1652 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 1 0
element elasticBeamColumn 4243 1588 1679 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4244 747 1588 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4245 1576 759 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4246 811 1652 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces
geomTransf Linear $braceTransfTag 0 0 1
element elasticBeamColumn 4247 1640 823 $A $E $G $J $Iy $Iz $braceTransfTag
incr braceTransfTag
incr numBraces

set numElements [expr $numColumns + $numBeamsX + $numBeamsY + $numBraces]
puts ""
puts ">>> Element Summary:"
puts "    Columns:    $numColumns"
puts "    Beams (X):  $numBeamsX"
puts "    Beams (Y):  $numBeamsY"
puts "    Braces:     $numBraces"
puts "    TOTAL:      $numElements"

# ============================================================================
# MASS ASSIGNMENT
# ============================================================================
puts ""
puts ">>> Assigning nodal masses..."

set floorMass 1.6       ;# kg per floor (distributed to all nodes)
set roofMass 2.22       ;# kg for roof floor
set g 981.0             ;# cm/s2


# Floor 1 mass assignment (64 nodes)
mass 32 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 33 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 34 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 35 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 36 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 37 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 38 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 39 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 40 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 41 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 42 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 43 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 44 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 45 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 46 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 47 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 48 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 49 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 50 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 51 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 52 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 53 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 54 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 55 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 56 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 57 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 58 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 59 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 60 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 61 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 62 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 63 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 864 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 865 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 866 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 867 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 868 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 869 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 870 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 871 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 872 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 873 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 874 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 875 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 876 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 877 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 878 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 879 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 880 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 881 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 882 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 883 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 884 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 885 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 886 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 887 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 888 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 889 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 890 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 891 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 892 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 893 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 894 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 895 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 2 mass assignment (64 nodes)
mass 64 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 65 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 66 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 67 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 68 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 69 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 70 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 71 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 72 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 73 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 74 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 75 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 76 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 77 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 78 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 79 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 80 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 81 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 82 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 83 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 84 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 85 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 86 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 87 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 88 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 89 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 90 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 91 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 92 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 93 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 94 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 95 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 896 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 897 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 898 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 899 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 900 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 901 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 902 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 903 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 904 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 905 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 906 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 907 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 908 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 909 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 910 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 911 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 912 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 913 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 914 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 915 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 916 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 917 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 918 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 919 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 920 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 921 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 922 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 923 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 924 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 925 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 926 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 927 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 3 mass assignment (64 nodes)
mass 96 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 97 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 98 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 99 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 100 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 101 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 102 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 103 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 104 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 105 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 106 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 107 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 108 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 109 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 110 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 111 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 112 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 113 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 114 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 115 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 116 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 117 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 118 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 119 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 120 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 121 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 122 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 123 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 124 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 125 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 126 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 127 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 928 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 929 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 930 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 931 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 932 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 933 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 934 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 935 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 936 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 937 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 938 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 939 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 940 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 941 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 942 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 943 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 944 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 945 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 946 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 947 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 948 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 949 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 950 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 951 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 952 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 953 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 954 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 955 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 956 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 957 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 958 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 959 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 4 mass assignment (64 nodes)
mass 128 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 129 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 130 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 131 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 132 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 133 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 134 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 135 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 136 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 137 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 138 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 139 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 140 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 141 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 142 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 143 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 144 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 145 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 146 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 147 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 148 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 149 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 150 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 151 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 152 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 153 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 154 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 155 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 156 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 157 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 158 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 159 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 960 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 961 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 962 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 963 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 964 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 965 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 966 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 967 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 968 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 969 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 970 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 971 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 972 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 973 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 974 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 975 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 976 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 977 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 978 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 979 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 980 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 981 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 982 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 983 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 984 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 985 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 986 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 987 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 988 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 989 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 990 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 991 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 5 mass assignment (66 nodes)
mass 160 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 161 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 162 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 163 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 164 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 165 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 166 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 167 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 168 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 169 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 170 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 171 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 172 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 173 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 174 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 175 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 176 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 177 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 178 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 179 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 180 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 181 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 182 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 183 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 184 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 185 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 186 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 187 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 188 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 189 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 190 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 191 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 992 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 993 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 994 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 995 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 996 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 997 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 998 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 999 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1000 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1001 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1002 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1003 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1004 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1005 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1006 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1007 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1008 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1009 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1010 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1011 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1012 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1013 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1014 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1015 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1016 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1017 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1018 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1019 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1020 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1021 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1022 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1023 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1664 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1665 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242

# Floor 6 mass assignment (66 nodes)
mass 192 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 193 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 194 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 195 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 196 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 197 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 198 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 199 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 200 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 201 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 202 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 203 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 204 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 205 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 206 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 207 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 208 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 209 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 210 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 211 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 212 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 213 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 214 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 215 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 216 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 217 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 218 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 219 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 220 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 221 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 222 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 223 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1024 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1025 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1026 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1027 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1028 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1029 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1030 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1031 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1032 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1033 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1034 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1035 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1036 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1037 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1038 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1039 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1040 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1041 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1042 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1043 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1044 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1045 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1046 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1047 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1048 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1049 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1050 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1051 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1052 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1053 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1054 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1055 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1666 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1667 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242

# Floor 7 mass assignment (64 nodes)
mass 224 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 225 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 226 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 227 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 228 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 229 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 230 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 231 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 232 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 233 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 234 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 235 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 236 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 237 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 238 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 239 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 240 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 241 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 242 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 243 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 244 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 245 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 246 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 247 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 248 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 249 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 250 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 251 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 252 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 253 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 254 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 255 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1056 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1057 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1058 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1059 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1060 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1061 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1062 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1063 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1064 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1065 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1066 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1067 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1068 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1069 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1070 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1071 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1072 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1073 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1074 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1075 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1076 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1077 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1078 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1079 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1080 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1081 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1082 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1083 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1084 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1085 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1086 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1087 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 8 mass assignment (64 nodes)
mass 256 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 257 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 258 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 259 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 260 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 261 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 262 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 263 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 264 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 265 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 266 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 267 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 268 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 269 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 270 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 271 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 272 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 273 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 274 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 275 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 276 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 277 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 278 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 279 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 280 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 281 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 282 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 283 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 284 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 285 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 286 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 287 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1088 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1089 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1090 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1091 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1092 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1093 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1094 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1095 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1096 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1097 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1098 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1099 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1100 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1101 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1102 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1103 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1104 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1105 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1106 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1107 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1108 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1109 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1110 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1111 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1112 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1113 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1114 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1115 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1116 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1117 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1118 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1119 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 9 mass assignment (64 nodes)
mass 288 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 289 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 290 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 291 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 292 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 293 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 294 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 295 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 296 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 297 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 298 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 299 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 300 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 301 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 302 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 303 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 304 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 305 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 306 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 307 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 308 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 309 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 310 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 311 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 312 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 313 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 314 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 315 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 316 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 317 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 318 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 319 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1120 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1121 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1122 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1123 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1124 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1125 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1126 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1127 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1128 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1129 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1130 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1131 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1132 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1133 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1134 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1135 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1136 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1137 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1138 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1139 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1140 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1141 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1142 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1143 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1144 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1145 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1146 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1147 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1148 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1149 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1150 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1151 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 10 mass assignment (64 nodes)
mass 320 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 321 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 322 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 323 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 324 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 325 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 326 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 327 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 328 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 329 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 330 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 331 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 332 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 333 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 334 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 335 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 336 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 337 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 338 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 339 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 340 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 341 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 342 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 343 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 344 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 345 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 346 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 347 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 348 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 349 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 350 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 351 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1152 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1153 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1154 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1155 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1156 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1157 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1158 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1159 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1160 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1161 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1162 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1163 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1164 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1165 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1166 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1167 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1168 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1169 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1170 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1171 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1172 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1173 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1174 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1175 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1176 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1177 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1178 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1179 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1180 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1181 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1182 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1183 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 11 mass assignment (66 nodes)
mass 352 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 353 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 354 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 355 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 356 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 357 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 358 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 359 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 360 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 361 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 362 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 363 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 364 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 365 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 366 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 367 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 368 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 369 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 370 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 371 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 372 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 373 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 374 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 375 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 376 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 377 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 378 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 379 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 380 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 381 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 382 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 383 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1184 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1185 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1186 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1187 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1188 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1189 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1190 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1191 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1192 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1193 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1194 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1195 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1196 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1197 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1198 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1199 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1200 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1201 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1202 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1203 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1204 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1205 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1206 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1207 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1208 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1209 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1210 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1211 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1212 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1213 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1214 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1215 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1668 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1669 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242

# Floor 12 mass assignment (66 nodes)
mass 384 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 385 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 386 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 387 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 388 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 389 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 390 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 391 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 392 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 393 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 394 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 395 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 396 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 397 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 398 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 399 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 400 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 401 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 402 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 403 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 404 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 405 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 406 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 407 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 408 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 409 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 410 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 411 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 412 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 413 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 414 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 415 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1216 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1217 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1218 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1219 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1220 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1221 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1222 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1223 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1224 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1225 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1226 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1227 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1228 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1229 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1230 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1231 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1232 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1233 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1234 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1235 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1236 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1237 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1238 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1239 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1240 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1241 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1242 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1243 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1244 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1245 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1246 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1247 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1670 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1671 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242

# Floor 13 mass assignment (64 nodes)
mass 416 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 417 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 418 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 419 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 420 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 421 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 422 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 423 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 424 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 425 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 426 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 427 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 428 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 429 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 430 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 431 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 432 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 433 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 434 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 435 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 436 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 437 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 438 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 439 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 440 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 441 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 442 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 443 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 444 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 445 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 446 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 447 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1248 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1249 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1250 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1251 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1252 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1253 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1254 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1255 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1256 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1257 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1258 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1259 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1260 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1261 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1262 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1263 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1264 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1265 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1266 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1267 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1268 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1269 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1270 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1271 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1272 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1273 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1274 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1275 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1276 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1277 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1278 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1279 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 14 mass assignment (64 nodes)
mass 448 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 449 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 450 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 451 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 452 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 453 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 454 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 455 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 456 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 457 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 458 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 459 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 460 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 461 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 462 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 463 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 464 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 465 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 466 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 467 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 468 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 469 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 470 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 471 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 472 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 473 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 474 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 475 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 476 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 477 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 478 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 479 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1280 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1281 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1282 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1283 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1284 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1285 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1286 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1287 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1288 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1289 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1290 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1291 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1292 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1293 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1294 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1295 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1296 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1297 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1298 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1299 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1300 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1301 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1302 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1303 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1304 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1305 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1306 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1307 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1308 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1309 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1310 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1311 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 15 mass assignment (64 nodes)
mass 480 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 481 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 482 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 483 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 484 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 485 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 486 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 487 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 488 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 489 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 490 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 491 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 492 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 493 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 494 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 495 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 496 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 497 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 498 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 499 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 500 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 501 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 502 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 503 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 504 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 505 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 506 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 507 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 508 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 509 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 510 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 511 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1312 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1313 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1314 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1315 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1316 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1317 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1318 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1319 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1320 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1321 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1322 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1323 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1324 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1325 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1326 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1327 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1328 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1329 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1330 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1331 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1332 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1333 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1334 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1335 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1336 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1337 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1338 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1339 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1340 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1341 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1342 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1343 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 16 mass assignment (64 nodes)
mass 512 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 513 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 514 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 515 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 516 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 517 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 518 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 519 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 520 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 521 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 522 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 523 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 524 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 525 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 526 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 527 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 528 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 529 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 530 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 531 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 532 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 533 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 534 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 535 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 536 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 537 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 538 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 539 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 540 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 541 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 542 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 543 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1344 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1345 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1346 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1347 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1348 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1349 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1350 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1351 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1352 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1353 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1354 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1355 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1356 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1357 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1358 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1359 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1360 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1361 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1362 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1363 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1364 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1365 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1366 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1367 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1368 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1369 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1370 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1371 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1372 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1373 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1374 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1375 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 17 mass assignment (66 nodes)
mass 544 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 545 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 546 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 547 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 548 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 549 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 550 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 551 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 552 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 553 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 554 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 555 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 556 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 557 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 558 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 559 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 560 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 561 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 562 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 563 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 564 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 565 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 566 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 567 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 568 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 569 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 570 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 571 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 572 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 573 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 574 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 575 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1376 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1377 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1378 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1379 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1380 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1381 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1382 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1383 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1384 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1385 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1386 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1387 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1388 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1389 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1390 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1391 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1392 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1393 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1394 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1395 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1396 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1397 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1398 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1399 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1400 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1401 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1402 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1403 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1404 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1405 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1406 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1407 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1672 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1673 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242

# Floor 18 mass assignment (66 nodes)
mass 576 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 577 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 578 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 579 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 580 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 581 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 582 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 583 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 584 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 585 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 586 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 587 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 588 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 589 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 590 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 591 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 592 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 593 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 594 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 595 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 596 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 597 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 598 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 599 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 600 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 601 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 602 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 603 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 604 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 605 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 606 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 607 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1408 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1409 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1410 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1411 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1412 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1413 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1414 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1415 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1416 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1417 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1418 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1419 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1420 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1421 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1422 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1423 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1424 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1425 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1426 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1427 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1428 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1429 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1430 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1431 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1432 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1433 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1434 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1435 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1436 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1437 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1438 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1439 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1674 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1675 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242

# Floor 19 mass assignment (64 nodes)
mass 608 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 609 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 610 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 611 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 612 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 613 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 614 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 615 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 616 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 617 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 618 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 619 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 620 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 621 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 622 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 623 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 624 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 625 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 626 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 627 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 628 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 629 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 630 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 631 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 632 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 633 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 634 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 635 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 636 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 637 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 638 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 639 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1440 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1441 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1442 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1443 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1444 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1445 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1446 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1447 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1448 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1449 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1450 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1451 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1452 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1453 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1454 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1455 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1456 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1457 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1458 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1459 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1460 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1461 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1462 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1463 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1464 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1465 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1466 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1467 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1468 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1469 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1470 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1471 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 20 mass assignment (64 nodes)
mass 640 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 641 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 642 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 643 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 644 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 645 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 646 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 647 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 648 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 649 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 650 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 651 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 652 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 653 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 654 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 655 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 656 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 657 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 658 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 659 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 660 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 661 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 662 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 663 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 664 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 665 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 666 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 667 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 668 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 669 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 670 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 671 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1472 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1473 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1474 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1475 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1476 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1477 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1478 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1479 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1480 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1481 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1482 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1483 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1484 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1485 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1486 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1487 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1488 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1489 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1490 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1491 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1492 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1493 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1494 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1495 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1496 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1497 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1498 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1499 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1500 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1501 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1502 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1503 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 21 mass assignment (64 nodes)
mass 672 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 673 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 674 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 675 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 676 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 677 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 678 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 679 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 680 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 681 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 682 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 683 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 684 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 685 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 686 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 687 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 688 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 689 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 690 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 691 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 692 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 693 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 694 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 695 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 696 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 697 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 698 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 699 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 700 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 701 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 702 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 703 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1504 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1505 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1506 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1507 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1508 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1509 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1510 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1511 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1512 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1513 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1514 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1515 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1516 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1517 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1518 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1519 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1520 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1521 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1522 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1523 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1524 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1525 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1526 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1527 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1528 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1529 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1530 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1531 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1532 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1533 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1534 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1535 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 22 mass assignment (64 nodes)
mass 704 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 705 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 706 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 707 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 708 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 709 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 710 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 711 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 712 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 713 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 714 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 715 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 716 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 717 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 718 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 719 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 720 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 721 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 722 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 723 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 724 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 725 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 726 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 727 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 728 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 729 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 730 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 731 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 732 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 733 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 734 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 735 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1536 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1537 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1538 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1539 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1540 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1541 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1542 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1543 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1544 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1545 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1546 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1547 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1548 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1549 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1550 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1551 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1552 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1553 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1554 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1555 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1556 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1557 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1558 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1559 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1560 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1561 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1562 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1563 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1564 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1565 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1566 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1567 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 23 mass assignment (66 nodes)
mass 736 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 737 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 738 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 739 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 740 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 741 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 742 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 743 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 744 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 745 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 746 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 747 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 748 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 749 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 750 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 751 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 752 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 753 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 754 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 755 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 756 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 757 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 758 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 759 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 760 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 761 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 762 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 763 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 764 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 765 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 766 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 767 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1568 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1569 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1570 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1571 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1572 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1573 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1574 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1575 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1576 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1577 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1578 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1579 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1580 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1581 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1582 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1583 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1584 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1585 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1586 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1587 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1588 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1589 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1590 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1591 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1592 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1593 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1594 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1595 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1596 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1597 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1598 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1599 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1676 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242
mass 1677 0.02424242 0.02424242 0.00242424 0.00024242 0.00024242 0.00024242

# Floor 24 mass assignment (64 nodes)
mass 768 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 769 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 770 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 771 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 772 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 773 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 774 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 775 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 776 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 777 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 778 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 779 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 780 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 781 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 782 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 783 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 784 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 785 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 786 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 787 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 788 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 789 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 790 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 791 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 792 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 793 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 794 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 795 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 796 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 797 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 798 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 799 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1600 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1601 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1602 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1603 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1604 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1605 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1606 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1607 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1608 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1609 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1610 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1611 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1612 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1613 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1614 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1615 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1616 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1617 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1618 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1619 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1620 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1621 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1622 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1623 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1624 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1625 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1626 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1627 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1628 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1629 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1630 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000
mass 1631 0.02500000 0.02500000 0.00250000 0.00025000 0.00025000 0.00025000

# Floor 25 mass assignment (66 nodes)
mass 800 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 801 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 802 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 803 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 804 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 805 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 806 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 807 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 808 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 809 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 810 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 811 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 812 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 813 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 814 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 815 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 816 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 817 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 818 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 819 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 820 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 821 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 822 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 823 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 824 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 825 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 826 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 827 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 828 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 829 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 830 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 831 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1632 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1633 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1634 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1635 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1636 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1637 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1638 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1639 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1640 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1641 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1642 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1643 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1644 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1645 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1646 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1647 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1648 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1649 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1650 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1651 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1652 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1653 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1654 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1655 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1656 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1657 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1658 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1659 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1660 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1661 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1662 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1663 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1678 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636
mass 1679 0.03363636 0.03363636 0.00336364 0.00033636 0.00033636 0.00033636

puts ">>> Mass assignment completed"

# ============================================================================
# EIGENVALUE ANALYSIS
# ============================================================================
puts ""
puts "============================================================"
puts "  EIGENVALUE ANALYSIS"
puts "============================================================"

set numModes 12
puts ">>> Computing $numModes eigenvalues..."

set eigenValues [eigen -fullGenLapack $numModes]

puts ""
puts ">>> Modal Analysis Results:"
puts "============================================================"
puts [format "%4s %14s %14s %10s %15s" "Mode" "Period (s)" "Freq (Hz)" "Sae (g)" "Region"]
puts "------------------------------------------------------------"

set pi 3.14159265359

for {set i 0} {$i < $numModes} {incr i} {
    set eigenValue [lindex $eigenValues $i]
    set omega [expr sqrt($eigenValue)]
    set freq [expr $omega / (2.0 * $pi)]
    set period [expr 1.0 / $freq]

    # Calculate Sae according to TBDY 2018
    if {$period < $TA} {
        set Sae [expr (0.4 + 0.6 * $period / $TA) * $SDS]
        set region "Ascending"
    } elseif {$period <= $TB} {
        set Sae $SDS
        set region "Plateau"
    } else {
        set Sae [expr $SD1 / $period]
        set region "Descending"
    }

    puts [format "%4d %14.6f %14.4f %10.4f %15s" [expr $i+1] $period $freq $Sae $region]

    # Store first mode period
    if {$i == 0} {
        set T1 $period
    }
}

puts "------------------------------------------------------------"
puts ""
puts ">>> Fundamental Period T1 = $T1 s"

# Calculate Ra (Response Modification Factor)
if {$T1 > $TB} {
    set Ra [expr $R / $I]
} else {
    set Ra [expr $D + ($R / $I - $D) * $T1 / $TB]
}
puts ">>> Response Modification Factor Ra = $Ra"

# Calculate SaR (Reduced Design Spectral Acceleration)
if {$T1 < $TA} {
    set Sae_T1 [expr (0.4 + 0.6 * $T1 / $TA) * $SDS]
} elseif {$T1 <= $TB} {
    set Sae_T1 $SDS
} else {
    set Sae_T1 [expr $SD1 / $T1]
}
set SaR [expr $Sae_T1 / $Ra]
puts ">>> Sae(T1) = $Sae_T1 g"
puts ">>> SaR(T1) = $SaR g"

# ============================================================================
# EQUIVALENT LATERAL FORCE METHOD (TBDY 2018 Section 4.7)
# ============================================================================
puts ""
puts "============================================================"
puts "  EQUIVALENT LATERAL FORCE METHOD"
puts "  TBDY 2018 Section 4.7"
puts "============================================================"

# Total mass
set totalMass 40.6200  ;# Total mass (kg)

# Base shear force (TBDY 2018 Eq. 4.19)
set Vt [expr $totalMass * $SaR * $g / 1000.0]  ;# kN
set Vt_min [expr 0.04 * $totalMass * $I * $SDS * $g / 1000.0]
if {$Vt < $Vt_min} {
    set Vt $Vt_min
}
puts ">>> Total Base Shear Vt = $Vt kN"

# Additional force at top (TBDY 2018 Eq. 4.22)
set N 25  ;# Number of floors

set dF_NE [expr 0.0075 * $N * $Vt]
puts ">>> Additional Top Force dF_NE = $dF_NE kN"

# ============================================================================
# A1a TORSIONAL IRREGULARITY ANALYSIS
# ============================================================================
puts ""
puts "============================================================"
puts "  A1a TORSIONAL IRREGULARITY ANALYSIS"
puts "  TBDY 2018 Section 3.6.2.1 and 4.7.4"
puts "============================================================"
puts ""
puts ">>> Analyzing torsional irregularity with +/- 5% eccentricity..."
puts ""

# Floor geometry data
set floor1_z 9.00
set floor1_Lx 30.00
set floor1_Ly 40.00
set floor1_ex 1.5000
set floor1_ey 2.0000
set floor2_z 15.00
set floor2_Lx 30.00
set floor2_Ly 40.00
set floor2_ex 1.5000
set floor2_ey 2.0000
set floor3_z 21.00
set floor3_Lx 30.00
set floor3_Ly 40.00
set floor3_ex 1.5000
set floor3_ey 2.0000
set floor4_z 27.00
set floor4_Lx 30.00
set floor4_Ly 40.00
set floor4_ex 1.5000
set floor4_ey 2.0000
set floor5_z 33.00
set floor5_Lx 30.00
set floor5_Ly 40.00
set floor5_ex 1.5000
set floor5_ey 2.0000
set floor6_z 39.00
set floor6_Lx 30.00
set floor6_Ly 40.00
set floor6_ex 1.5000
set floor6_ey 2.0000
set floor7_z 45.00
set floor7_Lx 30.00
set floor7_Ly 40.00
set floor7_ex 1.5000
set floor7_ey 2.0000
set floor8_z 51.00
set floor8_Lx 30.00
set floor8_Ly 40.00
set floor8_ex 1.5000
set floor8_ey 2.0000
set floor9_z 57.00
set floor9_Lx 30.00
set floor9_Ly 40.00
set floor9_ex 1.5000
set floor9_ey 2.0000
set floor10_z 63.00
set floor10_Lx 30.00
set floor10_Ly 40.00
set floor10_ex 1.5000
set floor10_ey 2.0000
set floor11_z 69.00
set floor11_Lx 30.00
set floor11_Ly 40.00
set floor11_ex 1.5000
set floor11_ey 2.0000
set floor12_z 75.00
set floor12_Lx 30.00
set floor12_Ly 40.00
set floor12_ex 1.5000
set floor12_ey 2.0000
set floor13_z 81.00
set floor13_Lx 30.00
set floor13_Ly 40.00
set floor13_ex 1.5000
set floor13_ey 2.0000
set floor14_z 87.00
set floor14_Lx 30.00
set floor14_Ly 40.00
set floor14_ex 1.5000
set floor14_ey 2.0000
set floor15_z 93.00
set floor15_Lx 30.00
set floor15_Ly 40.00
set floor15_ex 1.5000
set floor15_ey 2.0000
set floor16_z 99.00
set floor16_Lx 30.00
set floor16_Ly 40.00
set floor16_ex 1.5000
set floor16_ey 2.0000
set floor17_z 105.00
set floor17_Lx 30.00
set floor17_Ly 40.00
set floor17_ex 1.5000
set floor17_ey 2.0000
set floor18_z 111.00
set floor18_Lx 30.00
set floor18_Ly 40.00
set floor18_ex 1.5000
set floor18_ey 2.0000
set floor19_z 117.00
set floor19_Lx 30.00
set floor19_Ly 40.00
set floor19_ex 1.5000
set floor19_ey 2.0000
set floor20_z 123.00
set floor20_Lx 30.00
set floor20_Ly 40.00
set floor20_ex 1.5000
set floor20_ey 2.0000
set floor21_z 129.00
set floor21_Lx 30.00
set floor21_Ly 40.00
set floor21_ex 1.5000
set floor21_ey 2.0000
set floor22_z 135.00
set floor22_Lx 30.00
set floor22_Ly 40.00
set floor22_ex 1.5000
set floor22_ey 2.0000
set floor23_z 141.00
set floor23_Lx 30.00
set floor23_Ly 40.00
set floor23_ex 1.5000
set floor23_ey 2.0000
set floor24_z 147.00
set floor24_Lx 30.00
set floor24_Ly 40.00
set floor24_ex 1.5000
set floor24_ey 2.0000
set floor25_z 153.00
set floor25_Lx 30.00
set floor25_Ly 40.00
set floor25_ex 1.5000
set floor25_ey 2.0000


# Function to calculate eta_bi
proc calculateEtaBi {deltaMax deltaMin} {
    set deltaOrt [expr 0.5 * ($deltaMax + $deltaMin)]
    if {$deltaOrt > 1e-10} {
        return [expr $deltaMax / $deltaOrt]
    } else {
        return 1.0
    }
}

# Function to calculate D_bi (TBDY 2018 Eq. 4.29)
proc calculateDbi {eta} {
    if {$eta <= 1.2} {
        return 1.0
    } else {
        return [expr pow($eta / 1.2, 2)]
    }
}

# Store results
set results {}

# Loop through directions and eccentricity signs
foreach direction {X Y} {
    foreach eccSign {+1 -1} {

        puts ">>> Direction: $direction, Eccentricity: [expr $eccSign * 5]%"

        # Reset for new analysis
        remove loadPattern 1

        # Define load pattern
        timeSeries Linear 1
        pattern Plain 1 1 {

            # Loads will be applied based on direction and eccentricity
        }

        # Static analysis
        system BandSPD
        numberer RCM
        constraints Plain
        integrator LoadControl 1.0
        algorithm Linear
        analysis Static

        set ok [analyze 1]

        if {$ok != 0} {
            puts "WARNING: Analysis did not converge!"
        }

        # Extract displacements and calculate eta_bi for each floor
        puts ""
        puts [format "%4s %12s %12s %12s %8s %8s %18s" "Flr" "d_max" "d_min" "d_ort" "eta_bi" "D_bi" "Status"]
        puts "--------------------------------------------------------------------------------"


        # Floor 1
        set floor1_nodes {32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 864 865 866 867 868 869 870 871 872 873 874 875 876 877 878 879 880 881 882 883 884 885 886 887 888 889 890 891 892 893 894 895}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor1_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 1 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 1 $direction $eccSign $eta $Dbi $status]

        # Floor 2
        set floor2_nodes {64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 896 897 898 899 900 901 902 903 904 905 906 907 908 909 910 911 912 913 914 915 916 917 918 919 920 921 922 923 924 925 926 927}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor2_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 2 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 2 $direction $eccSign $eta $Dbi $status]

        # Floor 3
        set floor3_nodes {96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 928 929 930 931 932 933 934 935 936 937 938 939 940 941 942 943 944 945 946 947 948 949 950 951 952 953 954 955 956 957 958 959}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor3_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 3 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 3 $direction $eccSign $eta $Dbi $status]

        # Floor 4
        set floor4_nodes {128 129 130 131 132 133 134 135 136 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 155 156 157 158 159 960 961 962 963 964 965 966 967 968 969 970 971 972 973 974 975 976 977 978 979 980 981 982 983 984 985 986 987 988 989 990 991}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor4_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 4 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 4 $direction $eccSign $eta $Dbi $status]

        # Floor 5
        set floor5_nodes {160 161 162 163 164 165 166 167 168 169 170 171 172 173 174 175 176 177 178 179 180 181 182 183 184 185 186 187 188 189 190 191 992 993 994 995 996 997 998 999 1000 1001 1002 1003 1004 1005 1006 1007 1008 1009 1010 1011 1012 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1664 1665}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor5_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 5 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 5 $direction $eccSign $eta $Dbi $status]

        # Floor 6
        set floor6_nodes {192 193 194 195 196 197 198 199 200 201 202 203 204 205 206 207 208 209 210 211 212 213 214 215 216 217 218 219 220 221 222 223 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033 1034 1035 1036 1037 1038 1039 1040 1041 1042 1043 1044 1045 1046 1047 1048 1049 1050 1051 1052 1053 1054 1055 1666 1667}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor6_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 6 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 6 $direction $eccSign $eta $Dbi $status]

        # Floor 7
        set floor7_nodes {224 225 226 227 228 229 230 231 232 233 234 235 236 237 238 239 240 241 242 243 244 245 246 247 248 249 250 251 252 253 254 255 1056 1057 1058 1059 1060 1061 1062 1063 1064 1065 1066 1067 1068 1069 1070 1071 1072 1073 1074 1075 1076 1077 1078 1079 1080 1081 1082 1083 1084 1085 1086 1087}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor7_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 7 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 7 $direction $eccSign $eta $Dbi $status]

        # Floor 8
        set floor8_nodes {256 257 258 259 260 261 262 263 264 265 266 267 268 269 270 271 272 273 274 275 276 277 278 279 280 281 282 283 284 285 286 287 1088 1089 1090 1091 1092 1093 1094 1095 1096 1097 1098 1099 1100 1101 1102 1103 1104 1105 1106 1107 1108 1109 1110 1111 1112 1113 1114 1115 1116 1117 1118 1119}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor8_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 8 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 8 $direction $eccSign $eta $Dbi $status]

        # Floor 9
        set floor9_nodes {288 289 290 291 292 293 294 295 296 297 298 299 300 301 302 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 318 319 1120 1121 1122 1123 1124 1125 1126 1127 1128 1129 1130 1131 1132 1133 1134 1135 1136 1137 1138 1139 1140 1141 1142 1143 1144 1145 1146 1147 1148 1149 1150 1151}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor9_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 9 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 9 $direction $eccSign $eta $Dbi $status]

        # Floor 10
        set floor10_nodes {320 321 322 323 324 325 326 327 328 329 330 331 332 333 334 335 336 337 338 339 340 341 342 343 344 345 346 347 348 349 350 351 1152 1153 1154 1155 1156 1157 1158 1159 1160 1161 1162 1163 1164 1165 1166 1167 1168 1169 1170 1171 1172 1173 1174 1175 1176 1177 1178 1179 1180 1181 1182 1183}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor10_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 10 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 10 $direction $eccSign $eta $Dbi $status]

        # Floor 11
        set floor11_nodes {352 353 354 355 356 357 358 359 360 361 362 363 364 365 366 367 368 369 370 371 372 373 374 375 376 377 378 379 380 381 382 383 1184 1185 1186 1187 1188 1189 1190 1191 1192 1193 1194 1195 1196 1197 1198 1199 1200 1201 1202 1203 1204 1205 1206 1207 1208 1209 1210 1211 1212 1213 1214 1215 1668 1669}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor11_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 11 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 11 $direction $eccSign $eta $Dbi $status]

        # Floor 12
        set floor12_nodes {384 385 386 387 388 389 390 391 392 393 394 395 396 397 398 399 400 401 402 403 404 405 406 407 408 409 410 411 412 413 414 415 1216 1217 1218 1219 1220 1221 1222 1223 1224 1225 1226 1227 1228 1229 1230 1231 1232 1233 1234 1235 1236 1237 1238 1239 1240 1241 1242 1243 1244 1245 1246 1247 1670 1671}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor12_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 12 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 12 $direction $eccSign $eta $Dbi $status]

        # Floor 13
        set floor13_nodes {416 417 418 419 420 421 422 423 424 425 426 427 428 429 430 431 432 433 434 435 436 437 438 439 440 441 442 443 444 445 446 447 1248 1249 1250 1251 1252 1253 1254 1255 1256 1257 1258 1259 1260 1261 1262 1263 1264 1265 1266 1267 1268 1269 1270 1271 1272 1273 1274 1275 1276 1277 1278 1279}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor13_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 13 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 13 $direction $eccSign $eta $Dbi $status]

        # Floor 14
        set floor14_nodes {448 449 450 451 452 453 454 455 456 457 458 459 460 461 462 463 464 465 466 467 468 469 470 471 472 473 474 475 476 477 478 479 1280 1281 1282 1283 1284 1285 1286 1287 1288 1289 1290 1291 1292 1293 1294 1295 1296 1297 1298 1299 1300 1301 1302 1303 1304 1305 1306 1307 1308 1309 1310 1311}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor14_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 14 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 14 $direction $eccSign $eta $Dbi $status]

        # Floor 15
        set floor15_nodes {480 481 482 483 484 485 486 487 488 489 490 491 492 493 494 495 496 497 498 499 500 501 502 503 504 505 506 507 508 509 510 511 1312 1313 1314 1315 1316 1317 1318 1319 1320 1321 1322 1323 1324 1325 1326 1327 1328 1329 1330 1331 1332 1333 1334 1335 1336 1337 1338 1339 1340 1341 1342 1343}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor15_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 15 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 15 $direction $eccSign $eta $Dbi $status]

        # Floor 16
        set floor16_nodes {512 513 514 515 516 517 518 519 520 521 522 523 524 525 526 527 528 529 530 531 532 533 534 535 536 537 538 539 540 541 542 543 1344 1345 1346 1347 1348 1349 1350 1351 1352 1353 1354 1355 1356 1357 1358 1359 1360 1361 1362 1363 1364 1365 1366 1367 1368 1369 1370 1371 1372 1373 1374 1375}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor16_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 16 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 16 $direction $eccSign $eta $Dbi $status]

        # Floor 17
        set floor17_nodes {544 545 546 547 548 549 550 551 552 553 554 555 556 557 558 559 560 561 562 563 564 565 566 567 568 569 570 571 572 573 574 575 1376 1377 1378 1379 1380 1381 1382 1383 1384 1385 1386 1387 1388 1389 1390 1391 1392 1393 1394 1395 1396 1397 1398 1399 1400 1401 1402 1403 1404 1405 1406 1407 1672 1673}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor17_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 17 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 17 $direction $eccSign $eta $Dbi $status]

        # Floor 18
        set floor18_nodes {576 577 578 579 580 581 582 583 584 585 586 587 588 589 590 591 592 593 594 595 596 597 598 599 600 601 602 603 604 605 606 607 1408 1409 1410 1411 1412 1413 1414 1415 1416 1417 1418 1419 1420 1421 1422 1423 1424 1425 1426 1427 1428 1429 1430 1431 1432 1433 1434 1435 1436 1437 1438 1439 1674 1675}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor18_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 18 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 18 $direction $eccSign $eta $Dbi $status]

        # Floor 19
        set floor19_nodes {608 609 610 611 612 613 614 615 616 617 618 619 620 621 622 623 624 625 626 627 628 629 630 631 632 633 634 635 636 637 638 639 1440 1441 1442 1443 1444 1445 1446 1447 1448 1449 1450 1451 1452 1453 1454 1455 1456 1457 1458 1459 1460 1461 1462 1463 1464 1465 1466 1467 1468 1469 1470 1471}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor19_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 19 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 19 $direction $eccSign $eta $Dbi $status]

        # Floor 20
        set floor20_nodes {640 641 642 643 644 645 646 647 648 649 650 651 652 653 654 655 656 657 658 659 660 661 662 663 664 665 666 667 668 669 670 671 1472 1473 1474 1475 1476 1477 1478 1479 1480 1481 1482 1483 1484 1485 1486 1487 1488 1489 1490 1491 1492 1493 1494 1495 1496 1497 1498 1499 1500 1501 1502 1503}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor20_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 20 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 20 $direction $eccSign $eta $Dbi $status]

        # Floor 21
        set floor21_nodes {672 673 674 675 676 677 678 679 680 681 682 683 684 685 686 687 688 689 690 691 692 693 694 695 696 697 698 699 700 701 702 703 1504 1505 1506 1507 1508 1509 1510 1511 1512 1513 1514 1515 1516 1517 1518 1519 1520 1521 1522 1523 1524 1525 1526 1527 1528 1529 1530 1531 1532 1533 1534 1535}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor21_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 21 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 21 $direction $eccSign $eta $Dbi $status]

        # Floor 22
        set floor22_nodes {704 705 706 707 708 709 710 711 712 713 714 715 716 717 718 719 720 721 722 723 724 725 726 727 728 729 730 731 732 733 734 735 1536 1537 1538 1539 1540 1541 1542 1543 1544 1545 1546 1547 1548 1549 1550 1551 1552 1553 1554 1555 1556 1557 1558 1559 1560 1561 1562 1563 1564 1565 1566 1567}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor22_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 22 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 22 $direction $eccSign $eta $Dbi $status]

        # Floor 23
        set floor23_nodes {736 737 738 739 740 741 742 743 744 745 746 747 748 749 750 751 752 753 754 755 756 757 758 759 760 761 762 763 764 765 766 767 1568 1569 1570 1571 1572 1573 1574 1575 1576 1577 1578 1579 1580 1581 1582 1583 1584 1585 1586 1587 1588 1589 1590 1591 1592 1593 1594 1595 1596 1597 1598 1599 1676 1677}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor23_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 23 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 23 $direction $eccSign $eta $Dbi $status]

        # Floor 24
        set floor24_nodes {768 769 770 771 772 773 774 775 776 777 778 779 780 781 782 783 784 785 786 787 788 789 790 791 792 793 794 795 796 797 798 799 1600 1601 1602 1603 1604 1605 1606 1607 1608 1609 1610 1611 1612 1613 1614 1615 1616 1617 1618 1619 1620 1621 1622 1623 1624 1625 1626 1627 1628 1629 1630 1631}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor24_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 24 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 24 $direction $eccSign $eta $Dbi $status]

        # Floor 25
        set floor25_nodes {800 801 802 803 804 805 806 807 808 809 810 811 812 813 814 815 816 817 818 819 820 821 822 823 824 825 826 827 828 829 830 831 1632 1633 1634 1635 1636 1637 1638 1639 1640 1641 1642 1643 1644 1645 1646 1647 1648 1649 1650 1651 1652 1653 1654 1655 1656 1657 1658 1659 1660 1661 1662 1663 1678 1679}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor25_nodes {
            if {$direction == "X"} {
                set disp [expr abs([nodeDisp $nodeId 1])]
            } else {
                set disp [expr abs([nodeDisp $nodeId 2])]
            }
            if {$disp > $maxDisp} {set maxDisp $disp}
            if {$disp < $minDisp} {set minDisp $disp}
        }

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {$eta <= 1.2} {
            set status "REGULAR"
        } elseif {$eta <= 2.0} {
            set status "A1a IRREGULAR"
        } else {
            set status "NOT PERMITTED!"
        }

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" 25 $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list 25 $direction $eccSign $eta $Dbi $status]

        puts "--------------------------------------------------------------------------------"
        puts ""
    }
}

# ============================================================================
# SUMMARY REPORT
# ============================================================================
puts ""
puts "============================================================"
puts "  SUMMARY REPORT"
puts "============================================================"

# Find maximum eta_bi across all cases
set maxEta 0.0
set criticalFloor 0
set criticalCase ""

foreach result $results {
    set floor [lindex $result 0]
    set dir [lindex $result 1]
    set ecc [lindex $result 2]
    set eta [lindex $result 3]

    if {$eta > $maxEta} {
        set maxEta $eta
        set criticalFloor $floor
        set criticalCase "$dir, [expr $ecc * 5]%"
    }
}

puts ""
puts ">>> Maximum eta_bi = $maxEta"
puts ">>> Critical Floor = $criticalFloor"
puts ">>> Critical Case  = $criticalCase"
puts ""

if {$maxEta <= 1.2} {
    puts ">>> RESULT: Building is REGULAR with respect to A1a torsional irregularity"
    puts ">>> No eccentricity amplification required (D_bi = 1.0)"
} elseif {$maxEta <= 2.0} {
    set Dbi_max [calculateDbi $maxEta]
    puts ">>> RESULT: Building has A1a TORSIONAL IRREGULARITY (1.2 < eta <= 2.0)"
    puts ">>> Eccentricity amplification factor D_bi = $Dbi_max"
    puts ">>> According to TBDY 2018 Section 4.7.4:"
    puts ">>>   +/- 5% accidental eccentricity shall be multiplied by D_bi"
} else {
    puts ">>> RESULT: eta_bi > 2.0 - BUILDING PERMIT CANNOT BE ISSUED!"
    puts ">>> According to TBDY 2018, structures with eta_bi > 2.0 are not permitted."
}

puts ""
puts "============================================================"
puts "  ANALYSIS COMPLETED"
puts "============================================================"
puts ">>> Analysis completed successfully!"
puts ""

# ============================================================================
# SAVE RESULTS TO FILE
# ============================================================================
set outFile [open "torsion_results.txt" w]
puts $outFile "TBDY 2018 A1a Torsional Irregularity Analysis Results"
puts $outFile "======================================================"
puts $outFile "Generated: TBDY 2018 Torsion Analysis"
puts $outFile ""
puts $outFile "Fundamental Period T1 = $T1 s"
puts $outFile "Base Shear Vt = $Vt kN"
puts $outFile ""
puts $outFile "Maximum eta_bi = $maxEta"
puts $outFile "Critical Floor = $criticalFloor"
puts $outFile "Critical Case = $criticalCase"
if {$maxEta > 1.2 && $maxEta <= 2.0} {
    puts $outFile "D_bi = [calculateDbi $maxEta]"
}
close $outFile

puts ">>> Results saved to torsion_results.txt"

# ============================================================================
# PART 2: TIME HISTORY ANALYSIS (Zaman Tanimi Analizi)
# TBDY 2018 Section 5.6 - Using actual twin towers FEM model
# Ground Motion: 1999 Duzce - Bolu Station (BOL090), scaled 1:50
# ============================================================================

puts ""
puts "################################################################"
puts "################################################################"
puts "##                                                            ##"
puts "##  PART 2: TIME HISTORY ANALYSIS (Zaman Tanimi Analizi)      ##"
puts "##  TBDY 2018 Section 5.6                                     ##"
puts "##  Ground Motion: 1999 Duzce - Bolu (BOL090) Scaled 1:50    ##"
puts "##                                                            ##"
puts "################################################################"
puts "################################################################"
puts ""

# ============================================================================
# RESET ANALYSIS - KEEP MODEL, CLEAR ANALYSIS OBJECTS
# ============================================================================
puts ">>> Clearing previous analysis objects (model preserved)..."
wipeAnalysis
loadConst -time 0.0
puts ">>> Analysis reset complete. Model with 1680 nodes, 4248 elements intact."
puts ">>> Load constant applied, pseudo-time reset to 0."
puts ""

# ============================================================================
# KEY NODE DEFINITIONS FOR MONITORING
# ============================================================================
puts "============================================================"
puts "  KEY MONITORING NODES"
puts "============================================================"

# Tower 1 roof center node: 809 at (11.0, 7.4, 153.0)
# Tower 2 roof center node: 1641 at (11.0, 31.4, 153.0)
# Tower 1 mid-height node: 405 (approx floor 12-13)
# Building height
set H_building 153.0  ;# cm (roof z-coordinate)

set roofNode_T1  809   ;# Tower 1 roof center
set roofNode_T2  1641  ;# Tower 2 roof center
set midNode_T1   405   ;# Tower 1 mid-height

puts "  Roof Node Tower 1:   $roofNode_T1  (11.0, 7.4, 153.0 cm)"
puts "  Roof Node Tower 2:   $roofNode_T2  (11.0, 31.4, 153.0 cm)"
puts "  Mid Node Tower 1:    $midNode_T1"
puts "  Building Height:     $H_building cm"
puts ""

# Base node list (Tower 1: 0-31, Tower 2: 832-863)
set baseNodes_T1 {0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31}
set baseNodes_T2 {832 833 834 835 836 837 838 839 840 841 842 843 844 845 846 847 848 849 850 851 852 853 854 855 856 857 858 859 860 861 862 863}
puts "  Base Nodes Tower 1:  0 - 31 (32 nodes)"
puts "  Base Nodes Tower 2:  832 - 863 (32 nodes)"
puts ""

# ============================================================================
# READ PEER AT2 GROUND MOTION FILE
# ============================================================================
puts "============================================================"
puts "  GROUND MOTION INPUT"
puts "============================================================"
puts ""
puts "  Earthquake:   1999 Duzce, Turkey (Mw 7.2)"
puts "  Station:      Bolu (ERD)"
puts "  Component:    BOL090"
puts "  Scale:        1/sqrt(50) = 0.1414 for 1:50 model"
puts "  Format:       PEER AT2"
puts "  NPTS:         5590"
puts "  DT:           0.01 sec"
puts "  Scaled PGA:   0.1163 g"
puts ""

set gmFile "../../ground_motion/BOL090_scaled_1_50.AT2"
set dt_gm  0.01   ;# sec
set npts_gm 5590

puts ">>> Reading AT2 file: $gmFile"

if {![file exists $gmFile]} {
    puts "*** ERROR: Ground motion file not found: $gmFile"
    puts "*** Checking alternative path..."
    set gmFile "C:/Users/lenovo/Desktop/DASK_NEW/ground_motion/BOL090_scaled_1_50.AT2"
    if {![file exists $gmFile]} {
        puts "*** FATAL: Ground motion file not found!"
        puts "*** Expected: BOL090_scaled_1_50.AT2"
        return
    }
}
puts ">>> File found: $gmFile"

# Parse AT2 format: skip 4 header lines, read values (8 per line, scientific notation)
set gmData {}
set fp [open $gmFile r]
set lineNum 0

while {[gets $fp line] >= 0} {
    incr lineNum
    # Skip first 4 header lines
    if {$lineNum <= 4} {
        puts "  Header $lineNum: [string range $line 0 70]"
        continue
    }
    # Parse acceleration values from this line
    foreach val [split [string trim $line]] {
        set val [string trim $val]
        if {$val ne ""} {
            # Convert scientific notation (e.g., 1.23E-04)
            if {[catch {expr double($val)} numVal]} {
                puts "  WARNING: Could not parse value '$val' at line $lineNum"
            } else {
                lappend gmData $numVal
            }
        }
    }
}
close $fp

set nRead [llength $gmData]
puts ""
puts ">>> Parsed $nRead acceleration values from AT2 file"
puts "    Expected: $npts_gm values"

# Find PGA
set pga_gm 0.0
foreach val $gmData {
    if {[expr abs($val)] > $pga_gm} {
        set pga_gm [expr abs($val)]
    }
}
puts "    PGA (read) = [format "%.6f" $pga_gm] g = [format "%.4f" [expr $pga_gm * 981.0]] cm/s2"
puts ""

# Write single-column file for OpenSees timeSeries
file mkdir ground_motion
set tempGMfile "ground_motion/BOL090_opensees.txt"
set fpOut [open $tempGMfile w]
foreach val $gmData {
    # Convert g to cm/s2 for consistent model units
    puts $fpOut [format "%.8f" [expr $val * 981.0]]
}
close $fpOut
puts ">>> Converted to single-column format: $tempGMfile"
puts "    Units converted: g -> cm/s2 (multiply by 981.0)"
puts ""

# ============================================================================
# SETUP RECORDERS FOR TIME HISTORY
# ============================================================================
puts "============================================================"
puts "  RECORDER SETUP"
puts "============================================================"

file mkdir results
file mkdir results/time_history

# Roof displacement recorders
recorder Node -file results/time_history/roof_disp_T1.txt    -node $roofNode_T1 -dof 1 2 3 disp
recorder Node -file results/time_history/roof_disp_T2.txt    -node $roofNode_T2 -dof 1 2 3 disp
puts "  [OK] Roof displacement recorders (T1: node $roofNode_T1, T2: node $roofNode_T2)"

# Roof velocity recorders
recorder Node -file results/time_history/roof_vel_T1.txt     -node $roofNode_T1 -dof 1 2 3 vel
recorder Node -file results/time_history/roof_vel_T2.txt     -node $roofNode_T2 -dof 1 2 3 vel
puts "  [OK] Roof velocity recorders"

# Roof acceleration recorders
recorder Node -file results/time_history/roof_accel_T1.txt   -node $roofNode_T1 -dof 1 2 3 accel
recorder Node -file results/time_history/roof_accel_T2.txt   -node $roofNode_T2 -dof 1 2 3 accel
puts "  [OK] Roof acceleration recorders"

# Mid-height displacement
recorder Node -file results/time_history/mid_disp_T1.txt     -node $midNode_T1 -dof 1 2 3 disp
puts "  [OK] Mid-height displacement recorder (node $midNode_T1)"

# Base reaction recorder (first 10 base nodes per tower)
recorder Node -file results/time_history/base_reaction_T1.txt -node 0 1 2 3 4 5 6 7 8 9 -dof 1 2 3 reaction
recorder Node -file results/time_history/base_reaction_T2.txt -node 832 833 834 835 836 837 838 839 840 841 -dof 1 2 3 reaction
puts "  [OK] Base reaction recorders"

# Envelope recorders (max/min over entire analysis)
recorder EnvelopeNode -file results/time_history/envelope_roof_T1.txt -node $roofNode_T1 -dof 1 2 3 disp
recorder EnvelopeNode -file results/time_history/envelope_roof_T2.txt -node $roofNode_T2 -dof 1 2 3 disp
puts "  [OK] Envelope displacement recorders"

# All roof nodes X-displacement (for torsional check during TH)
recorder Node -file results/time_history/all_roof_ux_T1.txt -node 800 801 802 803 804 805 806 807 808 809 810 811 812 813 814 815 816 817 818 819 820 821 822 823 824 825 826 827 828 829 830 831 -dof 1 disp
recorder Node -file results/time_history/all_roof_ux_T2.txt -node 1632 1633 1634 1635 1636 1637 1638 1639 1640 1641 1642 1643 1644 1645 1646 1647 1648 1649 1650 1651 1652 1653 1654 1655 1656 1657 1658 1659 1660 1661 1662 1663 -dof 1 disp
puts "  [OK] All roof nodes X-displacement recorders (for dynamic torsion check)"

# Interstory drift recorders (Tower 1, representative nodes)
# Floor 0->1: nodes 0 -> 32, Floor 1->2: nodes 32 -> 64, etc.
# Each floor has 32 nodes for Tower 1 (node = floor*32 + local_index)
# Using local_index=9 (center-ish node at (11.0, 7.4))
recorder Drift -file results/time_history/drift_story_05.txt -iNode 137 -jNode 169 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_story_10.txt -iNode 297 -jNode 329 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_story_15.txt -iNode 457 -jNode 489 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_story_20.txt -iNode 617 -jNode 649 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_story_25.txt -iNode 777 -jNode 809 -dof 1 -perpDirn 3
puts "  [OK] Interstory drift recorders (floors 5, 10, 15, 20, 25)"

puts ""
puts ">>> Total recorders configured: 17"
puts ""

# ============================================================================
# RAYLEIGH DAMPING (5% critical - TBDY 2018 typical for steel structures)
# ============================================================================
puts "============================================================"
puts "  RAYLEIGH DAMPING CONFIGURATION"
puts "============================================================"

# Use T1 from eigenvalue analysis in Part 1
# T1 is already defined from the torsion analysis section
set omega1_th [expr 2.0 * 3.14159265358979 / $T1]

# Estimate 3rd mode: approximately 3x fundamental frequency for frame
set omega3_th [expr $omega1_th * 3.5]

set xi_damp 0.05   ;# 5% critical damping

# Rayleigh coefficients: C = a0*M + a1*K
# a0 = 2*xi*w1*w3/(w1+w3)
# a1 = 2*xi/(w1+w3)
set a0_damp [expr 2.0 * $xi_damp * $omega1_th * $omega3_th / ($omega1_th + $omega3_th)]
set a1_damp [expr 2.0 * $xi_damp / ($omega1_th + $omega3_th)]

puts ""
puts "  Damping ratio (xi):          [expr $xi_damp * 100.0]%"
puts "  Fundamental period T1:       [format "%.4f" $T1] s"
puts "  omega_1:                     [format "%.4f" $omega1_th] rad/s"
puts "  omega_3 (estimated):         [format "%.4f" $omega3_th] rad/s"
puts "  Rayleigh a0 (mass-prop):     [format "%.6f" $a0_damp]"
puts "  Rayleigh a1 (stiffness-prop):[format "%.6f" $a1_damp]"
puts ""

rayleigh $a0_damp $a1_damp 0.0 0.0
puts ">>> Rayleigh damping applied to all nodes and elements"
puts ""

# ============================================================================
# GROUND MOTION EXCITATION PATTERN
# ============================================================================
puts "============================================================"
puts "  APPLYING GROUND MOTION EXCITATION"
puts "============================================================"
puts ""

# Time series from converted ground motion file
# Factor = 1.0 because we already converted g -> cm/s2
set tsTag_TH 100
timeSeries Path $tsTag_TH -dt $dt_gm -filePath $tempGMfile -factor 1.0
puts ">>> Time series created (Tag=$tsTag_TH)"
puts "    dt = $dt_gm s, source = $tempGMfile"
puts "    Factor = 1.0 (data already in cm/s2)"
puts ""

# Uniform excitation in X-direction (DOF 1)
pattern UniformExcitation 200 1 -accel $tsTag_TH
puts ">>> Uniform Excitation applied:"
puts "    Pattern Tag:  200"
puts "    Direction:    1 (X-direction)"
puts "    Accel series: Tag $tsTag_TH"
puts "    All fixed nodes receive base acceleration simultaneously"
puts ""

# ============================================================================
# TRANSIENT ANALYSIS CONFIGURATION
# ============================================================================
puts "============================================================"
puts "  TRANSIENT ANALYSIS CONFIGURATION"
puts "============================================================"
puts ""

set dt_analysis 0.005   ;# Analysis time step (sec)
set duration_TH [expr $npts_gm * $dt_gm]  ;# Total duration from ground motion
set Nsteps_TH [expr int($duration_TH / $dt_analysis)]

constraints Transformation
puts "  Constraints handler:  Transformation"

numberer RCM
puts "  DOF numberer:         RCM (Reverse Cuthill-McKee)"

system BandGeneral
puts "  System of equations:  BandGeneral"

test NormDispIncr 1.0e-6 50
puts "  Convergence test:     NormDispIncr"
puts "    Tolerance:          1.0e-6"
puts "    Max iterations:     50"

algorithm Newton
puts "  Solution algorithm:   Newton-Raphson"

integrator Newmark 0.5 0.25
puts "  Time integrator:      Newmark (gamma=0.5, beta=0.25)"
puts "    Average acceleration method (unconditionally stable)"

analysis Transient
puts "  Analysis type:        Transient (direct integration)"
puts ""
puts "  Analysis time step:   $dt_analysis s"
puts "  Ground motion dt:     $dt_gm s"
puts "  Total duration:       [format "%.2f" $duration_TH] s"
puts "  Total analysis steps: $Nsteps_TH"
puts ""

# ============================================================================
# RUN TIME HISTORY ANALYSIS
# ============================================================================
puts "============================================================"
puts "  RUNNING TIME HISTORY ANALYSIS"
puts "  $Nsteps_TH steps x $dt_analysis s = [format "%.1f" $duration_TH] s"
puts "============================================================"
puts ""

set ok_th 0
set failedSteps 0
set maxRoofUx_T1 0.0
set maxRoofUx_T2 0.0
set maxRoofUy_T1 0.0

# Progress reporting interval (every 5%)
set progInterval [expr int($Nsteps_TH / 20)]
if {$progInterval < 1} { set progInterval 1 }

puts ">>> Step | Time(s) | Roof-T1 Ux(cm) | Roof-T2 Ux(cm) | Status"
puts ">>> -----|---------|----------------|----------------|-------"

for {set step 1} {$step <= $Nsteps_TH} {incr step} {

    set ok_th [analyze 1 $dt_analysis]

    # Convergence recovery strategies
    if {$ok_th != 0} {
        # Strategy 1: Modified Newton
        algorithm ModifiedNewton
        set ok_th [analyze 1 $dt_analysis]

        if {$ok_th != 0} {
            # Strategy 2: Relaxed tolerance + more iterations
            test NormDispIncr 1.0e-5 100
            algorithm Newton
            set ok_th [analyze 1 $dt_analysis]

            if {$ok_th != 0} {
                # Strategy 3: Subdivide time step (10 substeps)
                algorithm ModifiedNewton
                test NormDispIncr 1.0e-4 200
                set dt_sub [expr $dt_analysis / 10.0]
                set subOK 0
                for {set sub 1} {$sub <= 10} {incr sub} {
                    set subOK [analyze 1 $dt_sub]
                    if {$subOK != 0} {
                        puts "  *** Substep $sub/10 failed at step $step (t=[format "%.3f" [expr $step*$dt_analysis]]s)"
                        incr failedSteps
                        break
                    }
                }
                set ok_th $subOK
            }
        }

        # Restore default settings for next step
        algorithm Newton
        test NormDispIncr 1.0e-6 50
    }

    if {$ok_th != 0} {
        incr failedSteps
        if {$failedSteps > 20} {
            puts ""
            puts "*** ANALYSIS STOPPED: Too many convergence failures ($failedSteps)"
            puts "*** Last successful time: [format "%.3f" [expr ($step - $failedSteps) * $dt_analysis]] s"
            break
        }
    }

    # Track maximum responses and print progress
    if {[expr $step % $progInterval] == 0 || $step == $Nsteps_TH || $step <= 3} {
        set ux_t1 [nodeDisp $roofNode_T1 1]
        set ux_t2 [nodeDisp $roofNode_T2 1]
        set uy_t1 [nodeDisp $roofNode_T1 2]

        if {[expr abs($ux_t1)] > $maxRoofUx_T1} { set maxRoofUx_T1 [expr abs($ux_t1)] }
        if {[expr abs($ux_t2)] > $maxRoofUx_T2} { set maxRoofUx_T2 [expr abs($ux_t2)] }
        if {[expr abs($uy_t1)] > $maxRoofUy_T1} { set maxRoofUy_T1 [expr abs($uy_t1)] }

        set pct [expr int(100.0 * $step / $Nsteps_TH)]
        set tNow [format "%.3f" [expr $step * $dt_analysis]]
        puts ">>> [format "%4d" $step] | [format "%7s" $tNow] | [format "%14.6f" $ux_t1] | [format "%14.6f" $ux_t2] | ${pct}%"
    }
}

puts ""
if {$failedSteps == 0} {
    puts ">>> TIME HISTORY ANALYSIS COMPLETED SUCCESSFULLY"
    puts ">>> All $Nsteps_TH steps converged"
} else {
    puts ">>> TIME HISTORY ANALYSIS COMPLETED WITH $failedSteps CONVERGENCE ISSUES"
}
puts ""

# ============================================================================
# TIME HISTORY RESULTS SUMMARY
# ============================================================================
puts "============================================================"
puts "  TIME HISTORY RESULTS SUMMARY"
puts "============================================================"
puts ""

# Final state displacements
set finalUx_T1 [nodeDisp $roofNode_T1 1]
set finalUy_T1 [nodeDisp $roofNode_T1 2]
set finalUz_T1 [nodeDisp $roofNode_T1 3]
set finalUx_T2 [nodeDisp $roofNode_T2 1]
set finalUy_T2 [nodeDisp $roofNode_T2 2]
set finalUz_T2 [nodeDisp $roofNode_T2 3]

puts "  --- Final State Displacements ---"
puts "  Tower 1 Roof (Node $roofNode_T1):"
puts "    Ux = [format "%12.6f" $finalUx_T1] cm"
puts "    Uy = [format "%12.6f" $finalUy_T1] cm"
puts "    Uz = [format "%12.6f" $finalUz_T1] cm"
puts ""
puts "  Tower 2 Roof (Node $roofNode_T2):"
puts "    Ux = [format "%12.6f" $finalUx_T2] cm"
puts "    Uy = [format "%12.6f" $finalUy_T2] cm"
puts "    Uz = [format "%12.6f" $finalUz_T2] cm"
puts ""

puts "  --- Maximum Absolute Responses ---"
puts "  Max Roof Ux (Tower 1): [format "%.6f" $maxRoofUx_T1] cm"
puts "  Max Roof Ux (Tower 2): [format "%.6f" $maxRoofUx_T2] cm"
puts "  Max Roof Uy (Tower 1): [format "%.6f" $maxRoofUy_T1] cm"
puts ""

# Drift ratios
set driftX_T1 [expr $maxRoofUx_T1 / $H_building]
set driftX_T2 [expr $maxRoofUx_T2 / $H_building]

puts "  --- Roof Drift Ratios ---"
puts "  Tower 1 X-drift: [format "%.6f" $driftX_T1] = [format "%.3f" [expr $driftX_T1 * 100]]%  (1/[format "%.0f" [expr 1.0/$driftX_T1]])"
puts "  Tower 2 X-drift: [format "%.6f" $driftX_T2] = [format "%.3f" [expr $driftX_T2 * 100]]%  (1/[format "%.0f" [expr 1.0/$driftX_T2]])"
puts ""

# TBDY 2018 drift limit check
# Table 4.9: lambda * delta_i,max / h_i <= limit
# For steel moment frames: 0.008*h (serviceability), 0.02*h (collapse prevention)
set driftLimit_service 0.008
set driftLimit_collapse 0.020

puts "  --- TBDY 2018 Drift Limit Check ---"
puts "  Serviceability limit (Table 4.9):      $driftLimit_service"
puts "  Collapse prevention limit:              $driftLimit_collapse"
puts ""

if {$driftX_T1 > $driftLimit_collapse} {
    puts "  >>> WARNING: Tower 1 EXCEEDS collapse prevention limit!"
} elseif {$driftX_T1 > $driftLimit_service} {
    puts "  >>> Tower 1: Within collapse prevention, EXCEEDS serviceability"
} else {
    puts "  >>> Tower 1: WITHIN serviceability limits - OK"
}

if {$driftX_T2 > $driftLimit_collapse} {
    puts "  >>> WARNING: Tower 2 EXCEEDS collapse prevention limit!"
} elseif {$driftX_T2 > $driftLimit_service} {
    puts "  >>> Tower 2: Within collapse prevention, EXCEEDS serviceability"
} else {
    puts "  >>> Tower 2: WITHIN serviceability limits - OK"
}
puts ""

# Differential displacement between towers (important for sky bridges)
set diffDisp [expr abs($maxRoofUx_T1 - $maxRoofUx_T2)]
puts "  --- Sky Bridge Differential Movement ---"
puts "  Max differential roof X-disp: [format "%.6f" $diffDisp] cm"
puts "  This affects sky bridge connections at H/4, H/2, 3H/4, H"
puts ""

# ============================================================================
# SAVE TIME HISTORY SUMMARY
# ============================================================================
set thSumFile [open "results/time_history/th_summary.txt" w]
puts $thSumFile "==============================================="
puts $thSumFile "TBDY 2018 TIME HISTORY ANALYSIS - RESULTS"
puts $thSumFile "==============================================="
puts $thSumFile ""
puts $thSumFile "Model: Twin Towers V9 (1:50 Scale)"
puts $thSumFile "Nodes: 1680, Elements: 4248"
puts $thSumFile ""
puts $thSumFile "Ground Motion: 1999 Duzce - Bolu (BOL090)"
puts $thSumFile "  PGA (scaled): [format "%.4f" $pga_gm] g"
puts $thSumFile "  NPTS: $npts_gm, DT: $dt_gm s"
puts $thSumFile "  Duration: [format "%.1f" $duration_TH] s"
puts $thSumFile ""
puts $thSumFile "Damping: $xi_damp (Rayleigh)"
puts $thSumFile "Fundamental Period T1 = [format "%.4f" $T1] s"
puts $thSumFile ""
puts $thSumFile "RESULTS:"
puts $thSumFile "  Tower 1 Max Roof Ux: [format "%.6f" $maxRoofUx_T1] cm"
puts $thSumFile "  Tower 2 Max Roof Ux: [format "%.6f" $maxRoofUx_T2] cm"
puts $thSumFile "  Tower 1 Max Roof Uy: [format "%.6f" $maxRoofUy_T1] cm"
puts $thSumFile "  Tower 1 Drift Ratio: [format "%.6f" $driftX_T1]"
puts $thSumFile "  Tower 2 Drift Ratio: [format "%.6f" $driftX_T2]"
puts $thSumFile "  Differential Disp:   [format "%.6f" $diffDisp] cm"
puts $thSumFile ""
puts $thSumFile "Convergence failures: $failedSteps / $Nsteps_TH steps"
close $thSumFile

puts ">>> Time history results saved to results/time_history/"
puts ">>> Summary: results/time_history/th_summary.txt"
puts ""


# ############################################################################
# ############################################################################
# ##                                                                        ##
# ##  PART 3: STATIC PUSHOVER ANALYSIS (Statik Itme Analizi)               ##
# ##  TBDY 2018 Section 5.6.5 - Capacity Curve                             ##
# ##  Displacement-Controlled, Inverted Triangular Load Pattern             ##
# ##                                                                        ##
# ############################################################################
# ############################################################################

puts ""
puts "################################################################"
puts "################################################################"
puts "##                                                            ##"
puts "##  PART 3: STATIC PUSHOVER ANALYSIS                         ##"
puts "##  (Statik Itme Analizi - TBDY 2018)                        ##"
puts "##  Displacement-Controlled Monotonic Push                    ##"
puts "##                                                            ##"
puts "################################################################"
puts "################################################################"
puts ""

# ============================================================================
# RESET MODEL STATE FOR PUSHOVER
# ============================================================================
puts ">>> Resetting model state from time history to initial condition..."
reset
wipeAnalysis
remove recorders
loadConst -time 0.0
puts ">>> Model reset to initial state (zero displacements)"
puts ">>> All recorders removed"
puts ">>> Analysis objects cleared"
puts ""

# ============================================================================
# PUSHOVER PARAMETERS
# ============================================================================
puts "============================================================"
puts "  PUSHOVER ANALYSIS PARAMETERS"
puts "============================================================"
puts ""

# Control node (Tower 1 roof center)
set ctrlNode 809         ;# Node 809 at (11.0, 7.4, 153.0)
set ctrlDOF  1           ;# X-direction
set H_total  153.0       ;# Building height (cm)

# Target displacement: 4% of building height (generous for capacity curve)
set targetDisp [expr $H_total * 0.04]
set dU         0.005     ;# Displacement increment per step (cm)
set Nsteps_PO  [expr int($targetDisp / $dU)]

puts "  Control Node:         $ctrlNode (Tower 1 roof center)"
puts "  Control DOF:          $ctrlDOF (X-direction)"
puts "  Building Height:      $H_total cm"
puts "  Target Displacement:  [format "%.2f" $targetDisp] cm (4% drift)"
puts "  Displacement step:    $dU cm"
puts "  Total steps:          $Nsteps_PO"
puts ""

# ============================================================================
# PUSHOVER RECORDERS
# ============================================================================
puts "============================================================"
puts "  PUSHOVER RECORDER SETUP"
puts "============================================================"

file mkdir results/pushover

# Control node displacement
recorder Node -file results/pushover/ctrl_node_disp.txt -node $ctrlNode -dof 1 2 3 disp
puts "  [OK] Control node displacement (node $ctrlNode)"

# Both tower roof displacements
recorder Node -file results/pushover/roof_T1_disp.txt -node 809 -dof 1 disp
recorder Node -file results/pushover/roof_T2_disp.txt -node 1641 -dof 1 disp
puts "  [OK] Roof displacement both towers"

# Base reactions (all Tower 1 + Tower 2 base nodes)
recorder Node -file results/pushover/base_react_T1.txt -node 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 -dof 1 reaction
recorder Node -file results/pushover/base_react_T2.txt -node 832 833 834 835 836 837 838 839 840 841 842 843 844 845 846 847 848 849 850 851 852 853 854 855 856 857 858 859 860 861 862 863 -dof 1 reaction
puts "  [OK] Base reaction recorders (all 64 ground nodes)"

# Floor displacement profile (one node per floor, Tower 1)
# Using node index pattern: floor*32 + 9 (center node at (11.0, 7.4))
recorder Node -file results/pushover/floor_profile_ux.txt -node 41 73 105 137 169 201 233 265 297 329 361 393 425 457 489 521 553 585 617 649 681 713 745 777 809 -dof 1 disp
puts "  [OK] Floor displacement profile (25 floors, Tower 1 center)"

puts ""

# ============================================================================
# LATERAL LOAD PATTERN - INVERTED TRIANGULAR (TBDY 2018)
# ============================================================================
puts "============================================================"
puts "  PUSHOVER LOAD PATTERN"
puts "  Inverted Triangular Distribution (TBDY 2018 Sec. 5.6.5)"
puts "============================================================"
puts ""
puts "  Load distribution: F_i proportional to m_i * h_i"
puts "  Applied to both Tower 1 and Tower 2 nodes"
puts "  Direction: X (DOF 1)"
puts ""

# Linear time series for pushover (load factor increases with pseudo-time)
timeSeries Linear 500

# Inverted triangular load pattern
# F_i = h_i / sum(h_i) for each floor
# Floor heights: floor_i * (153/25) = floor_i * 6.12 cm
# sum of h_i for floors 1-25 = 6.12 * (1+2+...+25) = 6.12 * 325 = 1989 cm

set h_story [expr $H_total / 25.0]  ;# Story height = 6.12 cm
set sum_hi 0.0
for {set fl 1} {$fl <= 25} {incr fl} {
    set sum_hi [expr $sum_hi + $fl * $h_story]
}

puts "  Story height:  [format "%.3f" $h_story] cm"
puts "  Sum(h_i):      [format "%.3f" $sum_hi] cm"
puts ""
puts "  Floor | Height(cm) | Load Factor | Force/Node(kN)"
puts "  ------|------------|-------------|---------------"

pattern Plain 500 500 {

    # Apply loads floor by floor
    # Tower 1 nodes: floor*32 + 0..31
    # Tower 2 nodes: 832 + floor*32 + 0..31
    # Apply to every 4th node to reduce computational effort (8 nodes per floor per tower)

    # Floor 1
    set h_1 [expr 1 * 6.12]; set lf_1 [expr $h_1 / 1989.0]; set fn_1 [expr $lf_1 / 16.0]
    load  36 $fn_1 0 0 0 0 0;  load  40 $fn_1 0 0 0 0 0;  load  44 $fn_1 0 0 0 0 0;  load  48 $fn_1 0 0 0 0 0
    load  52 $fn_1 0 0 0 0 0;  load  56 $fn_1 0 0 0 0 0;  load  60 $fn_1 0 0 0 0 0;  load  63 $fn_1 0 0 0 0 0
    load 868 $fn_1 0 0 0 0 0;  load 872 $fn_1 0 0 0 0 0;  load 876 $fn_1 0 0 0 0 0;  load 880 $fn_1 0 0 0 0 0
    load 884 $fn_1 0 0 0 0 0;  load 888 $fn_1 0 0 0 0 0;  load 892 $fn_1 0 0 0 0 0;  load 895 $fn_1 0 0 0 0 0

    # Floor 2
    set h_2 [expr 2 * 6.12]; set lf_2 [expr $h_2 / 1989.0]; set fn_2 [expr $lf_2 / 16.0]
    load  68 $fn_2 0 0 0 0 0;  load  72 $fn_2 0 0 0 0 0;  load  76 $fn_2 0 0 0 0 0;  load  80 $fn_2 0 0 0 0 0
    load  84 $fn_2 0 0 0 0 0;  load  88 $fn_2 0 0 0 0 0;  load  92 $fn_2 0 0 0 0 0;  load  95 $fn_2 0 0 0 0 0
    load 900 $fn_2 0 0 0 0 0;  load 904 $fn_2 0 0 0 0 0;  load 908 $fn_2 0 0 0 0 0;  load 912 $fn_2 0 0 0 0 0
    load 916 $fn_2 0 0 0 0 0;  load 920 $fn_2 0 0 0 0 0;  load 924 $fn_2 0 0 0 0 0;  load 927 $fn_2 0 0 0 0 0

    # Floor 3
    set h_3 [expr 3 * 6.12]; set lf_3 [expr $h_3 / 1989.0]; set fn_3 [expr $lf_3 / 16.0]
    load 100 $fn_3 0 0 0 0 0;  load 104 $fn_3 0 0 0 0 0;  load 108 $fn_3 0 0 0 0 0;  load 112 $fn_3 0 0 0 0 0
    load 116 $fn_3 0 0 0 0 0;  load 120 $fn_3 0 0 0 0 0;  load 124 $fn_3 0 0 0 0 0;  load 127 $fn_3 0 0 0 0 0
    load 932 $fn_3 0 0 0 0 0;  load 936 $fn_3 0 0 0 0 0;  load 940 $fn_3 0 0 0 0 0;  load 944 $fn_3 0 0 0 0 0
    load 948 $fn_3 0 0 0 0 0;  load 952 $fn_3 0 0 0 0 0;  load 956 $fn_3 0 0 0 0 0;  load 959 $fn_3 0 0 0 0 0

    # Floor 4
    set h_4 [expr 4 * 6.12]; set lf_4 [expr $h_4 / 1989.0]; set fn_4 [expr $lf_4 / 16.0]
    load 132 $fn_4 0 0 0 0 0;  load 136 $fn_4 0 0 0 0 0;  load 140 $fn_4 0 0 0 0 0;  load 144 $fn_4 0 0 0 0 0
    load 148 $fn_4 0 0 0 0 0;  load 152 $fn_4 0 0 0 0 0;  load 156 $fn_4 0 0 0 0 0;  load 159 $fn_4 0 0 0 0 0
    load 964 $fn_4 0 0 0 0 0;  load 968 $fn_4 0 0 0 0 0;  load 972 $fn_4 0 0 0 0 0;  load 976 $fn_4 0 0 0 0 0
    load 980 $fn_4 0 0 0 0 0;  load 984 $fn_4 0 0 0 0 0;  load 988 $fn_4 0 0 0 0 0;  load 991 $fn_4 0 0 0 0 0

    # Floor 5
    set h_5 [expr 5 * 6.12]; set lf_5 [expr $h_5 / 1989.0]; set fn_5 [expr $lf_5 / 16.0]
    load 164 $fn_5 0 0 0 0 0;  load 168 $fn_5 0 0 0 0 0;  load 172 $fn_5 0 0 0 0 0;  load 176 $fn_5 0 0 0 0 0
    load 180 $fn_5 0 0 0 0 0;  load 184 $fn_5 0 0 0 0 0;  load 188 $fn_5 0 0 0 0 0;  load 191 $fn_5 0 0 0 0 0
    load 996 $fn_5 0 0 0 0 0;  load 1000 $fn_5 0 0 0 0 0;  load 1004 $fn_5 0 0 0 0 0;  load 1008 $fn_5 0 0 0 0 0
    load 1012 $fn_5 0 0 0 0 0;  load 1016 $fn_5 0 0 0 0 0;  load 1020 $fn_5 0 0 0 0 0;  load 1023 $fn_5 0 0 0 0 0
}

# Print load summary using a loop
puts ""
for {set fl 1} {$fl <= 5} {incr fl} {
    set hi [expr $fl * $h_story]
    set lfi [expr $hi / $sum_hi]
    set fni [expr $lfi / 16.0]
    puts "  [format "%5d" $fl] | [format "%10.3f" $hi] | [format "%11.6f" $lfi] | [format "%13.8f" $fni]"
}
puts "  ... (continuing for all 25 floors)"

# We need to add floors 6-25 outside the pattern block using separate load commands
# Actually, loads must be inside the pattern block. Let me use a different approach.

puts ""
puts ">>> NOTE: Loads applied to floors 1-5 within pattern block"
puts ">>> Floors 6-25 will be added via additional pattern"
puts ""

# Additional load pattern for floors 6-25
timeSeries Linear 501
pattern Plain 501 501 {

    # Floor 6-25: generate loads programmatically
    for {set fl 6} {$fl <= 25} {incr fl} {
        set hi [expr $fl * 6.12]
        set lfi [expr $hi / 1989.0]
        set fni [expr $lfi / 16.0]

        # Tower 1 nodes: floor*32 + offsets (4, 8, 12, 16, 20, 24, 28, 31)
        set baseN1 [expr $fl * 32]
        load [expr $baseN1 + 4]  $fni 0 0 0 0 0
        load [expr $baseN1 + 8]  $fni 0 0 0 0 0
        load [expr $baseN1 + 12] $fni 0 0 0 0 0
        load [expr $baseN1 + 16] $fni 0 0 0 0 0
        load [expr $baseN1 + 20] $fni 0 0 0 0 0
        load [expr $baseN1 + 24] $fni 0 0 0 0 0
        load [expr $baseN1 + 28] $fni 0 0 0 0 0
        load [expr $baseN1 + 31] $fni 0 0 0 0 0

        # Tower 2 nodes: 832 + floor*32 + offsets
        set baseN2 [expr 832 + $fl * 32]
        load [expr $baseN2 + 4]  $fni 0 0 0 0 0
        load [expr $baseN2 + 8]  $fni 0 0 0 0 0
        load [expr $baseN2 + 12] $fni 0 0 0 0 0
        load [expr $baseN2 + 16] $fni 0 0 0 0 0
        load [expr $baseN2 + 20] $fni 0 0 0 0 0
        load [expr $baseN2 + 24] $fni 0 0 0 0 0
        load [expr $baseN2 + 28] $fni 0 0 0 0 0
        load [expr $baseN2 + 31] $fni 0 0 0 0 0
    }
}

puts ">>> Inverted triangular load pattern applied to all 25 floors"
puts ">>> Both Tower 1 and Tower 2 loaded simultaneously"
puts ""

# ============================================================================
# PUSHOVER ANALYSIS CONFIGURATION
# ============================================================================
puts "============================================================"
puts "  PUSHOVER ANALYSIS CONFIGURATION"
puts "============================================================"
puts ""

constraints Transformation
puts "  Constraints:   Transformation"

numberer RCM
puts "  Numberer:      RCM"

system BandGeneral
puts "  System:        BandGeneral"

test NormDispIncr 1.0e-6 100
puts "  Test:          NormDispIncr (tol=1e-6, maxIter=100)"

algorithm Newton
puts "  Algorithm:     Newton"

integrator DisplacementControl $ctrlNode $ctrlDOF $dU
puts "  Integrator:    DisplacementControl"
puts "    Control node:  $ctrlNode"
puts "    Control DOF:   $ctrlDOF (X-direction)"
puts "    dU increment:  $dU cm"

analysis Static
puts "  Analysis:      Static"
puts ""

# ============================================================================
# RUN PUSHOVER ANALYSIS
# ============================================================================
puts "============================================================"
puts "  RUNNING PUSHOVER ANALYSIS"
puts "  Target: [format "%.2f" $targetDisp] cm ($Nsteps_PO steps)"
puts "============================================================"
puts ""

set ok_po 0
set completedSteps 0
set maxBaseShear 0.0
set dispAtMaxV 0.0

# Store pushover curve data in list
set poData {}

# Progress interval
set poInterval [expr int($Nsteps_PO / 25)]
if {$poInterval < 1} { set poInterval 1 }

puts ">>> Step | Roof Disp(cm) | Base Shear(kN) | Drift(%) | Status"
puts ">>> -----|---------------|----------------|----------|-------"

for {set step 1} {$step <= $Nsteps_PO} {incr step} {

    set ok_po [analyze 1]

    # Convergence recovery
    if {$ok_po != 0} {
        puts "  *** Step $step: Newton failed, trying ModifiedNewton..."
        algorithm ModifiedNewton
        set ok_po [analyze 1]

        if {$ok_po != 0} {
            puts "  *** Step $step: Trying NewtonLineSearch..."
            algorithm NewtonLineSearch 0.8
            test NormDispIncr 1.0e-5 200
            set ok_po [analyze 1]

            if {$ok_po != 0} {
                puts "  *** Step $step: Trying smaller increment (dU/5)..."
                integrator DisplacementControl $ctrlNode $ctrlDOF [expr $dU / 5.0]
                algorithm Newton
                test NormDispIncr 1.0e-5 200
                set subOK 0
                for {set s 1} {$s <= 5} {incr s} {
                    set subOK [analyze 1]
                    if {$subOK != 0} { break }
                }
                set ok_po $subOK
                # Restore original increment
                integrator DisplacementControl $ctrlNode $ctrlDOF $dU
            }
        }
        # Restore defaults
        algorithm Newton
        test NormDispIncr 1.0e-6 100
    }

    if {$ok_po != 0} {
        puts ""
        puts ">>> PUSHOVER STOPPED at step $step (disp = [format "%.4f" [nodeDisp $ctrlNode $ctrlDOF]] cm)"
        break
    }

    incr completedSteps

    # Current roof displacement
    set currDisp [nodeDisp $ctrlNode $ctrlDOF]

    # Calculate base shear (sum of X-reactions at all fixed nodes)
    set Vbase 0.0
    for {set bn 0} {$bn <= 31} {incr bn} {
        set Vbase [expr $Vbase + [nodeReaction $bn 1]]
    }
    for {set bn 832} {$bn <= 863} {incr bn} {
        set Vbase [expr $Vbase + [nodeReaction $bn 1]]
    }
    set Vbase [expr abs($Vbase)]

    # Track max base shear
    if {$Vbase > $maxBaseShear} {
        set maxBaseShear $Vbase
        set dispAtMaxV $currDisp
    }

    # Store pushover data point
    lappend poData [list $currDisp $Vbase]

    # Print progress
    if {[expr $step % $poInterval] == 0 || $step == 1 || $step == $Nsteps_PO} {
        set drift_pct [expr $currDisp / $H_total * 100.0]
        set pct [expr int(100.0 * $step / $Nsteps_PO)]
        puts ">>> [format "%4d" $step] | [format "%13.4f" $currDisp] | [format "%14.4f" $Vbase] | [format "%8.3f" $drift_pct] | ${pct}%"
    }
}

puts ""
if {$ok_po == 0} {
    puts ">>> PUSHOVER ANALYSIS COMPLETED SUCCESSFULLY"
    puts ">>> All $completedSteps steps converged"
} else {
    puts ">>> PUSHOVER ANALYSIS COMPLETED ($completedSteps / $Nsteps_PO steps)"
}
puts ""

# ============================================================================
# PUSHOVER RESULTS SUMMARY
# ============================================================================
puts "============================================================"
puts "  PUSHOVER RESULTS SUMMARY"
puts "============================================================"
puts ""

set finalDisp_po [nodeDisp $ctrlNode $ctrlDOF]
set finalDrift [expr $finalDisp_po / $H_total]

# Tower 2 roof displacement at final state
set finalDisp_T2 [nodeDisp 1641 1]

puts "  --- Capacity Curve Summary ---"
puts "  Final Roof Disp (Tower 1):  [format "%.6f" $finalDisp_po] cm"
puts "  Final Roof Disp (Tower 2):  [format "%.6f" $finalDisp_T2] cm"
puts "  Final Drift Ratio:          [format "%.6f" $finalDrift] ([format "%.3f" [expr $finalDrift * 100]]%)"
puts "  Max Base Shear:             [format "%.4f" $maxBaseShear] kN"
puts "  Disp at Max Shear:          [format "%.4f" $dispAtMaxV] cm"
puts ""

# Estimate yield point and ductility
set nPts [llength $poData]
puts "  Pushover data points: $nPts"

if {$nPts > 20} {
    # Initial stiffness from first 5% of data
    set pt_early [lindex $poData [expr int($nPts * 0.05)]]
    set d_early [lindex $pt_early 0]
    set v_early [lindex $pt_early 1]

    if {$d_early > 0.0} {
        set K_init [expr $v_early / $d_early]
        puts "  Initial Stiffness K0:         [format "%.4f" $K_init] kN/cm"

        # Find approximate yield: where tangent stiffness drops below 50% of initial
        set yieldFound 0
        set yieldDisp 0.0
        set yieldForce 0.0

        for {set k 10} {$k < $nPts} {incr k} {
            set ptA [lindex $poData [expr $k - 5]]
            set ptB [lindex $poData $k]
            set dA [lindex $ptA 0]; set vA [lindex $ptA 1]
            set dB [lindex $ptB 0]; set vB [lindex $ptB 1]
            set dd [expr $dB - $dA]
            if {$dd > 0.0} {
                set K_tan [expr ($vB - $vA) / $dd]
                if {$K_init > 0.0 && [expr $K_tan / $K_init] < 0.5} {
                    set yieldDisp $dA
                    set yieldForce $vA
                    set yieldFound 1
                    break
                }
            }
        }

        if {$yieldFound} {
            puts ""
            puts "  --- Bilinear Approximation ---"
            puts "  Yield Displacement:           [format "%.4f" $yieldDisp] cm"
            puts "  Yield Force:                  [format "%.4f" $yieldForce] kN"
            set ductility [expr $finalDisp_po / $yieldDisp]
            puts "  Ductility Ratio (mu):         [format "%.2f" $ductility]"
            puts "  Yield Drift:                  [format "%.4f" [expr $yieldDisp / $H_total * 100]]%"
        } else {
            puts "  >>> Structure remained essentially elastic (no significant stiffness reduction)"
        }
    }
}
puts ""

# ============================================================================
# SAVE PUSHOVER CURVE TO FILE
# ============================================================================
puts ">>> Saving pushover curve data..."

set poFile [open "results/pushover/pushover_curve.txt" w]
puts $poFile "# TBDY 2018 Static Pushover Analysis - Capacity Curve"
puts $poFile "# Twin Towers V9 (1:50 Scale Model)"
puts $poFile "# Control Node: $ctrlNode (Tower 1 roof center)"
puts $poFile "# Column 1: Roof Displacement (cm)"
puts $poFile "# Column 2: Base Shear (kN)"
puts $poFile "#"
puts $poFile "0.00000000 0.00000000"
foreach pt $poData {
    puts $poFile "[format "%.8f" [lindex $pt 0]] [format "%.8f" [lindex $pt 1]]"
}
close $poFile
puts ">>> Pushover curve: results/pushover/pushover_curve.txt ($nPts data points)"

# Save pushover summary
set poSumFile [open "results/pushover/pushover_summary.txt" w]
puts $poSumFile "==============================================="
puts $poSumFile "TBDY 2018 STATIC PUSHOVER ANALYSIS - RESULTS"
puts $poSumFile "==============================================="
puts $poSumFile ""
puts $poSumFile "Model: Twin Towers V9 (1:50 Scale)"
puts $poSumFile "Nodes: 1680, Elements: 4248"
puts $poSumFile ""
puts $poSumFile "Control Node: $ctrlNode (11.0, 7.4, 153.0 cm)"
puts $poSumFile "Load Pattern: Inverted Triangular (TBDY 2018)"
puts $poSumFile ""
puts $poSumFile "Target Displacement: [format "%.2f" $targetDisp] cm (4% drift)"
puts $poSumFile "Achieved Displacement: [format "%.4f" $finalDisp_po] cm"
puts $poSumFile "Final Drift Ratio: [format "%.6f" $finalDrift]"
puts $poSumFile ""
puts $poSumFile "Max Base Shear: [format "%.4f" $maxBaseShear] kN"
puts $poSumFile "Disp at Max Shear: [format "%.4f" $dispAtMaxV] cm"
puts $poSumFile ""
puts $poSumFile "Completed Steps: $completedSteps / $Nsteps_PO"
close $poSumFile
puts ">>> Pushover summary: results/pushover/pushover_summary.txt"
puts ""

# ============================================================================
# FINAL SUMMARY - ALL THREE ANALYSES
# ============================================================================
puts ""
puts "################################################################"
puts "################################################################"
puts "##                                                            ##"
puts "##           ALL ANALYSES COMPLETED SUCCESSFULLY              ##"
puts "##                                                            ##"
puts "################################################################"
puts "################################################################"
puts ""
puts "  PART 1: A1a Torsional Irregularity Analysis"
puts "    -> torsion_results.txt"
puts "    -> eta_bi (torsional irregularity ratio)"
puts "    -> D_bi (eccentricity amplification factor)"
puts ""
puts "  PART 2: Time History Analysis"
puts "    -> results/time_history/roof_disp_T1.txt"
puts "    -> results/time_history/roof_disp_T2.txt"
puts "    -> results/time_history/roof_vel_T1.txt"
puts "    -> results/time_history/roof_accel_T1.txt"
puts "    -> results/time_history/base_reaction_T1.txt"
puts "    -> results/time_history/envelope_roof_T1.txt"
puts "    -> results/time_history/th_summary.txt"
puts ""
puts "  PART 3: Static Pushover Analysis"
puts "    -> results/pushover/pushover_curve.txt"
puts "    -> results/pushover/pushover_summary.txt"
puts "    -> results/pushover/ctrl_node_disp.txt"
puts "    -> results/pushover/base_react_T1.txt"
puts "    -> results/pushover/floor_profile_ux.txt"
puts ""

# Final cleanup
wipe
puts ">>> Final model cleanup complete"
puts ">>> All output files written to results/ directory"
puts ""
