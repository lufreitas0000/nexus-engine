# Identified Issues and Improvements

## 1. Missing `pypdf` Fallback in PDF-to-Markdown Conversion
**File**: `src/converter/spliter_integration.py`
**Description**: The requirements state that the PDF-to-Markdown conversion pipeline must include a fallback mechanism using `pypdf` to extract raw text if the `spliter` CLI fails or acts as a stub. Currently, if the `spliter` CLI fails to generate the output file, the code only creates a placeholder Markdown file rather than extracting the text with `pypdf`. Furthermore, if `cli_path` does not exist, it raises a `FileNotFoundError` without any fallback attempt.

## 2. Resource Leaks in EPUB Converter
**File**: `src/converter/epub_converter.py`
**Description**: Temporary files (`temp_buffer` and `temp_css`) are created with `delete=False`. The code attempts to clean them up at the end of the function or inside the `except subprocess.CalledProcessError` block. However, if an exception occurs *before* the `try...except` block (e.g., during the generation of the temporary CSS file or if `subprocess.run` raises an exception other than `CalledProcessError`, such as `FileNotFoundError`), these temporary files will not be deleted, resulting in resource leaks on the filesystem. A `finally` block or context manager (`with`) should be used to ensure reliable cleanup.

## 3. Incomplete Cleanup of Temporary Uploads in UI
**File**: `src/ui/app.py`
**Description**: Uploaded files and intermediate Markdown files are saved to a `temp_upload` directory. While there is a cleanup step (`shutil.rmtree(temp_dir)`) upon successful completion (when the user clicks "Start Over"), there is no reliable cleanup if an error occurs during PDF conversion or EPUB compilation. This will cause the `temp_upload` directory to accumulate abandoned files over time.

## 4. Potential Type Conversion Failure Not Fully Handled
**File**: `src/dispatcher/config.py`
**Description**: While `int(port_str)` is wrapped in a `try...except ValueError`, `host` is not validated and could lead to strange behaviors if empty or malformed. Not a critical bug, but could be improved.

## 5. Potential Unhandled Exceptions
**File**: `src/dispatcher/mailer.py`
**Description**: Reads the entire binary file into memory (`binary_payload = file_descriptor.read()`). For very large PDFs or EPUBs, this could lead to memory exhaustion. While likely fine for Kindle-sized files, it is not optimally resilient.

## 6. Deprecated/Missing Feature
**File**: `main.py`
**Description**: The `--keep` flag is present in `argparse` but its functionality is deprecated and ignored by the script. It could be removed for cleaner code.
