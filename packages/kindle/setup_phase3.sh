#!/usr/bin/env bash
set -e

# 1. Update Dependency Manifest
echo "pypdf" >> requirements.in
echo "k2pdfopt path resolution variable"
echo "K2PDFOPT_PATH=k2pdfopt" >> .env.example

# 2. Scaffolding
mkdir -p src/optimizer/domain
mkdir -p src/optimizer/infra
mkdir -p src/optimizer/services
touch src/optimizer/__init__.py
touch src/optimizer/domain/__init__.py
touch src/optimizer/infra/__init__.py
touch src/optimizer/services/__init__.py

# 3. Domain Models
cat << 'EOF' > src/optimizer/domain/types.py
from dataclasses import dataclass

@dataclass(frozen=True)
class TargetHardwareConstraints:
    width: int = 1264
    height: int = 1680
    dpi: int = 300
    margin_crop: str = "0.2"

@dataclass(frozen=True)
class OptimizerConfig:
    binary_path: str
    hardware: TargetHardwareConstraints
    fallback_chunk_pages: int = 20
    timeout_per_page_sec: float = 15.0
    large_document_threshold: int = 50
EOF

# 4. Infrastructure: PDF Manipulator
cat << 'EOF' > src/optimizer/infra/pypdf_adapter.py
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import Destination

def extract_metadata(input_path: Path) -> dict:
    reader = PdfReader(input_path)
    meta = reader.metadata
    return {
        '/Title': meta.title if meta and meta.title else input_path.stem,
        '/Author': meta.author if meta and meta.author else "Automated Pipeline"
    }

def _get_bookmark_page_indices(reader: PdfReader) -> list[int]:
    indices = set([0])
    for outline_item in reader.outline:
        if isinstance(outline_item, Destination):
            page_idx = reader.get_page_number(outline_item.page)
            if page_idx != -1:
                indices.add(page_idx)
        elif isinstance(outline_item, list) and isinstance(outline_item[0], Destination):
            page_idx = reader.get_page_number(outline_item[0].page)
            if page_idx != -1:
                indices.add(page_idx)
    sorted_indices = sorted(list(indices))
    if sorted_indices and sorted_indices[-1] != len(reader.pages):
        sorted_indices.append(len(reader.pages))
    return sorted_indices

def partition_pdf(input_path: Path, temp_dir: Path, threshold: int, fallback_chunk: int) -> list[Path]:
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    boundaries = []
    if total_pages > threshold and reader.outline:
        boundaries = _get_bookmark_page_indices(reader)
        
    if len(boundaries) < 3:
        boundaries = list(range(0, total_pages, fallback_chunk))
        if boundaries[-1] != total_pages:
            boundaries.append(total_pages)

    chunk_paths = []
    for idx in range(len(boundaries) - 1):
        start = boundaries[idx]
        end = boundaries[idx + 1]
        
        writer = PdfWriter()
        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])
            
        chunk_path = temp_dir / f"chunk_{idx:04d}.pdf"
        with open(chunk_path, "wb") as f_out:
            writer.write(f_out)
        chunk_paths.append(chunk_path)
        
    return chunk_paths

def merge_and_inject_metadata(chunk_paths: list[Path], output_path: Path, metadata: dict) -> Path:
    writer = PdfWriter()
    for chunk in sorted(chunk_paths):
        reader = PdfReader(chunk)
        writer.append_pages_from_reader(reader)
        
    writer.add_metadata(metadata)
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
        
    return output_path
EOF

# 5. Infrastructure: Subprocess Adapter
cat << 'EOF' > src/optimizer/infra/subprocess_adapter.py
import subprocess
from pathlib import Path
from src.optimizer.domain.types import OptimizerConfig

def execute_k2pdfopt_rasterization(input_pdf: Path, output_pdf: Path, config: OptimizerConfig, page_count: int) -> Path:
    hw = config.hardware
    execution_vector = [
        config.binary_path,
        '-ui-', '-x',
        '-w', str(hw.width),
        '-h', str(hw.height),
        '-dpi', str(hw.dpi),
        '-m', hw.margin_crop,
        '-wrap', '-col', '2',
        '-o', str(output_pdf),
        str(input_pdf)
    ]
    
    timeout_limit = page_count * config.timeout_per_page_sec
    
    try:
        subprocess.run(
            execution_vector,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_limit
        )
    except subprocess.TimeoutExpired as timeout_err:
        raise RuntimeError(f"Rasterization timeout exceeded ({timeout_limit}s) for chunk: {input_pdf.name}") from timeout_err
    except subprocess.CalledProcessError as process_err:
        raise RuntimeError(f"k2pdfopt binary execution failed with code {process_err.returncode}.\nTrace: {process_err.stderr}") from process_err
        
    if not output_pdf.exists() or output_pdf.stat().st_size == 0:
        raise RuntimeError(f"k2pdfopt returned 0 but generated invalid artifact for chunk: {input_pdf.name}")
        
    return output_pdf
EOF

# 6. Services: Pipeline Orchestrator
cat << 'EOF' > src/optimizer/services/orchestrator.py
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
EOF

# 7. Update Main Dispatcher
cat << 'EOF' > main.py
import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

from src.converter.epub_converter import convert_markdown_to_epub
from src.dispatcher.config import load_smtp_config
from src.dispatcher.mailer import dispatch_artifact_to_kindle
from src.optimizer.domain.types import OptimizerConfig, TargetHardwareConstraints
from src.optimizer.services.orchestrator import optimize_pdf_for_oasis

def main() -> None:
    parser = argparse.ArgumentParser(description="Artifact Compilation and Kindle Dispatch Pipeline")
    parser.add_argument("input_file", type=str, help="Target path to the source file (.md or .pdf)")
    parser.add_argument("--keep", action="store_true", help="Retain the generated artifact on the filesystem post-transmission")
    arguments = parser.parse_args()
    
    source_path = Path(arguments.input_file).resolve()
    if not source_path.exists():
        sys.exit(f"Fatal: Input boundary invalid. Target file not found.\nPath evaluated: {source_path}")

    load_dotenv()

    try:
        config = load_smtp_config()

        if source_path.suffix.lower() == '.md':
            sys.stdout.write(f"Initiating EPUB compilation pipeline for: {source_path.name}\n")
            artifact_path = convert_markdown_to_epub(source_path)
            sys.stdout.write(f"Artifact generated: {artifact_path.name}\n")
            
        elif source_path.suffix.lower() == '.pdf':
            sys.stdout.write(f"Initiating PDF optimization pipeline for: {source_path.name}\n")
            opt_config = OptimizerConfig(
                binary_path=os.getenv('K2PDFOPT_PATH', 'k2pdfopt'),
                hardware=TargetHardwareConstraints()
            )
            artifact_path = optimize_pdf_for_oasis(source_path, opt_config)
            sys.stdout.write(f"Artifact generated: {artifact_path.name}\n")
            
        else:
            sys.exit(f"Fatal: Unsupported file extension {source_path.suffix}. Expected .md or .pdf.")

        sys.stdout.write(f"Initializing network dispatch to {config.destination}...\n")
        dispatch_artifact_to_kindle(artifact_path, config)
        sys.stdout.write("Pipeline execution complete.\n")

        if not arguments.keep:
            artifact_path.unlink(missing_ok=True)
            sys.stdout.write("Transient artifact purged from local storage.\n")

    except Exception as execution_error:
        sys.exit(f"Pipeline Terminated with Exception:\n{execution_error}")

if __name__ == "__main__":
    main()
EOF

chmod +x setup_phase3.sh
echo "Setup script generated. Execute ./setup_phase3.sh to inject Phase 3 architecture."
