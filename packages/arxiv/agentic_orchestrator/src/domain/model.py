"""
Entities and Types.
Strictly pure data structures representing task payloads, execution states, and I/O schemas.
"""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class BaseTask(BaseModel):
    """Base schema for tasks dispatched by the orchestrator."""
    task_id: str
    status: TaskStatus = TaskStatus.PENDING

class ScrapingTask(BaseTask):
    """Payload representing a lightweight API fetching/parsing task (e.g., arXiv)."""
    query: str
    max_results: int = 10
    output_dir: str

class ComputeHeavyTask(BaseTask):
    """Payload representing a heavy Colab job (e.g., GPU chunking/translation)."""
    input_uri: str = Field(..., description="URI to the raw file (e.g., s3://bucket/doc.pdf)")
    expected_output_schema: Dict[str, Any] = Field(default_factory=dict, description="Expected schema structure of the output JSON")
    colab_script_path: str = Field(..., description="Path to the script to execute on Colab")

class ExecutionResult(BaseModel):
    """Standardized output state from any delegated task."""
    task_id: str
    status: TaskStatus
    exit_code: int
    output_artifact_uri: Optional[str] = None
    error_message: Optional[str] = None
