# Development Guide for Flatten Tool

This guide provides detailed instructions for setting up a development environment, running tests, and troubleshooting common issues for contributors to the `flatten-tool` project. For contribution guidelines, see CONTRIBUTING.md.

## Prerequisites

- **Python**: Version 3.8 or higher.
- **Git**: For cloning and version control.
- **VS Code** (optional): Recommended for linting and formatting integration.
- **pipx** (optional): For isolated package installation.

## Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/mshittiah/flatten-tool.git
   cd flatten-tool
   ```

2. **Create a Virtual Environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:

   Install the package in editable mode and development dependencies:

   ```bash
   pip install -e .[dev]
   ```

4. **Install Pre-commit Hooks**:

   ```bash
   pre-commit install
   ```

5. **Configure VS Code** (optional):

   - Open the project: `code .`
   - Select the `.venv` interpreter (Ctrl+Shift+P, "Python: Select Interpreter", choose `.venv/bin/python`).
   - Install recommended extensions:

     ```bash
     code --install-extension ms-python.python
     code --install-extension ms-python.black-formatter
     code --install-extension ms-python.flake8
     ```
   - The `.vscode/settings.json` enables linting, formatting, and import sorting on save.

## Linting and Formatting

The project uses:

- **Flake8**: For code quality checks (line length, undefined names, etc.).
- **Black**: For consistent code formatting.
- **isort**: For sorting imports.

### Run Manually

```bash
flake8 . --max-line-length=120 --extend-exclude=.venv,venv,dist,build,.git,.github,.pre-commit-cache
black . --line-length=120
isort . --profile=black --line-length=120
```

### Pre-commit Hooks

Pre-commit runs these checks automatically on `git commit`. To test all files:

```bash
pre-commit run --all-files
```

### Troubleshooting

- **Dependency Conflicts**:
  - Clear the pre-commit cache:

    ```bash
    rm -rf ~/.cache/pre-commit
    pre-commit install
    ```
  - Update hooks to stable versions:

    ```bash
    pre-commit autoupdate
    ```
  - Check `.pre-commit-config.yaml` for pinned versions (e.g., `black==24.8.0`).
- **Flake8 Errors**:
  - Run `flake8` manually to identify issues:

    ```bash
    flake8 . --max-line-length=120 --extend-exclude=.venv,venv,dist,build,.git,.github,.pre-commit-cache
    ```
  - Save files in VS Code to apply fixes automatically.
- **Black/isort Modifications**:
  - If hooks reformat files, stage changes:

    ```bash
    git add .
    git commit -m "Apply Black/isort formatting"
    ```
  - Ensure `.vscode/settings.json` enables formatting on save.
- **E902 FileNotFoundError**:
  - Verify `--extend-exclude` in `.pre-commit-config.yaml` includes `.venv,venv,dist,build,.git,.github,.pre-commit-cache`.
  - Clear pre-commit cache if errors persist.
- **Deprecated Stage Warnings**:
  - Run `pre-commit autoupdate` to update hook versions.
  - Commit changes to `.pre-commit-config.yaml`.

## Testing

Tests are located in `tests/` and use pytest.

### Run Tests

```bash
pip install -e .
pytest tests/test_flatten.py
```

### Generate Coverage

```bash
pytest tests/test_flatten.py --cov=src/flatten_tool/flatten --cov-report=xml
```

### Troubleshooting

- **ModuleNotFoundError or Circular Imports**:
  - Ensure the package is installed:

    ```bash
    pip install -e .
    ```
  - Check for circular imports in `src/flatten_tool/flatten/`. The `config.py` and `logging.py` modules have been refactored to avoid this.
  - Run tests with `python -m pytest`:

    ```bash
    python -m pytest tests/test_flatten.py
    ```
- **Test Discovery**:
  - Run `pytest --collect-only` to debug test collection.
  - Ensure test files follow the `test_*.py` naming convention and `pytest.ini` includes `pythonpath = src`.

## Running the CLI

After installing the package:

```bash
pip install -e .
flatten init
flatten ./src/ --recursive
```

Alternatively, run as a module:

```bash
python -m flatten_tool.flatten.cli init
python -m flatten_tool.flatten.cli flatten ./src/ --recursive
```

### Troubleshooting

- **ImportError: attempted relative import with no known parent package**:
  - Avoid running `python src/flatten_tool/flatten/cli.py` directly.
  - Use `python -m flatten_tool.flatten.cli` or install the package (`pip install -e .`) and run `flatten`.
- **Command Not Found**:
  - Ensure the package is installed and the virtual environment is active.
  - Verify `pyproject.toml`’s `[project.scripts]` entry: `flatten = "flatten_tool.flatten.cli:main"`.

## CI/CD

The project uses GitHub Actions (`.github/workflows/ci.yml`) to:

- Run linting (`flake8`) and tests (`pytest`) on Python 3.8, 3.9, and 3.10.
- Test `pipx` installation.
- Publish to PyPI on tagged releases (`.github/workflows/release.yml`).

To match CI locally:

```bash
flake8 . --max-line-length=120 --extend-exclude=.venv,venv,dist,build,.git,.github,.pre-commit-cache
pytest tests/test_flatten.py --cov=src/flatten_tool/flatten --cov-report=xml
```

## Common Issues

- **Pre-commit Cache Corruption**:
  - Symptom: `CalledProcessError` or version conflicts.
  - Fix: Clear cache (`rm -rf ~/.cache/pre-commit`) and reinstall (`pre-commit install`).
- **Circular Imports**:
  - Symptom: `ImportError` when running tests or CLI.
  - Fix: Check `src/flatten_tool/flatten/` for mutual imports. Refactor to use lazy imports or pass config as a parameter (e.g., `logging.py`).
- **Tests Not Found**:
  - Symptom: `collected 0 items`.
  - Fix: Check `pytest.ini` and test file names. Run `pytest --collect-only`.
- **CLI Import Errors**:
  - Symptom: `ImportError` when running `python src/flatten_tool/flatten/cli.py`.
  - Fix: Use `python -m flatten_tool.flatten.cli` or install the package.
- **CI Failures**:
  - Symptom: Linting or test errors in GitHub Actions.
  - Fix: Reproduce locally with CI commands. Check error logs in the Actions tab.

## Releasing

To release a new version:

1. Update `pyproject.toml` with the new version (e.g., `version = "1.0.1"`).
2. Commit changes:

   ```bash
   git commit -m "Bump version to 1.0.1"
   ```
3. Tag the release:

   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```
4. The `release.yml` workflow will build and publish to PyPI.

Ensure you have a `PYPI_API_TOKEN` in GitHub Secrets.

## Feedback

Run `flatten feedback` to submit feedback, or open an issue on GitHub.

## License

This project is licensed under the MIT License. See LICENSE.
