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
    parser.add_argument("--keep", action="store_true", help="Deprecated: artifacts are now auto-archived")
    arguments = parser.parse_args()
    
    source_path = Path(arguments.input_file).resolve()
    if not source_path.exists():
        sys.exit(f"Fatal: Input boundary invalid. Target file not found.\nPath evaluated: {source_path}")

    load_dotenv()
    artifacts_dir = Path("artifacts").resolve()
    artifacts_dir.mkdir(exist_ok=True)

    try:
        config = load_smtp_config()
        artifacts_to_dispatch = []

        if source_path.suffix.lower() == '.md':
            sys.stdout.write(f"Initiating EPUB compilation pipeline for: {source_path.name}\n")
            artifacts_to_dispatch.append(convert_markdown_to_epub(source_path))
            
        elif source_path.suffix.lower() == '.pdf':
            sys.stdout.write(f"Initiating PDF optimization pipeline for: {source_path.name}\n")
            opt_config = OptimizerConfig(
                binary_path=os.getenv('K2PDFOPT_PATH', 'k2pdfopt'),
                hardware=TargetHardwareConstraints()
            )
            # The orchestrator now returns a list of artifacts (handling dynamic splits)
            artifacts_to_dispatch.extend(optimize_pdf_for_oasis(source_path, opt_config))
            
        else:
            sys.exit(f"Fatal: Unsupported file extension {source_path.suffix}.")

        # Archival and Validation Phase
        sys.stdout.write(f"\nArtifact Validation Complete:\n")
        archived_paths = []
        for artifact in artifacts_to_dispatch:
            archived_path = artifacts_dir / artifact.name
            shutil.move(str(artifact), str(archived_path))
            archived_paths.append(archived_path)
            
            size_mb = archived_path.stat().st_size / (1024 * 1024)
            pages = len(PdfReader(archived_path).pages) if archived_path.suffix.lower() == '.pdf' else "N/A"
            sys.stdout.write(f"- File:  {archived_path.name} | Pages: {pages} | Size: {size_mb:.2f} MB\n")

        # Interactive Gate
        user_intent = input(f"\nDispatch to {config.destination}? [y/N]: ").strip().lower()
        if user_intent != 'y':
            sys.exit(f"Dispatch aborted by user. Artifacts retained locally in: {artifacts_dir}")

        sys.stdout.write(f"\nInitializing network dispatch to {config.destination}...\n")
        for artifact in archived_paths:
            dispatch_artifact_to_kindle(artifact, config)
            
        sys.stdout.write("Pipeline execution complete.\n")

    except Exception as execution_error:
        sys.exit(f"Pipeline Terminated with Exception:\n{execution_error}")

if __name__ == "__main__":
    main()
