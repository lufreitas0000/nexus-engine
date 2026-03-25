
import os

import sys

import tempfile

import concurrent.futures

from pathlib import Path

from pypdf import PdfReader



from src.optimizer.domain.types import OptimizerConfig

from src.optimizer.infra.pypdf_adapter import extract_metadata, partition_pdf, merge_and_inject_metadata, split_large_payload

from src.optimizer.infra.subprocess_adapter import execute_k2pdfopt_rasterization



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

        

        chunks = partition_pdf(

            input_path=source_path,

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

        

    # Implement dynamic payload splitting to clear the 14.5MB threshold

    final_artifacts = split_large_payload(target_path, max_size_mb=14.0)

    return final_artifacts

