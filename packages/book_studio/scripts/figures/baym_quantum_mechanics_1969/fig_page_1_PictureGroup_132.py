import os
import matplotlib.pyplot as plt
import numpy as np

def main():
    # Style configuration from instructions
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 11,
        'axes.linewidth': 0.8,
        'lines.linewidth': 1.5,
        'figure.dpi': 300,
    })

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')
    ax.set_aspect('equal')

    # Generate the orbital shape
    # r = |1 + 2 cos(theta)| provides the exact 3:1 lobe length ratio and pear shape
    theta = np.linspace(0, 2 * np.pi, 1000)
    r = np.abs(1 + 2 * np.cos(theta))
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    # Plot the lobes filled with diagonal hatching
    ax.fill(x, y, facecolor='none', edgecolor='black', hatch='////', linewidth=1.5)

    # Add the horizontal axis line
    ax.plot([-1.5, 3.5], [0, 0], color='black', linewidth=1.2)

    # Add the label "(a)" below the central figure
    ax.text(1.0, -2.2, '(a)', fontsize=12, ha='center', va='center')

    # Set limits to center the plot nicely
    ax.set_xlim(-2, 4)
    ax.set_ylim(-2.8, 2.8)

    # Ensure destination directory exists
    out_dir = '/home/lucas/Projects/pdf_ingestion_pipeline/books/baym_quantum_mechanics_1969/05_figures/enhanced'
    os.makedirs(out_dir, exist_ok=True)

    # Save both PDF and PNG
    pdf_path = os.path.join(out_dir, 'fig_page_1_PictureGroup_132.pdf')
    png_path = os.path.join(out_dir, 'fig_page_1_PictureGroup_132.png')

    plt.savefig(pdf_path, bbox_inches='tight')
    plt.savefig(png_path, bbox_inches='tight')

if __name__ == '__main__':
    main()
