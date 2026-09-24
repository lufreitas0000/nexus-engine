"""
Abstract base classes defining the contracts for task delegation and I/O verification.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from agentic_orchestrator.src.domain.model import BaseTask, ExecutionResult

class TaskDelegator(ABC):
    """
    Port for delegating tasks to external agents or infrastructure.
    """

    @abstractmethod
    async def dispatch(self, task: BaseTask) -> str:
        """
        Dispatches a task and returns a tracking job ID.
        """
        pass

    @abstractmethod
    async def poll_status(self, job_id: str) -> ExecutionResult:
        """
        Polls the execution status of a previously dispatched job.
        """
        pass

class ResultVerifier(ABC):
    """
    Port for pure functional verification of output artifacts.
    """

    @abstractmethod
    def verify_schema(self, result: ExecutionResult, expected_schema: Dict[str, Any]) -> bool:
        """
        Verifies if the output artifact matches the expected schema.
        """
        pass
