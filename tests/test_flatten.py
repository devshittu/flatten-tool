"""
Unit tests for the flatten tool.
"""

import json
import os

import pytest

from flatten_tool.flatten.config import init_project, load_config
from flatten_tool.flatten.file_handler import collect_files, flatten_files, parse_imports


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    os.chdir(tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def mock_stdin(mocker):
    """Mock sys.stdin to avoid fileno() issues in tests."""
    mock_stdin = mocker.patch("sys.stdin")
    mock_stdin.isatty.return_value = False
    mock_stdin.fileno.side_effect = AttributeError("Mocked stdin has no fileno")
    return mock_stdin


def test_load_config(temp_dir):
    """Test loading a custom configuration."""
    config_path = temp_dir / ".flatten/config.json"
    config_path.parent.mkdir()
    with open(config_path, "w") as f:
        json.dump({"line_limit": 1000, "output_format": "txt"}, f)
    config = load_config()
    assert config["line_limit"] == 1000
    assert config["output_format"] == "txt"


def test_parse_imports(temp_dir):
    """Test parsing imports from a JavaScript file."""
    file_path = temp_dir / "test.js"
    with open(file_path, "w") as f:
        f.write('import x from "./x.js";')
    aliases = {"@": "src"}
    imports = parse_imports(str(file_path), tuple(sorted(aliases.items())), ())
    assert str(temp_dir / "x.js") in imports


def test_flatten_file(temp_dir):
    """Test flattening a file with its dependencies."""
    init_project(interactive=False)
    file_path = temp_dir / "test.js"
    dep_path = temp_dir / "dep.js"
    with open(file_path, "w") as f:
        f.write('import dep from "./dep.js";\nconsole.log("test");')
    with open(dep_path, "w") as f:
        f.write("export default function dep() {}")
    flatten_files([str(file_path)], with_imports=True)
    output_path = temp_dir / ".flatten/output" / f"{os.path.basename(temp_dir)}_flattened.txt"
    assert output_path.exists()
    with open(output_path, "r") as f:
        content = f.read()
    assert f"# File path: {file_path}" in content
    assert f"# File path: {dep_path}" in content
    assert "console.log(" in content
    assert "export default" in content


def test_flatten_file_without_imports(temp_dir):
    """Test flattening a file without including imports."""
    init_project(interactive=False)
    file_path = temp_dir / "test.js"
    with open(file_path, "w") as f:
        f.write('console.log("test");')
    flatten_files([str(file_path)], with_imports=False)
    output_path = temp_dir / ".flatten/output" / f"{os.path.basename(temp_dir)}_flattened.txt"
    assert output_path.exists()
    with open(output_path, "r") as f:
        content = f.read()
    assert f"# File path: {file_path}" in content
    assert "console.log(" in content
    assert len([line for line in content.splitlines() if line.startswith("# File path:")]) == 1


def test_flatten_directory(temp_dir):
    """Test flattening a directory non-recursively."""
    init_project(interactive=False)
    src_dir = temp_dir / "src"
    src_dir.mkdir()
    file1 = src_dir / "file1.js"
    file2 = src_dir / "file2.py"
    with open(file1, "w") as f:
        f.write("console.log('file1');")
    with open(file2, "w") as f:
        f.write("print('file2')")
    flatten_files([str(src_dir)], recursive=False)
    output_path = temp_dir / ".flatten/output" / f"{os.path.basename(temp_dir)}_flattened.txt"
    assert output_path.exists()
    with open(output_path, "r") as f:
        content = f.read()
    assert f"# File path: {file1}" in content
    assert f"# File path: {file2}" in content
    assert "console.log" in content
    assert "print('file2')" in content


def test_flatten_directory_recursive(temp_dir):
    """Test flattening a directory recursively."""
    init_project(interactive=False)
    src_dir = temp_dir / "src"
    sub_dir = src_dir / "sub"
    sub_dir.mkdir(parents=True)
    file1 = src_dir / "file1.js"
    file2 = sub_dir / "file2.py"
    with open(file1, "w") as f:
        f.write("console.log('file1');")
    with open(file2, "w") as f:
        f.write("print('file2')")
    flatten_files([str(src_dir)], recursive=True)
    output_path = temp_dir / ".flatten/output" / f"{os.path.basename(temp_dir)}_flattened.txt"
    assert output_path.exists()
    with open(output_path, "r") as f:
        content = f.read()
    assert f"# File path: {file1}" in content
    assert f"# File path: {file2}" in content
    assert "console.log" in content
    assert "print('file2')" in content


def test_flatten_wildcard(temp_dir):
    """Test flattening files matching a wildcard pattern."""
    init_project(interactive=False)
    src_dir = temp_dir / "src"
    sub_dir = src_dir / "sub"
    sub_dir.mkdir(parents=True)
    file1 = src_dir / "readme.md"
    file2 = sub_dir / "readme.md"
    with open(file1, "w") as f:
        f.write("# File1")
    with open(file2, "w") as f:
        f.write("# File2")
    config = load_config()
    config["supported_extensions"] = [".md"]
    config_path = temp_dir / ".flatten/config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f)
    flatten_files(["**/readme.md"], recursive=True)
    output_path = temp_dir / ".flatten/output" / f"{os.path.basename(temp_dir)}_flattened.txt"
    assert output_path.exists()
    with open(output_path, "r") as f:
        content = f.read()
    assert f"# File path: {file1}" in content
    assert f"# File path: {file2}" in content
    assert "# File1" in content
    assert "# File2" in content


def test_collect_files(temp_dir):
    """Test collecting files from a directory with exclusions."""
    init_project(interactive=False)
    config = load_config()
    config["supported_extensions"] = [".js"]
    src_dir = temp_dir / "src"
    src_dir.mkdir()
    file1 = src_dir / "file1.js"
    file2 = src_dir / "node_modules" / "file2.js"
    file2.parent.mkdir()
    with open(file1, "w") as f:
        f.write("")
    with open(file2, "w") as f:
        f.write("")
    files = collect_files([str(src_dir)], config, recursive=False)
    assert str(file1) in files
    assert str(file2) not in files


def test_flatten_recursive_with_init(temp_dir):
    """Test flattening a directory recursively after initialization."""
    init_project(interactive=False)
    src_dir = temp_dir / "src"
    sub_dir = src_dir / "sub"
    sub_dir.mkdir(parents=True)
    file1 = src_dir / "file1.js"
    file2 = sub_dir / "file2.js"
    with open(file1, "w") as f:
        f.write("console.log('file1');")
    with open(file2, "w") as f:
        f.write("console.log('file2');")
    config = load_config()
    config["supported_extensions"] = [".js"]
    config_path = temp_dir / ".flatten/config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f)
    flatten_files([str(src_dir)], recursive=True)
    output_path = temp_dir / ".flatten/output" / f"{os.path.basename(temp_dir)}_flattened.txt"
    assert output_path.exists()
    with open(output_path, "r") as f:
        content = f.read()
    assert f"# File path: {file1}" in content
    assert f"# File path: {file2}" in content
    assert "console.log('file1')" in content
    assert "console.log('file2')" in content


def test_init_project_non_interactive(temp_dir):
    """Test non-interactive project initialization."""
    init_project(interactive=False)
    config_path = temp_dir / ".flatten/config.json"
    assert config_path.exists()
    with open(config_path, "r") as f:
        config = json.load(f)
    assert config["supported_extensions"] == [".py", ".js", ".ts", ".tsx"]
    assert config["output_format"] == "txt"
    assert config["line_limit"] == 2000
    gitignore_path = temp_dir / ".gitignore"
    assert gitignore_path.exists()
    with open(gitignore_path, "r") as f:
        assert ".flatten/" in f.read()


# File path: tests/test_flatten.py
