
import fitz

from pathlib import Path

import statistics



def calculate_global_safe_zone(input_path: Path, sample_rate: float = 0.10) -> tuple[float, float, float, float]:

    """

    Samples core pages to determine the median Y-axis boundaries,

    ignoring frontmatter and backmatter. Returns a (x0, y0, x1, y1) Safe Zone.

    """

    doc = fitz.open(input_path)

    total_pages = len(doc)

    

    # Establish base matrix dimensions from the first page

    base_rect = doc[0].rect

    width = base_rect.width

    height = base_rect.height

    

    if total_pages < 10:

        pages_to_sample = list(range(total_pages))

    else:

        # Ignore first 10% and last 10% to bypass titles and indices

        start_idx = int(total_pages * 0.1)

        end_idx = int(total_pages * 0.9)

        sample_size = max(1, int(total_pages * sample_rate))

        step = max(1, (end_idx - start_idx) // sample_size)

        pages_to_sample = list(range(start_idx, end_idx, step))



    top_boundaries = []

    bottom_boundaries = []



    for page_num in pages_to_sample:

        page = doc[page_num]

        blocks = page.get_text("blocks")

        if not blocks:

            continue

            

        # Filter for text blocks only (block_type == 0)

        text_blocks = [b for b in blocks if b[6] == 0]

        if not text_blocks:

            continue

            

        # Top Boundary Heuristic (Top-Down Search)

        text_blocks.sort(key=lambda b: b[1])

        top_boundary = height * 0.05 # Default fallback

        for i in range(len(text_blocks) - 1):

            current_block = text_blocks[i]

            next_block = text_blocks[i+1]

            gap = next_block[1] - current_block[3]

            

            # If gap > 20 points in the top 20% of the page

            if gap > 20 and current_block[3] < height * 0.20:

                top_boundary = next_block[1] - 5 # Inject 5pt buffer

                break

        top_boundaries.append(top_boundary)

        

        # Bottom Boundary Heuristic (Bottom-Up Search)

        text_blocks.sort(key=lambda b: b[3], reverse=True)

        bottom_boundary = height * 0.95 # Default fallback

        for i in range(len(text_blocks) - 1):

            current_block = text_blocks[i]

            prev_block = text_blocks[i+1] # physically above it

            gap = current_block[1] - prev_block[3]

            

            # If gap > 20 points in the bottom 20% of the page

            if gap > 20 and current_block[1] > height * 0.80:

                bottom_boundary = prev_block[3] + 5 # Inject 5pt buffer

                break

        bottom_boundaries.append(bottom_boundary)

        

    doc.close()

    

    # Calculate robust medians to reject anomalous pages

    median_top = statistics.median(top_boundaries) if top_boundaries else height * 0.05

    median_bottom = statistics.median(bottom_boundaries) if bottom_boundaries else height * 0.95

    

    return (0, median_top, width, median_bottom)



def apply_dynamic_crop(input_path: Path, output_path: Path, safe_zone: tuple[float, float, float, float]) -> Path:

    """Mutates the PDF /CropBox to hide headers and footers from k2pdfopt."""

    doc = fitz.open(input_path)

    crop_rect = fitz.Rect(*safe_zone)

    

    for page in doc:

        page.set_cropbox(crop_rect)

        

    doc.save(output_path)

    doc.close()

    return output_path

EOF# 3. Services: Update Orchestrator to integrate Pre-Processing

cat << 'EOF' > src/optimizer/services/orchestrator.py

import os

import sys

import tempfile

import concurrent.futures

from pathlib import Path

from pypdf import PdfReader



from src.optimizer.domain.types import OptimizerConfig

from src.optimizer.infra.pypdf_adapter import extract_metadata, partition_pdf, merge_and_inject_metadata, split_large_payload

from src.optimizer.infra.subprocess_adapter import execute_k2pdfopt_rasterization

from src.optimizer.infra.boundary_analyzer import calculate_global_safe_zone, apply_dynamic_crop



def _process_chunk_pipeline(idx: int, total: int, chunk_path: Path, temp_dir: Path, config: OptimizerConfig) -> tuple[int, Path]:

    chunk_page_count = len(PdfReader(chunk_path).pages)

    sys.stdout.write(f"[Worker {idx}/{total}] Rasterizing {chunk_page_count} pages...\n")

    sys.stdout.flush()

    

    rasterized_path = temp_dir / f"rasterized_{chunk_path.name}"

    execute_k2pdfopt_rasterization(

        input_pdf=chunk_path,

        output_pdf=rasterized_path,

        config=config,

        page_count=chunk_page_count

    )

    

    sys.stdout.write(f"[Worker {idx}/{total}] Artifact finalized.\n")

    sys.stdout.flush()

    return idx, rasterized_path



def optimize_pdf_for_oasis(input_path: Path | str, config: OptimizerConfig, output_path: Path | str | None = None) -> list[Path]:

    source_path = Path(input_path).resolve()

    if not source_path.exists():

        raise FileNotFoundError(f"Source PDF not located: {source_path}")

        

    target_path = Path(output_path).resolve() if output_path else source_path.with_name(f"{source_path.stem}_optimized.pdf")

    metadata = extract_metadata(source_path)

    

    with tempfile.TemporaryDirectory(prefix="kindle_pipeline_") as uow_dir:

        temp_path = Path(uow_dir)

        

        # Pre-Processing: Dynamic Boundary Isolation

        sys.stdout.write("Analyzing Cartesian boundaries (10% sampling)...\n")

        sys.stdout.flush()

        safe_zone = calculate_global_safe_zone(source_path)

        cropped_source_path = temp_path / f"cropped_{source_path.name}"

        apply_dynamic_crop(source_path, cropped_source_path, safe_zone)

        

        # Partitioning utilizing the cropped source

        chunks = partition_pdf(

            input_path=cropped_source_path,

            temp_dir=temp_path,

            threshold=config.large_document_threshold,

            fallback_chunk=config.fallback_chunk_pages

        )

        

        total_chunks = len(chunks)

        max_workers = max(1, (os.cpu_count() or 2) - 1)

        

        sys.stdout.write(f"\nDistributing {total_chunks} chunks across {max_workers} worker processes...\n")

        sys.stdout.flush()

        

        processed_results = []

        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:

            futures = [

                executor.submit(_process_chunk_pipeline, idx, total_chunks, chunk, temp_path, config)

                for idx, chunk in enumerate(chunks, 1)

            ]

            for future in concurrent.futures.as_completed(futures):

                processed_results.append(future.result())

                

        processed_results.sort(key=lambda x: x[0])

        ordered_chunk_paths = [path for _, path in processed_results]

        

        sys.stdout.write("\nMerging parallelized artifacts...\n")

        sys.stdout.flush()

        merge_and_inject_metadata(ordered_chunk_paths, target_path, metadata)

        

    final_artifacts = split_large_payload(target_path, max_size_mb=14.0)

    return final_artifacts

