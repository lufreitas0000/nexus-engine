# Contributing to Kindle Artifact Pipeline

Thank you for your interest in contributing to the Kindle Artifact Pipeline! This open-source tool relies on community support to handle edge cases, expand hardware configurations, and improve the user experience.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```shell
   git clone --recurse-submodules https://github.com/your-username/kindle-artifact-pipeline.git
   ```
   *Note: Using `--recurse-submodules` is required to fetch the `spliter` dependency.*
3. **Install dependencies**:
   It is recommended to use a virtual environment (`venv` or `conda`):
   ```shell
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   *You also need to install `pandoc` on your local machine to run tests locally.*

## Branching Strategy

- **`main`**: The primary branch representing the stable release.
- **Feature Branches**: Branch off from `main` using descriptive names (e.g., `feature/add-scribe-settings`, `fix/epub-margins`).

## Testing

This project uses `unittest` to maintain a high degree of reliability. Before submitting any pull request, please run the full test suite:

```shell
PYTHONPATH=. python -m unittest discover tests/
```

Ensure that your new code also includes test coverage.

## Pull Request Guidelines

- Describe your changes in detail in the PR description.
- Reference any open issues that your PR addresses.
- Ensure all tests pass.
- Format code according to PEP-8 standards.

Thank you for contributing!
