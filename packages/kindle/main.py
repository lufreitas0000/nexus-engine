import argparse
import sys
from pathlib import Path
from src.converter.epub_converter import convert_markdown_to_epub
from src.dispatcher.config import load_smtp_config
from src.dispatcher.mailer import dispatch_epub_to_kindle

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Markdown to EPUB Compilation and Kindle Dispatch Pipeline"
    )
    parser.add_argument(
        "input_file", 
        type=str, 
        help="Target path to the source Markdown file"
    )
    parser.add_argument(
        "--keep", 
        action="store_true", 
        help="Retain the generated EPUB artifact on the filesystem post-transmission"
    )
    
    arguments = parser.parse_args()
    source_path = Path(arguments.input_file).resolve()

    if not source_path.exists() or source_path.suffix.lower() != '.md':
        sys.exit(f"Fatal: Input boundary invalid. Target must be an existing .md file.\nPath evaluated: {source_path}")

    try:
        # Phase 1: Environment State Validation
        config = load_smtp_config()

        # Phase 2: Pre-processing and AST Compilation
        sys.stdout.write(f"Initiating compilation pipeline for: {source_path.name}\n")
        epub_artifact_path = convert_markdown_to_epub(source_path)
        sys.stdout.write(f"Artifact generated: {epub_artifact_path.name}\n")

        # Phase 3: TLS Network Dispatch
        sys.stdout.write(f"Initializing network dispatch to {config.destination}...\n")
        dispatch_epub_to_kindle(epub_artifact_path, config)
        sys.stdout.write("Transmission successful.\n")

        # Phase 4: Filesystem State Reversion
        if not arguments.keep:
            epub_artifact_path.unlink(missing_ok=True)
            sys.stdout.write("Transient EPUB artifact purged from local storage.\n")

    except (EnvironmentError, FileNotFoundError, RuntimeError) as execution_error:
        sys.exit(f"Pipeline Terminated with Exception:\n{execution_error}")

if __name__ == "__main__":
    main()
