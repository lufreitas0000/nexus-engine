import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from abc import ABC, abstractmethod
from src.core.schemas import ExtractionResult, Page

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, pdf_path: Path, output_dir: Path) -> ExtractionResult:
        pass

class MarkerExtractor(BaseExtractor):
    """Memory-safe chunked extraction. Splits PDF to prevent WSL OOM kills."""

    def __init__(self, chunk_size: int = 30):
        self.chunk_size = chunk_size

    def extract(self, pdf_path: Path, output_dir: Path) -> ExtractionResult:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        aggregated_pages = []
        global_metadata = {}

        # Isolate processing into a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for start_idx in range(0, total_pages, self.chunk_size):
                end_idx = min(start_idx + self.chunk_size, total_pages)
                print(f"    -> Extracting pages {start_idx + 1} to {end_idx} of {total_pages}...")

                # 1. Create physical chunk
                chunk_pdf_path = temp_path / f"chunk_{start_idx}.pdf"
                writer = PdfWriter()
                for i in range(start_idx, end_idx):
                    writer.add_page(reader.pages[i])

                with open(chunk_pdf_path, "wb") as f:
                    writer.write(f)

                # 2. Execute isolated OCR subprocess
                # This guarantees RAM is freed upon subprocess termination
                chunk_output_dir = temp_path / f"out_{start_idx}"
                chunk_output_dir.mkdir()

                result = subprocess.run(
                    [
                        "marker_single",
                        str(chunk_pdf_path),
                        "--output_format", "json",
                        "--output_dir", str(chunk_output_dir)
                    ],
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    error_log = output_dir / f"error_chunk_{start_idx}.log"
                    error_log.write_text(result.stderr)
                    raise RuntimeError(f"OCR failed at chunk {start_idx}. Error log dumped to {error_log}")

                # 3. Parse JSON and offset page numbers
                expected_json = chunk_output_dir / f"chunk_{start_idx}" / f"chunk_{start_idx}.json"
                if not expected_json.exists():
                    raise FileNotFoundError(f"Expected JSON not found: {expected_json}")

                with open(expected_json, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)

                if not global_metadata:
                    global_metadata = chunk_data.get("metadata", {})

                # Offset page numbers to align with the original 600-page document
                for page_dict in chunk_data.get("pages", []):
                    page = Page(**page_dict)
                    if page.page_number is not None:
                        # Marker internally numbers the chunk from 1 to N
                        # We subtract 1 to get a 0-index, add start_idx, and add 1 back.
                        page.page_number = (page.page_number - 1) + start_idx + 1
                    aggregated_pages.append(page)

                # 4. Route physical image files out of the isolated temp directory
                final_img_dir = output_dir / pdf_path.stem
                final_img_dir.mkdir(parents=True, exist_ok=True)
                for img_file in (chunk_output_dir / f"chunk_{start_idx}").iterdir():
                    if img_file.is_file() and img_file.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                        shutil.copy2(img_file, final_img_dir / img_file.name)

        print("[*] All chunks extracted and successfully aggregated.")
        return ExtractionResult(metadata=global_metadata, pages=aggregated_pages)
