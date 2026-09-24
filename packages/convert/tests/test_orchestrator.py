import pytest
from unittest.mock import MagicMock, call
from pathlib import Path

# We expect this import to fail initially (TDD)
from app_orchestrator.pipeline import PipelineOrchestrator


def test_orchestrator_sequence_execution():
    # Arrange
    mock_extractor = MagicMock(return_value="extracted_manifold_data")
    mock_spatial = MagicMock(return_value="spatial_ast_with_placeholders")
    mock_vision = MagicMock(return_value="final_resolved_ast")

    orchestrator = PipelineOrchestrator(
        extractor_fn=mock_extractor, spatial_fn=mock_spatial, vision_fn=mock_vision
    )

    test_pdf_path = Path("dummy.pdf")

    # Act
    result = orchestrator.process(test_pdf_path)

    # Assert
    assert result == "final_resolved_ast"

    # Verify sequence of calls
    mock_extractor.assert_called_once_with(test_pdf_path)
    mock_spatial.assert_called_once_with("extracted_manifold_data")
    mock_vision.assert_called_once_with("spatial_ast_with_placeholders")
