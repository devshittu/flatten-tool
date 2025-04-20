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

Install `flatten-tool` in an isolated environment with a globally accessible command:

1. Install `pipx` (if not already installed):

   ```bash
   pip3 install pipx
   pipx ensurepath
   ```

   Restart your terminal after running `pipx ensurepath`.

2. Install `flatten-tool`:

   ```bash
   pipx install flatten-tool
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
- Easy to uninstall: `pipx uninstall flatten-tool`.

### Alternative 1: Local (Sandboxed)

Run the tool in a local virtual environment:

1. Clone the repository:

   ```bash
   git clone https://github.com/<your-username>/flatten-tool.git
   cd flatten-tool
   ```
2. Install locally:

   ```bash
   chmod +x install.sh
   ./install.sh --local
   ```
3. Run the tool:

   ```bash
   python flatten/cli.py flatten init
   python flatten/cli.py flatten ./src/ --recursive
   ```

**Benefits**:

- Fully isolated, no system interference.
- No `sudo` required.
- Easy to uninstall: `./uninstall.sh --local` or delete the `flatten-tool` directory.

### Alternative 2: Global

Install system-wide (use with caution):

1. Install from source:

   ```bash
   git clone https://github.com/<your-username>/flatten-tool.git
   cd flatten-tool
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
pipx uninstall flatten-tool
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
- `flatten/`: Core Python package with CLI, config, file handling, output, and logging modules.
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

## Testing

Run tests:

```bash
pytest tests/test_flatten.py
```

For local installations:

```bash
source .venv/bin/activate
pytest tests/test_flatten.py
deactivate
```

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