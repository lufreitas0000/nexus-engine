# Branch Scope: feature/concurrency-manager

## Task Description
Build a utility library to manage concurrent execution. Implement `ProcessPoolExecutor` logic that takes a list of PDF file paths and processes them in parallel. Implement the VRAM locking semaphore logic.

## Why it's safe
This is purely infrastructure logic. It can be developed using dummy functions first, then injected into the Orchestrator later.
