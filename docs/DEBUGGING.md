# Debugging Guide for `flatten-tool`

This document outlines the steps taken to resolve the `TypeError: init_project() got an unexpected keyword argument 'interactive'` error in the `flatten-tool` project, along with additional debugging tips for Python projects. The issue stemmed from the Python runtime loading an outdated `init_project` function, despite the updated `src/flatten_tool/flatten/config.py` defining `init_project(interactive=True)`. The steps below were executed in the project root (`/home/mshittu/dev/tools/flatten-tool`) and are specific to the project’s structure and environment (Python 3.12, `zsh` shell, virtual environment).

## Implementation Steps

### 1. Fix `pip install -e .[dev]` in Zsh

The `zsh: no matches found: .[dev]` error occurred because `zsh` interprets square brackets as glob patterns. Quoting the argument or installing dependencies individually resolved this, ensuring `pytest-cov`, `pytest-mock`, and other dev dependencies were installed.

```bash
cd /home/mshittu/dev/tools/flatten-tool
source .venv/bin/activate
# Quote the argument to escape zsh globbing
pip install -e ".[dev]"
# Alternatively, install dev dependencies individually
pip install pytest pytest-cov pre-commit pytest-mock
```

**Verification**:

```bash
pip show pytest-cov
pip show pytest-mock
```

**Expected Output** (for `pytest-cov`):

```
Name: pytest-cov
Version: 6.1.1
Summary: Pytest plugin for measuring coverage.
...
```

### 2. Fully Reset Environment

To eliminate stale bytecode, package state, or conflicting installations, the virtual environment was recreated, and all caches were cleared.

```bash
cd /home/mshittu/dev/tools/flatten-tool
# Deactivate and remove virtual environment
deactivate
rm -rf .venv
# Clear caches
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -exec rm -f {} +
rm -rf .pytest_cache
rm -rf ~/.cache/pre-commit
# Recreate virtual environment
python3 -m venv .venv
source .venv/bin/activate
# Install package and dev dependencies
pip install -e ".[dev]"
```

**Check for conflicting packages**:

```bash
pip list | grep flatten-tool
```

**Expected Output**:

```
flatten-tool 0.1.0 /home/mshittu/dev/tools/flatten-tool
```

**Check global/user installations**:

```bash
python3 -m pip list --user | grep flatten-tool
python3 -m pip list | grep flatten-tool
```

If `flatten-tool` appears outside the virtual environment, uninstall it:

```bash
python3 -m pip uninstall flatten-tool -y
python3 -m pip uninstall flatten-tool -y --user
```

**Note**: On Debian-based systems (e.g., Ubuntu), `pip uninstall` may fail with an `externally-managed-environment` error due to PEP 668. Use `--break-system-packages` cautiously or ensure you’re in a virtual environment:

```bash
pip uninstall flatten-tool -y --break-system-packages
```

### 3. Verify `init_project` Signature

To confirm the correct `init_project` function was loaded, debug prints were added to `src/flatten_tool/flatten/config.py`, and the function’s signature was inspected.

**Update `src/flatten_tool/flatten/config.py`** (only the `init_project` function):

```python
def init_project(interactive=True):
    """Initialize a project with .flatten directory and configuration."""
    from .logging import log
    print(f"DEBUG: init_project signature: interactive={interactive}")  # Debug
    flatten_dir = Path(".flatten")
    if flatten_dir.exists():
        log("Project already initialized", "INFO")
        return
    flatten_dir.mkdir(parents=True, exist_ok=True)
    if interactive and sys.stdin.isatty():
        interactive_config()
    else:
        non_interactive_config()
```

**Inspect the module**:

```bash
python -c "from flatten_tool.flatten.config import init_project; print(init_project.__code__.co_varnames); print(init_project.__module__)"
```

**Expected Output**:

```
('interactive', 'log', 'flatten_dir')
flatten_tool.flatten.config
```

**Note**: The original command attempted `init_project.__file__`, which raised `AttributeError` because functions don’t have a `__file__` attribute. Use `init_project.__module__` or inspect the module’s `__file__`:

```bash
python -c "import flatten_tool.flatten.config; print(flatten_tool.flatten.config.__file__)"
```

**Expected Output**:

```
/home/mshittu/dev/tools/flatten-tool/src/flatten_tool/flatten/config.py
```

### 4. Update Tests and CLI

The `cli.py` and `test_flatten.py` files were already correctly updated:

- `cli.py` calls `init_project(interactive=True)` for the `init` command.
- `test_flatten.py` calls `init_project(interactive=False)` in tests, with `pytest-mock` mocking `sys.stdin`.

**Run a single test with debug output**:

```bash
pytest tests/test_flatten.py::test_init_project_non_interactive --verbose
```

**Expected Output**:

```
DEBUG: init_project signature: interactive=False
...
test_init_project_non_interactive ... ok
```

**Debug with PDB if needed**:

```bash
pytest --pdb tests/test_flatten.py::test_init_project_non_interactive
```

In the debugger:

```python
(Pdb) import inspect
(Pdb) from flatten_tool.flatten.config import init_project
(Pdb) print(inspect.signature(init_project))
(Pdb) print(init_project.__module__)
```

**Expected**:

```
(interactive=True)
flatten_tool.flatten.config
```

### 5. Run Full Test Suite

Run the full test suite with coverage to ensure all tests pass and coverage is generated.

```bash
pytest tests/test_flatten.py --cov=src/flatten_tool/flatten --cov-report=xml
```

**Expected Output**:

