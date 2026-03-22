import re
import subprocess
import tempfile
from pathlib import Path

def convert_markdown_to_epub(input_path: Path | str, output_path: Path | str | None = None) -> Path:
    input_file = Path(input_path).resolve()
    
    if not input_file.exists():
        raise FileNotFoundError(f"Source markdown file not located: {input_file}")

    if output_path is None:
        output_file = input_file.with_suffix('.epub')
    else:
        output_file = Path(output_path).resolve()

    with open(input_file, 'r', encoding='utf-8') as file_descriptor:
        source_content = file_descriptor.read()

    processed_content = re.sub(r'\[\[(.*?)\|(.*?)\]\]', r'[\2](\1.md)', source_content)
    processed_content = re.sub(r'\[\[(.*?)\]\]', r'[\1](\1.md)', processed_content)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_buffer:
        temp_buffer.write(processed_content)
        temp_file_path = temp_buffer.name

    execution_vector = [
        'pandoc',
        temp_file_path,
        '-f', 'markdown',
        '-t', 'epub3',
        '--mathml',
        '-o', str(output_file)
    ]

    try:
        subprocess.run(
            execution_vector,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as process_error:
        Path(temp_file_path).unlink(missing_ok=True)
        raise RuntimeError(
            f"AST compilation failure. Pandoc exited with code {process_error.returncode}.\n"
            f"Error trace: {process_error.stderr}"
        ) from process_error

    Path(temp_file_path).unlink(missing_ok=True)
    
    return output_file
