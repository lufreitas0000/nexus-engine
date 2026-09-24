from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class JobSubmissionResponse(BaseModel):
    job_id: str = Field(..., description="Unique task identifier assigned by the queue")
    status: str = Field(default="PENDING", description="Current execution state")

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    ready: bool
    successful: Optional[bool] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
