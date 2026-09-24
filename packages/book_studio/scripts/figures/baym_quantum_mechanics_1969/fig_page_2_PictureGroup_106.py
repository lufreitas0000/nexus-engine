import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.patches import FancyArrowPatch

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
    'text.usetex': False
})

colors = {
    'primary': '#000000',
}

fig, ax = plt.subplots(figsize=(5, 5))

N = np.array([0, 1.2])
H_L = np.array([-1.8, 0])
H_R = np.array([1.8, 0])
H_B = np.array([0.2, -1.0])

ax.plot([H_L[0], H_R[0]], [H_L[1], H_R[1]], linestyle='--', color=colors['primary'], zorder=1)
ax.plot([N[0], H_L[0]], [N[1], H_L[1]], color=colors['primary'], zorder=2)
ax.plot([N[0], H_R[0]], [N[1], H_R[1]], color=colors['primary'], zorder=2)
ax.plot([N[0], H_B[0]], [N[1], H_B[1]], color=colors['primary'], zorder=3)
ax.plot([H_L[0], H_B[0]], [H_L[1], H_B[1]], color=colors['primary'], zorder=2)
ax.plot([H_R[0], H_B[0]], [H_R[1], H_B[1]], color=colors['primary'], zorder=2)

ax.text(N[0], N[1] + 0.1, 'N', ha='center', va='bottom')
ax.text(H_L[0] - 0.1, H_L[1], 'H', ha='right', va='center')
ax.text(H_R[0] + 0.1, H_R[1], 'H', ha='left', va='center')
ax.text(H_B[0], H_B[1] - 0.1, 'H', ha='center', va='top')

v_R = H_R - N
u_R = v_R / np.linalg.norm(v_R)
start_pt = N + u_R * 0.5

v_B = H_B - N
u_B = v_B / np.linalg.norm(v_B)
end_pt = N + u_B * 0.6

# Notice the arrow in the original goes from outside towards the center
arrow = FancyArrowPatch(start_pt, end_pt,
                        connectionstyle="arc3,rad=-0.4",
                        arrowstyle="-|>",
                        mutation_scale=15,
                        color=colors['primary'])
ax.add_patch(arrow)

ax.text(start_pt[0] + 0.2, start_pt[1] + 0.1, r'107$^\circ$', ha='left', va='bottom')

ax.set_aspect('equal')
ax.axis('off')

# Add caption
ax.text(0, -1.6, 'Fig. 21-14', ha='center', va='top', fontsize=12, fontweight='bold')
ax.text(0, -1.8, 'The ammonia molecule.', ha='center', va='top', fontsize=11)

out_dir = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced'
os.makedirs(out_dir, exist_ok=True)
out_base = os.path.join(out_dir, 'fig_page_2_PictureGroup_106')
plt.savefig(out_base + '.pdf', bbox_inches='tight', pad_inches=0.1)
plt.savefig(out_base + '.png', bbox_inches='tight', pad_inches=0.1)
