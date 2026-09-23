import os

from arq import create_pool
from arq.connections import RedisSettings

from common.logging import get_logger

logger = get_logger(__name__)

class BackgroundQueue:
    def __init__(self, redis_url: str = "redis://localhost:6379/0", output_dir: str = "./output"):
        self.redis_url = redis_url
        self.output_dir = output_dir
        self.pool = None
        self.redis_settings = RedisSettings.from_dsn(self.redis_url)

    async def add_query(self, query: str, max_results: int = 3):
        if not self.pool:
            logger.error("queue_pool_not_initialized")
            raise RuntimeError("Queue pool not initialized. Call start_worker() first.")

        await self.pool.enqueue_job("process_query_task", query, max_results, self.output_dir)
        logger.info("added_to_queue", query=query, max_results=max_results)

    async def start_worker(self):
        self.pool = await create_pool(self.redis_settings)
        logger.info("queue_pool_started")

    async def stop_worker(self):
        if self.pool:
            await self.pool.close()
            logger.info("queue_pool_stopped")
