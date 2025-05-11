# Flatten Tool

A command-line tool to flatten project files into a single file with descriptive paths, designed for Python and JavaScript projects on Unix/Linux. It supports auto-detection of files and directories, wildcard patterns, and one-depth import inclusion, making it ideal for code sharing, documentation, or analysis.

## Features

- **Auto-Detection**: Automatically handles files (e.g., `./file.js`) and directories (e.g., `./src/`, `.`).
- **Wildcard Support**: Flatten files matching patterns (e.g., `**/readme.md`).
- **Imports**: Include one-depth dependencies with `--with-imports`.
- **Modular Design**: Organized as a Python package with plugins for extensibility.
- **Output Formats**: Supports `txt`, `md`, and `json`.
- **Parallel Processing**: Uses `multiprocessing` for performance.
- **Interactive Setup**: Configure projects with `flatten init`.

## Installation

### Recommended: Pipx (Isolated and Global)

Install `flattenify` in an isolated environment with a globally accessible command:

1. Install `pipx` (if not already installed):

   ```bash
   pip3 install pipx
   pipx ensurepath
   ```

   Restart your terminal after running `pipx ensurepath`.

2. Install `flattenify`:

   ```bash
   pipx install flattenify
   ```

3. Run the tool:

   ```bash
   flatten init
   flatten ./src/ --recursive
   ```

**Benefits**:

- Isolated dependencies, no conflicts with system Python or other projects.
- No `sudo` required.
- Global `flatten` command available everywhere.
- Easy to uninstall: `pipx uninstall flattenify`.

### Alternative 1: Local (Sandboxed)

Run the tool in a local virtual environment:

1. Clone the repository:

   ```bash
   git clone https://github.com/mshittiah/flattenify.git
   cd flattenify
   ```

2. Install locally:

   ```bash
   chmod +x install.sh
   ./install.sh --local
   ```

3. Install the package:

   ```bash
   pip install -e .
   ```

4. Run the tool:

   ```bash
   python -m flatten_tool.flatten.cli init
   python -m flatten_tool.flatten.cli flatten ./src/ --recursive
   ```

**Benefits**:

- Fully isolated, no system interference.
- No `sudo` required.
- Easy to uninstall: `./uninstall.sh --local` or delete the `flattenify` directory.

### Alternative 2: Global

Install system-wide (use with caution):

1. Install from source:

   ```bash
   git clone https://github.com/mshittiah/flattenify.git
   cd flattenify
   chmod +x install.sh
   ./install.sh --global
   ```

2. Run the tool:

   ```bash
   flatten init
   flatten ./src/ --recursive
   ```

**Notes**:

- Requires `sudo` for file copying.
- Checks for dependency conflicts and prompts for confirmation.
- Risk of conflicts with existing Python packages.

## Uninstallation

### Pipx

```bash
pipx uninstall flattenify
```

### Local

```bash
chmod +x uninstall.sh
./uninstall.sh --local
```

### Global

```bash
chmod +x uninstall.sh
./uninstall.sh --global
```

## Directory Structure

- `.github/workflows/`: GitHub Actions for CI/CD.
- `src/flatten_tool/`: Core Python package, plugins, and templates.
  - `flatten/`: CLI, config, file handling, output, and logging modules.
  - `plugins/`: Custom import parsers.
  - `templates/`: Sample configurations (e.g., for Next.js).
- `tests/`: Unit tests using pytest.
- `install.sh`: Installs the tool (pipx, local, or global).
- `uninstall.sh`: Removes the tool and dependencies.
- `pyproject.toml`: Package metadata for PyPI.
- `README.md`: Project documentation.
- `CONTRIBUTING.md`: Contribution guidelines.
- `CODE_OF_CONDUCT.md`: Community standards.
- `LICENSE`: MIT License.
- `docs/`: Additional documentation, including tool overview.
- `.pre-commit-config.yaml`: Pre-commit hooks for linting.
- `.vscode/settings.json`: VS Code settings for linting and formatting.

## Development

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/mshittiah/flattenify.git
   cd flattenify
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies and the package in editable mode:

   ```bash
   pip install -e .[dev]
   pip install pre-commit pytest pytest-cov
   ```

4. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

5. Configure VS Code:

   - Open the project in VS Code: `code .`

   - Ensure the `.venv` interpreter is selected (Ctrl+Shift+P, "Python: Select Interpreter", choose `.venv/bin/python`).

   - Install recommended extensions:

     ```bash
     code --install-extension ms-python.python
     code --install-extension ms-python.black-formatter
     code --install-extension ms-python.flake8
     ```

   - The `.vscode/settings.json` configures automatic linting and formatting on save.

### Linting and Formatting

- **Flake8**: Enforces code quality (e.g., undefined names, line length).
- **Black**: Formats code with a consistent style.
- **isort**: Organizes imports.

Run manually:

