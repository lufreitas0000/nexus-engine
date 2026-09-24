"""
Pure generic functions mapped to verify inputs and outputs of agentic scripts.
No side effects are permitted here.
"""
from typing import Dict, Any
from agentic_orchestrator.src.domain.model import ExecutionResult, TaskStatus
import jsonschema # type: ignore

def verify_execution_success(result: ExecutionResult) -> bool:
    """
    Pure function to verify if an execution result denotes a successful execution.
    """
    return result.status == TaskStatus.SUCCESS and result.exit_code == 0

def verify_artifact_schema(artifact_data: Dict[str, Any], expected_schema: Dict[str, Any]) -> bool:
    """
    Pure function to verify if a given artifact data (e.g., loaded JSON) matches the expected schema.
    Uses jsonschema for validation.
    """
    try:
        jsonschema.validate(instance=artifact_data, schema=expected_schema)
        return True
    except jsonschema.exceptions.ValidationError:
        return False
    except Exception:
        # Catch unexpected validation engine errors safely
        return False
