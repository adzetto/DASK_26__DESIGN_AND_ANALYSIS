import json
import os
from pathlib import Path

# Setup paths
NOTEBOOK_DIR = Path(__file__).parent.parent / 'notebooks'
NOTEBOOK_DIR.mkdir(exist_ok=True)
NOTEBOOK_PATH = NOTEBOOK_DIR / 'final.ipynb'

# Define the Notebook Structure
notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# DASK 2026: Final Structural Analysis & Design Spectrum\n",
    "**Model Version:** V8 (Optimized Balsa Model)  \n",
    "**Date:** Feb 2026\n",
    "\n",
    "This notebook performs a comprehensive **Finite Element Analysis (FEM)** of the Twin Towers model using **OpenSeesPy**. It utilizes advanced vectorization techniques (Pandas/Numpy) to construct the model without explicit loops, solves the generalized eigenvalue problem for structural dynamics, and evaluates the performance against the **TBDY 2018 Design Spectrum**.\n",
    "\n",
    "---"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Mathematical Formulation\n",
    "\n",
    "### 1.1. Equation of Motion\n",
    "The free vibration of the multi-degree-of-freedom (MDOF) system is governed by:\n",
    "\n",
    "$$\n",
    "\\mathbf{M} \\ddot{\\mathbf{u}}(t) + \\mathbf{C} \\dot{\\mathbf{u}}(t) + \\mathbf{K} \\mathbf{u}(t) = \\mathbf{0}
",
    "$$\n",
    "\n",
    "Where:\n",
    "*   $\mathbf{M}$: Global Mass Matrix (Diagonal lumped mass)\n",
    "*   $\mathbf{K}$: Global Stiffness Matrix (Assembled from element stiffness matrices $\\mathbf{k}_e$)\n",
    "*   $\mathbf{C}$: Damping Matrix (Rayleigh Damping $\\mathbf{C} = \\alpha \\mathbf{M} + \\beta \\mathbf{K}$)\n",
    "\n",
    "### 1.2. The Eigenvalue Problem\n",
    "To find the natural periods ($T_n$) and mode shapes ($\phi_n$), we assume undamped harmonic motion $\\mathbf{u}(t) = \\phi \\sin(\\omega t)$. This leads to the generalized eigenvalue problem:\n",
    "\n",
    "$$\n",
    "[\\mathbf{K} - \\omega_n^2 \\mathbf{M}] \\mathbf{\\phi}_n = \\mathbf{0}
",
    "$$\n",
    "\n",
    "Solving for the roots $\\omega_n$ (circular frequency) gives the periods:\n",
    "\n",
    "$$\n",
    "T_n = \\frac{2\\pi}{\\omega_n}
