"""Exports the environment variables a package references to the following workflow steps.

Reads the names from the package's metadata/env-references.json and takes each value from the Environment's secrets,
else its variables, else the empty string; the package's preflight.sh then refuses missing or empty values. Values
are written only to $GITHUB_ENV, in the delimiter form that keeps multiline values intact, and never printed.

Usage: export-environment.py <package_dir>; SECRETS_JSON and VARS_JSON hold toJSON(secrets) and toJSON(vars).
"""

import json
import os
import secrets
import sys


def main() -> None:
    package_dir = sys.argv[1]
    with open(os.path.join(package_dir, "metadata", "env-references.json"), encoding="utf-8") as file:
        references = json.load(file)
    environment_secrets = json.loads(os.environ.get("SECRETS_JSON") or "{}")
    environment_variables = json.loads(os.environ.get("VARS_JSON") or "{}")

    names = list(dict.fromkeys(reference["envVar"] for reference in references))
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as github_env:
        for name in names:
            value = environment_secrets.get(name) or environment_variables.get(name) or ""
            delimiter = "EOF_" + secrets.token_hex(16)
            while delimiter in value:
                delimiter = "EOF_" + secrets.token_hex(16)
            github_env.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")
    print(f"Exported {len(names)} package variables: {' '.join(names)}")


if __name__ == "__main__":
    main()
