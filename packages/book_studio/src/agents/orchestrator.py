from typing import List
from src.core.schemas import ExtractionResult, Page
from src.agents.subagent import VerificationSubagent

class AgentOrchestrator:
    def __init__(self, api_key: str = "sk-placeholder", api_base: str = "http://127.0.0.1:8000/v1"):
        self.api_key = api_key
        self.api_base = api_base

    def verify_document(self, data: ExtractionResult) -> ExtractionResult:
        """
        Splits the document into sections and uses subagents to verify them.
        """
        print(f"[*] Orchestrator: Starting agentic verification of {len(data.pages)} pages...")
        verified_pages = []
        
        # We process in small logical batches (e.g., 2 pages at a time) to fit into context window
        batch_size = 2
        
        for i in range(0, len(data.pages), batch_size):
            batch = data.pages[i:i+batch_size]
            subagent = VerificationSubagent(self.api_base, self.api_key)
            print(f"    -> Agent verifying pages {i+1} to {min(i+batch_size, len(data.pages))}...")
            verified_batch = subagent.verify(batch)
            verified_pages.extend(verified_batch)
            
        data.pages = verified_pages
        return data
