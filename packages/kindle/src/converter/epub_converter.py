import re
import subprocess
import tempfile
from pathlib import Path

from src.domain.types import TargetHardwareConstraints


def convert_markdown_to_epub(
    input_path: Path | str,
    output_path: Path | str | None = None,
    hardware_constraints: TargetHardwareConstraints | None = None,
) -> Path:
    input_file = Path(input_path).resolve()

    if not input_file.exists():
        raise FileNotFoundError(f"Source markdown file not located: {input_file}")

    if output_path is None:
        output_file = input_file.with_suffix(".epub")
    else:
        output_file = Path(output_path).resolve()

    with open(input_file, "r", encoding="utf-8") as file_descriptor:
        source_content = file_descriptor.read()

    # Phase 1: Regex boundary substitutions
    processed_content = re.sub(r"\[\[(.*?)\|(.*?)\]\]", r"[\2](\1.md)", source_content)
    processed_content = re.sub(r"\[\[(.*?)\]\]", r"[\1](\1.md)", processed_content)
    processed_content = re.sub(r"==(.*?)==", r"\1", processed_content)

    # Phase 2: Metadata Extraction
    title_match = re.search(r"^#\s+(.+)$", source_content, flags=re.MULTILINE)
    document_title = title_match.group(1).strip() if title_match else input_file.stem

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as temp_buffer:
        temp_buffer.write(processed_content)
        temp_file_path = temp_buffer.name

    css_path = Path(__file__).parent / "kindle.css"

    # If hardware constraints are provided, generate a temporary CSS with overrides
    temp_css_path = None
    if hardware_constraints:
        with open(css_path, "r", encoding="utf-8") as f:
            base_css = f.read()

        # Example override: Adjusting margins based on margin_crop (interpreted as relative margin size for epub)
        # Margin crop in k2pdfopt represents how much margin to crop, so lower margin_crop means smaller device margins needed.
        margin_percentage = float(hardware_constraints.margin_crop) * 10
        margin_override = f"\n@page {{ margin: {margin_percentage}% !important; }}"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".css", delete=False, encoding="utf-8"
        ) as temp_css:
            temp_css.write(base_css + margin_override)
            temp_css_path = temp_css.name

        final_css_path = temp_css_path
    else:
        final_css_path = str(css_path)

    # Phase 3: AST Compilation Execution Vector
    execution_vector = [
        "pandoc",
        temp_file_path,
        "-f",
        "markdown",
        "-t",
        "epub3",
        "--mathml",
        "--css",
        final_css_path,
        "--metadata",
        f"title={document_title}",
        "--metadata",
        "author=Freitas",
        "--metadata",
        "language=pt-BR",
        "-o",
        str(output_file),
    ]

    try:
        subprocess.run(execution_vector, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as process_error:
        Path(temp_file_path).unlink(missing_ok=True)
        if temp_css_path:
            Path(temp_css_path).unlink(missing_ok=True)
        raise RuntimeError(
            f"AST compilation failure. Pandoc exited with code {process_error.returncode}.\n"
            f"Error trace: {process_error.stderr}"
        ) from process_error

    Path(temp_file_path).unlink(missing_ok=True)
    if temp_css_path:
        Path(temp_css_path).unlink(missing_ok=True)

    return output_file
