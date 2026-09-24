"""
book_studio/main.py — Book-Agnostic Pipeline CLI

Usage:
    python -m book_studio.main run-pipeline books/baym_quantum_mechanics_1969/book.yaml
    python -m book_studio.main run-pipeline books/baym_quantum_mechanics_1969/book.yaml --skip-ocr
    python -m book_studio.main run-pipeline books/baym_quantum_mechanics_1969/book.yaml --stage 3
"""
import json
import click
import subprocess
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from book_studio.pipeline.extractor import MarkerExtractor
from book_studio.pipeline.stitcher import CrossPageStitcher
from book_studio.pipeline.assembler import Assembler
from book_studio.core.assets import AssetManager
from book_studio.core.schemas import ExtractionResult


def load_book_config(book_yaml: Path) -> dict:
    """Load and validate a book.yaml configuration file."""
    if not book_yaml.exists():
        raise FileNotFoundError(f"book.yaml not found: {book_yaml}")
    if HAS_YAML:
        with open(book_yaml) as f:
            cfg = yaml.safe_load(f)
    else:
        # Fallback: minimal manual parse for key fields
        cfg = {}
        with open(book_yaml) as f:
            for line in f:
                if ':' in line and not line.strip().startswith('#'):
                    k, _, v = line.partition(':')
                    cfg[k.strip()] = v.strip().strip('"\'')
    return cfg


def get_book_dirs(book_yaml: Path) -> dict:
    """Derive all pipeline stage directories from the book.yaml location."""
    book_root = book_yaml.parent
    return {
        'root':      book_root,
        'raw':       book_root / '00_raw',
        'segmented': book_root / '01_segmented',
        'stitched':  book_root / '02_stitched',
        'verified_md': book_root / '03_verified_md',
        'final_tex': book_root / '04_final_tex',
        'figures':   book_root / '05_figures',
        'compiled':  book_root / '06_compiled',
    }


def save_state(data: ExtractionResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data.model_dump(), f, indent=2, ensure_ascii=False)
    print(f"  [✓] State saved: {path}")


def load_state(path: Path) -> ExtractionResult:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return ExtractionResult(**data)


def dvc_track(path: Path) -> None:
    try:
        subprocess.run(['dvc', 'add', str(path)], check=True,
                       capture_output=True, text=True)
        print(f"  [DVC] Tracked: {path.name}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  [!] DVC unavailable — skipping tracking for {path.name}")


@click.group()
def cli():
    """PDF Ingestion Pipeline — Multi-Book State Machine."""
    pass


@cli.command('run-pipeline')
@click.argument('book_yaml', type=click.Path(exists=True, path_type=Path))
@click.option('--skip-ocr', is_flag=True, help='Skip Stage 1 (load from 01_segmented).')
@click.option('--stage', default=None, type=int,
              help='Run only up to this stage (1=OCR, 2=Stitch, 3=Verify, 4=Assemble).')