```bash
flake8 . --max-line-length=120 --extend-exclude=.venv,venv,dist,build,.git,.github,.pre-commit-cache
black . --line-length=120
isort . --profile=black --line-length=120
```

Pre-commit hooks run these automatically on commit. VS Code applies Black and Flake8 on save.

**Troubleshooting Pre-commit Failures**:

- **Dependency Conflicts**:

  - If pre-commit fails with a `CalledProcessError`, clear the cache:

    ```bash
    rm -rf ~/.cache/pre-commit
    pre-commit install
    ```

  - Update hooks to stable versions:

    ```bash
    pre-commit autoupdate
    ```

- **Flake8 Errors**:

  - Run `flake8 . --max-line-length=120 --extend-exclude=.venv,venv,dist,build,.git,.github,.pre-commit-cache` to identify issues.
  - Fix errors manually or use VS Code’s linting (save files to apply fixes).

- **Black/isort Modifications**:

  - If Black or isort reformats files, save changes in VS Code (Ctrl+S) before committing.
  - Run `black . --line-length=120` and `isort . --profile=black --line-length=120` manually to fix.

- **Unstaged Files**:

  - Pre-commit stashes unstaged changes. After a failed commit, check modified files (`git diff`), stage them (`git add .`), and recommit.

- **General**:

  - Run `pre-commit run --all-files` to test all hooks.
  - Ensure `.venv` is active (`source .venv/bin/activate`) and dependencies are installed.

### Testing

Run tests after installing the package:

```bash
pip install -e .
pytest tests/test_flatten.py
```

Generate coverage report:

```bash
pytest tests/test_flatten.py --cov=src/flatten_tool/flatten --cov-report=xml
```

**Troubleshooting Test Failures**:

- **ModuleNotFoundError or Circular Imports**:

  - Ensure the package is installed in editable mode:

    ```bash
    pip install -e .
    ```

  - Check for circular imports in `src/flatten_tool/flatten/`. Refactor modules to avoid mutual dependencies.

  - Run tests with `python -m pytest` to ensure proper module resolution:

    ```bash
    python -m pytest tests/test_flatten.py
    ```

- **Test Discovery**:

  - Check that test files are in `tests/` and follow the `test_*.py` naming convention.
  - Run `pytest --collect-only` to debug test collection.

- **ImportError: attempted relative import with no known parent package**:
  - Avoid running `python src/flatten_tool/flatten/cli.py` directly.
  - Use `python -m flatten_tool.flatten.cli` or install the package (`pip install -e .`) and run `flatten`.
- **Command Not Found**:
  - Ensure the package is installed (`pip install -e .`) and the virtual environment is active (`source .venv/bin/activate`).
  - Check `pyproject.toml`’s `[project.scripts]` entry: `flatten = "flatten_tool.flatten.cli:main"`.
- **Flake8 E902 FileNotFoundError for .venv, venv, dist, build, etc.**:
  - Ensure `.flake8` and `.pre-commit-config.yaml` exclude these paths (e.g., `.venv`, `.git`, `tests/__pycache__`).
  - Clear pre-commit cache: `rm -rf ~/.cache/pre-commit`.
  - Run Flake8 manually to verify: `flake8 . --config=.flake8`.
- **Test Failures in tests/test_flatten.py**:
  - **test_load_config**: If `ValidationError` occurs, ensure `config.py` merges partial configs with `DEFAULT_CONFIG`.
  - **test_flatten_wildcard**: Create `.flatten` directory before writing `config.json` in tests.
  - **test_collect_files**: Set `supported_extensions` to include relevant file types (e.g., `.js`) in tests.
  - **test_flatten_file_without_imports**: Verify output has one `# File path:` marker per file.
  - Run tests: `pytest tests/test_flatten.py --cov=src/flatten_tool/flatten --cov-report=xml`.

### Running the CLI

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

**Troubleshooting CLI Issues**:

- **ImportError**:
  - Avoid running `python src/flatten_tool/flatten/cli.py` directly, as it breaks relative imports.
  - Use `python -m flatten_tool.flatten.cli` or install the package (`pip install -e .`) and run `flatten`.
- **Command Not Found**:
  - Ensure the package is installed and the virtual environment is active.
  - Check `pyproject.toml`’s `[project.scripts]` entry.

### Updating Hooks

To keep pre-commit hooks stable:

```bash
pre-commit autoupdate
git add .pre-commit-config.yaml
git commit -m "Update pre-commit hooks to stable versions"
```

Check versions in `.pre-commit-config.yaml` to avoid unstable releases.

## Contributing

We welcome contributions! See CONTRIBUTING.md for guidelines on reporting issues, submitting pull requests, adding plugins, and more.

## Code of Conduct

Please adhere to our Code of Conduct to ensure a welcoming and inclusive community.

## Feedback

Submit feedback:

```bash
flatten feedback
```

Feedback is saved to `.flatten/feedback/`.

## License

This project is licensed under the MIT License. See LICENSE for details.
