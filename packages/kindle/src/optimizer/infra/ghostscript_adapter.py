import subprocess
from pathlib import Path

def compress_pdf_artifact(input_path: Path, output_path: Path) -> Path:
    execution_vector = [
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/ebook',
        '-dColorConversionStrategy=/Gray',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_path}',
        str(input_path)
    ]
    
    try:
        subprocess.run(
            execution_vector,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as process_error:
        raise RuntimeError(
            f"Ghostscript compression failed with code {process_error.returncode}.\n"
            f"Trace: {process_error.stderr}"
        ) from process_error
        
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("Ghostscript returned 0 but generated an invalid artifact.")
        
    return output_path
