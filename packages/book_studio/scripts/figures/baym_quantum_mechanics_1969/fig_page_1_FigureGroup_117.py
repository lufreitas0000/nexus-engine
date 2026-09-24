import matplotlib.pyplot as plt
import numpy as np
import os

# Create directories if they don't exist
os.makedirs('/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced', exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 14,
    'axes.linewidth': 1.0,
    'lines.linewidth': 2.0,
    'figure.dpi': 300,
    'text.usetex': False
})

fig, ax = plt.subplots(figsize=(8, 5))

# Remove default spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

# Draw axes with arrows
# x-axis
ax.annotate('', xy=(5.5, 0), xytext=(-0.2, 0),
            arrowprops=dict(arrowstyle='-|>', color='black', lw=1.5, mutation_scale=15))
# y-axis
ax.annotate('', xy=(0, 5), xytext=(0, -3.5),
            arrowprops=dict(arrowstyle='-|>', color='black', lw=1.5, mutation_scale=15))

# Labels for axes
ax.text(5.6, 0, 'R', va='center', ha='left', fontsize=14)
ax.text(-0.2, 4.8, r'$\varepsilon$(R)', va='center', ha='right', fontsize=14)

# Data for curves
R = np.linspace(0.2, 5.2, 400)
R_e = 1.3
D_e = 1.76
alpha = 1.2

eps_plus = D_e * (np.exp(-2 * alpha * (R - R_e)) - 2 * np.exp(-alpha * (R - R_e)))
eps_minus = D_e * (np.exp(-2 * alpha * (R - R_e)) + 0.4 * np.exp(-alpha * (R - R_e)))

# Filter to avoid huge values blowing up the plot boundaries
mask_plus = eps_plus < 4.8
mask_minus = eps_minus < 4.8

ax.plot(R[mask_plus], eps_plus[mask_plus], color='black', lw=2)
ax.plot(R[mask_minus], eps_minus[mask_minus], color='black', lw=2)

# Dashed lines
ax.plot([0, R_e], [-D_e, -D_e], 'k--', lw=1.5)
ax.plot([R_e, R_e], [0, -D_e], 'k--', lw=1.5)

# Labels for curves
ax.text(3.5, -1.0, r'$\varepsilon_+$(R)', fontsize=14)
ax.text(1.5, 2.0, r'$\varepsilon_-$(R)', fontsize=14)

# Tick labels
ax.text(-0.1, -D_e, r'$-1.76$ eV', va='center', ha='right', fontsize=14)
ax.text(R_e, 0.2, '1.3 \u00C5', va='bottom', ha='center', fontsize=14)

ax.set_xlim(-1, 6)
ax.set_ylim(-4, 6)

output_base = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced/fig_page_1_FigureGroup_117'
plt.savefig(f'{output_base}.pdf', bbox_inches='tight')
plt.savefig(f'{output_base}.png', bbox_inches='tight')
