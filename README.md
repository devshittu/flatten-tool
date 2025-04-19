# Flatten Tool

A command-line tool to flatten project files into a single file with descriptive paths, designed for Python and JavaScript projects on Unix/Linux.

## Installation

1. Clone the repository or download the files.
2. Run the installer:

   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. Install dependencies:

   ```bash
   pip3 install tqdm colorama jsonschema pytest
   ```

## Usage

Initialize a project:

```bash
flatten init
```

Flatten a file:

```bash
flatten ./src/components/Button.tsx
```

Flatten a file with dependencies:

```bash
flatten ./src/components/Button.tsx --with-imports
```

Flatten a directory:

```bash
flatten ./src/
```

Flatten a directory recursively:

```bash
flatten ./src/ --recursive
```

Flatten files matching a pattern:

```bash
flatten **/readme.md --recursive
```

View examples:

```bash
flatten examples
```

Get detailed help:

```bash
flatten help
```

## Uninstallation

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## Directory Structure

- `flatten/`: Core Python package with CLI, config, file handling, output, and logging modules.
- `plugins/`: Custom import parsers.
- `templates/`: Sample configurations (e.g., for Next.js).
- `tests/`: Unit tests using pytest.
- `install.sh`: Installs the tool system-wide.
- `uninstall.sh`: Removes the tool.
- `README.md`: Project documentation.

## Testing

Run tests:

```bash
pytest tests/test_flatten.py
```

## Feedback

Submit feedback:

```bash
flatten feedback
```

Feedback is saved to `.flatten/feedback/`.