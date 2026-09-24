import fitz
from pathlib import Path
import subprocess

doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "End to End Test Document", fontsize=20)
page.insert_text((50, 100), "This is a paragraph inside the test document.", fontsize=12)

pdf_path = Path("e2e_dummy.pdf")
doc.save(str(pdf_path))

print(f"Created {pdf_path}, running pipeline...")
# Need to set NEXUS_WORKSPACE
import os
env = os.environ.copy()
env["NEXUS_WORKSPACE"] = "/home/lucas/Projects/nexus-workspace"

# We run nexus_cli
result = subprocess.run(
    [".venv/bin/python", "packages/nexus_cli/src/main.py", str(pdf_path.resolve())],
    env=env,
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
    exit(1)
