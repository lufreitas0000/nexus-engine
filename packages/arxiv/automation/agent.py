import asyncio
from google.antigravity import LocalAgentConfig, CapabilitiesConfig, Agent
from google.antigravity.utils.interactive import run_interactive_loop
from automation.tools import (
    push_arxiv_query,
    read_dlq,
    check_completed_graphs,
    semantic_search_papers
)
from automation.tools_obsidian import export_graph_to_obsidian

async def main():
    # 1. Extraction Sub-Agent (Mathematical derivations)
    extraction_agent = Agent(
        config=LocalAgentConfig(
            system_instructions=(
                "You are the Extraction Sub-Agent. Your focus is mathematical purity and context isolation.\n"
                "You parse high-density academic papers and isolate Definitions, Lemmas, Theorems, and Proofs."
            ),
            tools=[],
            capabilities=CapabilitiesConfig()
        ),
        name="ExtractionAgent"
    )

    # 2. Literature Sub-Agent (Cross-referencing)
    literature_agent = Agent(
        config=LocalAgentConfig(
            system_instructions=(
                "You are the Literature Sub-Agent. Your objective is cross-referencing and semantic synthesis.\n"
                "You synthesize literature reviews and answer specific physics questions."
            ),
            tools=[semantic_search_papers],
            capabilities=CapabilitiesConfig()
        ),
        name="LiteratureAgent"
    )

    # 3. Main Orchestrator Agent
    system_instructions = (
        "You are the Research Orchestrator Agent. Your primary objectives are:\n"
        "1. Feed the ingestion pipeline by pushing relevant arXiv IDs based on user requests using push_arxiv_query().\n"
        "2. Proactively monitor the Redis Dead-Letter Queue (DLQ) using read_dlq().\n"
        "3. Analyze any failed tasks and suggest re-routing or re-queueing strategies.\n"
        "4. Check PostgreSQL using check_completed_graphs() to verify the pipeline's output.\n"
        "5. Export completed graphs to Obsidian using export_graph_to_obsidian().\n"
        "6. Delegate deep mathematical parsing to the ExtractionAgent and literature synthesis to the LiteratureAgent.\n\n"
        "Operate autonomously but report your logic and findings clearly to the terminal."
    )

    config = LocalAgentConfig(
        system_instructions=system_instructions,
        tools=[push_arxiv_query, read_dlq, check_completed_graphs, export_graph_to_obsidian],
        capabilities=CapabilitiesConfig(),
        sub_agents=[extraction_agent, literature_agent]
    )

    print("[INFO] Initializing Antigravity Research Orchestrator with Sub-Agents...")
    print("[INFO] Sub-Agents loaded: ExtractionAgent, LiteratureAgent")
    print("[INFO] Tools loaded: push_arxiv_query, read_dlq, check_completed_graphs, export_graph_to_obsidian, semantic_search_papers")

    # Launch the asynchronous agentic loop
    await run_interactive_loop(config)

if __name__ == "__main__":
    asyncio.run(main())
