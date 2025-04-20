"""
Command-line interface for the flatten tool.
Handles argument parsing and command execution.
"""

import argparse

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
    print("    Flatten files or directories into a single file.")
    print("    Usage: flatten <paths> [-o OUTPUT] [-r] [--with-imports]")
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
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    subparsers.add_parser("init", help="Initialize flatten in the project")

    # Uninit command
    subparsers.add_parser("uninit", help="Remove flatten configuration")

    # Flatten command
    flatten_parser = subparsers.add_parser("flatten", help="Flatten files or directories")
    flatten_parser.add_argument(
        "paths",
        nargs="+",
        help="Files, directories, or patterns (e.g., ./file.js, ./src/, **/readme.md)",
    )
    flatten_parser.add_argument(
        "-o",
        "--output",
        help="Output file name (default: <project>_flattened.<format>)",
    )
    flatten_parser.add_argument("-r", "--recursive", action="store_true", help="Flatten directories recursively")
    flatten_parser.add_argument(
        "--with-imports",
        action="store_true",
        help="Include one-depth imports/requires for files",
    )

    # Examples command
    subparsers.add_parser("examples", help="Show usage examples")

    # Feedback command
    subparsers.add_parser("feedback", help="Provide feedback")

    # Help command
    subparsers.add_parser("help", help="Display detailed help")

    args = parser.parse_args()

    if args.command == "init":
        init_project()
    elif args.command == "uninit":
        uninit_project()
    elif args.command == "flatten":
        flatten_files(
            args.paths,
            args.output,
            recursive=args.recursive,
            with_imports=args.with_imports,
        )
    elif args.command == "examples":
        show_examples()
    elif args.command == "feedback":
        collect_feedback()
    elif args.command == "help":
        show_help()
    else:
        log("No command provided, displaying help", "INFO", config=config)
        parser.print_help()


if __name__ == "__main__":
    main()

# File path: src/flatten_tool/flatten/cli.py
