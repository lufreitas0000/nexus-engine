import sys
import tempfile
from pathlib import Path
from pypdf import PdfReader
from src.optimizer.domain.types import OptimizerConfig
from src.optimizer.infra.pypdf_adapter import extract_metadata, partition_pdf, merge_and_inject_metadata
from src.optimizer.infra.subprocess_adapter import execute_k2pdfopt_rasterization
from src.optimizer.infra.ghostscript_adapter import compress_pdf_artifact

def optimize_pdf_for_oasis(input_path: Path | str, config: OptimizerConfig, output_path: Path | str | None = None) -> Path:
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
        
        optimized_chunks = []
        total_chunks = len(chunks)
        
        for idx, chunk in enumerate(chunks, 1):
            chunk_page_count = len(PdfReader(chunk).pages)
            sys.stdout.write(f"[Chunk {idx}/{total_chunks}] Rasterizing {chunk_page_count} pages...\n")
            sys.stdout.flush()
            
            opt_chunk_path = temp_path / f"opt_{chunk.name}"
            execute_k2pdfopt_rasterization(
                input_pdf=chunk,
                output_pdf=opt_chunk_path,
                config=config,
                page_count=chunk_page_count
            )
            optimized_chunks.append(opt_chunk_path)
            
        uncompressed_merged = temp_path / "uncompressed_merged.pdf"
        merge_and_inject_metadata(optimized_chunks, uncompressed_merged, metadata)
        
        sys.stdout.write("Initiating 8-bit grayscale downsampling (Ghostscript)...\n")
        sys.stdout.flush()
        compress_pdf_artifact(uncompressed_merged, target_path)
        
    return target_path
