import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess

from src.optimizer.domain.types import OptimizerConfig, TargetHardwareConstraints
from src.optimizer.services.orchestrator import optimize_pdf_for_oasis
from src.optimizer.infra.subprocess_adapter import execute_k2pdfopt_rasterization
from src.optimizer.infra.ghostscript_adapter import compress_pdf_artifact

class TestPdfOptimizerInfrastructure(unittest.TestCase):
    def setUp(self):
        self.config = OptimizerConfig(
            binary_path="k2pdfopt",
            hardware=TargetHardwareConstraints(),
            timeout_per_page_sec=1.0
        )
        self.input_path = Path("mock_input.pdf")
        self.output_path = Path("mock_output.pdf")

    @patch('src.optimizer.infra.subprocess_adapter.subprocess.run')
    @patch('src.optimizer.infra.subprocess_adapter.Path.exists')
    @patch('src.optimizer.infra.subprocess_adapter.Path.stat')
    def test_k2pdfopt_successful_execution(self, mock_stat, mock_exists, mock_run):
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024
        mock_run.return_value = MagicMock(returncode=0)

        result = execute_k2pdfopt_rasterization(self.input_path, self.output_path, self.config, page_count=5)
        self.assertEqual(result, self.output_path)
        mock_run.assert_called_once()

    @patch('src.optimizer.infra.ghostscript_adapter.subprocess.run')
    @patch('src.optimizer.infra.ghostscript_adapter.Path.exists')
    @patch('src.optimizer.infra.ghostscript_adapter.Path.stat')
    def test_ghostscript_successful_execution(self, mock_stat, mock_exists, mock_run):
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 512 # Compressed size
        mock_run.return_value = MagicMock(returncode=0)
        
        result = compress_pdf_artifact(self.input_path, self.output_path)
        self.assertEqual(result, self.output_path)
        
        executed_args = mock_run.call_args[0][0]
        self.assertIn('-dPDFSETTINGS=/ebook', executed_args)

class TestPdfOptimizerOrchestrator(unittest.TestCase):
    def setUp(self):
        self.config = OptimizerConfig(binary_path="k2pdfopt", hardware=TargetHardwareConstraints())

    @patch('src.optimizer.services.orchestrator.compress_pdf_artifact')
    @patch('src.optimizer.services.orchestrator.merge_and_inject_metadata')
    @patch('src.optimizer.services.orchestrator.execute_k2pdfopt_rasterization')
    @patch('src.optimizer.services.orchestrator.partition_pdf')
    @patch('src.optimizer.services.orchestrator.extract_metadata')
    @patch('src.optimizer.services.orchestrator.Path.exists')
    @patch('src.optimizer.services.orchestrator.PdfReader')
    def test_pipeline_orchestration_flow(
        self, mock_pdf_reader, mock_exists, mock_extract, mock_partition, mock_execute, mock_merge, mock_compress
    ):
        mock_exists.return_value = True
        mock_extract.return_value = {'/Title': 'Test', '/Author': 'Author'}
        
        mock_chunk_1 = Path("chunk_1.pdf")
        mock_partition.return_value = [mock_chunk_1]
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [1] 
        mock_pdf_reader.return_value = mock_reader_instance

        optimize_pdf_for_oasis("valid_source.pdf", self.config, "final_output.pdf")

        mock_execute.assert_called_once()
        mock_merge.assert_called_once()
        mock_compress.assert_called_once()

if __name__ == '__main__':
    unittest.main()
