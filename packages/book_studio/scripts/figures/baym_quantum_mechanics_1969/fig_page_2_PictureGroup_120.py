import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 18,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
})

fig, ax = plt.subplots(figsize=(6, 4))
ax.axis('off')

source_x, source_y = 0.2, 0.5
ax.plot(source_x, source_y, 'ko', markersize=8)
ax.text(source_x - 0.05, source_y, 'source', ha='right', va='center')

# Box with 'cle'
ax.text(-0.05, 0.25, 'cle', ha='center', va='center', bbox=dict(facecolor='none', edgecolor='black', pad=3))

# Vertical line
line_x = 0.8
ax.plot([line_x, line_x], [0.6, 0.9], 'k-', lw=2)
ax.plot([line_x, line_x], [0.1, 0.4], 'k-', lw=2)

# Top path
t = np.linspace(0, 1, 100)
x_top = source_x + (line_x - source_x) * t + 0.1 * t
y_top = source_y + 0.15 * np.sin(np.pi * t) - 0.02 * t
ax.plot(x_top, y_top, 'k-', lw=2)
# arrow in middle
idx = 65
dx = x_top[idx+1] - x_top[idx]
dy = y_top[idx+1] - y_top[idx]
ax.annotate('', xy=(x_top[idx] + dx*0.01, y_top[idx] + dy*0.01), xytext=(x_top[idx], y_top[idx]),
            arrowprops=dict(arrowstyle='-|>', color='k', lw=2, mutation_scale=20))

# Bottom path
x_bot = source_x + (line_x - source_x) * t + 0.1 * t
y_bot = source_y - 0.1 * np.sin(np.pi * t) - 0.02 * t
ax.plot(x_bot, y_bot, 'k-', lw=2)
# arrow in middle
idx2 = 65
dx2 = x_bot[idx2+1] - x_bot[idx2]
dy2 = y_bot[idx2+1] - y_bot[idx2]
ax.annotate('', xy=(x_bot[idx2] + dx2*0.01, y_bot[idx2] + dy2*0.01), xytext=(x_bot[idx2], y_bot[idx2]),
            arrowprops=dict(arrowstyle='-|>', color='k', lw=2, mutation_scale=20))

ax.set_xlim(-0.2, 1)
ax.set_ylim(0, 1)

output_dir = "/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced"
os.makedirs(output_dir, exist_ok=True)
fig.savefig(os.path.join(output_dir, "fig_page_2_PictureGroup_120.pdf"), bbox_inches='tight')
fig.savefig(os.path.join(output_dir, "fig_page_2_PictureGroup_120.png"), bbox_inches='tight')
