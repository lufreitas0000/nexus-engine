import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 14,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
})

fig, ax = plt.subplots(figsize=(4, 4))
ax.set_aspect('equal')

# Lobe shape
theta = np.linspace(-np.pi/2, np.pi/2, 200)
r = np.cos(theta)**2

x = r * np.sin(theta)
z = r * np.cos(theta)

ax.fill(x, z, facecolor='none', edgecolor='black', hatch='////', linewidth=2)
ax.plot(x, z, color='black', linewidth=2)

# Z-axis
ax.annotate('', xy=(0, 1.3), xytext=(0, -0.2),
            arrowprops=dict(arrowstyle="-|>,head_length=0.8,head_width=0.3", color='black', lw=1.5))
ax.text(0, 1.35, 'z', ha='center', va='bottom', fontsize=16)

ax.axis('off')
ax.set_xlim(-0.8, 0.8)
ax.set_ylim(-0.3, 1.6)

out_dir = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced/'
os.makedirs(out_dir, exist_ok=True)
plt.savefig(os.path.join(out_dir, 'fig_page_1_FigureGroup_110.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(out_dir, 'fig_page_1_FigureGroup_110.png'), bbox_inches='tight', dpi=300)
