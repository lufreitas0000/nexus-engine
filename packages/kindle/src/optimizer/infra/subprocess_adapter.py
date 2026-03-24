import subprocess
from pathlib import Path
from src.optimizer.domain.types import OptimizerConfig

def execute_k2pdfopt_rasterization(input_pdf: Path, output_pdf: Path, config: OptimizerConfig, page_count: int) -> Path:
    hw = config.hardware
    execution_vector = [
        config.binary_path,
        '-ui-', '-x',
        '-w', str(hw.width),
        '-h', str(hw.height),
        '-dpi', str(hw.dpi),
        '-m', hw.margin_crop,
        '-wrap', '-col', '2',
        '-o', str(output_pdf),
        str(input_pdf)
    ]
    
    timeout_limit = page_count * config.timeout_per_page_sec
    
    try:
        subprocess.run(
            execution_vector,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_limit
        )
    except subprocess.TimeoutExpired as timeout_err:
        raise RuntimeError(f"Rasterization timeout exceeded ({timeout_limit}s) for chunk: {input_pdf.name}") from timeout_err
    except subprocess.CalledProcessError as process_err:
        raise RuntimeError(f"k2pdfopt binary execution failed with code {process_err.returncode}.\nTrace: {process_err.stderr}") from process_err
        
    if not output_pdf.exists() or output_pdf.stat().st_size == 0:
        raise RuntimeError(f"k2pdfopt returned 0 but generated invalid artifact for chunk: {input_pdf.name}")
        
    return output_pdf
