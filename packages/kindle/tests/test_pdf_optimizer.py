import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess

from src.optimizer.domain.types import OptimizerConfig, TargetHardwareConstraints
from src.optimizer.services.orchestrator import optimize_pdf_for_oasis
from src.optimizer.infra.subprocess_adapter import execute_k2pdfopt_rasterization

class TestPdfOptimizerSubprocess(unittest.TestCase):
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
    def test_successful_rasterization_execution(self, mock_stat, mock_exists, mock_run):
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024 # Simulate valid non-zero artifact
        mock_run.return_value = MagicMock(returncode=0)

        result = execute_k2pdfopt_rasterization(self.input_path, self.output_path, self.config, page_count=5)
        
        self.assertEqual(result, self.output_path)
        mock_run.assert_called_once()
        
        # Verify execution vector constraints
        executed_args = mock_run.call_args[0][0]
        self.assertIn('-w', executed_args)
        self.assertIn('1264', executed_args)
        self.assertIn('-wrap', executed_args)

    @patch('src.optimizer.infra.subprocess_adapter.subprocess.run')
    def test_timeout_enforcement_raises_runtime_error(self, mock_run):
        # Simulate a process hanging on complex tensor equations
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="k2pdfopt", timeout=5.0)

        with self.assertRaises(RuntimeError) as context:
            execute_k2pdfopt_rasterization(self.input_path, self.output_path, self.config, page_count=5)
            
        self.assertIn("Rasterization timeout exceeded", str(context.exception))

class TestPdfOptimizerOrchestrator(unittest.TestCase):
    def setUp(self):
        self.config = OptimizerConfig(
            binary_path="k2pdfopt",
            hardware=TargetHardwareConstraints()
        )

    @patch('src.optimizer.services.orchestrator.Path.exists')
    def test_invalid_source_boundary_raises_exception(self, mock_exists):
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError):
            optimize_pdf_for_oasis("invalid_state.pdf", self.config)

    @patch('src.optimizer.services.orchestrator.merge_and_inject_metadata')
    @patch('src.optimizer.services.orchestrator.execute_k2pdfopt_rasterization')
    @patch('src.optimizer.services.orchestrator.partition_pdf')
    @patch('src.optimizer.services.orchestrator.extract_metadata')
    @patch('src.optimizer.services.orchestrator.Path.exists')
    @patch('src.optimizer.services.orchestrator.PdfReader')
    def test_pipeline_orchestration_flow(
        self, mock_pdf_reader, mock_exists, mock_extract, mock_partition, mock_execute, mock_merge
    ):
        mock_exists.return_value = True
        mock_extract.return_value = {'/Title': 'Test', '/Author': 'Author'}
        
        # Simulate partitioning returning two transient chunks
        mock_chunk_1 = Path("chunk_1.pdf")
        mock_chunk_2 = Path("chunk_2.pdf")
        mock_partition.return_value = [mock_chunk_1, mock_chunk_2]
        
        # Simulate internal page counts for chunks
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [1, 2, 3] 
        mock_pdf_reader.return_value = mock_reader_instance

        optimize_pdf_for_oasis("valid_source.pdf", self.config, "final_output.pdf")

        # Verify sequential processing
        self.assertEqual(mock_execute.call_count, 2)
        mock_merge.assert_called_once()

if __name__ == '__main__':
    unittest.main()