def run_pipeline(book_yaml: Path, skip_ocr: bool, stage: int):
    """Run the full ingestion pipeline for a book defined by BOOK_YAML."""
    cfg  = load_book_config(book_yaml)
    dirs = get_book_dirs(book_yaml)
    book_id = cfg.get('book_id', book_yaml.parent.name)
    source_pdf_name = cfg.get('source_pdf', f'{book_id}.pdf')
    pdf_path = dirs['raw'] / source_pdf_name

    click.echo(f"\n📚 Book: {cfg.get('title', book_id)}")
    click.echo(f"   Author: {cfg.get('author_full', '?')}, {cfg.get('year', '?')}")
    click.echo(f"   Book root: {dirs['root']}\n")

    state_segmented = dirs['segmented'] / f'{book_id}.json'
    state_stitched  = dirs['stitched']  / f'{book_id}.json'
    state_verified  = dirs['segmented'] / f'{book_id}_verified.json'

    chunk_size = int(cfg.get('stages', {}).get('ocr_chunk_size', 3))

    # ── Stage 1: OCR Extraction ────────────────────────────────────────────
    if not skip_ocr:
        if not pdf_path.exists():
            raise FileNotFoundError(
                f"Source PDF not found: {pdf_path}\n"
                f"Place it in: {dirs['raw']}/"
            )
        click.echo(f"[Stage 1] Extracting: {pdf_path.name}  (chunk_size={chunk_size})")
        extractor = MarkerExtractor(chunk_size=chunk_size)
        raw_data = extractor.extract(pdf_path, dirs['segmented'])
        save_state(raw_data, state_segmented)
        dvc_track(state_segmented)
    else:
        click.echo(f"[Stage 1] Skipped — loading from: {state_segmented}")
        raw_data = load_state(state_segmented)

    if stage == 1:
        click.echo("[✓] Stopped at Stage 1."); return

    # ── Stage 1.5: Asset Routing ───────────────────────────────────────────
    click.echo("[Stage 1.5] Routing visual assets from figures/raw/ ...")
    source_img_dir = dirs['segmented'] / pdf_path.stem
    asset_manager = AssetManager(dirs['figures'] / 'raw')
    asset_data = asset_manager.process_and_route(raw_data, source_img_dir)

    # ── Stage 2: Cross-Page Stitching ─────────────────────────────────────
    click.echo("[Stage 2] Cross-page stitching ...")
    stitcher = CrossPageStitcher()
    stitched_data = stitcher.stitch(asset_data)
    save_state(stitched_data, state_stitched)
    dvc_track(state_stitched)

    if stage == 2:
        click.echo("[✓] Stopped at Stage 2."); return

    # ── Stage 3: Agent Verification ───────────────────────────────────────
    click.echo("[Stage 3] Agent verification hook ...")
    click.echo("  NOTE: For manual agent verification, use skills/02_stage3_verification/SKILL.md")
    click.echo(f"  Verified MD output directory: {dirs['verified_md']}")

    if stage == 3:
        click.echo("[✓] Stopped at Stage 3."); return

    # ── Stage 4: LaTeX Assembly ────────────────────────────────────────────
    click.echo("[Stage 4] Assembling LaTeX chunks ...")
    assembler = Assembler(dirs['verified_md'], dirs['final_tex'])
    assembler.assemble(stitched_data)

    click.echo(f"\n[✓] Pipeline complete.")
    click.echo(f"    Markdown: {dirs['verified_md']}/")
    click.echo(f"    LaTeX:    {dirs['final_tex']}/")
    click.echo(f"    Next: python {dirs['compiled']}/generate_main_tex.py && pdflatex {dirs['compiled']}/{book_id}.tex")


@cli.command('compile')
@click.argument('book_yaml', type=click.Path(exists=True, path_type=Path))
def compile_book(book_yaml: Path):
    """Regenerate master .tex and compile to PDF for a book."""
    cfg  = load_book_config(book_yaml)
    dirs = get_book_dirs(book_yaml)
    book_id = cfg.get('book_id', book_yaml.parent.name)

    gen_script = dirs['compiled'] / 'generate_main_tex.py'
    master_tex = dirs['compiled'] / f'{book_id}.tex'

    if gen_script.exists():
        click.echo(f"[compile] Generating {master_tex.name} ...")
        subprocess.run(['python3', str(gen_script)], check=True)
    else:
        click.echo(f"[!] No generate_main_tex.py found in {dirs['compiled']}")
        return

    click.echo(f"[compile] Running pdflatex ...")
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', str(master_tex)],
        cwd=dirs['compiled'],
        capture_output=True, text=True
    )
    if 'Output written on' in result.stdout:
        click.echo(f"[✓] PDF compiled: {dirs['compiled']}/{book_id}.pdf")
    else:
        click.echo(f"[!] Compilation may have errors. Check: {dirs['compiled']}/{book_id}.log")
        click.echo(result.stdout[-2000:])


if __name__ == '__main__':
    cli()
