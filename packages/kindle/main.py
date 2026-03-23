import argparse
import sys
from pathlib import Path
from src.converter.epub_converter import convert_markdown_to_epub
from src.dispatcher.config import load_smtp_config
from src.dispatcher.mailer import dispatch_artifact_to_kindle

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Artifact Compilation and Kindle Dispatch Pipeline"
    )
    parser.add_argument(
        "input_file", 
        type=str, 
        help="Target path to the source file (.md or .pdf)"
    )
    parser.add_argument(
        "--keep", 
        action="store_true", 
        help="Retain the generated artifact on the filesystem post-transmission"
    )
    
    arguments = parser.parse_args()
    source_path = Path(arguments.input_file).resolve()

    if not source_path.exists():
        sys.exit(f"Fatal: Input boundary invalid. Target file not found.\nPath evaluated: {source_path}")

    try:
        config = load_smtp_config()

        # Phase 2 & 5: Extensible routing logic
        if source_path.suffix.lower() == '.md':
            sys.stdout.write(f"Initiating EPUB compilation pipeline for: {source_path.name}\n")
            artifact_path = convert_markdown_to_epub(source_path)
            sys.stdout.write(f"Artifact generated: {artifact_path.name}\n")
        elif source_path.suffix.lower() == '.pdf':
            sys.exit("Fatal: PDF optimization module (Phase 3) is not yet implemented.")
        else:
            sys.exit(f"Fatal: Unsupported file extension {source_path.suffix}. Expected .md or .pdf.")

        sys.stdout.write(f"Initializing network dispatch to {config.destination}...\n")
        dispatch_artifact_to_kindle(artifact_path, config)
        sys.stdout.write("Pipeline execution complete.\n")

        if not arguments.keep:
            artifact_path.unlink(missing_ok=True)
            sys.stdout.write("Transient artifact purged from local storage.\n")

    except (EnvironmentError, FileNotFoundError, RuntimeError) as execution_error:
        sys.exit(f"Pipeline Terminated with Exception:\n{execution_error}")

if __name__ == "__main__":
    main()
