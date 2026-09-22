import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
from src.converter.spliter_integration import convert_pdf_to_md


class TestSpliterIntegration(unittest.TestCase):
    def test_convert_pdf_to_md_cli_missing(self):
        # Test the scenario where cli.py doesn't exist.
        # We will patch Path.exists to always return False for cli.py,
        # but we need it to return True/False correctly for other things, or just mock selectively.

        # A simpler way is to just let it run against the real filesystem where we know what exists,
        # but we want to isolate it. Let's patch the specific Path object for cli_path.

        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "test_doc.pdf"
            with open(pdf_path, "wb") as f:
                f.write(b"%PDF-1.4 dummy")

            with patch(
                "src.converter.spliter_integration.Path.resolve"
            ) as mock_resolve:
                # Mock resolve to point to our temp dir where there is no cli.py
                mock_resolve.return_value = Path(temp_dir)

                with patch(
                    "src.converter.spliter_integration.PdfReader"
                ) as mock_pdf_reader:
                    mock_page = MagicMock()
                    mock_page.extract_text.return_value = "Extracted missing CLI text"
                    mock_reader_instance = MagicMock()
                    mock_reader_instance.pages = [mock_page]
                    mock_pdf_reader.return_value = mock_reader_instance

                    md_path = convert_pdf_to_md(pdf_path)

                    self.assertTrue(md_path.exists())
                    with open(md_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    self.assertIn("Extracted Content from test_doc.pdf", content)
                    self.assertIn("Extracted missing CLI text", content)
                    self.assertIn(
                        "spliter CLI not found or failed to execute.", content
                    )


if __name__ == "__main__":
    unittest.main()
