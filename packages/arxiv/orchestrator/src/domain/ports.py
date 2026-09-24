from typing import Protocol, Any, Dict

class IDLQAdapter(Protocol):
    async def enqueue_failed_task(self, task_name: str, payload: Dict[str, Any], error_metadata: str) -> None:
        pass
