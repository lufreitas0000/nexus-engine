from dataclasses import dataclass
from typing import Optional
from enum import Enum

class TaskType(Enum):
    SEARCH_QUERY = "SEARCH_QUERY"
    ARXIV_IDENTIFIER = "ARXIV_IDENTIFIER"
    LOCAL_PATH = "LOCAL_PATH"

@dataclass(frozen=True)
class IngestionTask:
    task_id: str
    task_type: TaskType
    payload: str
    max_results: int = 3  # Relevant only for SEARCH_QUERY

@dataclass(frozen=True)
class DownloadTask:
    arxiv_id: str
    download_dir: str
    file_path: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
