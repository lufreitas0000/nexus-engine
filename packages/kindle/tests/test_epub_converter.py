import unittest
from unittest.mock import patch, mock_open
import subprocess
from pathlib import Path
from src.converter.epub_converter import convert_markdown_to_epub

class TestEpubConverter(unittest.TestCase):

    @patch('src.converter.epub_converter.Path.exists')
    def test_file_not_found_raises_exception(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            convert_markdown_to_epub('invalid_path.md')

    @patch('src.converter.epub_converter.subprocess.run')
    @patch('src.converter.epub_converter.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="Abstract [[System|Dynamics]]")
    def test_subprocess_deterministic_failure(self, mock_file, mock_exists, mock_subprocess):
        mock_exists.return_value = True
        
        # Simulate an OS-level compilation failure from Pandoc
        mock_error = subprocess.CalledProcessError(
            returncode=1, 
            cmd=['pandoc'], 
            stderr="pandoc: AST parsing error at line 1"
        )
        mock_subprocess.side_effect = mock_error

        with self.assertRaises(RuntimeError) as context_manager:
            convert_markdown_to_epub('source.md')
        
        exception_message = str(context_manager.exception)
        self.assertIn("AST compilation failure", exception_message)
        self.assertIn("exited with code 1", exception_message)

if __name__ == '__main__':
    unittest.main()
