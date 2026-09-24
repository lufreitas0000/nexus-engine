import traceback
from typing import Callable, Any, Dict
from orchestrator.src.domain.ports import IDLQAdapter

async def execute_with_dlq(
    task_name: str,
    payload: Dict[str, Any],
    logic: Callable,
    dlq_adapter: IDLQAdapter
) -> Any:
    """Pure function orchestrating task execution and DLQ routing on failure."""
    try:
        return await logic(payload)
    except Exception as e:
        error_metadata = traceback.format_exc()
        await dlq_adapter.enqueue_failed_task(task_name, payload, error_metadata)
        raise e
