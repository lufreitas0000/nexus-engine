import subprocess
import tempfile
import os
from dataclasses import dataclass
from typing import Tuple

@dataclass
class CompilationResult:
    success: bool
    log: str

class TectonicCompiler:
    def __init__(self, timeout: int = 90):
        self.timeout = timeout

    def compile(self, latex_content: str) -> CompilationResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, "document.tex")
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_content)

            try:
                process = subprocess.run(
                    ["tectonic", tex_file],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )

                if process.returncode == 0:
                    return CompilationResult(success=True, log="")
                else:
                    return CompilationResult(success=False, log=process.stderr.strip())

            except subprocess.TimeoutExpired:
                return CompilationResult(success=False, log="Compilation timed out.")
            except FileNotFoundError:
                return CompilationResult(success=False, log="Tectonic binary not found.")
