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

fig, ax = plt.subplots(figsize=(6, 4))

# Draw axes
ax.annotate('', xy=(5, 0), xytext=(-2, 0),
            arrowprops=dict(arrowstyle='->', lw=1.5))
ax.annotate('', xy=(0, 4), xytext=(0, -0.5),
            arrowprops=dict(arrowstyle='->', lw=1.5))

# Axis labels
ax.text(5.2, 0, 'Re $l$', va='center', ha='left', fontsize=12)
ax.text(0.1, 4.0, 'Im $l$', va='center', ha='left', fontsize=12)

# Ticks and labels
ticks = [-1, 0, 1, 2]
tick_labels = ['$-1$', '$0$', '$1$', '$2$']
for t, l in zip(ticks, tick_labels):
    ax.plot([t, t], [0, -0.1], 'k-', lw=1.2)
    ax.text(t, -0.2, l, va='top', ha='center', fontsize=11)

# Thick vertical line at x = -1
ax.plot([-1, -1], [0, 3], 'k-', lw=3)
# Arrow on thick vertical line
ax.annotate('', xy=(-1, 1.2), xytext=(-1, 1.8),
            arrowprops=dict(arrowstyle='->', lw=2))

# Thick horizontal line from x = -1 to x = 4
ax.plot([-1, 4], [0, 0], 'k-', lw=3)

# Dashed arc from (-1, 3) to (4, 0)
theta = np.linspace(np.pi/2, 0, 100)
x_arc = -1 + 5 * np.cos(theta)
y_arc = 3 * np.sin(theta)
ax.plot(x_arc, y_arc, 'k--', lw=2.5, dashes=(6, 3))

# Labels with arrows
# E = 0^+
ax.annotate(r'E = $0^+$', xy=(-1, 3), xytext=(-1.5, 2.5),
            arrowprops=dict(arrowstyle='->', lw=1.2), va='center', ha='right', fontsize=11)

# E = +\infty
ax.annotate(r'E = $+\infty$', xy=(-1.05, 0.05), xytext=(-1.8, 0.8),
            arrowprops=dict(arrowstyle='->', lw=1.2), va='center', ha='right', rotation=90)
# Wait, let's just use text and draw the arrow manually for better rotation control
ax.text(-1.8, 0.8, r'E = $+\infty$', va='center', ha='center', rotation=90, fontsize=11)
ax.annotate('', xy=(-1.05, 0.05), xytext=(-1.8, 0.4), arrowprops=dict(arrowstyle='->', lw=1.2))

# E = -\infty
ax.text(-0.6, 0.8, r'E = $-\infty$', va='center', ha='center', rotation=90, fontsize=11)
ax.annotate('', xy=(-0.95, 0.05), xytext=(-0.6, 0.4), arrowprops=dict(arrowstyle='->', lw=1.2))

# E = -Ry
ax.text(0.4, 0.8, r'E = $-{\rm Ry}$', va='center', ha='center', rotation=90, fontsize=11)
ax.annotate('', xy=(0.05, 0.05), xytext=(0.4, 0.4), arrowprops=dict(arrowstyle='->', lw=1.2))

# E = -Ry/4
ax.text(1.4, 0.8, r'E = $-{\rm Ry}/4$', va='center', ha='center', rotation=90, fontsize=11)
ax.annotate('', xy=(1.05, 0.05), xytext=(1.4, 0.4), arrowprops=dict(arrowstyle='->', lw=1.2))

# E = -Ry/9
ax.text(2.4, 0.8, r'E = $-{\rm Ry}/9$', va='center', ha='center', rotation=90, fontsize=11)
ax.annotate('', xy=(2.05, 0.05), xytext=(2.4, 0.4), arrowprops=dict(arrowstyle='->', lw=1.2))

# at \infty
ax.annotate(r'at $\infty$', xy=(2.5, 3*np.sin(np.arccos((2.5+1)/5))), xytext=(3.5, 2.5),
            arrowprops=dict(arrowstyle='->', lw=1.2), va='center', ha='left', fontsize=11)

# E = 0^-
ax.annotate('E = $0^-$', xy=(4, 0), xytext=(4, -0.4),
            arrowprops=dict(arrowstyle='->', lw=1.2), va='top', ha='center', fontsize=11)

ax.set_xlim(-2.5, 6)
ax.set_ylim(-1, 4.5)
ax.axis('off')

plt.tight_layout()

# Save directories
output_dir = "/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced"
os.makedirs(output_dir, exist_ok=True)

pdf_path = os.path.join(output_dir, "fig_page_2_FigureGroup_75.pdf")
png_path = os.path.join(output_dir, "fig_page_2_FigureGroup_75.png")

plt.savefig(pdf_path, bbox_inches='tight')
plt.savefig(png_path, bbox_inches='tight')
