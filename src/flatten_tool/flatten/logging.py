"""
Logging utilities for the flatten tool.
Handles colored terminal output and file logging.
"""

from datetime import datetime
from pathlib import Path

import colorama
from colorama import Fore, Style

colorama.init()


def log(message, level="INFO", file_path=None, config=None):
    """Log a message to terminal and/or file based on config."""
    if config is None:
        config = {
            "log_to_terminal": True,
            "log_to_file": True,
            "log_dir": ".flatten/logs",
            "log_file": "flatten.log",
        }

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = {"DEBUG": Fore.CYAN, "INFO": Fore.GREEN, "ERROR": Fore.RED}.get(level, Fore.WHITE)
    prefix = f"{timestamp} [{level}]"
    if file_path:
        prefix += f" {file_path}:"
    log_message = f"{color}{prefix} {message}{Style.RESET_ALL}"

    if config["log_to_terminal"]:
        print(log_message)
    if config["log_to_file"]:
        log_dir = Path(config["log_dir"])
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / config["log_file"], "a") as f:
            f.write(f"{timestamp} [{level}] {message}\n")


# File path: src/flatten_tool/flatten/logging.py
