# System Architecture and Conversion Specifications

This document outlines the design principles and operational logic for the Markdown to EPUB conversion and dispatch pipeline. The system is designed to be modular, safe, and efficient.

## 1. Pre-processing: Obsidian Wikilink Resolution

The Obsidian note-taking structure uses internal links called Wikilinks, formatted as `[[Target]]` or `[[Target|Alias]]`. The standard EPUB format does not understand these. Before converting the file, the system must transform these into standard Markdown links.

The transformation applies the following rules sequentially:
1. **Aliased links:** `[[Filename|Custom Text]]` becomes `[Custom Text](Filename.md)`
2. **Standard links:** `[[Filename]]` becomes `[Filename](Filename.md)`

## 2. Pandoc Compilation Pipeline

We use an external program called Pandoc to convert the text. Pandoc works in three distinct steps:
1. **Reader:** It reads our corrected Markdown text and builds an internal map of the document's structure (an Abstract Syntax Tree).
2. **Filter:** It scans for mathematical equations (LaTeX) and translates them into MathML, which is the required format for math in EPUB3 files.
3. **Writer:** It takes the internal map and generates the final EPUB3 file.

## 3. Conversion Module Architecture (`epub_converter.py`)

* **System Memory Management:** The program reads the original Markdown file into memory, applies the link corrections, and immediately saves the result to a temporary file on the hard drive. This approach protects the original file from being permanently altered. Furthermore, it passes the temporary file to Pandoc, ensuring that the heavy memory processing required for conversion is handled by the external program, not our Python script.
* **Process Execution Overhead:** When the program commands Pandoc to run, it waits for the process to finish. Instead of printing errors to the computer screen, it captures all output internally. If Pandoc fails (for example, due to a formatting error), our program catches the exact error message and safely stops, notifying the user exactly what went wrong.
* **Encapsulation:** The conversion code has a single responsibility. It takes a file path, safely converts the file, and returns the path to the newly created EPUB file. It does not handle emails or configuration.

## 4. Testing Strategy

To ensure the conversion module handles errors correctly, we use an isolated testing approach. 
* We use Python's built-in `unittest.mock` tool to simulate a situation where Pandoc fails. 
* This allows us to verify that our program catches the error and behaves safely without actually needing to run Pandoc or create broken files during the test.

## 5. Dispatcher Module Architecture (`config.py` & `mailer.py`)

The Dispatch module is responsible for taking the finished EPUB file and sending it to the Kindle via email.

### Configuration (`config.py`)
* **Eager State Validation:** Before the system does any work (like converting the file), it checks if the email credentials and Kindle address are provided in the `.env` file. If they are missing, the program stops immediately. This prevents the system from doing the hard work of conversion only to fail at the very end because it cannot send the email.
* **Immutability:** Once the configuration settings are loaded, they are locked into a read-only structure (a frozen dataclass). This ensures that the email password or destination cannot be accidentally changed by the program while it is running.

### Network Transmission (`mailer.py`)
* **MIME Payload Construction:** To send a file via email, it must be packaged correctly. The program reads the EPUB file and labels it strictly as `application/epub+zip`. This ensures the receiving Amazon server recognizes it as a valid book and processes it for the Kindle.
* **Network Protocol State Machine:** The system connects to the email server (using port 587) and immediately requests a secure, encrypted connection (TLS) before sending the password or the book. This keeps the credentials safe.
* **Data Model Constraints:** The provided `.env` setup only requires the sender email, password, and destination. To keep the setup simple, the code automatically defaults to using Gmail's servers (`smtp.gmail.com`). This can be easily changed in the code if a different email provider is used.
