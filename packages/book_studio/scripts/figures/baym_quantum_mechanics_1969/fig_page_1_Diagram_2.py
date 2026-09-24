import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.patches import FancyArrowPatch

# Set up the style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
})

fig, ax = plt.subplots(figsize=(4, 4))
ax.set_aspect('equal')
ax.axis('off')

# Define angles and lengths
angle_up = np.pi / 2
angle_right = np.radians(90 - 109.6) # -19.6 degrees
angle_dl = np.radians(210)
angle_dr = np.radians(310)

L_up = 1.5
L_right = 1.6
L_dl = 1.2
L_dr = 1.2

# Plot lines
ax.plot([0, L_up * np.cos(angle_up)], [0, L_up * np.sin(angle_up)], 'k-', lw=1.5)
ax.plot([0, L_right * np.cos(angle_right)], [0, L_right * np.sin(angle_right)], 'k-', lw=1.5)
ax.plot([0, L_dl * np.cos(angle_dl)], [0, L_dl * np.sin(angle_dl)], 'k-', lw=1.5)
ax.plot([0, L_dr * np.cos(angle_dr)], [0, L_dr * np.sin(angle_dr)], 'k-', lw=1.5)

# Add labels
ax.text(-0.1, L_up - 0.1, 'H', fontsize=14, ha='right', va='top')
ax.text(-0.1, 0.05, 'O', fontsize=14, ha='right', va='bottom')

# Draw arc for the angle
r = 0.5
theta = np.linspace(angle_right, angle_up, 100)
ax.plot(r * np.cos(theta), r * np.sin(theta), 'k-', lw=1)

# Add arrowheads to the arc
# Arrow pointing to the vertical line
arrow1 = FancyArrowPatch(posA=(r * np.cos(angle_up - 0.1), r * np.sin(angle_up - 0.1)),
                         posB=(r * np.cos(angle_up), r * np.sin(angle_up)),
                         arrowstyle="-|>", mutation_scale=10, color='k', lw=1)
ax.add_patch(arrow1)

# Arrow pointing to the right line
arrow2 = FancyArrowPatch(posA=(r * np.cos(angle_right + 0.1), r * np.sin(angle_right + 0.1)),
                         posB=(r * np.cos(angle_right), r * np.sin(angle_right)),
                         arrowstyle="-|>", mutation_scale=10, color='k', lw=1)
ax.add_patch(arrow2)

# Add text for the angle
mid_angle = (angle_up + angle_right) / 2
ax.text((r + 0.2) * np.cos(mid_angle), (r + 0.2) * np.sin(mid_angle), '109.6°', 
        fontsize=12, ha='center', va='center')

# Set limits
ax.set_xlim(-1.5, 1.8)
ax.set_ylim(-1.5, 1.8)

# Save the figure
output_dir = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced'
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, 'fig_page_1_Diagram_2.pdf'), bbox_inches='tight')
plt.savefig(os.path.join(output_dir, 'fig_page_1_Diagram_2.png'), bbox_inches='tight')
