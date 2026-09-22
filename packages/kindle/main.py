import argparse
import sys
import os
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

from src.converter.epub_converter import convert_markdown_to_epub
from src.dispatcher.config import load_smtp_config
from src.dispatcher.mailer import dispatch_artifact_to_kindle
from src.domain.registry import KINDLE_MODELS

def main() -> None:
    parser = argparse.ArgumentParser(description="Artifact Compilation and Kindle Dispatch Pipeline")
    parser.add_argument("input_file", type=str, help="Target path to the source file (.md or .pdf)")
    parser.add_argument("--keep", action="store_true", help="Deprecated: artifacts are now auto-archived")
    parser.add_argument("--model", type=str, default="Oasis", choices=list(KINDLE_MODELS.keys()), help="Target Kindle model for optimization.")
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
        target_hardware = KINDLE_MODELS[arguments.model]

        if source_path.suffix.lower() == '.pdf':
            sys.stdout.write(f"Initiating PDF to Markdown pipeline via spliter for: {source_path.name}\n")

            # Using spliter to convert PDF to MD
            from src.converter.spliter_integration import convert_pdf_to_md
            md_path = convert_pdf_to_md(source_path)

            sys.stdout.write(f"Initiating EPUB compilation pipeline for generated markdown: {md_path.name} (Model: {arguments.model})\n")
            artifacts_to_dispatch.append(convert_markdown_to_epub(md_path, hardware_constraints=target_hardware))

        elif source_path.suffix.lower() == '.md':
            sys.stdout.write(f"Initiating EPUB compilation pipeline for: {source_path.name} (Model: {arguments.model})\n")
            artifacts_to_dispatch.append(convert_markdown_to_epub(source_path, hardware_constraints=target_hardware))
            
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
            sys.stdout.write(f"- File:  {archived_path.name} | Size: {size_mb:.2f} MB\n")

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
