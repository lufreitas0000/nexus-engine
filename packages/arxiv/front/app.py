"""
Primary adapter for Textual Application
"""

import asyncio
import json
import uuid
import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Input
from textual import work
import redis.asyncio as redis_async

from pipeline import create_pipeline
from front.components.widgets import TaskInput, ProcessingQueueTable, DLQDataTable
from ingestion_engine.src.domain.model import TaskType

class OrchestratorApp(App):
    """A Textual UI to orchestrate the arXiv background pipeline."""

    TITLE = "arXiv Orchestrator TUI"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit application")
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queue = None
        self.pubsub_task = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield TaskInput()
        yield ProcessingQueueTable(id="queue_table")
        yield DLQDataTable(id="dlq_table")
        yield RichLog(id="main_log", highlight=True, markup=True)
        yield Footer()

    async def on_mount(self) -> None:
        """Lifecycle event when application is first mounted."""
        self.queue = create_pipeline()
        log_widget = self.query_one("#main_log", RichLog)
        log_widget.write("[bold green]Starting orchestrator pipeline...[/bold green]")
        self.start_pipeline_worker()
        self.start_pubsub_listener()
        self.poll_dlq()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Intercepts user input, constructs task, and pushes to queue."""
        user_input = message.value.strip()
        if not user_input:
            return

        task_id = str(uuid.uuid4())

        # Simple heuristic to determine task type
        if os.path.exists(user_input):
            task_type = "LOCAL_PATH"
        elif user_input.replace(".", "").isdigit() or (len(user_input) > 5 and user_input[4] == "."):
             # naive arXiv ID check (e.g. 2305.12345)
             task_type = "ARXIV_IDENTIFIER"
        else:
            task_type = "SEARCH_QUERY"

        if self.queue:
            try:
                from ingestion_engine.src.domain.model import IngestionTask, TaskType
                task = IngestionTask(task_id=task_id, task_type=TaskType(task_type), payload=user_input)
                await self.queue.add_task(task)

                # Update UI safely
                table = self.query_one("#queue_table", ProcessingQueueTable)
                table.add_row(task_id, user_input, "Queued", "Pending", key=task_id)

                log_widget = self.query_one("#main_log", RichLog)
                log_widget.write(f"Task [cyan]{task_id}[/cyan] of type [yellow]{task_type}[/yellow] queued.")

                message.input.value = ""
            except Exception as e:
                log_widget = self.query_one("#main_log", RichLog)
                log_widget.write(f"[bold red]Failed to queue task:[/bold red] {e}")

    @work(exclusive=True, thread=False)
    async def start_pipeline_worker(self) -> None:
        """Executes the pipeline orchestrator worker asynchronously."""
        if self.queue:
            try:
                await self.queue.start_worker()
            except Exception as e:
                log_widget = self.query_one("#main_log", RichLog)
                log_widget.write(f"[bold red]Worker error: {e}[/bold red]")

    @work(exclusive=True, thread=False)
    async def start_pubsub_listener(self) -> None:
        """Listens to Redis Pub/Sub for state updates and reacts."""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            client = redis_async.from_url(redis_url)
            pubsub = client.pubsub()
            await pubsub.subscribe("pipeline_state")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    task_id = data.get("task_id")
                    origin = data.get("origin")
                    stage = data.get("stage")
                    status = data.get("status")

                    # Update DataTable safely within the event loop
                    table = self.query_one("#queue_table", ProcessingQueueTable)

                    # Ensure thread safety when calling UI updates from async task
                    def update_ui():
                        if table.has_row(task_id):
                            table.update_cell(task_id, "stage", stage)
                            table.update_cell(task_id, "status", status)
                        else:
                            table.add_row(task_id, origin, stage, status, key=task_id)

                    self.call_from_thread(update_ui)

        except Exception as e:
            log_widget = self.query_one("#main_log", RichLog)
            log_widget.write(f"[bold red]PubSub error: {e}[/bold red]")

    @work(exclusive=True, thread=False)
    async def poll_dlq(self) -> None:
        """Polls the Redis DLQ periodically and updates the UI."""
        table = self.query_one("#dlq_table", DLQDataTable)
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            client = redis_async.from_url(redis_url)

            while True:
                dlq_items = await client.lrange("pipeline_dlq", 0, -1)

                # Update UI thread-safely
                def update_table():
                    table.clear()
                    for item in dlq_items:
                        data = json.loads(item)
                        task_id = data["task_payload"].get("task_id", "N/A")
                        table.add_row(
                            task_id,
                            data.get("error", "N/A"),
                            str(data.get("required_vram_gb", "N/A")),
                            data.get("status", "N/A"),
                            key=task_id
                        )
                self.call_from_thread(update_table)
                await asyncio.sleep(2)
        except Exception as e:
            log_widget = self.query_one("#main_log", RichLog)
            log_widget.write(f"[bold red]DLQ poll error: {e}[/bold red]")

    async def on_dlq_data_table_retry_requested(self, message: DLQDataTable.RetryRequested) -> None:
        """Intercepts the retry event, removes item from DLQ, and requeues it."""
        task_id = message.task_id
        log_widget = self.query_one("#main_log", RichLog)

        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            client = redis_async.from_url(redis_url)
            dlq_items = await client.lrange("pipeline_dlq", 0, -1)

            for item in dlq_items:
                data = json.loads(item)
                if data["task_payload"].get("task_id") == task_id:
                    # Remove from DLQ
                    await client.lrem("pipeline_dlq", 1, item)
                    # Requeue to ARQ orchestrator by interacting with the established pool
                    if self.queue and self.queue.pool:
                        await self.queue.pool.enqueue_job(
                            "process_remote_task",
                            data["task_payload"],
                            data["required_vram_gb"]
                        )
                        log_widget.write(f"[bold green]Task {task_id} successfully re-queued from DLQ.[/bold green]")
                    else:
                        log_widget.write(f"[bold red]Failed to requeue: Queue pool not initialized.[/bold red]")
                    break
        except Exception as e:
            log_widget.write(f"[bold red]Retry error: {e}[/bold red]")


    async def on_unmount(self) -> None:
        """Lifecycle event when application unmounts."""
        if self.queue:
            await self.queue.stop_worker()

if __name__ == "__main__":
    app = OrchestratorApp()
    app.run()
