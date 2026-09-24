from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ProcessedDocument:
    arxiv_id: str
    extracted_dir: str
    main_file_path: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
