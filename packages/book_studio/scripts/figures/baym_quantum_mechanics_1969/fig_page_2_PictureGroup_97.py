import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
})

fig, ax = plt.subplots(figsize=(6, 3))
ax.axis('off')

# horizontal line
ax.plot([-1.5, 2.0], [0, 0], color='black', linewidth=1.5)

# s orbital: circle
theta = np.linspace(0, 2*np.pi, 200)
xs = 1.0 * np.cos(theta)
ys = 1.0 * np.sin(theta)
ax.fill(xs, ys, fill=False, edgecolor='black', hatch='\\\\', linewidth=1.5, zorder=2)

# p orbital right lobe
theta_r = np.linspace(-np.pi/2, np.pi/2, 100)
r_r = 1.3 * np.cos(theta_r)
x_pr = r_r * np.cos(theta_r)
y_pr = r_r * np.sin(theta_r)
ax.fill(x_pr, y_pr, fill=False, edgecolor='black', hatch='//', linewidth=1.5, zorder=1)

# p orbital left lobe
x_pl = -x_pr
y_pl = y_pr
ax.fill(x_pl, y_pl, fill=False, edgecolor='black', hatch='//', linewidth=1.5, zorder=1)

# Plus sign
ax.text(0.8, 0.2, '+', fontsize=14, ha='center', va='center')

# Arrow
ax.arrow(1.6, 0, 0.5, 0, head_width=0.1, head_length=0.15, fc='black', ec='black')

ax.set_aspect('equal')
ax.set_xlim(-1.5, 2.5)
ax.set_ylim(-1.2, 1.2)

# Caption
ax.text(0.5, -1.5, 'Fig. 21-11\nHybridization of s and p orbitals', ha='center', va='center', fontsize=12)

out_dir = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced'
os.makedirs(out_dir, exist_ok=True)
plt.savefig(os.path.join(out_dir, 'fig_page_2_PictureGroup_97.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(out_dir, 'fig_page_2_PictureGroup_97.png'), bbox_inches='tight')
