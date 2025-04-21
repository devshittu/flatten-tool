"""
Configuration management for the flatten tool.
Handles loading, saving, and initializing project settings.
"""

import json
import shutil
import sys
import termios
import tty
from pathlib import Path
from select import select
from termios import tcgetattr, tcsetattr

import jsonschema

# JSON Schema for config validation
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "excluded_dirs": {"type": "array", "items": {"type": "string"}},
        "excluded_files": {"type": "array", "items": {"type": "string"}},
        "supported_extensions": {"type": "array", "items": {"type": "string"}},
        "line_limit": {"type": "integer", "minimum": 100},
        "output_dir": {"type": "string"},
        "log_dir": {"type": "string"},
        "log_file": {"type": "string"},
        "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "ERROR"]},
        "log_to_file": {"type": "boolean"},
        "log_to_terminal": {"type": "boolean"},
        "config_files": {"type": "array", "items": {"type": "string"}},
        "aliases": {"type": "object"},
        "output_format": {"type": "string", "enum": ["txt", "md", "json"]},
    },
    "required": [
        "excluded_dirs",
        "excluded_files",
        "supported_extensions",
        "line_limit",
        "output_dir",
        "log_dir",
        "log_file",
        "log_level",
        "log_to_file",
        "log_to_terminal",
        "config_files",
        "aliases",
        "output_format",
    ],
}

# Default configuration
DEFAULT_CONFIG = {
    "excluded_dirs": [
        "node_modules",
        ".venv",
        "__pycache__",
        "dist",
        "build",
        ".env",
        ".git",
        "venv",
        "models",
    ],
    "excluded_files": [".env", "*.pyc"],
    "supported_extensions": [".py", ".js", ".ts", ".tsx"],
    "line_limit": 2000,
    "output_dir": ".flatten/output",
    "log_dir": ".flatten/logs",
    "log_file": "flatten.log",
    "log_level": "INFO",
    "log_to_file": True,
    "log_to_terminal": True,
    "config_files": [
        "tsconfig.json",
        "jsconfig.json",
        "vite.config.js",
        "webpack.config.js",
    ],
    "aliases": {},
    "output_format": "txt",
}


def load_config():
    """Load configuration from .flatten/config.json, merging with default."""
    from .logging import log

    config_path = Path(".flatten/config.json")
    config = DEFAULT_CONFIG.copy()
    if config_path.exists():
        with open(config_path, "r") as f:
            user_config = json.load(f)
        try:
            # Merge user config with default
            config.update(user_config)
            jsonschema.validate(config, CONFIG_SCHEMA)
        except jsonschema.ValidationError as e:
            log(
                f"Invalid config, using defaults with partial merge: {e.message}",
                "WARNING",
            )
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)  # Apply valid fields
    return config


