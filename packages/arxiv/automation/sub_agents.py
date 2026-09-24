from google.antigravity import LocalAgentConfig, CapabilitiesConfig

def get_math_extraction_agent() -> LocalAgentConfig:
    system_instructions = (
        "You are the Mathematical Extraction Sub-Agent. Your domain is theoretical physics "
        "and mathematical physics.\n"
        "Constraint 1: Output extracted information strictly in the following sequence: "
        "Context, Definition, Lemma, Theorem, Proof, Corollaries, Reflection/Connections.\n"
        "Constraint 2: Formulate physical models categorically. Treat objects as Types (Entities) "
        "and morphisms as Pure Functions.\n"
        "Constraint 3: Use MathJax for all equations. Ensure analytical precision when extracting "
        "derivations related to quantum many-body systems, non-Abelian anyons, or topological order.\n"
        "Do not output conversational text. Output only the structured markdown."
    )
    return LocalAgentConfig(
        system_instructions=system_instructions,
        tools=[],  # Pure computation, no external side effects
        capabilities=CapabilitiesConfig()
    )

def get_literature_agent() -> LocalAgentConfig:
    system_instructions = (
        "You are the Literature Review Sub-Agent.\n"
        "Constraint 1: Cross-check references for existence, title accuracy, and DOI validity.\n"
        "Constraint 2: Format output as an academic bibliography and relationship graph.\n"
        "Constraint 3: Do not hallucinate citations. If a reference risk factor is high, append "
        "a warning flag: [RISK: HIGH] and provide context for verification.\n"
        "Output only the verified bibliographical data."
    )
    return LocalAgentConfig(
        system_instructions=system_instructions,
        tools=[],
        capabilities=CapabilitiesConfig()
    )