",
    "$$"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import openseespy.opensees as ops\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import sys\n",
    "from pathlib import Path\n",
    "\n",
    "# Configuration\n",
    "DATA_DIR = Path('../data')\n",
    "MAKET_SCALE = 0.01  # cm to m conversion\n",
    "\n",
    "# Material Properties (Balsa)\n",
    "E_long = 3.5e6    # kPa (3.5 GPa)\n",
    "G_balsa = 0.2e6   # kPa (0.2 GPa - Realistic Shear)\n",
    "A_frame = 0.006**2\n",
    "I_frame = 0.006**4 / 12\n",
    "J_frame = 0.1406 * 0.006**4\n",
    "\n",
    "# Panel Properties (Equivalent Strut for 3mm Balsa in 3.4cm Bay)\n",
    "t_panel = 0.003\n",
    "w_panel_eq = 0.017 # Reduced effective width\n",
    "A_panel = t_panel * w_panel_eq\n",
    "\n",
    "print(\"Libraries loaded. Physics constants defined.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Advanced Model Construction (Vectorized)\n",
    "\n",
    "Instead of slow iterative loops, we use `pandas.DataFrame.apply` to vectorize the calls to the OpenSees API. This is more efficient and concise for handling large datasets of nodes and elements."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 1. Initialize Model\n",
    "ops.wipe()\n",
    "ops.model('basic', '-ndm', 3, '-ndf', 6)\n",
    "\n",
    "# 2. Load Data Matrices\n",
    "pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')\n",
    "conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')\n",
    "\n",
    "# 3. Create Nodes (Vectorized Apply)\n",
    "# Lambda function maps row data directly to ops.node command\n",
    "_ = pos_df.apply(lambda r: ops.node(int(r.node_id), r.x*MAKET_SCALE, r.y*MAKET_SCALE, r.z*MAKET_SCALE), axis=1)\n",
    "\n",
    "# 4. Boundary Conditions (Base Fixity)\n",
    "# Filter floor 0 and apply fixity\n",
    "base_ids = pos_df[pos_df.floor == 0].node_id.astype(int)\n",
    "_ = base_ids.apply(lambda nid: ops.fix(nid, 1, 1, 1, 1, 1, 1))\n",
    "\n",
    "print(f\"Model Nodes Created: {len(pos_df)}\")\n",
    "print(f\"Base Nodes Fixed: {len(base_ids)}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 5. Element Construction Strategy\n",
    "ops.geomTransf('Linear', 1, 0, 1, 0) # X-Oriented\n",
    "ops.geomTransf('Linear', 2, 1, 0, 0) # Y-Oriented\n",
    "ops.geomTransf('Linear', 3, 0, 1, 0) # Z-Oriented (Columns)\n",
    "\n",
    "ops.uniaxialMaterial('Elastic', 1, E_long)\n",
    "\n",
    "# Element Categorization Logic\n",
    "def create_element(row):\n",
    "    eid = int(row.element_id)\n",
    "    ni, nj = int(row.node_i), int(row.node_j)\n",
    "    etype = row.element_type\n",
    "    \n",
    "    # Coordinates lookup (optimized via simple dict previously, but here we query ops)\n",
    "    # Note: For pure vectorization without lookups, we'd merge pos_df. \n",
    "    # For simplicity in this demo, we do a quick coordinate grab.\n",
    "    xi, yi, zi = ops.nodeCoord(ni)\n",
    "    xj, yj, zj = ops.nodeCoord(nj)\n",
    "    dx, dy, dz = abs(xi-xj), abs(yi-yj), abs(zi-zj)\n",
    "    \n",
    "    # Logic Tree\n",
    "    if 'brace' in etype or 'truss' in etype:\n",
    "        ops.element('Truss', eid, ni, nj, A_frame, 1)\n",
    "    elif 'shear_wall' in etype:\n",
    "        ops.element('Truss', eid, ni, nj, A_panel, 1)\n",
    "    else: \n",
    "        # Frame Elements\n",
    "        transf = 3\n",
    "        if dz < 0.1 * max(dx, dy):\n",
    "            transf = 1 if dx > dy else 2\n",
    "        ops.element('elasticBeamColumn', eid, ni, nj, A_frame, E_long, G_balsa, J_frame, I_frame, I_frame, transf)\n",
    "\n",
    "# Apply Element Creation\n",
    "_ = conn_df.apply(create_element, axis=1)\n",
    "print(f\"Elements Created: {len(conn_df)}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 6. Mass Assignment (Vectorized Distribution)\n",
    "MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]\n",
    "MASS_PER_PLATE = 1.60 / 1000 # tonnes\n",
    "ROOF_MASS = 2.22 / 1000\n",
    "ROOF_FLOOR = pos_df.floor.max()\n",
    "\n",
    "# Floor Plates\n",
    "for f in MASS_FLOORS:\n",
    "    nodes = pos_df[pos_df.floor == f].node_id.values\n",
    "    m_node = MASS_PER_PLATE / len(nodes)\n",
    "    # Vectorized mass application not supported by OpenseesPy, use simple iteration\n",
    "    [ops.mass(int(n), m_node, m_node, m_node, 0, 0, 0) for n in nodes]\n",
    "\n",
    "# Roof\n",
    "roof_nodes = pos_df[pos_df.floor == ROOF_FLOOR].node_id.values\n",
    "m_roof = ROOF_MASS / len(roof_nodes)\n",
    "[ops.mass(int(n), m_roof, m_roof, m_roof, 0, 0, 0) for n in roof_nodes]\n",
    "\n",
    "# Self Weight\n",
    "SELF_WEIGHT = 1.4 / 1000\n",
    "m_self = SELF_WEIGHT / len(pos_df)\n",
    "_ = pos_df.node_id.apply(lambda n: ops.mass(int(n), m_self, m_self, m_self, 0, 0, 0))\n",
    "\n",
    "print(\"Masses applied.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Modal Analysis & TBDY 2018 Spectrum\n",
    "\n",
    "We calculate the eigenvalues $\\lambda$ and periods $T = 2\\pi / \\sqrt{\\lambda}$.\n",
    "\n",
    "### TBDY 2018 Spectrum Formula\n",
    "For the Bolu region (High Seismicity):\n",
    "*   $S_{DS} = 2.046 \\text{ g}$\n",
    "*   $T_A = 0.061 \\text{ s}$\n",
    "*   $T_B = 0.303 \\text{ s}$\n",
    "\n",
    "**Linear Ascending Region ($T < T_A$):**\n",
    "$$\n",
    "S_{ae}(T) = \\left( 0.4 + 0.6 \\frac{T}{T_A} \\right) S_{DS}