def save_config(config):
    """Save configuration to .flatten/config.json with validation."""
    from .logging import log

    config_path = Path(".flatten/config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        jsonschema.validate(config, CONFIG_SCHEMA)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except jsonschema.ValidationError as e:
        log(f"Cannot save invalid config: {e.message}", "ERROR")
        sys.exit(1)


def update_gitignore():
    """Add .flatten/ to .gitignore if not already present."""
    gitignore = Path(".gitignore")
    flatten_entry = ".flatten/"
    if gitignore.exists():
        with open(gitignore, "r") as f:
            content = f.read()
        if flatten_entry not in content:
            with open(gitignore, "a") as f:
                f.write(f"\n{flatten_entry}\n")
    else:
        with open(gitignore, "w") as f:
            f.write(f"{flatten_entry}\n")


def detect_project_type():
    """Detect project type based on common files."""
    if Path("package.json").exists():
        with open("package.json", "r") as f:
            data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "next" in deps:
                return "nextjs"
            if "react" in deps:
                return "react"
            return "javascript"
    if Path("requirements.txt").exists() or Path("pyproject.toml").exists():
        return "python"
    return "unknown"


def non_interactive_config():
    """Configure project settings non-interactively using defaults."""
    from .logging import log

    config = DEFAULT_CONFIG.copy()
    project_type = detect_project_type()
    log("Non-interactive environment detected, using default configuration", "INFO")
    if project_type == "nextjs":
        config["config_files"] = ["tsconfig.json", "jsconfig.json"]
        config["supported_extensions"] = [".js", ".ts", ".tsx"]
    elif project_type == "python":
        config["supported_extensions"] = [".py"]
        config["config_files"] = []
    save_config(config)
    update_gitignore()
    log("Project initialized with default .flatten configuration", "INFO")


def interactive_config():
    """Interactively configure project settings."""
    from .logging import log

    config = DEFAULT_CONFIG.copy()
    project_type = detect_project_type()
    print(f"\033[1;33mConfiguring flatten (Detected project: {project_type})...\033[0m")

    def select_option(prompt, options, default=None):
        """Helper to select an option interactively."""
        print(f"\033[1;36m{prompt}\033[0m")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        selected = 0
        if default in options:
            selected = options.index(default)

        fd = sys.stdin.fileno()
        old_settings = tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                r, _, _ = select([sys.stdin], [], [], 0.1)
                if r:
                    key = sys.stdin.read(1)
                    if key == "\x1b":
                        next_key = sys.stdin.read(2)
                        if next_key == "[A":
                            selected = (selected - 1) % len(options)
                        elif next_key == "[B":
                            selected = (selected + 1) % len(options)
                    elif key == "\r":
                        break
                    print(f"\r\033[1;36m{prompt} {options[selected]}\033[0m", end="")
                else:
                    print(f"\r\033[1;36m{prompt} {options[selected]}\033[0m", end="")
        finally:
            tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print()
        return options[selected]

    # Project-specific defaults
    if project_type == "nextjs":
        config["config_files"] = ["tsconfig.json", "jsconfig.json"]
        config["supported_extensions"] = [".js", ".ts", ".tsx"]
    elif project_type == "python":
        config["supported_extensions"] = [".py"]

    # Ask for config files
    config_files = select_option(
        "Select configuration files to parse for aliases:",
        [
            "tsconfig.json",
            "jsconfig.json",
            "vite.config.js",
            "webpack.config.js",
            "All",
            "None",
        ],
        "All" if project_type in ["nextjs", "javascript"] else "None",
    )
    if config_files == "None":
        config["config_files"] = []
    elif config_files == "All":
        config["config_files"] = [
            "tsconfig.json",
            "jsconfig.json",
            "vite.config.js",
            "webpack.config.js",
        ]
    else:
        config["config_files"] = [config_files]

    # Ask for supported extensions
    extensions = input(
        "\033[1;36mEnter supported file extensions (comma-separated, default: "
        f"{','.join(config['supported_extensions'])}): \033[0m"
    ).strip()
    if extensions:
        config["supported_extensions"] = [ext.strip() for ext in extensions.split(",")]

    # Ask for excluded directories
    excluded_dirs = input(
        "\033[1;36mEnter excluded directories (comma-separated, default: "
        f"{','.join(config['excluded_dirs'])}): \033[0m"
    ).strip()
    if excluded_dirs:
        config["excluded_dirs"] = [d.strip() for d in excluded_dirs.split(",")]

    # Ask for line limit
    line_limit = input(f"\033[1;36mEnter line limit per file (default: {config['line_limit']}): \033[0m").strip()
    config["line_limit"] = int(line_limit) if line_limit.isdigit() else config["line_limit"]

    # Ask for log level
    config["log_level"] = select_option("Select log level:", ["DEBUG", "INFO", "ERROR"], config["log_level"])

    # Ask for log destinations
    log_to = select_option("Log output destination:", ["Terminal only", "File only", "Both"], "Both")
    config["log_to_terminal"] = log_to in ["Terminal only", "Both"]
    config["log_to_file"] = log_to in ["File only", "Both"]

    # Ask for output format
    config["output_format"] = select_option("Select output format:", ["txt", "md", "json"], config["output_format"])

    save_config(config)
    update_gitignore()

    # Copy sample configs
    template_dir = Path("/usr/local/share/flatten/templates")
    if template_dir.exists():
        local_template_dir = Path(".flatten/templates")
        local_template_dir.mkdir(parents=True, exist_ok=True)
        for template in template_dir.glob("*.json"):
            with open(template, "r") as src, open(local_template_dir / template.name, "w") as dst:
                dst.write(src.read())
        log("Copied sample configurations to .flatten/templates", "INFO")

    log("Project initialized with .flatten directory", "INFO")


def init_project(interactive=True):
    """Initialize a project with .flatten directory and configuration."""
    from .logging import log

    flatten_dir = Path(".flatten")
    if flatten_dir.exists():
        log("Project already initialized", "INFO")
        return
    flatten_dir.mkdir(parents=True, exist_ok=True)

    # Only go interactive if explicitly requested and stdin is a tty
    if interactive and sys.stdin.isatty():
        interactive_config()
    else:
        non_interactive_config()


def uninit_project():
    """Remove .flatten directory and update .gitignore."""
    from .logging import log

    flatten_dir = Path(".flatten")
    if flatten_dir.exists():
        shutil.rmtree(flatten_dir)
        log("Removed .flatten directory", "INFO")
    gitignore = Path(".gitignore")
    if gitignore.exists():
        with open(gitignore, "r") as f:
            lines = f.readlines()
        with open(gitignore, "w") as f:
            for line in lines:
                if ".flatten/" not in line:
                    f.write(line)
        log("Updated .gitignore", "INFO")


def resolve_aliases(config_files):
    """Resolve aliases from configuration files (stub)."""
    return {}


# File path: src/flatten_tool/flatten/config.py
