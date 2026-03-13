# arxiv_scraper

## Project Goal
This system automates the process of finding, downloading, and converting scientific papers from arXiv into Markdown. It moves beyond simple metadata searching by analyzing how papers cite one another to find the most relevant research on a given topic.

## How it Works
1. **Search & Rank**: You provide a topic. The system finds related papers and uses citation data to rank them by importance.
2. **Download**: The system safely downloads the source files (LaTeX) or PDFs of the top-ranked papers.
3. **Extract**: It opens the downloaded archives and identifies the main document.
4. **Convert**: It transforms the complex LaTeX or PDF content into a clean Markdown file, keeping math equations intact but replacing images with compressed ones.

## Folder Structure Guide

The project is split into four main areas to keep the code organized and easy to maintain:

### /research_graph
This is the search and discovery module.
- It talks to the arXiv and Semantic Scholar APIs.
- It builds a map of which papers cite each other.
- It stores this information in the PostgreSQL database so we don't have to search the same paper twice.

### /ingestion_engine
This is the downloader.
- It manages the connection to the arXiv servers.
- It ensures we download files at a controlled speed so the servers do not block our access.
- It handles retries if a download fails due to a bad connection.

### /document_processor
This is the file manager.
- It takes the downloaded zip or tar files and unpacks them.
- It looks through the files to find which one is the "main" paper (the one that needs to be read).

### /document_converter
This is the translator.
- It takes the scientific paper format and turns it into Markdown.
- It ensures math formulas are preserved.
- It extracts figure captions so that your notes contain the context of the images even if the images themselves are removed.

### /common
Contains shared logic used by all modules, such as settings and basic utility functions.

## Setup
1. **Prepare Environment**: Create a virtual environment and install the requirements.
2. **Start Database**: Use `docker-compose up -d` to start the local database.
3. **Run**: Start a search via the `research_graph` module.
