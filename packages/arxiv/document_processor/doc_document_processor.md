# Document Processor Specification

The `document_processor` module acts as the file manager for downloaded research papers.

## Responsibilities

1.  **Archive Extraction:** Downloaded files are typically `.tar.gz` archives containing multiple files (images, `.tex` source files, `.bib` files, etc.). The processor must extract these into a temporary working directory.
2.  **Main File Discovery:** It must locate the primary document file that contains the actual paper content.
    *   For LaTeX projects, this means finding the `.tex` file that contains `\begin{document}`.
    *   If no such file exists, it should fall back to checking if there is only one `.tex` file.
    *   If the downloaded file was directly a `.pdf`, it simply marks the PDF as the main file.
3.  **State Management:** It outputs a domain model representing the extracted location and the path to the main file, to be passed to the converter.
