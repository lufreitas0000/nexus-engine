import os
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 12,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
})

fig, ax = plt.subplots(figsize=(8, 3))
ax.set_aspect('equal')
ax.axis('off')

def draw_box(xc, yc, W, H, G):
    lines = [
        ([xc - W/2, xc + W/2], [yc + H/2, yc + H/2]),
        ([xc - W/2, xc + W/2], [yc - H/2, yc - H/2]),
        ([xc - W/2, xc - W/2], [yc + G/2, yc + H/2]),
        ([xc - W/2, xc - W/2], [yc - H/2, yc - G/2]),
        ([xc + W/2, xc + W/2], [yc + G/2, yc + H/2]),
        ([xc + W/2, xc + W/2], [yc - H/2, yc - G/2])
    ]
    for x, y in lines:
        ax.plot(x, y, color='black', lw=2)

W = 2.0
H = 1.6
G = 0.4

draw_box(-2.5, 0, W, H, G)
draw_box(2.5, 0, W, H, G)

ax.text(-2.5, 0.4, '1', ha='center', va='center', fontsize=16)
ax.text(2.5, 0.4, '2', ha='center', va='center', fontsize=16)

# Beam
ax.plot([-5.5, 5.5], [0, 0], color='black', lw=1.5)

# Arrows on beam
def draw_line_arrow(x, y):
    ax.annotate('', xy=(x+0.01, y), xytext=(x, y),
                arrowprops=dict(arrowstyle='-|>', color='black', lw=1.5,
                                mutation_scale=15))

draw_line_arrow(-4.5, 0)
draw_line_arrow(0, 0)
draw_line_arrow(4.5, 0)

# Coordinate system
ox, oy = 7.5, 0
def draw_axis_arrow(x, y, dx, dy, label, tx, ty):
    ax.annotate('', xy=(x+dx, y+dy), xytext=(x, y),
                arrowprops=dict(arrowstyle='-|>', color='black', lw=1.5,
                                mutation_scale=15))
    ax.text(x+dx+tx, y+dy+ty, label, ha='center', va='center', fontsize=14)

draw_axis_arrow(ox, oy, 1.0, 0, 'y', 0.3, 0)
draw_axis_arrow(ox, oy, 0, 1.0, 'z', 0, 0.3)
draw_axis_arrow(ox, oy, -0.4, -0.6, 'x', -0.2, -0.2)

# Save
out_dir = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced'
os.makedirs(out_dir, exist_ok=True)
plt.savefig(f'{out_dir}/fig_page_2_FigureGroup_157.pdf', bbox_inches='tight')
plt.savefig(f'{out_dir}/fig_page_2_FigureGroup_157.png', bbox_inches='tight')
