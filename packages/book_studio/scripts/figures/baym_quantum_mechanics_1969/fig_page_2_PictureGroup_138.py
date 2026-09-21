import os
import matplotlib.pyplot as plt
import numpy as np

# Configure matplotlib for publication-quality output
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'figure.dpi': 300,
    'hatch.linewidth': 0.8,
})

def create_plot():
    fig, ax = plt.subplots(figsize=(7, 3.5))

    L = 1.7
    H = 0.65
    x_c1 = -1
    x_c2 = 1

    # Horizontal axis
    ax.plot([-3, 3], [0, 0], color='black', linewidth=1.5, zorder=1)

    # Densities of hatches
    hatch_c1 = '////'
    hatch_c2 = '\\\\\\\\'

    # C1 left lobe
    x_c1_L = np.linspace(x_c1 - L, x_c1, 200)
    y_c1_L = H * np.sin(np.pi * (x_c1_L - (x_c1 - L)) / L)
    ax.fill_between(x_c1_L, -y_c1_L, y_c1_L, facecolor='none', edgecolor='black', hatch=hatch_c1, zorder=2)
    ax.plot(x_c1_L, y_c1_L, color='black', linewidth=1.5, zorder=3)
    ax.plot(x_c1_L, -y_c1_L, color='black', linewidth=1.5, zorder=3)

    # C1 right lobe
    x_c1_R = np.linspace(x_c1, x_c1 + L, 200)
    y_c1_R = H * np.sin(np.pi * (x_c1_R - x_c1) / L)
    ax.fill_between(x_c1_R, -y_c1_R, y_c1_R, facecolor='none', edgecolor='black', hatch=hatch_c1, zorder=2)
    ax.plot(x_c1_R, y_c1_R, color='black', linewidth=1.5, zorder=3)
    ax.plot(x_c1_R, -y_c1_R, color='black', linewidth=1.5, zorder=3)

    # C2 left lobe
    x_c2_L = np.linspace(x_c2 - L, x_c2, 200)
    y_c2_L = H * np.sin(np.pi * (x_c2_L - (x_c2 - L)) / L)
    ax.fill_between(x_c2_L, -y_c2_L, y_c2_L, facecolor='none', edgecolor='black', hatch=hatch_c2, zorder=2)
    ax.plot(x_c2_L, y_c2_L, color='black', linewidth=1.5, zorder=3)
    ax.plot(x_c2_L, -y_c2_L, color='black', linewidth=1.5, zorder=3)

    # C2 right lobe
    x_c2_R = np.linspace(x_c2, x_c2 + L, 200)
    y_c2_R = H * np.sin(np.pi * (x_c2_R - x_c2) / L)
    ax.fill_between(x_c2_R, -y_c2_R, y_c2_R, facecolor='none', edgecolor='black', hatch=hatch_c2, zorder=2)
    ax.plot(x_c2_R, y_c2_R, color='black', linewidth=1.5, zorder=3)
    ax.plot(x_c2_R, -y_c2_R, color='black', linewidth=1.5, zorder=3)

    # Labels for atoms
    ax.text(x_c1, -0.15, 'C', ha='center', va='top', fontsize=16, fontfamily='serif', fontweight='bold', zorder=4)
    ax.text(x_c2, -0.15, 'C', ha='center', va='top', fontsize=16, fontfamily='serif', fontweight='bold', zorder=4)

    # Caption texts
    ax.text(0, -1.1, 'Fig. 21-8', ha='center', va='top', fontsize=13, fontfamily='serif', fontweight='bold')
    ax.text(0, -1.4, r'$\mathbf{\sigma}$ bond formed by two p electrons in $\mathbf{C_2}$.', ha='center', va='top', fontsize=12, fontfamily='serif')

    ax.axis('off')
    ax.set_aspect('equal')
    
    ax.set_xlim(-3, 3)
    ax.set_ylim(-1.6, 1.0)

    # Save outputs
    out_dir = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced'
    os.makedirs(out_dir, exist_ok=True)
    
    pdf_path = os.path.join(out_dir, 'fig_page_2_PictureGroup_138.pdf')
    png_path = os.path.join(out_dir, 'fig_page_2_PictureGroup_138.png')
    
    plt.savefig(pdf_path, bbox_inches='tight', format='pdf')
    plt.savefig(png_path, bbox_inches='tight', format='png', dpi=300)
    plt.close()

if __name__ == '__main__':
    create_plot()
