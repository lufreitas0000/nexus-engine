import asyncio
from google.antigravity import LocalAgentConfig, CapabilitiesConfig
from google.antigravity.utils.interactive import run_interactive_loop
from google.antigravity.execution import execute_agent_stateless

from automation.tools import push_arxiv_query, read_dlq, check_completed_graphs
from automation.tools_obsidian import export_graph_to_obsidian
from automation.sub_agents import get_math_extraction_agent, get_literature_agent

async def delegate_to_math_agent(text_payload: str) -> str:
    """Delegates mathematical derivation extraction to the specialized Math Sub-Agent."""
    config = get_math_extraction_agent()
    result = await execute_agent_stateless(config, prompt=text_payload)
    return result.text

async def delegate_to_literature_agent(text_payload: str) -> str:
    """Delegates bibliographical verification to the specialized Literature Sub-Agent."""
    config = get_literature_agent()
    result = await execute_agent_stateless(config, prompt=text_payload)
    return result.text

async def main():
    system_instructions = (
        "You are the Research Orchestrator Agent acting as a Scrum Master. "
        "You decompose complex academic processing tasks into orthogonal submodules.\n"
        "1. Identify the input source (e.g., arXiv ID or raw text).\n"
        "2. Use delegate_to_math_agent for extracting pure mathematical physics derivations.\n"
        "3. Use delegate_to_literature_agent for cross-referencing and citation validation.\n"
        "4. Use export_graph_to_obsidian to save the final synthesized output.\n"
        "5. Monitor infrastructure queues via read_dlq and check_completed_graphs.\n"
        "State facts, define constraints, and explain logical steps during orchestration."
    )

    tools = [
        push_arxiv_query,
        read_dlq,
        check_completed_graphs,
        export_graph_to_obsidian,
        delegate_to_math_agent,
        delegate_to_literature_agent
    ]

    config = LocalAgentConfig(
        system_instructions=system_instructions,
        tools=tools,
        capabilities=CapabilitiesConfig(),
    )

    print("[INFO] Initializing Multi-Agent Research Orchestrator...")
    await run_interactive_loop(config)

if __name__ == "__main__":
    asyncio.run(main())
