from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class DownloadTask:
    arxiv_id: str
    download_dir: str
    file_path: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
