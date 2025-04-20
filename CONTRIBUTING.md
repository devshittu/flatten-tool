# Contributing to Flatten Tool

Thank you for your interest in contributing to the Flatten Tool! We welcome contributions from the community to make this tool more robust, extensible, and user-friendly. This guide outlines how to contribute effectively.

## Getting Started

### Prerequisites

- **Python 3.8+**: Required to run the tool.

- **Git**: For cloning and managing the repository.

- **GitHub CLI (optional)**: Simplifies repository interactions (`gh`).

- **Dependencies**: Install required Python packages:

  ```bash
  pip install tqdm colorama jsonschema pytest
  ```

### Setting Up the Development Environment

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/<your-username>/flatten-tool.git
   cd flatten-tool
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   If `requirements.txt` is not present, install manually:

   ```bash
   pip install tqdm colorama jsonschema pytest
   ```

3. **Run Tests**: Verify the setup by running the test suite:

   ```bash
   pytest tests/test_flatten.py
   ```

4. **Install Locally**: To test the CLI locally:

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

## How to Contribute

### Reporting Issues

- Use the GitHub Issues page to report bugs or suggest features.
- Provide a clear title, description, steps to reproduce (for bugs), and expected behavior.
- Include relevant logs or screenshots if applicable.

### Submitting Pull Requests

1. **Fork the Repository**:

   ```bash
   gh repo fork <your-username>/flatten-tool --clone
   ```

2. **Create a Branch**: Use a descriptive branch name:

   ```bash
   git checkout -b feature/add-new-feature
   ```

3. **Make Changes**:

   - Follow the Coding Standards below.
   - Update tests in `tests/` to cover new functionality.
   - Add or update documentation in `README.md` or `docs/`.

4. **Test Your Changes**: Run the test suite:

   ```bash
   pytest tests/test_flatten.py
   ```

5. **Commit Changes**: Use clear, concise commit messages:

   ```bash
   git commit -m "Add new feature: describe the feature"
   ```

6. **Push and Create a Pull Request**:

   ```bash
   git push origin feature/add-new-feature
   gh pr create --title "Add new feature" --body "Description of changes"
   ```

7. **Code Review**:

   - Respond to feedback promptly.
   - Make requested changes and update the PR.

### Coding Standards

- **Python Style**: Adhere to PEP 8 and PEP 257 for docstrings.
- **Modularity**: Keep code modular, with single-responsibility modules (e.g., `cli.py`, `config.py`).
- **Documentation**:
  - Add docstrings for all functions, classes, and modules.
  - Include inline comments for complex logic.
  - Update `README.md` or `docs/` for user-facing changes.
- **Testing**:
  - Write unit tests for new functionality using `pytest`.
  - Ensure 100% test coverage for new code.
- **Error Handling**: Handle exceptions gracefully and log using the `logging.log` function.

### Sharing Code with LLMs

To improve development efficiency, you may share code snippets with large language models (LLMs) like Grok or ChatGPT for context or suggestions. When doing so:

- **Provide Context**: Include the relevant module (e.g., `file_handler.py`), function, or feature description.
- **Sanitize Code**: Remove sensitive data (e.g., API keys, personal info) before sharing.
- **Validate Suggestions**: Always review and test LLM-generated code to ensure it aligns with the project’s standards and functionality.
- **Credit**: If an LLM significantly contributes to a solution, note it in the PR description (e.g., "Used Grok to draft initial parsing logic, then refined manually").

Example:

```python
# Sharing this function with an LLM to optimize performance
def parse_imports(file_path, aliases, plugins):
    ...
```

### Adding Plugins

To extend import parsing:

1. Create a new plugin in `plugins/` (e.g., `my_parser.py`).
2. Implement a `parse_imports(content, file_path)` function returning a list of imports.
3. Test the plugin by adding it to `/usr/local/share/flatten/plugins/` during development.

### Adding Documentation

- Update `README.md` for user-facing changes.
- Add detailed guides in `docs/` for complex features (e.g., `docs/new-feature.md`).
- Ensure CLI help (`flatten help`) reflects new commands or options.

## Community Guidelines

- Be respectful and inclusive in all interactions.
- Follow the Code of Conduct (to be added).
- Engage constructively in discussions on issues and PRs.

## Contact

For questions, reach out via GitHub Issues or Discussions. Happy contributing!
