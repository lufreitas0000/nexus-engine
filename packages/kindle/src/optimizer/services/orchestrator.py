import tempfile
from pathlib import Path
from pypdf import PdfReader
from src.optimizer.domain.types import OptimizerConfig
from src.optimizer.infra.pypdf_adapter import extract_metadata, partition_pdf, merge_and_inject_metadata
from src.optimizer.infra.subprocess_adapter import execute_k2pdfopt_rasterization

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
        for chunk in chunks:
            opt_chunk_path = temp_path / f"opt_{chunk.name}"
            chunk_page_count = len(PdfReader(chunk).pages)
            
            execute_k2pdfopt_rasterization(
                input_pdf=chunk,
                output_pdf=opt_chunk_path,
                config=config,
                page_count=chunk_page_count
            )
            optimized_chunks.append(opt_chunk_path)
            
        merge_and_inject_metadata(optimized_chunks, target_path, metadata)
        
    return target_path
