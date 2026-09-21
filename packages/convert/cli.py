import typer

app = typer.Typer(help="Semantic PDF Pipeline CLI")

@app.command()
def convert() -> None:
    """
    Convert a PDF into a structured Markdown AST.
    """
    typer.echo("Converting PDF...")
    # Further implementation will go here based on user inputs/options

if __name__ == "__main__":
    app()
