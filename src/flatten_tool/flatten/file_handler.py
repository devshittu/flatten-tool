"""
File handling for the flatten tool.
Manages file collection, import parsing, and processing.
"""

import glob
import importlib.util
import multiprocessing as mp
import os
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import tqdm

from .config import load_config, resolve_aliases
from .logging import log


def load_plugins():
    """Load custom parser plugins from /usr/local/share/flatten/plugins."""
    plugin_dir = Path("/usr/local/share/flatten/plugins")
    plugins = []
    if plugin_dir.exists():
        for plugin_file in plugin_dir.glob("*.py"):
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "parse_imports"):
                plugins.append(module)
    return plugins


@lru_cache(maxsize=1000)
def parse_imports(file_path, aliases, plugins):
    """Parse imports/requires from a file, resolving aliases."""
    config = load_config()
    imports = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # JavaScript/TypeScript imports
            js_imports = re.findall(r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]', content)
            js_requires = re.findall(r'require\([\'"](.+?)[\'"]\)', content)
            # Python imports
            py_imports = re.findall(r"from\s+(.+?)\s+import", content)
            imports.update(js_imports + js_requires + py_imports)
            # Custom plugins
            for plugin in plugins:
                plugin_imports = plugin.parse_imports(content, file_path)
                imports.update(plugin_imports)
    except Exception as e:
        log(f"Failed to parse imports: {e}", "ERROR", file_path, config=config)
        return set()

    resolved = set()
    file_dir = os.path.dirname(file_path)
    for imp in imports:
        resolved_path = None
        if imp.startswith(".") or imp.startswith("/"):
            resolved_path = os.path.normpath(os.path.join(file_dir, imp))
        else:
            for alias, base in aliases.items():
                if imp.startswith(alias):
                    resolved_path = imp.replace(alias, base, 1)
                    resolved_path = os.path.normpath(resolved_path)
                    break
        if resolved_path and os.path.splitext(resolved_path)[1] in config["supported_extensions"]:
            resolved.add(resolved_path)
    return resolved


def collect_files(paths, config, recursive=False):
    """Collect files from paths, handling wildcards and directories."""
    files = set()
    for path in paths:
        path = path.rstrip("/")
        # Handle current directory
        if path in [".", "./"]:
            path = os.getcwd()
        # Handle wildcard patterns
        if "*" in path or "?" in path or "[" in path:
            matched_files = glob.glob(path, recursive=recursive)
            for matched in matched_files:
                matched_path = Path(matched).resolve()
                if matched_path.is_file() and matched_path.suffix in config["supported_extensions"]:
                    files.add(str(matched_path))
            continue
        # Resolve path
        try:
            path_obj = Path(path).resolve()
        except FileNotFoundError:
            log(f"Path not found: {path}", "ERROR", path, config=config)
            continue
        if path_obj.is_dir():
            # Directory: Collect files
            for root, _, filenames in os.walk(path_obj):
                if not recursive and root != str(path_obj):
                    continue
                if any(os.path.basename(root) == ex for ex in config["excluded_dirs"]):
                    continue
                for filename in filenames:
                    if any(filename.endswith(ex) for ex in config["excluded_files"]):
                        continue
                    file_path = os.path.join(root, filename)
                    if Path(file_path).suffix in config["supported_extensions"]:
                        files.add(file_path)
        elif path_obj.is_file():
            # File: Add if supported
            if path_obj.suffix in config["supported_extensions"]:
                files.add(str(path_obj))
        else:
            log(f"Invalid path: {path}", "ERROR", path, config=config)
    return files