",
    "$$"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Solve Eigenvalues\n",
    "num_modes = 8\n",
    "eigenvalues = ops.eigen(num_modes)\n",
    "periods = [2 * np.pi / np.sqrt(e) for e in eigenvalues]\n",
    "freqs = [1/p for p in periods]\n",
    "\n",
    "# Create Results DataFrame\n",
    "df_modes = pd.DataFrame({\n",
    "    'Mode': range(1, num_modes+1),\n",
    "    'Period (s)': periods,\n",
    "    'Frequency (Hz)': freqs,\n",
    "    'Omega (rad/s)': np.sqrt(eigenvalues)\n",
    "})\n",
    "\n",
    "T1 = periods[0]\n",
    "print(f\"Fundamental Period T1: {T1:.4f} s\")\n",
    "df_modes.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Spectrum Calculation using Numpy Vectorization\n",
    "SDS = 2.046\n",
    "SD1 = 0.619\n",
    "TA = 0.061\n",
    "TB = 0.303\n",
    "TL = 6.0\n",
    "\n",
    "T_axis = np.linspace(0, 1.0, 1000)\n",
    "\n",
    "# Vectorized Condition Logic (np.select or np.where)\n",
    "condlist = [
",
    "    T_axis < TA,\n",
    "    (T_axis >= TA) & (T_axis <= TB),\n",
    "    (T_axis > TB) & (T_axis <= TL)
",
    "]
    choicelist = [
",
    "    (0.4 + 0.6 * (T_axis / TA)) * SDS,  # Ascending\n",
    "    SDS,                                # Plateau\n",
    "    SD1 / T_axis                        # Descending
",
    "]
    Sae_axis = np.select(condlist, choicelist, default=SD1*TL/(T_axis**2))
",
    "\n",
    "# Calculate for Model T1\n",
    "if T1 < TA:\n",
    "    Sae_model = (0.4 + 0.6 * (T1 / TA)) * SDS\n",
    "    region = \"Ascending\"\n",
    "elif T1 <= TB:\n",
    "    Sae_model = SDS\n",
    "    region = \"Plateau\"\n",
    "else:\n",
    "    Sae_model = SD1 / T1\n",
    "    region = \"Descending\"\n",
    "\n",
    "print(f\"Model Sae: {Sae_model:.3f} g ({region} Region)\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Visualization\n",
    "plt.figure(figsize=(12, 7))\n",
    "\n",
    "# Plot Spectrum\n",
    "plt.plot(T_axis, Sae_axis, label='TBDY 2018 Design Spectrum', color='#0056b3', linewidth=2.5)\n",
    "\n",
    "# Mark TA and TB\n",
    "plt.axvline(TA, color='gray', linestyle='--', alpha=0.6)\n",
    "plt.axvline(TB, color='gray', linestyle='--', alpha=0.6)\n",
    "plt.text(TA, SDS*1.02, '$T_A$', ha='center', fontsize=10)\n",
    "plt.text(TB, SDS*1.02, '$T_B$', ha='center', fontsize=10)\n",
    "\n",
    "# Fill Regions\n",
    "plt.fill_between(T_axis, 0, Sae_axis, where=(T_axis < TA), color='green', alpha=0.1, label='Ascending (Stiff)')\n",
    "plt.fill_between(T_axis, 0, Sae_axis, where=((T_axis >= TA) & (T_axis <= TB)), color='red', alpha=0.1, label='Plateau (Max Accel)')\n",
    "\n",
    "# Plot Model Point\n",
    "plt.scatter([T1], [Sae_model], color='red', s=150, zorder=5, edgecolor='black', label=f'Model V8 ($T_1={T1:.3f}s$)')\n",
    "\n",
    "# Annotation\n",
    "plt.annotate(f'Sae = {Sae_model:.2f}g',\n",
    "             xy=(T1, Sae_model),\n",
    "             xytext=(T1 + 0.1, Sae_model - 0.5),\n",
    "             arrowprops=dict(facecolor='black', shrink=0.05),\n",
    "             fontsize=12, fontweight='bold')\n",
    "\n",
    "plt.title('Structural Period vs. Design Spectrum', fontsize=16)\n",
    "plt.xlabel('Period $T$ (s)', fontsize=14)\n",
    "plt.ylabel('Spectral Acceleration $S_{ae}$ (g)', fontsize=14)\n",
    "plt.grid(True, linestyle=':', alpha=0.7)\n",
    "plt.legend(loc='upper right', fontsize=12)\n",
    "plt.xlim(0, 1.0)\n",
    "plt.ylim(0, SDS * 1.2)\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

# Write to file
with open(NOTEBOOK_PATH, 'w') as f:
    json.dump(notebook_content, f, indent=2)

print(f"Notebook generated: {NOTEBOOK_PATH}")
