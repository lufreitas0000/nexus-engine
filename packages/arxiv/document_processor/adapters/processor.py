import os
import tarfile
import zipfile
import shutil
from pathlib import Path
from typing import Optional

from document_processor.domain.model import ProcessedDocument

class ArchiveProcessor:
    def process_archive(self, arxiv_id: str, archive_path: str, extract_dir: str) -> ProcessedDocument:
        try:
            if not os.path.exists(archive_path):
                raise FileNotFoundError(f"Archive not found: {archive_path}")

            os.makedirs(extract_dir, exist_ok=True)

            # If it's already a PDF, just copy it to extract_dir and set as main
            if archive_path.endswith(".pdf"):
                dest_path = Path(extract_dir) / f"{arxiv_id}.pdf"
                shutil.copy2(archive_path, dest_path)
                return ProcessedDocument(
                    arxiv_id=arxiv_id,
                    extracted_dir=extract_dir,
                    main_file_path=str(dest_path),
                    success=True
                )

            # Try extracting as tar
            self._extract_archive(archive_path, extract_dir)

            # Find main tex file
            main_file = self._find_main_tex_file(extract_dir)

            if main_file:
                return ProcessedDocument(
                    arxiv_id=arxiv_id,
                    extracted_dir=extract_dir,
                    main_file_path=str(main_file),
                    success=True
                )
            else:
                raise Exception("No main LaTeX file found in archive.")

        except Exception as e:
            return ProcessedDocument(
                arxiv_id=arxiv_id,
                extracted_dir=extract_dir,
                success=False,
                error=str(e)
            )

    def _extract_archive(self, archive_path: str, extract_dir: str) -> None:
        # ArXiv tar.gz might not have the .tar.gz extension, so we use module methods
        if tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, "r:*") as tar:
                tar.extractall(path=extract_dir)
        elif zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, "r") as zipf:
                zipf.extractall(path=extract_dir)
        else:
            raise Exception("Unsupported archive format.")

    def _find_main_tex_file(self, directory: str) -> Optional[Path]:
        tex_files = list(Path(directory).rglob("*.tex"))

        if not tex_files:
            return None

        if len(tex_files) == 1:
            return tex_files[0]

        # Search for \begin{document}
        for tex_file in tex_files:
            try:
                with open(tex_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if r"\begin{document}" in content:
                        return tex_file
            except Exception:
                continue

        return None
