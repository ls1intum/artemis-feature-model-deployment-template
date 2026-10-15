"""Lists the package variables that are empty in this run, with their descriptions, in the run summary.

Runs after a failed preflight. Each row says whether the variable belongs in the target's GitHub Environment as a
secret or as a variable, following the kind recorded in the package's metadata/env-references.json.

Usage: missing-variables-summary.py <package_dir> <environment_name>
"""

import json
import os
import sys


def main() -> None:
    package_dir, environment_name = sys.argv[1], sys.argv[2]
    with open(os.path.join(package_dir, "metadata", "env-references.json"), encoding="utf-8") as file:
        references = json.load(file)

    rows = []
    listed = set()
    for reference in references:
        name = reference["envVar"]
        if name in listed or os.environ.get(name):
            continue
        listed.add(name)
        place = "Environment secret" if reference.get("kind") == "secret" else "Environment variable"
        description = reference.get("description", "").replace("|", "\\|")
        rows.append(f"| `{name}` | {place} | {description} |")

    lines = ["## Missing deployment values", ""]
    if rows:
        lines += [
            f"Add these values to the GitHub Environment `{environment_name}`, then re-run this workflow.",
            "",
            "| Variable | Set on GitHub as | Description |",
            "|---|---|---|",
            *rows,
        ]
    else:
        lines.append("Every package variable has a value; the preflight failed for another reason, see its log.")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
        summary.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
