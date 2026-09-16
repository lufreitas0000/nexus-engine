import subprocess
import json
from pathlib import Path
from abc import ABC, abstractmethod
from src.core.schemas import ExtractionResult

class BaseExtractor(ABC):
    """Abstract contract for PDF extraction tools."""
    @abstractmethod
    def extract(self, pdf_path: Path, output_dir: Path) -> ExtractionResult:
        pass

class MarkerExtractor(BaseExtractor):
    """Concrete implementation utilizing marker-pdf via CLI subprocess."""
    
    def extract(self, pdf_path: Path, output_dir: Path) -> ExtractionResult:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # marker_single creates a subfolder with the PDF stem name
        result = subprocess.run(
            [
                "marker_single", 
                str(pdf_path), 
                "--output_format", "json",
                "--output_dir", str(output_dir)
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Marker extraction failed:\n{result.stderr}")
            
        expected_json = output_dir / pdf_path.stem / f"{pdf_path.stem}.json"
        if not expected_json.exists():
            raise FileNotFoundError(f"Expected JSON output not found at {expected_json}")
            
        with open(expected_json, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        return ExtractionResult(**raw_data)
