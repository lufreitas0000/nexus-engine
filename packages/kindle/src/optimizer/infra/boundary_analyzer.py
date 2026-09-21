import fitz
import sys
import statistics
from pathlib import Path

def calculate_global_safe_zone(input_path: Path, sample_rate: float = 0.20) -> tuple[float, float]:
    """
    Calculates ONLY the Y-axis bounds (top_cut, bottom_cut).
    Returns a 2-tuple to preserve native X geometry.
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)

    if total_pages == 0:
        return (0.0, 792.0)

    height = doc[0].rect.height

    start_idx = int(total_pages * 0.1)
    end_idx = int(total_pages * 0.9)
    sample_size = max(1, int((end_idx - start_idx) * sample_rate))
    step = max(1, (end_idx - start_idx) // sample_size)
    if step == 0: step = 1

    pages_to_sample = list(range(start_idx, end_idx, step))

    top_cuts = []
    bottom_cuts = []

    sys.stdout.write("\n--- Precise Y-Axis Boundary Diagnostic ---\n")

    for page_num in pages_to_sample:
        page = doc[page_num]
        h = page.rect.height
        blocks = page.get_text("blocks")
        if not blocks: continue

        text_blocks = [b for b in blocks if b[6] == 0]
        if len(text_blocks) < 2: continue

        # --- Top Boundary: Strict First-Block Isolation ---
        text_blocks.sort(key=lambda b: b[1])
        first_block = text_blocks[0]
        second_block = text_blocks[1]

        if first_block[1] < h * 0.12:
            gap = second_block[1] - first_block[3]
            if gap > 14:
                top_cuts.append(first_block[3] + 2)

        # --- Bottom Boundary: Strict Last-Block Isolation ---
        text_blocks.sort(key=lambda b: b[3], reverse=True)
        last_block = text_blocks[0]
        second_to_last = text_blocks[1]

        if last_block[3] > h * 0.88:
            gap = last_block[1] - second_to_last[3]
            if gap > 14:
                bottom_cuts.append(last_block[1] - 2)

    doc.close()

    final_top = statistics.median(top_cuts) if top_cuts else 0.0
    final_bottom = statistics.median(bottom_cuts) if bottom_cuts else height

    # Hard constraints to prevent catastrophic Y-axis excision
    if final_top > height * 0.12: final_top = 0.0
    if final_bottom < height * 0.88: final_bottom = height

    sys.stdout.write(f"Calculated Safe Y-Zone: Top={final_top:.1f}, Bottom={final_bottom:.1f}\n")
    sys.stdout.flush()

    return (final_top, final_bottom)

def apply_dynamic_crop(input_path: Path, output_path: Path, safe_zone: tuple[float, float]) -> Path:
    top_cut, bottom_cut = safe_zone
    doc = fitz.open(input_path)

    for page in doc:
        r = page.rect
        # CRITICAL FIX: Preserve native r.x0 and r.x1. Mutate only the Y-axis.
        new_rect = fitz.Rect(r.x0, top_cut, r.x1, bottom_cut)

        page.set_artbox(new_rect)
        page.set_bleedbox(new_rect)
        page.set_trimbox(new_rect)
        page.set_cropbox(new_rect)
        page.set_mediabox(new_rect)

    doc.save(output_path)
    doc.close()
    return output_path
