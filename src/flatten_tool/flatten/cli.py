"""
Command-line interface for the flatten tool.
Handles argument parsing and command execution.
"""

import argparse
import sys

from .config import init_project, load_config, uninit_project
from .file_handler import flatten_files
from .logging import log
from .output import collect_feedback, show_examples


def show_help():
    """Display detailed help for all commands."""
    config = load_config()
    print("\033[1;33mFlatten CLI Help\033[0m")
    print("\n\033[1mDescription:\033[0m")
    print("  Flatten project files into a single file with descriptive paths.")
    print("  Supports Python and JavaScript projects, with auto-detection of files and directories.")
    print("\n\033[1mUsage:\033[0m")
    print("  flatten [PATHS] [OPTIONS]")
    print("  flatten COMMAND [OPTIONS]")
    print("\n\033[1mCommands:\033[0m")
    print("  \033[1minit\033[0m")
    print("    Initialize a project with a .flatten directory and configuration.")
    print("    Usage: flatten init")
    print("    Example: flatten init")
    print("\n  \033[1muninit\033[0m")
    print("    Remove the .flatten directory and update .gitignore.")
    print("    Usage: flatten uninit")
    print("    Example: flatten uninit")
    print("\n  \033[1mflatten\033[0m")
    print("    Flatten files or directories into a single file (default if PATHS provided).")
    print("    Usage: flatten [PATHS] [-o OUTPUT] [-r] [--with-imports]")
    print("    Options:")
    print("      -o, --output     Output file name (default: <project>_flattened.<format>)")
    print("      -r, --recursive  Flatten directories recursively")
    print("      --with-imports   Include one-depth imports/requires")
    print("    Examples:")
    print("      flatten ./src/components/Button.tsx")
    print("      flatten ./src/ --recursive")
    print("      flatten **/readme.md --recursive -o docs.md")
    print("\n  \033[1mexamples\033[0m")
    print("    Show practical usage examples.")
    print("    Usage: flatten examples")
    print("    Example: flatten examples")
    print("\n  \033[1mfeedback\033[0m")
    print("    Submit feedback to improve the tool.")
    print("    Usage: flatten feedback")
    print("    Example: flatten feedback")
    print("\n  \033[1mhelp\033[0m")
    print("    Display this help message.")
    print("    Usage: flatten help")
    print("    Example: flatten help")
    print("\n\033[1mNotes:\033[0m")
    print(f"  - Default output format: {config['output_format']}.")
    print("  - Paths are relative to the current working directory.")
    print("  - Use ./ for current directory, ./file.js for files, or **/pattern for wildcards.")
    print("  - Run 'flatten --help' for CLI argument details.")


def main():
    """Parse command-line arguments and execute commands."""
    config = load_config()
    parser = argparse.ArgumentParser(
        description="Flatten project files into a single file with descriptive paths.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  flatten init\n"
        "  flatten ./src/components/Button.tsx --with-imports\n"
        "  flatten ./src/ --recursive\n"
        "  flatten **/readme.md --recursive -o docs.md\n"
        "  flatten examples",
    )

    # Define valid commands
    valid_commands = {"init", "uninit", "flatten", "examples", "feedback", "help"}

    # Positional argument for command or path
    parser.add_argument(
        "command_or_path",
        nargs="?",
        help="Command (init, uninit, flatten, examples, feedback, help) or path to flatten",
    )
    parser.add_argument(
        "extra_paths",
        nargs="*",
        help="Additional files, directories, or patterns (e.g., ./file.js, ./src/, **/readme.md)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file name (default: <project>_flattened.<format>)",
    )
    parser.add_argument("-r", "--recursive", action="store_true", help="Flatten directories recursively")
    parser.add_argument(
        "--with-imports",
        action="store_true",
        help="Include one-depth imports/requires for files",
    )

    args = parser.parse_args()

    # Determine if command_or_path is a path or command
    if args.command_or_path:
        if args.command_or_path in valid_commands and args.command_or_path != "flatten":
            # Handle non-flatten commands
            if args.command_or_path == "init":
                init_project(interactive=True)
            elif args.command_or_path == "uninit":
                uninit_project()
            elif args.command_or_path == "examples":
                show_examples()
            elif args.command_or_path == "feedback":
                collect_feedback()
            elif args.command_or_path == "help":
                show_help()
            return
        else:
            # Treat as flatten command with paths
            paths = [args.command_or_path] + args.extra_paths
            flatten_files(
                paths,
                args.output,
                recursive=args.recursive,
                with_imports=args.with_imports,
            )
            return

    # No command or path provided, show help
    log("No command or path provided, displaying help", "INFO", config=config)
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()

# File path: src/flatten_tool/flatten/cli.py
