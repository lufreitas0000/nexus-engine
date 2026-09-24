import os
from pathlib import Path

def get_workspace_path() -> Path:
    """
    Returns the absolute path of the workspace as defined by the NEXUS_WORKSPACE
    environment variable. Raises RuntimeError if it's not set or empty.
    """
    workspace_env = os.environ.get("NEXUS_WORKSPACE")
    if not workspace_env or not workspace_env.strip():
        raise RuntimeError("NEXUS_WORKSPACE environment variable is missing or empty.")
    
    return Path(workspace_env.strip()).resolve()
