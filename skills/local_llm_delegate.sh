#!/bin/sh
# Usage: ./skills/local_llm_delegate.sh <model_tag> <prompt_file> [source_file]
# Offloads mechanical coding/refactoring tasks to local Ollama (qwen2.5-coder:3b or 7b)
# to consume ZERO Google Antigravity credits.
set -eu

MODEL="${1:-qwen2.5-coder:7b}"
PROMPT_FILE="${2:?Prompt file required}"
SOURCE_FILE="${3:-}"
OLLAMA_URL="${OLLAMA_HOST:-http://127.0.0.1:11434}/api/generate"

PROMPT_CONTENT=$(cat "$PROMPT_FILE")
if [ -n "$SOURCE_FILE" ]; then
    SOURCE_CONTENT=$(cat "$SOURCE_FILE")
    FULL_PROMPT="${PROMPT_CONTENT}\n\n---\nSOURCE FILE (${SOURCE_FILE}):\n${SOURCE_CONTENT}"
else
    FULL_PROMPT="${PROMPT_CONTENT}"
fi

python3 - "$MODEL" "$OLLAMA_URL" "$FULL_PROMPT" << 'PYEOF'
import json
import sys
import urllib.request

model, url, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
payload = json.dumps({
    "model": model,
    "prompt": prompt,
    "stream": False,
    "options": {"temperature": 0.0}
}).encode("utf-8")

req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=120) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    print(data.get("response", ""))
PYEOF
