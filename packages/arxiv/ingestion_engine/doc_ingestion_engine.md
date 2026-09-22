# Ingestion Engine Specification

The `ingestion_engine` module is responsible for reliably downloading source files (PDFs or LaTeX source tarballs) from arXiv.

## Downloading Strategy

- The engine needs to fetch the source files using the arXiv ID.
- ArXiv provides source tarballs at `https://export.arxiv.org/e-print/{arxiv_id}` and PDFs at `https://export.arxiv.org/pdf/{arxiv_id}.pdf`.
- We prioritize e-print (LaTeX) since we want to parse LaTeX to Markdown for better structured representation.
- The downloaded files will be temporarily stored on disk.

## Rate Limiting Requirements

- ArXiv's automated download terms of service require strict rate limiting.
- The engine must wait an appropriate time between requests to prevent IP bans.
- A `asyncio.Semaphore` combined with `asyncio.sleep` can be used to limit concurrent downloads and maintain a delay.
- Retries with exponential backoff should be implemented to handle temporary failures (`503`, `429`).
