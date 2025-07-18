#!/usr/bin/env python3

# import re
# import sys

# conventional_commit_pattern = r"^(feat|fix|chore|docs|style|refactor|perf|test)(\([^)]+\))?: .+"

# def main():
#     commit_msg_file = sys.argv[1]
#     with open(commit_msg_file, "r") as f:
#         commit_msg = f.readline().strip()

#     if not re.match(conventional_commit_pattern, commit_msg):
#         print(f"❌ Invalid commit message:\n  \"{commit_msg}\"\n\nFollow Conventional Commit format:")
#         print("  e.g., feat(JIRA_ID): add new endpoint\n")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()

import re
import subprocess
import sys

PATTERN = r"^(feat|fix|chore|docs|style|refactor|perf|test)(\([^)]+\))?: .+"


def get_commits_to_push():
    try:
        upstream = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        print(
            "❌ No upstream branch set. Set it with:\n  git push --set-upstream origin <branch>"
        )
        sys.exit(1)

    commits = (
        subprocess.check_output(["git", "log", f"{upstream}..HEAD", "--pretty=%s"])
        .decode()
        .splitlines()
    )
    return commits


def main():
    commits = get_commits_to_push()

    if not commits:
        sys.exit(0)  # Nothing to push

    failed = []
    for msg in commits:
        if not re.match(PATTERN, msg):
            failed.append(msg)

    if failed:
        print("❌ The following commits do not follow Conventional Commit format:\n")
        for msg in failed:
            print(f"  - {msg}")
        print("\n💡 Format should be like: feat(JIRA_ID): add new endpoint")
        sys.exit(1)


if __name__ == "__main__":
    main()
