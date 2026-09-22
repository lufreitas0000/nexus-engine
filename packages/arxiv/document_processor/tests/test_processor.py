import pytest
import os
import tarfile
import tempfile
from pathlib import Path

from document_processor.adapters.processor import ArchiveProcessor

def test_processor_with_pdf():
    processor = ArchiveProcessor()
    arxiv_id = "1234"

    with tempfile.TemporaryDirectory() as tempdir:
        pdf_path = os.path.join(tempdir, f"{arxiv_id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"fake pdf")

        extract_dir = os.path.join(tempdir, "extract")

        result = processor.process_archive(arxiv_id, pdf_path, extract_dir)

        assert result.success is True
        assert result.main_file_path is not None
        assert result.main_file_path.endswith(".pdf")
        assert os.path.exists(result.main_file_path)

def test_processor_with_tar_finding_main_tex():
    processor = ArchiveProcessor()
    arxiv_id = "5678"

    with tempfile.TemporaryDirectory() as tempdir:
        # Create a dummy tar containing two tex files, one with begin document
        tar_path = os.path.join(tempdir, f"{arxiv_id}.tar.gz")

        main_tex_path = os.path.join(tempdir, "main.tex")
        with open(main_tex_path, "w") as f:
            f.write("some latex \\begin{document} content")

        aux_tex_path = os.path.join(tempdir, "aux.tex")
        with open(aux_tex_path, "w") as f:
            f.write("just some macros")

        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(main_tex_path, arcname="main.tex")
            tar.add(aux_tex_path, arcname="aux.tex")

        extract_dir = os.path.join(tempdir, "extract")

        result = processor.process_archive(arxiv_id, tar_path, extract_dir)

        assert result.success is True
        assert result.main_file_path is not None
        assert result.main_file_path.endswith("main.tex")
        assert os.path.exists(result.main_file_path)
