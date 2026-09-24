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

## 6. Troubleshooting and Historical Failure States

During the architectural development and testing of this pipeline, several deterministic failure states were encountered. This section documents the symptoms, the diagnostic isolation process, and the structural resolutions to serve as a reference for future maintenance.

### 6.1. Missing System Dependencies (Pandoc)
* **Symptom:** The pipeline terminated immediately with `[Errno 2] No such file or directory: 'pandoc'`.
* **Diagnostic:** The Python `subprocess` module successfully attempted the system call, but the host operating system (Ubuntu/WSL) could not locate the binary executable in its `$PATH`.
* **Resolution:** The system dependency was explicitly installed via the OS package manager (`sudo apt install pandoc`).

### 6.2. Network Routing Anomalies (Hardcoded Hosts)
* **Symptom:** The system attempted to authenticate with `smtp.gmail.com` and was rejected, despite the user providing iCloud credentials in the `.env` file.
* **Diagnostic:** The initial mailer implementation utilized a hardcoded fallback for the Gmail SMTP servers, which bypassed the user's intended iCloud configuration.
* **Resolution:** The `config.py` data model was expanded to dynamically ingest `SMTP_HOST` and `SMTP_PORT` from the environment, allowing deterministic routing to any standard mail provider (e.g., `smtp.mail.me.com`).

### 6.3. The Amazon "Black Box" and Loopback Diagnostics
* **Symptom:** The Python terminal reported a successful transmission ("Transmission successful"), but the EPUB artifact never appeared on the destination Kindle device. No error email was received.
* **Diagnostic:** Amazon's receiving servers operate as a "black box" and will silently drop network payloads if they suspect spam. To determine if the failure was in our Python code or Amazon's filters, we created an isolated "Loopback Diagnostic" (`scripts/verify_network.py`). This script sent a test email from the user's iCloud account *back* to the user's iCloud account. 
* **Result:** The loopback test succeeded, mathematically proving our SMTP network logic was flawless and isolating the failure state entirely to Amazon's inbound filter heuristics.
* **Resolution:** Standard cryptographic and temporal headers (`Message-ID` and `Date`) were injected into the MIME payload to make the automated emails look identical to standard human-sent emails, bypassing basic spam filters.

### 6.4. Amazon E999 Internal Error (Metadata Constraints)
* **Symptom:** Amazon sent an automated bounce-back email citing a generic "E999 — Send to Kindle internal error" for the attached `.epub` file.
* **Diagnostic:** Amazon's proprietary ingestion engine enforces strict adherence to Dublin Core EPUB3 standards. If an EPUB container lacks mandatory metadata—specifically a Title and a Language code—the Amazon parser fails to read the file and aborts the transfer. Since our source `.md` files lacked explicit YAML frontmatter, Pandoc was generating structurally valid but metadata-deficient EPUBs.
* **Resolution:** The `epub_converter.py` execution vector was patched to dynamically inject the file's name as the `--metadata title=...` and a standard language code `--metadata language=pt-BR`. This guaranteed the generated abstract syntax tree satisfied Amazon's strict boundary constraints.
