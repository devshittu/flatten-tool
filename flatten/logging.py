"""
Logging utilities for the flatten tool.
Handles colored terminal output and file logging.
"""
import colorama
from colorama import Fore, Style
from datetime import datetime
from pathlib import Path
from .config import load_config


colorama.init()


def log(message, level="INFO", file_path=None):
    """Log a message to terminal and/or file based on config."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "ERROR": Fore.RED
    }.get(level, Fore.WHITE)
    prefix = f"{timestamp} [{level}]"
    if file_path:
        prefix += f" {file_path}:"
    log_message = f"{color}{prefix} {message}{Style.RESET_ALL}"

    config = load_config()
    if config["log_to_terminal"]:
        print(log_message)
    if config["log_to_file"]:
        log_dir = Path(config["log_dir"])
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / config["log_file"], "a") as f:
            f.write(f"{timestamp} [{level}] {message}\n")