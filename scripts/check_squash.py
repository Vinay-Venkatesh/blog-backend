#!/usr/bin/env python3

import subprocess
import sys


def get_unpushed_commits_count():
    try:
        upstream = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        print(
            "❌ No upstream branch set. Use:\n  git push --set-upstream origin <branch>"
        )
        sys.exit(1)

    commits = (
        subprocess.check_output(["git", "rev-list", f"{upstream}..HEAD"])
        .decode()
        .splitlines()
    )

    return len(commits)


def main():
    count = get_unpushed_commits_count()

    if count > 1:
        print(f"❌ You are trying to push {count} commits.")
        print("🔒 Please squash your commits into one before pushing.")
        sys.exit(1)

    # okay to push
    sys.exit(0)


if __name__ == "__main__":
    main()
