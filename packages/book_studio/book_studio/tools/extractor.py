import subprocess
import json
import tempfile
import shutil
import fitz  # PyMuPDF
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from abc import ABC, abstractmethod
from book_studio.core.schemas import ExtractionResult, Page

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, pdf_path: Path, output_dir: Path) -> ExtractionResult:
        pass

class MarkerExtractor(BaseExtractor):
    """Memory-safe chunked extraction. Splits PDF to prevent WSL OOM kills."""

    def __init__(self, chunk_size: int = 3):
        self.chunk_size = chunk_size

    def extract_images_from_chunk(self, doc_chunk: fitz.Document, chunk_data: dict, final_img_dir: Path, start_idx: int):
        # Extract images using fitz based on the polygon from marker
        for page_dict in chunk_data.get("children", []):
            # Page number is not directly stored in children for JSON mode,
            # so we try to extract it from the page id like /page/1/Page/1
            page_id = page_dict.get("id", "")
            page_num_in_chunk = 0
            if "/page/" in page_id:
                try:
                    page_num_in_chunk = int(page_id.split("/")[2]) - 1
                except:
                    pass
            if page_num_in_chunk < 0 or page_num_in_chunk >= len(doc_chunk):
                continue

            fitz_page = doc_chunk[page_num_in_chunk]
            page_width = fitz_page.rect.width
            page_height = fitz_page.rect.height

            for block in page_dict.get("children", []):
                # We can extract Picture, Table, or Equation
                if block.get("block_type") in ["Picture", "PictureGroup", "Figure", "FigureGroup", "Diagram", "Table"]:
                    polygon = block.get("polygon")
                    block_id = block.get("id", "").replace("/", "_")
                    if polygon and len(polygon) >= 2:
                        # Find min/max x and y
                        xs = [pt[0] for pt in polygon]
                        ys = [pt[1] for pt in polygon]
                        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)

                        # Clip to page bounds
                        x0 = max(0, x0)
                        y0 = max(0, y0)
                        x1 = min(page_width, x1)
                        y1 = min(page_height, y1)

                        if x1 > x0 and y1 > y0:
                            rect = fitz.Rect(x0, y0, x1, y1)
                            pix = fitz_page.get_pixmap(clip=rect, dpi=200) # High-res
                            img_path = final_img_dir / f"{block_id}.png"
                            pix.save(str(img_path))


    def extract(self, pdf_path: Path, output_dir: Path) -> ExtractionResult:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        chunks_dir = output_dir / f"{pdf_path.stem}_chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        final_img_dir = output_dir / pdf_path.stem
        final_img_dir.mkdir(parents=True, exist_ok=True)

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        aggregated_pages = []
        global_metadata = {}

        # Isolate processing into a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for start_idx in range(0, total_pages, self.chunk_size):
                end_idx = min(start_idx + self.chunk_size, total_pages)

                chunk_state_file = chunks_dir / f"chunk_{start_idx}.json"

                if chunk_state_file.exists():
                    print(f"    -> Skipping pages {start_idx + 1} to {end_idx} of {total_pages} (Already processed)...")
                    with open(chunk_state_file, 'r', encoding='utf-8') as f:
                        chunk_data = json.load(f)
                        if not global_metadata:
                            global_metadata = chunk_data.get("metadata", {})
                        for page_dict in chunk_data.get("pages", []):
                            aggregated_pages.append(Page(**page_dict))
                    continue

                print(f"    -> Extracting pages {start_idx + 1} to {end_idx} of {total_pages}...")

                # 1. Create physical chunk
                chunk_pdf_path = temp_path / f"chunk_{start_idx}.pdf"
                writer = PdfWriter()
                for i in range(start_idx, end_idx):
                    writer.add_page(reader.pages[i])

                with open(chunk_pdf_path, "wb") as f:
                    writer.write(f)

                # 2. Execute isolated OCR subprocess
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

                # 3.5 Use fitz to extract images manually since marker json mode drops them
                try:
                    fitz_doc = fitz.open(str(chunk_pdf_path))
                    self.extract_images_from_chunk(fitz_doc, chunk_data, final_img_dir, start_idx)
                    fitz_doc.close()
                except Exception as e:
                    print(f"    -> Warning: Image extraction failed for chunk {start_idx}: {e}")

                # Save modified pages back to our tracking
                processed_pages_in_chunk = []
                for page_dict in chunk_data.get("children", []):
                    # For our Page schema, we need to convert the blocks/children structure
                    # JSONBlockOutput has 'children' for elements on the page
                    blocks_data = []
                    for child_block in page_dict.get("children", []):
                        blocks_data.append({
                            "id": child_block.get("id"),
                            "block_type": child_block.get("block_type"),
                            "content": child_block.get("html", ""),
                            "polygon": child_block.get("polygon")
                        })

                    page_id = page_dict.get("id", "")
                    page_num_in_chunk = 0
                    if "/page/" in page_id:
                        try:
                            page_num_in_chunk = int(page_id.split("/")[2]) - 1
                        except:
                            pass

                    page = Page(page_number=page_num_in_chunk + start_idx + 1, blocks=blocks_data)
                    aggregated_pages.append(page)
                    processed_pages_in_chunk.append(page.model_dump())

                # Save the independent chunk state
                chunk_state_data = {
                    "metadata": global_metadata,
                    "pages": processed_pages_in_chunk
                }
                with open(chunk_state_file, 'w', encoding='utf-8') as f:
                    json.dump(chunk_state_data, f, indent=2, ensure_ascii=False)

        print("[*] All chunks extracted and successfully aggregated.")
        return ExtractionResult(metadata=global_metadata, pages=aggregated_pages)