```
========== 10 passed in 0.xx seconds ==========
Coverage XML written to file coverage.xml
```

**Note**: The logs showed 40 `DeprecationWarning` messages about `fork()` in `multiprocessing`. These are harmless but can be suppressed by updating `pytest.ini` or using `pytest -p no:warnings`.

### 6. Verify CLI

Test CLI commands to ensure the `flatten` tool works as expected.

```bash
rm -rf .flatten/
flatten init  # Should prompt interactively
flatten ./src/ --recursive
flatten ./src/components/Button.tsx --with-imports
flatten **/readme.md --recursive -o docs.md
flatten examples
flatten feedback
flatten help
```

**Expected**:

- `flatten init` prompts interactively (e.g., “Configuring flatten…”).
- Other commands produce outputs in `.flatten/output/<project>_flattened.txt` or as specified.

**Debug CLI if needed**:

```bash
python -c "from flatten_tool.flatten.config import init_project; import inspect; print(inspect.signature(init_project))"
```

**Expected**:

```
(interactive=True)
```

## Good to Try - Might Be Helpful Tips

These additional debugging techniques can help diagnose similar issues in Python projects, particularly those involving module loading, package installations, or test failures.

1. **Clear Python Module Cache Explicitly**:

   - Stale `.pyc` files or `__pycache__` directories can cause Python to load outdated code.

   ```bash
   find . -name "__pycache__" -exec rm -rf {} +
   find . -name "*.pyc" -exec rm -f {} +
   ```

2. **Set `PYTHONPATH` to Prioritize Local Modules**:

   - Ensure the project’s `src/` directory is loaded before other paths to avoid conflicts.

   ```bash
   export PYTHONPATH=$PWD/src:$PYTHONPATH
   echo $PYTHONPATH
   ```

   - You used this precaution, which is helpful if global packages shadow local ones.

3. **Inspect `sys.path` for Module Resolution**:

   - Check where Python is looking for modules to identify conflicts.

   ```bash
   python -c "import sys; print('\n'.join(sys.path))"
   ```

   - Ensure `/home/mshittu/dev/tools/flatten-tool/src` appears early in the list.

4. **Use `pipdeptree` to Debug Dependency Conflicts**:

   - Install `pipdeptree` to visualize dependency conflicts or unexpected versions.

   ```bash
   pip install pipdeptree
   pipdeptree | grep flatten-tool
   ```

5. **Run Tests with `-s` to Capture Debug Output**:

   - Disable output capturing to see debug prints (e.g., `DEBUG: init_project signature`).

   ```bash
   pytest -s tests/test_flatten.py::test_init_project_non_interactive
   ```

6. **Check for Global Package Conflicts**:

   - Verify no `flatten-tool` is installed globally or in user site-packages.

   ```bash
   python3 -m pip list --user | grep flatten-tool
   python3 -m pip list | grep flatten-tool
   ```

7. **Use `python -m` to Run Modules Directly**:

   - Bypass entrypoint issues by running the CLI module directly.

   ```bash
   python -m flatten_tool.flatten.cli init
   ```

8. **Enable Verbose Pip Output**:

   - Use `-v` to debug pip installation issues.

   ```bash
   pip install -e ".[dev]" -v
   ```

9. **Inspect Editable Installation**:

   - Check the `.pth` file created by `pip install -e` to ensure it points to the correct path.

   ```bash
   cat .venv/lib/python3.12/site-packages/__editable__.flatten_tool-0.1.0.pth
   ```

   - Expected: `/home/mshittu/dev/tools/flatten-tool/src`

10. **Suppress Multiprocessing Warnings**:

    - Address `DeprecationWarning` about `fork()` in tests by updating `pytest.ini`.

    ```ini
    [pytest]
    python_files = tests/*.py
    python_functions = test_*
    pythonpath = src
    filterwarnings =
        ignore::DeprecationWarning:multiprocessing
    ```

11. **Use `pre-commit` for Code Quality**:

    - Ensure linting and formatting are consistent to catch syntax errors.

    ```bash
    pre-commit run --all-files
    ```

12. **Debug with `strace` for System-Level Issues**:

    - If Python loads unexpected files, use `strace` to trace file access.

    ```bash
    strace -o strace.log python -c "from flatten_tool.flatten.config import init_project"
    grep config.py strace.log
    ```

13. **Check Python Version Consistency**:

    - Ensure the virtual environment uses the expected Python version.

    ```bash
    python --version
    .venv/bin/python --version
    ```

    - Expected: `Python 3.12.3`

14. **Rebuild Package Metadata**:

    - If `pip install -e` fails, clear `dist/` and rebuild.

    ```bash
    rm -rf dist/ build/
    pip install -e ".[dev]"
    ```

15. **Use `pytest` with `--pdbcls=IPython.terminal.debugger:TerminalPdb`**:

    - Enable an interactive debugger for better debugging.

    ```bash
    pytest --pdbcls=IPython.terminal.debugger:TerminalPdb tests/test_flatten.py
    ```

16. **Check for `.egg-info` Artifacts**:

    - Remove stale `.egg-info` directories that might interfere with installations.

    ```bash
    rm -rf *.egg-info
    ```

17. **Verify `pyproject.toml` Parsing**:

    - Ensure `pyproject.toml` is valid and dependencies are correctly defined.

    ```bash
    python -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb')))"
    ```

18. **Use `pip cache purge`**:
    - Clear pip’s cache to avoid corrupted downloads.
    ```bash
    pip cache purge
    ```
