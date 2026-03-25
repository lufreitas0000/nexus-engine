import fitz
import sys
from pathlib import Path

def calculate_global_safe_zone(input_path: Path, sample_rate: float = 0.15) -> tuple[float, float, float, float]:
    """
    Samples core pages to determine aggressive Y-axis boundaries with verbose logging.
    Returns a (x0, y0, x1, y1) Safe Zone.
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)

    base_rect = doc[0].rect
    width = base_rect.width
    height = base_rect.height

    if total_pages < 10:
        pages_to_sample = list(range(total_pages))
    else:
        start_idx = int(total_pages * 0.1)
        end_idx = int(total_pages * 0.9)
        sample_size = max(1, int(total_pages * sample_rate))
        step = max(1, (end_idx - start_idx) // sample_size)
        pages_to_sample = list(range(start_idx, end_idx, step))

    top_boundaries = []
    bottom_boundaries = []

    sys.stdout.write(f"\n--- Initiating Boundary Diagnostic [Total Pages: {total_pages}] ---\n")
    sys.stdout.write(f"Page Height: {height:.1f} | Search Zone: Top {height*0.25:.1f}, Bottom {height*0.75:.1f}\n")

    for page_num in pages_to_sample:
        page = doc[page_num]
        blocks = page.get_text("blocks")
        if not blocks: continue

        text_blocks = [b for b in blocks if b[6] == 0]
        if not text_blocks: continue

        sys.stdout.write(f"\n[Page {page_num}] Top-Down Analysis:\n")
        text_blocks.sort(key=lambda b: b[1])

        # Top Boundary
        for i in range(len(text_blocks) - 1):
            current = text_blocks[i]
            next_blk = text_blocks[i+1]
            gap = next_blk[1] - current[3]
            text_snippet = current[4].replace('\n', ' ').strip()[:30]

            sys.stdout.write(f"  Block: '{text_snippet}' | y1: {current[3]:.1f} | Next y0: {next_blk[1]:.1f} | Gap: {gap:.1f}\n")

            # Lowered gap threshold to 10pt
            if gap > 10 and current[3] < height * 0.25:
                # Add a 2pt buffer below the top block
                top_bound = next_blk[1] - 2
                sys.stdout.write(f"  >>> TOP BOUNDARY TRIGGERED at Y={top_bound:.1f}\n")
                top_boundaries.append(top_bound)
                break

        sys.stdout.write(f"[Page {page_num}] Bottom-Up Analysis:\n")
        text_blocks.sort(key=lambda b: b[3], reverse=True)

        # Bottom Boundary
        for i in range(len(text_blocks) - 1):
            current = text_blocks[i]
            prev_blk = text_blocks[i+1]
            gap = current[1] - prev_blk[3]
            text_snippet = current[4].replace('\n', ' ').strip()[:30]

            sys.stdout.write(f"  Block: '{text_snippet}' | y0: {current[1]:.1f} | Prev y1: {prev_blk[3]:.1f} | Gap: {gap:.1f}\n")

            if gap > 10 and current[1] > height * 0.75:
                bottom_bound = prev_blk[3] + 2
                sys.stdout.write(f"  >>> BOTTOM BOUNDARY TRIGGERED at Y={bottom_bound:.1f}\n")
                bottom_boundaries.append(bottom_bound)
                break

    doc.close()

    final_top = max(top_boundaries) if top_boundaries else height * 0.12
    final_bottom = min(bottom_boundaries) if bottom_boundaries else height * 0.88

    if final_top > height * 0.30: final_top = height * 0.12
    if final_bottom < height * 0.70: final_bottom = height * 0.88

    sys.stdout.write(f"\n--- Global Safe Zone Calculated ---\n")
    sys.stdout.write(f"Top Boundary Cut: {final_top:.1f}\n")
    sys.stdout.write(f"Bottom Boundary Cut: {final_bottom:.1f}\n")
    sys.stdout.write(f"-----------------------------------\n\n")
    sys.stdout.flush()

    return (0, final_top, width, final_bottom)

def apply_dynamic_crop(input_path: Path, output_path: Path, safe_zone: tuple[float, float, float, float]) -> Path:
    doc = fitz.open(input_path)
    crop_rect = fitz.Rect(*safe_zone)

    for page in doc:
        page.set_cropbox(crop_rect)
        page.set_mediabox(crop_rect)
        page.set_trimbox(crop_rect)
        page.set_artbox(crop_rect)

    doc.save(output_path)
    doc.close()
    return output_path
