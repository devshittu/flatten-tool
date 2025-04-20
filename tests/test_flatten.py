"""
Unit tests for the flatten tool.
"""

import json
import os

import pytest
from flatten.config import load_config, resolve_aliases
from flatten.file_handler import collect_files, flatten_files, parse_imports


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    os.chdir(tmp_path)
    return tmp_path


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
    assert len([line for line in content.splitlines() if line.startswith("# File path:")]) == 2  # Only one file


def test_flatten_directory(temp_dir):
    """Test flattening a directory non-recursively."""
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
    with open(temp_dir / ".flatten/config.json", "w") as f:
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
    config = load_config()
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


def test_resolve_aliases(temp_dir):
    """Test resolving aliases from a tsconfig.json."""
    tsconfig = temp_dir / "tsconfig.json"
    with open(tsconfig, "w") as f:
        json.dump({"compilerOptions": {"baseUrl": "src", "paths": {"@/*": ["*"]}}}, f)
    aliases = resolve_aliases(["tsconfig.json"])
    assert aliases["@"] == "src"

# File path: tests/test_flatten.py
