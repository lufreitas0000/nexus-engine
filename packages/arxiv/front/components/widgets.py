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
