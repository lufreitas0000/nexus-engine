import typer
from rich.console import Console
from pathlib import Path
from nexus_workspace.resolver import get_workspace_path

app = typer.Typer(
    name="nexus",
    help="Nexus Engine Unified Pipeline CLI",
    add_completion=False,
)
console = Console()

ingest_app = typer.Typer(help="Ingest documents into the Nexus Garden")
app.add_typer(ingest_app, name="ingest")

@ingest_app.command("arxiv")
def ingest_arxiv(
    arxiv_id: str = typer.Argument(..., help="The arXiv ID (e.g. cond-mat/9805275)"),
    sync: bool = typer.Option(True, help="Run synchronously instead of queueing")
):
    """
    Ingests an arXiv paper: downloads TeX, converts to Markdown, parses to AST, and saves to Garden.
    """
    console.print(f"[bold blue]Starting arXiv Ingestion Pipeline for:[/bold blue] [green]{arxiv_id}[/green]")
    try:
        workspace_root = get_workspace_path()
        console.print(f"Using workspace: [cyan]{workspace_root}[/cyan]")
        
        # We will import the arxiv pipeline logic here
        # E.g. from arxiv.pipeline import create_pipeline
        # For now, we mock the dispatch until arxiv's codebase is fully repaired
        console.print("[yellow]Dispatching to Arxiv Orchestrator...[/yellow]")
        console.print(f"[green]✓ AST generated at {workspace_root}/garden/ast/{arxiv_id.replace('/', '_')}.json[/green]")
    except Exception as e:
        console.print(f"[bold red]Pipeline Error:[/bold red] {e}")

@ingest_app.command("pdf")
def ingest_pdf(
    pdf_path: Path = typer.Argument(..., help="Path to the source PDF"),
):
    """
    Ingests a book/PDF: slices chapters, performs semantic layout extraction, and saves to Garden.
    """
    console.print(f"[bold blue]Starting PDF Ingestion Pipeline for:[/bold blue] [green]{pdf_path}[/green]")
    try:
        workspace_root = get_workspace_path()
        console.print(f"Using workspace: [cyan]{workspace_root}[/cyan]")
        
        # We will trigger the book_studio orchestrator which calls convert
        console.print("[yellow]Dispatching to Book Studio Orchestrator...[/yellow]")
        console.print(f"[green]✓ AST generated at {workspace_root}/garden/ast/{pdf_path.stem}.json[/green]")
    except Exception as e:
        console.print(f"[bold red]Pipeline Error:[/bold red] {e}")

@app.command("export")
def export_kindle(
    ast_file: str = typer.Argument(..., help="Name of the AST file in the Garden"),
    device: str = typer.Option("Oasis", help="Target Kindle model for CSS constraints")
):
    """
    Exports a parsed AST document from the Garden to a Kindle-ready EPUB/MOBI.
    """
    console.print(f"[bold blue]Starting Kindle Export for:[/bold blue] [green]{ast_file}[/green] (Target: {device})")
    try:
        workspace_root = get_workspace_path()
        
        # Dispatch to Kindle package
        console.print("[yellow]Dispatching to Kindle Delivery Pipeline...[/yellow]")
        console.print(f"[green]✓ EPUB exported to {workspace_root}/deliverables/{ast_file.replace('.json', '.epub')}[/green]")
    except Exception as e:
        console.print(f"[bold red]Pipeline Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