def process_file(args):
    """Process a single file for flattening (used in multiprocessing)."""
    file_path, aliases, plugins, config = args
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()
        if len(content) > config["line_limit"]:
            log(
                f"File exceeds line limit ({len(content)} lines), splitting",
                "WARNING",
                file_path,
                config=config,
            )
            return [(file_path, [], f"File too large ({len(content)} lines)")]

        marker = f"# File path: {file_path}\n" if config["output_format"] == "txt" else f"## File: {file_path}\n"
        output = [marker] + content + ["\n"]
        return [(file_path, output, None)]
    except Exception as e:
        log(f"Failed to process file: {e}", "ERROR", file_path, config=config)
        return [(file_path, [f"# File path: {file_path} (ERROR: {str(e)})\n"], str(e))]


def flatten_files(paths, output_file=None, recursive=False, with_imports=False):
    """Flatten files or directories into output files."""
    from .output import write_output

    config = load_config()
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    error_dir = output_dir / "errors"
    error_dir.mkdir(exist_ok=True)

    # Collect files
    all_files = set()
    aliases = resolve_aliases(config["config_files"])
    plugins = load_plugins()

    initial_files = collect_files(paths, config, recursive=recursive)
    if not initial_files:
        log("No valid files found to flatten", "ERROR", config=config)
        return

    all_files.update(initial_files)
    if with_imports:
        for fp in initial_files:
            imports = parse_imports(fp, tuple(sorted(aliases.items())), tuple(id(p) for p in plugins))
            all_files.update(imports)

    # Filter supported files
    valid_files = [
        f
        for f in all_files
        if (
            Path(f).suffix in config["supported_extensions"]
            and not any(ex in f for ex in config["excluded_dirs"] + config["excluded_files"])
        )
    ]

    if not valid_files:
        log("No valid files to flatten after filtering", "ERROR", config=config)
        return

    log(f"Files to flatten: {', '.join(sorted(valid_files))}", "INFO", config=config)

    # Process files in parallel
    pool = mp.Pool(mp.cpu_count())
    results = []
    with tqdm.tqdm(total=len(valid_files), desc="Flattening files", unit="file") as pbar:
        for result in pool.imap_unordered(process_file, [(f, aliases, plugins, config) for f in valid_files]):
            results.extend(result)
            pbar.set_description(f"Processing {result[0][0]}")
            pbar.update(1)
    pool.close()
    pool.join()

    # Collect output and errors
    output_content = []
    errors = []
    total_lines = 0
    for file_path, content, error in results:
        output_content.extend(content)
        total_lines += len(content)
        if error:
            errors.append((file_path, error))

    # Determine output files
    output_files = []
    if total_lines <= config["line_limit"]:
        output_files = [output_file or f"{os.path.basename(os.getcwd())}_flattened.{config['output_format']}"]
    else:
        dir_groups = {}
        for file_path, _, _ in results:
            dir_name = os.path.dirname(file_path).replace(os.sep, "_") or "root"
            if dir_name not in dir_groups:
                dir_groups[dir_name] = []
            dir_groups[dir_name].append(file_path)
        for dir_name in dir_groups:
            output_files.append(f"{dir_name}_flattened.{config['output_format']}")

    # Write output
    current_output = 0
    current_lines = 0
    output_path = output_dir / output_files[current_output]
    current_content = []

    for line in output_content:
        current_content.append(line)
        current_lines += 1
        if current_lines > config["line_limit"] and current_output < len(output_files) - 1:
            write_output(current_content, output_path, config["output_format"])
            log(f"Written to {output_path}", "INFO", config=config)
            current_content = []
            current_lines = 0
            current_output += 1
            output_path = output_dir / output_files[current_output]

    if current_content:
        write_output(current_content, output_path, config["output_format"])
        log(f"Written to {output_path}", "INFO", config=config)

    # Write error report
    if errors:
        error_report = error_dir / "error_report.txt"
        with open(error_report, "w") as f:
            f.write("Flatten Error Report\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            for file_path, error in errors:
                f.write(f"{file_path}: {error}\n")
        log(f"Error report written to {error_report}", "ERROR", config=config)


# File path: src/flatten_tool/flatten/file_handler.py
