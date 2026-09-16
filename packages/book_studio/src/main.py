import json
import click
import subprocess
from pathlib import Path
from src.tools.extractor import MarkerExtractor
from src.core.stitcher import CrossPageStitcher
from src.core.assembler import Assembler
from src.core.schemas import ExtractionResult

def save_state(data: ExtractionResult, path: Path) -> None:
    """Serializes pipeline state to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data.model_dump(), f, indent=2, ensure_ascii=False)

def load_state(path: Path) -> ExtractionResult:
    """Loads pipeline state from disk."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ExtractionResult(**data)

def dvc_track(path: Path) -> None:
    """Tracks intermediate files deterministically via DVC."""
    subprocess.run(["dvc", "add", str(path)], check=True, capture_output=True)

@click.group()
def cli():
    """PDF Ingestion Pipeline - State Machine Controller."""
    pass

@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@click.option('--skip-ocr', is_flag=True, help="Skip extraction and load from 02_segmented state.")
def run_pipeline(pdf_path: Path, skip_ocr: bool):
    """Executes the deterministic ingestion pipeline."""
    project_root = Path(__file__).parent.parent
    
    dir_segmented = project_root / "data" / "02_segmented"
    dir_stitched = project_root / "data" / "03_stitched"
    dir_verified = project_root / "data" / "04_verified"
    dir_md = project_root / "data" / "06_final_md"
    dir_tex = project_root / "data" / "07_final_tex"

    state_segmented = dir_segmented / f"{pdf_path.stem}.json"
    state_stitched = dir_stitched / f"{pdf_path.stem}.json"
    state_verified = dir_verified / f"{pdf_path.stem}.json"

    # Stage 1: Extraction
    if not skip_ocr:
        click.echo(f"[*] Stage 1: Extracting {pdf_path.name}...")
        extractor = MarkerExtractor()
        raw_data = extractor.extract(pdf_path, dir_segmented)
        save_state(raw_data, state_segmented)
        dvc_track(state_segmented)
    else:
        click.echo(f"[*] Stage 1: Loading existing extraction from {state_segmented}...")
        raw_data = load_state(state_segmented)

    # Stage 2: Cross-Page Stitching
    click.echo("[*] Stage 2: Deterministic Cross-Page Stitching...")
    stitcher = CrossPageStitcher()
    stitched_data = stitcher.stitch(raw_data)
    save_state(stitched_data, state_stitched)
    dvc_track(state_stitched)

    # Stage 3: Verification (Agent Interception Point)
    click.echo("[*] Stage 3: Agent Verification Hook (Pass-through for now)...")
    # Note: Orchestrator agent will halt execution here, invoke Physics/LaTeX subagents, 
    # mutate the stitched_data, and then resume. For the baseline, we pass it through.
    verified_data = stitched_data 
    save_state(verified_data, state_verified)
    dvc_track(state_verified)

    # Stage 4: Semantic Assembly
    click.echo("[*] Stage 4: Semantic Chunking and Assembly...")
    assembler = Assembler(dir_md, dir_tex)
    assembler.assemble(verified_data)
    
    click.echo("[*] Pipeline execution complete. Outputs generated in 06_final_md and 07_final_tex.")

if __name__ == "__main__":
    cli()
