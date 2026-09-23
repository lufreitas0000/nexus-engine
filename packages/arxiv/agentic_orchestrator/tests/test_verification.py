"""
Global TDD: Unit tests for pure I/O verification logic.
"""
from agentic_orchestrator.src.domain.model import ExecutionResult, TaskStatus
from agentic_orchestrator.src.services.verification import verify_execution_success, verify_artifact_schema

def test_verify_execution_success():
    result = ExecutionResult(task_id="1", status=TaskStatus.SUCCESS, exit_code=0)
    assert verify_execution_success(result) is True

def test_verify_execution_failure():
    result = ExecutionResult(task_id="1", status=TaskStatus.FAILED, exit_code=1)
    assert verify_execution_success(result) is False

def test_verify_artifact_schema_valid():
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"}
        },
        "required": ["title"]
    }
    data = {"title": "Test Paper"}
    assert verify_artifact_schema(data, schema) is True

def test_verify_artifact_schema_invalid():
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"}
        },
        "required": ["title"]
    }
    data = {"name": "Test Paper"}
    assert verify_artifact_schema(data, schema) is False
