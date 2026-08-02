#!/usr/bin/env python3
"""Update todo.md after a task is completed.

Usage: python scripts/update_todo.py <task_number>
Example: python scripts/update_todo.py 2
"""

import re
import sys
from pathlib import Path


def main(task_number: int) -> int:
    todo_path = Path(__file__).parent.parent / "todo.md"
    if not todo_path.exists():
        print(f"ERROR: {todo_path} not found", file=sys.stderr)
        return 1

    content = todo_path.read_text(encoding="utf-8")
    original = content

    # Match the entire Task N section: from "## Task N:" up to but not including the next "## " or "---"
    section_pattern = rf"(## Task {task_number}:.*?)(?=\n## |\n--- |\Z)"

    def replace_checkboxes_in_section(match: re.Match) -> str:
        section = match.group(1)
        updated = re.sub(r"^- \[ \]", "- [x]", section, flags=re.MULTILINE)
        return updated

    updated = re.sub(section_pattern, replace_checkboxes_in_section, content, flags=re.DOTALL)

    if updated == original:
        print(f"WARNING: No changes made (Task {task_number} may already be checked)", file=sys.stderr)
        return 1

    todo_path.write_text(updated, encoding="utf-8")
    print(f"Marked all items in Task {task_number} as complete in {todo_path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update_todo.py <task_number>", file=sys.stderr)
        sys.exit(1)

    try:
        task_num = int(sys.argv[1])
    except ValueError:
        print(f"Invalid task number: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)

    sys.exit(main(task_num))
