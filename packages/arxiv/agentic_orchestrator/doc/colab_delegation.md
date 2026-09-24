# Google Colab Infrastructure Delegation

This document specifies the protocols and instructions for the Agentic Orchestrator to offload computationally expensive tasks to Google Colab environments.

## Rationale
The core infrastructure running the `agentic_orchestrator` is designed for I/O verification and lightweight scheduling. Tasks requiring GPUs or high compute memory must be executed externally on virtual cloud machines to prevent resource starvation on the orchestrator node.

## Hand-off Protocol

### 1. Identify Compute-Heavy Tasks
The orchestrator must classify tasks that trigger the Colab delegation adapter.
**Examples of Compute-Heavy Tasks:**
- Advanced PDF parsing and semantic chunking using vision-language models.
- Heavy translation tasks on full documents.
- Any machine learning inference task requiring CUDA/GPU acceleration.

### 2. Payload Construction
Before delegating, the orchestrator must construct a purely deterministic data payload.
- The payload must conform to the `ComputeHeavyTask` data structure defined in `agentic_orchestrator/src/domain/model.py`.
- It must contain URIs (e.g., S3 buckets, presigned URLs, or local paths accessible via an established tunnel) to the raw data files, rather than embedding the data directly in the payload.
- It must include an expected output schema or hash for verification.

### 3. Execution via Colab Adapter
- The orchestrator will trigger the `colab_execution_adapter.py`.
- This adapter interacts with the Google Colab environment via out-of-band CLI tools or OAuth APIs.
- The adapter will submit a Jupyter notebook script or Python file, along with the payload, to the Colab machine.
- The adapter must run asynchronously and poll for the task status to avoid blocking the main orchestrator thread.

### 4. Output Verification
- Upon completion, Colab will return an exit code and a reference to the output artifacts (e.g., a processed Markdown file or a JSON data structure).
- The orchestrator must **not** attempt to evaluate the quality of the compute task via LLM reasoning.
- Instead, it must invoke the pure generic functions in `agentic_orchestrator/src/services/verification.py` to validate that the output artifact conforms to the expected schemas, exists at the specified URI, and has the correct file size/hash.

## Constraints
- **Authentication:** The orchestrator must rely on the underlying infrastructure (e.g., predefined environment variables or `cli_runner.py`) to handle Google OAuth tokens. It must never hardcode credentials into task payloads.
- **State Management:** The orchestrator must treat Colab jobs as stateless, functional transformations: given Input `X`, Colab produces Output `Y`. It must gracefully handle Colab preemption or timeouts by retrying the payload via the ARQ queue.
