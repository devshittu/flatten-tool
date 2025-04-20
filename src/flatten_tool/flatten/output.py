"""
Output handling for the flatten tool.
Manages writing output files and displaying examples/feedback.
"""

import json
from datetime import datetime
from pathlib import Path

from .config import load_config
from .logging import log


def write_output(content, output_path, format_type):
    """Write content to output file in specified format."""
    with open(output_path, "w", encoding="utf-8") as f:
        if format_type == "txt":
            f.writelines(content)
        elif format_type == "md":
            f.writelines([line.replace("# File path:", "## File:") for line in content])
        elif format_type == "json":
            files = []
            current_file = None
            current_content = []
            for line in content:
                if line.startswith("# File path:"):
                    if current_file:
                        files.append({"file": current_file, "content": "".join(current_content)})
                        current_content = []
                    current_file = line.replace("# File path: ", "").strip()
                else:
                    current_content.append(line)
            if current_file:
                files.append({"file": current_file, "content": "".join(current_content)})
            json.dump({"files": files}, f, indent=2)


def show_examples():
    """Display practical usage examples for the flatten tool."""
    print("\033[1;33mFlatten Example Usage:\033[0m")
    print("1. Initialize a project:")
    print("   $ flatten init")
    print("   (Sets up .flatten directory and configures settings)")
    print("\n2. Flatten a single file:")
    print("   $ flatten ./src/components/Button.tsx")
    print("   (Outputs to .flatten/output/project_flattened.txt)")
    print("\n3. Flatten a single file with its dependencies:")
    print("   $ flatten ./src/components/Button.tsx --with-imports")
    print("   (Includes one-depth imports)")
    print("\n4. Flatten all files in a directory:")
    print("   $ flatten ./src/")
    print("   (Flattens non-recursively)")
    print("\n5. Flatten all files in a directory recursively:")
    print("   $ flatten ./src/ --recursive")
    print("   (Includes subdirectories)")
    print("\n6. Flatten files matching a pattern:")
    print("   $ flatten **/readme.md --recursive")
    print("   (Flattens all readme.md files in subdirectories)")
    print("\n7. Flatten with custom output:")
    print("   $ flatten . -o combined.md")
    print("   (Outputs to .flatten/output/combined.md in Markdown format)")
    print("\n8. View error report:")
    print("   (Check .flatten/output/errors/error_report.txt for issues)")
    print("\n9. Use a sample config:")
    print("   $ cp .flatten/templates/nextjs.json .flatten/config.json")
    print("   (Applies Next.js-specific settings)")
    print("\n10. Get detailed help:")
    print("    $ flatten help")
    print("\nRun 'flatten --help' for CLI argument details.")


def collect_feedback():
    """Collect user feedback and save to .flatten/feedback."""
    config = load_config()
    print("\033[1;33mWe value your feedback!\033[0m")
    feedback = input("\033[1;36mEnter your feedback (or press Enter to skip): \033[0m")
    if feedback:
        feedback_dir = Path(".flatten/feedback")
        feedback_dir.mkdir(parents=True, exist_ok=True)
        with open(
            feedback_dir / f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "w",
        ) as f:
            f.write(feedback)
        log("Feedback saved. Thank you!", "INFO", config=config)
    else:
        log("No feedback provided", "INFO", config=config)


# File path: src/flatten_tool/flatten/output.py
