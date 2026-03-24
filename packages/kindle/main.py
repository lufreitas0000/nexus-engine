import argparse
import sys
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from pypdf import PdfReader

from src.converter.epub_converter import convert_markdown_to_epub
from src.dispatcher.config import load_smtp_config
from src.dispatcher.mailer import dispatch_artifact_to_kindle
from src.optimizer.domain.types import OptimizerConfig, TargetHardwareConstraints
from src.optimizer.services.orchestrator import optimize_pdf_for_oasis

def main() -> None:
    parser = argparse.ArgumentParser(description="Artifact Compilation and Kindle Dispatch Pipeline")
    parser.add_argument("input_file", type=str, help="Target path to the source file (.md or .pdf)")
    parser.add_argument("--keep", action="store_true", help="Retain artifact (Deprecated: artifacts are now auto-archived)")
    arguments = parser.parse_args()
    
    source_path = Path(arguments.input_file).resolve()
    if not source_path.exists():
        sys.exit(f"Fatal: Input boundary invalid. Target file not found.\nPath evaluated: {source_path}")

    load_dotenv()
    artifacts_dir = Path("artifacts").resolve()
    artifacts_dir.mkdir(exist_ok=True)

    try:
        config = load_smtp_config()

        if source_path.suffix.lower() == '.md':
            sys.stdout.write(f"Initiating EPUB compilation pipeline for: {source_path.name}\n")
            artifact_path = convert_markdown_to_epub(source_path)
            
        elif source_path.suffix.lower() == '.pdf':
            sys.stdout.write(f"Initiating PDF optimization pipeline for: {source_path.name}\n")
            opt_config = OptimizerConfig(
                binary_path=os.getenv('K2PDFOPT_PATH', 'k2pdfopt'),
                hardware=TargetHardwareConstraints()
            )
            artifact_path = optimize_pdf_for_oasis(source_path, opt_config)
            
        else:
            sys.exit(f"Fatal: Unsupported file extension {source_path.suffix}. Expected .md or .pdf.")

        # Archival Phase
        archived_path = artifacts_dir / artifact_path.name
        shutil.move(str(artifact_path), str(archived_path))
        artifact_path = archived_path
        
        # Validation Phase
        size_mb = artifact_path.stat().st_size / (1024 * 1024)
        pages = "N/A"
        if artifact_path.suffix.lower() == '.pdf':
            pages = len(PdfReader(artifact_path).pages)
            
        sys.stdout.write(f"\nArtifact Validation Complete:\n")
        sys.stdout.write(f"- File:  {artifact_path.name}\n")
        sys.stdout.write(f"- Pages: {pages}\n")
        sys.stdout.write(f"- Size:  {size_mb:.2f} MB\n")

        if size_mb > 14.5:
            sys.exit(f"\nFatal: Artifact exceeds 14.5 MB strict SMTP boundary. Network dispatch aborted.\nArtifact retained at: {artifact_path}")

        # Interactive Gate
        user_intent = input(f"\nDispatch to {config.destination}? [y/N]: ").strip().lower()
        if user_intent != 'y':
            sys.exit(f"Dispatch aborted by user. Artifact retained locally at: {artifact_path}")

        sys.stdout.write(f"\nInitializing network dispatch to {config.destination}...\n")
        dispatch_artifact_to_kindle(artifact_path, config)
        sys.stdout.write("Pipeline execution complete.\n")

    except Exception as execution_error:
        sys.exit(f"Pipeline Terminated with Exception:\n{execution_error}")

if __name__ == "__main__":
    main()
