from textual.app import ComposeResult
from textual.widgets import Input, DataTable, Static

class TaskInput(Static):
    """Widget to capture task input."""
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter search query, arXiv ID, or local file path...", id="task_input")

class ProcessingQueueTable(DataTable):
    """DataTable to visualize the processing queue."""
    def on_mount(self) -> None:
        self.add_column("Task ID", key="task_id")
        self.add_column("Origin", key="origin")
        self.add_column("Current Stage", key="stage")
        self.add_column("Status", key="status")

from textual.binding import Binding
from textual.message import Message

class DLQDataTable(DataTable):
    """DataTable to visualize tasks in the Redis Dead-Letter Queue."""

    BINDINGS = [
        Binding("r", "retry_task", "Retry Task", show=True),
    ]

    class RetryRequested(Message):
        def __init__(self, task_id: str):
            self.task_id = task_id
            super().__init__()

    def on_mount(self) -> None:
        self.add_columns("Task ID", "Error", "VRAM (GB)", "Status")

    def action_retry_task(self) -> None:
        """Emits a RetryRequested event for the currently selected row."""
        if self.cursor_row is not None:
            task_id = self.get_row_at(self.cursor_row)[0]
            self.post_message(self.RetryRequested(task_id))
