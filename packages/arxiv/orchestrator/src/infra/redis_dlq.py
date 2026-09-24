from arq import create_pool
from arq.connections import RedisSettings
from orchestrator.src.domain.ports import IDLQAdapter
from typing import Any, Dict

class RedisDLQAdapter(IDLQAdapter):
    def __init__(self, redis_settings: RedisSettings):
        self.redis_settings = redis_settings
        self._pool = None

    async def _get_pool(self):
        if not self._pool:
            self._pool = await create_pool(self.redis_settings)
        return self._pool

    async def enqueue_failed_task(self, task_name: str, payload: Dict[str, Any], error_metadata: str) -> None:
        pool = await self._get_pool()
        dlq_payload = {
            "flagged": True,
            "original_task": task_name,
            "payload": payload,
            "error_trace": error_metadata
        }
        # Enqueues to a separate logical stream within Redis for TUI inspection
        await pool.enqueue_job("process_dlq_entry", dlq_payload, _queue_name="dlq")
