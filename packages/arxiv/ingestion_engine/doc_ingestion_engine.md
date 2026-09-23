# Ingestion Engine Specification

## 1. Domain Modeling

The ingestion engine is responsible for orchestrating the download of papers from arXiv. It primarily acts as an HTTP client that respects the target server's rate limits and handles potential connection issues.

- `DownloadTask`: A domain model representing the current state of a file download request (e.g., `success`, `file_path`, `error`).

## 2. Ports (Interfaces)

- ArXiv's automated download terms of service require strict rate limiting.
- The engine must wait an appropriate time between requests to prevent IP bans.
- A `asyncio.Semaphore` combined with `asyncio.sleep` can be used to limit concurrent downloads and maintain a delay.
- Retries with exponential backoff should be implemented to handle temporary failures (`503`, `429`).

## 1. Domain Modeling

The ingestion engine is responsible for orchestrating the download of papers from arXiv. It primarily acts as an HTTP client that respects the target server's rate limits and handles potential connection issues.

- `DownloadTask`: A domain model representing the current state of a file download request (e.g., `success`, `file_path`, `error`).

## 2. Ports (Interfaces)

- `Downloader`: An interface that exposes a method to securely download a paper using an arXiv ID.

## 3. Adapters

- `ArxivDownloader`: An adapter that uses `httpx.AsyncClient` to asynchronously execute downloads. It includes fallback logic:
  - Tries to fetch `.tar.gz` source archives first.
  - If unavailable, falls back to fetching `.pdf` files.
- **Strict Rate Limiting:** Enforces bounded concurrency (e.g., via `asyncio.Semaphore(1)`) and configurable delays between requests to comply with arXiv API limits.
- **Backoff/Retry Mechanism:** Uses a retry loop with exponential backoff on HTTP status codes like 429, 500, 502, 503, and 504.
