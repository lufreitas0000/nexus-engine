import argparse
from pathlib import Path
import sys

# To enable importing across the workspace from the root script if uv sync doesn't magically link them in the PYTHONPATH for normal scripts
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "convert"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "arxiv"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nexus_workspace.resolver import get_workspace_path

def main():
    parser = argparse.ArgumentParser(description="Nexus Engine Unified Pipeline")
    parser.add_argument("input", type=str, help="PDF path or Arxiv ID")
    parser.add_argument("--device", type=str, default="Oasis", help="Target Kindle model")
    
    args = parser.parse_args()
    
    input_val = args.input
    ast_path = None
    
    workspace_root = get_workspace_path()
    output_dir = workspace_root / "data" / "ast"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if input_val.endswith(".pdf"):
            print(f"Routing PDF to Convert Pipeline: {input_val}")
            
            # Use the fallback logic from kindle's old convert_integration for now, or direct import if we write it properly.
            # Let's write the direct import of the pure pure function.
            # The Convert pipeline requires topology_analyzer, vision_extractor etc.
            # It's better to just call the convert CLI or Orchestrator.
            import subprocess
            convert_dir = Path(__file__).parent.parent.parent / "convert" / "app_structurizer"
            
            ast_path = output_dir / f"{Path(input_val).stem}.json"
            
            print(f"Running extract via subprocess...")
            subprocess.run(
                [sys.executable, "-m", "src.cli", "extract", str(Path(input_val).resolve()), "--output-dir", str(output_dir), "--use-fake"],
                cwd=str(convert_dir),
                check=True
            )
            
        else:
            print(f"Routing to Arxiv Scraper Pipeline for ID: {input_val}")
            from fetcher.src.infra.api import ArxivApiAdapter
            from document_converter.src.infra.converter import LatexToMarkdownConverter
            from fetcher.src.infra.tarball import TarballManager
            
            api = ArxivApiAdapter()
            paper = api.fetch_metadata(input_val)
            print(f"Fetched metadata: {paper.title}")
            
            tarball_mgr = TarballManager(workspace_root / "data" / "arxiv" / "tarballs")
            tar_path = tarball_mgr.download(input_val)
            source_dir = tarball_mgr.extract(tar_path)
            
            # Find main .tex file
            tex_files = list(Path(source_dir).rglob("*.tex"))
            if not tex_files:
                raise Exception("No .tex files found in arxiv tarball")
            
            converter = LatexToMarkdownConverter()
            result = converter.convert(paper, str(tex_files[0]), str(output_dir))
            if not result.success:
                raise Exception(f"Arxiv conversion failed: {result.error}")
                
            ast_path = Path(result.ast_path)

        if ast_path and ast_path.exists():
            print(f"AST generated successfully at {ast_path}. Routing to Kindle Delivery...")
            from src.converter.epub_converter import convert_ast_to_epub
            from src.domain.registry import KINDLE_MODELS
            
            target_hardware = KINDLE_MODELS.get(args.device, KINDLE_MODELS["Oasis"])
            epub_path = convert_ast_to_epub(ast_path, hardware_constraints=target_hardware)
            print(f"Pipeline finished! EPUB generated at: {epub_path}")
            
            # Phase 8: Automated DVC Hooks
            import subprocess
            print(f"Committing data state to DVC in {workspace_root}...")
            # Automatically add and commit the generated AST and EPUB into the DVC graph
            subprocess.run(["dvc", "add", str(ast_path.resolve())], cwd=str(workspace_root), check=False)
            subprocess.run(["dvc", "add", str(epub_path.resolve())], cwd=str(workspace_root), check=False)
            # We don't fail if DVC isn't initialized yet, but we trigger the hook.
            
        else:
            print("Pipeline failed to generate AST.")
            
    except Exception as e:
        print(f"Pipeline error: {e}")
        
if __name__ == "__main__":
    main()
