import numpy as np
import matplotlib.pyplot as plt
import os

# Set matplotlib parameters matching the textbook style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
    # 'text.usetex': True # Disabled to avoid missing TeX dependencies, using mathtext instead
})

# P parameter for the Kronig-Penney model: f(qa) = cos(qa) + P * sin(qa) / qa
# Tuning P=2.5 gives a good visual match to the original figure's peak heights
P = 2.5

def f(x):
    val = np.zeros_like(x)
    idx = x != 0
    val[idx] = np.cos(x[idx]) + P * np.sin(x[idx]) / x[idx]
    val[~idx] = 1 + P
    return val

# Create dense x array for smooth curve and precise hatching
x = np.linspace(-10, 11.5, 10000)
y = f(x)

# Find crossing points (band edges) where |f(x)| = 1
def get_crossings(x, y, level):
    crossings = []
    for i in range(len(x)-1):
        if (y[i] - level) * (y[i+1] - level) < 0:
            x_cross = x[i] + (x[i+1] - x[i]) * (level - y[i]) / (y[i+1] - y[i])
            crossings.append(x_cross)
    return np.array(crossings)

crossings_1 = get_crossings(x, y, 1)
crossings_m1 = get_crossings(x, y, -1)

def get_root(target, roots):
    if len(roots) == 0:
        return target
    return roots[np.argmin(np.abs(roots - target))]

# specific roots to annotate
r_m2pi = get_root(-2*np.pi, crossings_1)
r_m0 = get_root(-2.1, crossings_1)
r_p0 = get_root(2.1, crossings_1)
r_p2pi = get_root(2*np.pi, crossings_1)

r_mpi = get_root(-np.pi, crossings_m1)
r_p1 = get_root(4.8, crossings_m1)

fig, ax = plt.subplots(figsize=(8, 4))

# Shaded regions (band gaps)
# Hatching goes to y=-1 for peaks, and y=1 for valleys
ax.fill_between(x, y, -1, where=(y >= 1), hatch='\\\\\\\\\\\\', facecolor='none', edgecolor='black', lw=1.2, zorder=1)
ax.fill_between(x, y, 1, where=(y <= -1), hatch='\\\\\\\\\\\\', facecolor='none', edgecolor='black', lw=1.2, zorder=1)

# Main horizontal axes and thresholds
ax.plot([-10, 11.5], [0, 0], 'k-', lw=1.2) # x-axis
ax.plot([0, 0], [-3, 4.5], 'k-', lw=1.2)   # y-axis

ax.plot([-10, 11.2], [1, 1], 'k-', lw=1)
ax.plot([-10, 11.2], [-1, -1], 'k-', lw=1)

# Main curve
# Solid in the main visible region, dashed at the ends
mask_solid = (x >= -7.8) & (x <= 10.2)
ax.plot(x[mask_solid], y[mask_solid], 'k-', lw=2, zorder=2)
ax.plot(x[x < -7.8], y[x < -7.8], 'k--', lw=2, zorder=2)
ax.plot(x[x > 10.2], y[x > 10.2], 'k--', lw=2, zorder=2)

# Arrows at axis ends
ax.annotate('', xy=(11.5, 0), xytext=(11.2, 0), arrowprops=dict(arrowstyle="-|>", lw=1.2, color='k', facecolor='k'))
ax.annotate('', xy=(0, 4.5), xytext=(0, 4.2), arrowprops=dict(arrowstyle="-|>", lw=1.2, color='k', facecolor='k'))

# Hide default spines and ticks
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

# Labels
ax.text(12, 0, r'$q\alpha$', va='center', fontsize=14)
ax.text(0.3, 1.2, r'$+1$', fontsize=12)
ax.text(0.3, -0.4, r'$0$', fontsize=12)
ax.text(0.3, -1.4, r'$-1$', fontsize=12)

# Formula text
ax.text(6.5, 3.5, r'$\cos q\alpha + \frac{mv_0\alpha}{\hbar^2} \frac{\sin q\alpha}{q\alpha}$', fontsize=16)

# k = 0 annotations
ax.annotate('k = 0', xy=(r_m2pi, 1), xytext=(r_m2pi + 1.2, 1.8),
            arrowprops=dict(arrowstyle="->", lw=1), ha='center', fontsize=12)
ax.annotate('k = 0', xy=(r_m0, 1), xytext=(r_m0 - 1.2, 1.8),
            arrowprops=dict(arrowstyle="->", lw=1), ha='center', fontsize=12)
ax.annotate('k = 0', xy=(r_p0, 1), xytext=(r_p0 + 1.2, 1.8),
            arrowprops=dict(arrowstyle="->", lw=1), ha='center', fontsize=12)
ax.annotate('k = 0', xy=(r_p2pi, 1), xytext=(r_p2pi - 1.2, 1.8),
            arrowprops=dict(arrowstyle="->", lw=1), ha='center', fontsize=12)

# k\alpha = \pi annotations
ax.annotate(r'$k\alpha = \pi$', xy=(r_mpi, -1), xytext=(r_mpi - 0.5, -2.2),
            arrowprops=dict(arrowstyle="->", lw=1), ha='center', fontsize=12)
ax.annotate(r'$k\alpha = \pi$', xy=(r_p1, -1), xytext=(r_p1 + 0.5, -2.2),
            arrowprops=dict(arrowstyle="->", lw=1), ha='center', fontsize=12)

# Ensure y limits accommodate everything nicely
ax.set_ylim(-3, 4.5)
ax.set_xlim(-10.5, 12.5)

plt.tight_layout()

# Save the figure
out_pdf = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced/fig_4_15.pdf'
out_png = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced/fig_4_15.png'

os.makedirs(os.path.dirname(out_pdf), exist_ok=True)

plt.savefig(out_pdf, bbox_inches='tight')
plt.savefig(out_png, bbox_inches='tight', dpi=300)
