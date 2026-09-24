import os
import matplotlib.pyplot as plt
import numpy as np

# Set textbook style parameters
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
})

fig, ax = plt.subplots(figsize=(10, 5))
ax.axis('off')

# Helper function to draw a line segment with an arrowhead at its midpoint
def add_segment(ax, p1, p2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', lw=1.5)
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    angle = np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
    ax.plot(mx, my, marker=(3, 0, angle - 90), markersize=8, color='k')

# --- Left Figure (Fig 3-5) ---
r3t3 = (3, 0)
t4_nodes = [(2.5, 1), (4.5, 1), (6, 1)]
t2_nodes = [(1, 2), (2.5, 2), (6, 2)]
r1t1 = (4, 3)

# Draw horizontal lines
ax.plot([1.5, 6.8], [1, 1], 'k-', lw=1.2)
ax.text(7.0, 1, r"$t_4$", va='center', fontsize=12)

ax.plot([0.0, 6.8], [2, 2], 'k-', lw=1.2)
ax.text(7.0, 2, r"$t_2$", va='center', fontsize=12)

# Draw segments
for p4 in t4_nodes:
    add_segment(ax, r3t3, p4)

for p4, p2 in zip(t4_nodes, t2_nodes):
    add_segment(ax, p4, p2)

for p2 in t2_nodes:
    add_segment(ax, p2, r1t1)

# Draw nodes
nodes = [r3t3] + t4_nodes + t2_nodes + [r1t1]
for n in nodes:
    ax.plot(n[0], n[1], 'ko', markersize=5)

# Labels
ax.text(r3t3[0], r3t3[1] - 0.2, r"$r_3t_3$", ha='center', va='top', fontsize=12)
ax.text(r1t1[0] + 0.2, r1t1[1], r"$r_1t_1$", ha='left', va='center', fontsize=12)

# Caption
ax.text(3.5, -0.8, r"$\mathbf{Fig.\ 3-5}$", ha='center', va='top', fontsize=12)
ax.text(3.5, -1.2, "Motion from $r_3t_3$ to $r_1t_1$ as a sum over\nall three-legged paths.", ha='center', va='top', fontsize=11)


# --- Right Figure (Fig 3-6) ---
# Helper function to add arrows on curved paths
def add_curve_arrow(ax, x_vals, y_vals, target_y):
    idx = np.argmin(np.abs(y_vals - target_y))
    # use a small step to calculate angle
    x1, y1 = x_vals[idx], y_vals[idx]
    x2, y2 = x_vals[min(idx+2, len(x_vals)-1)], y_vals[min(idx+2, len(y_vals)-1)]
    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    ax.plot(x1, y1, marker=(3, 0, angle - 90), markersize=8, color='k')

y = np.linspace(0, 3, 300)
x_base = 12.5 + 0.2 * y
x1 = x_base - 1.8 * np.sin(np.pi * y / 3) + 0.2 * np.sin(2 * np.pi * y / 3)
x2 = x_base - 0.6 * np.sin(np.pi * y / 3) - 0.3 * np.sin(2 * np.pi * y / 3)
x3 = x_base + 0.6 * np.sin(np.pi * y / 3) - 0.3 * np.sin(2 * np.pi * y / 3)
x4 = x_base + 1.6 * np.sin(np.pi * y / 3) + 0.4 * np.sin(2 * np.pi * y / 3)

paths = [x1, x2, x3, x4]
arrow_targets = [[1.0, 2.2], [1.2, 2.0], [0.8, 2.2], [1.0, 2.0]]

for x_vals, targets in zip(paths, arrow_targets):
    ax.plot(x_vals, y, 'k-', lw=1.5)
    for target in targets:
        add_curve_arrow(ax, x_vals, y, target)

# Draw nodes
r3t3_right = (x_base[0], y[0])
r1t1_right = (x_base[-1], y[-1])
ax.plot(r3t3_right[0], r3t3_right[1], 'ko', markersize=5)
ax.plot(r1t1_right[0], r1t1_right[1], 'ko', markersize=5)

# Labels
ax.text(r3t3_right[0], r3t3_right[1] - 0.2, r"$r_3t_3$", ha='center', va='top', fontsize=12)
ax.text(r1t1_right[0] + 0.2, r1t1_right[1], r"$r_1t_1$", ha='left', va='center', fontsize=12)

# Caption
ax.text(12.8, -0.8, r"$\mathbf{Fig.\ 3-6}$", ha='center', va='top', fontsize=12)
ax.text(12.8, -1.2, "Motion from $r_3t_3$ to $r_1t_1$ as a sum over\nall forward-going paths in space time.", ha='center', va='top', fontsize=11)

# Set limits so everything fits nicely
ax.set_xlim(-0.5, 15.5)
ax.set_ylim(-2.0, 3.5)

output_dir = "/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced"
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, "fig_page_1_PictureGroup_75.pdf"), bbox_inches='tight')
plt.savefig(os.path.join(output_dir, "fig_page_1_PictureGroup_75.png"), bbox_inches='tight')
