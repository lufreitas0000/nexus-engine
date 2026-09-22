import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from common.logging import setup_logging, get_logger
from orchestrator.queue import BackgroundQueue

setup_logging()
logger = get_logger(__name__)

queue = BackgroundQueue()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("api_startup")
    await queue.start_worker()
    yield
    # Shutdown
    logger.info("api_shutdown")
    await queue.stop_worker()

app = FastAPI(lifespan=lifespan, title="arXiv Scraper API")

class ResearchRequest(BaseModel):
    query: str
    max_results: int = 3

@app.post("/api/research")
async def submit_research(request: ResearchRequest):
    await queue.add_query(request.query, request.max_results)
    return {"message": "Query submitted", "query": request.query, "max_results": request.max_results}

@app.get("/api/notes/{arxiv_id}")
async def get_notes(arxiv_id: str):
    # For now, it retrieves from the default output folder setup in queue
    markdown_path = os.path.join(queue.output_dir, "markdown", f"{arxiv_id}.md")

    if not os.path.exists(markdown_path):
        raise HTTPException(status_code=404, detail="Notes not found or not processed yet.")

    with open(markdown_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {"arxiv_id": arxiv_id, "content": content}
