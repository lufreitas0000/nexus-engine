from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import Destination

def extract_metadata(input_path: Path) -> dict:
    reader = PdfReader(input_path)
    meta = reader.metadata
    return {
        '/Title': meta.title if meta and meta.title else input_path.stem,
        '/Author': meta.author if meta and meta.author else "Automated Pipeline"
    }

def _get_bookmark_page_indices(reader: PdfReader) -> list[int]:
    indices = set([0])
    for outline_item in reader.outline:
        if isinstance(outline_item, Destination):
            page_idx = reader.get_page_number(outline_item.page)
            if page_idx != -1:
                indices.add(page_idx)
        elif isinstance(outline_item, list) and isinstance(outline_item[0], Destination):
            page_idx = reader.get_page_number(outline_item[0].page)
            if page_idx != -1:
                indices.add(page_idx)
    sorted_indices = sorted(list(indices))
    if sorted_indices and sorted_indices[-1] != len(reader.pages):
        sorted_indices.append(len(reader.pages))
    return sorted_indices

def partition_pdf(input_path: Path, temp_dir: Path, threshold: int, fallback_chunk: int) -> list[Path]:
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    boundaries = []
    if total_pages > threshold and reader.outline:
        boundaries = _get_bookmark_page_indices(reader)
        
    if len(boundaries) < 3:
        boundaries = list(range(0, total_pages, fallback_chunk))
        if boundaries[-1] != total_pages:
            boundaries.append(total_pages)

    chunk_paths = []
    for idx in range(len(boundaries) - 1):
        start = boundaries[idx]
        end = boundaries[idx + 1]
        
        writer = PdfWriter()
        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])
            
        chunk_path = temp_dir / f"chunk_{idx:04d}.pdf"
        with open(chunk_path, "wb") as f_out:
            writer.write(f_out)
        chunk_paths.append(chunk_path)
        
    return chunk_paths

def merge_and_inject_metadata(chunk_paths: list[Path], output_path: Path, metadata: dict) -> Path:
    writer = PdfWriter()
    for chunk in sorted(chunk_paths):
        reader = PdfReader(chunk)
        writer.append_pages_from_reader(reader)
        
    writer.add_metadata(metadata)
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
        
    return output_path
