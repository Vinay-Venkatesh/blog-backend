#!/usr/bin/env python3

import os
import subprocess


def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def main():
    root = (
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .decode()
        .strip()
    )
    os.chdir(root)
    run("pipenv run pre-commit install --hook-type pre-commit")
    run("pipenv run pre-commit install --hook-type commit-msg")
    run("pipenv run pre-commit install --hook-type pre-push")


if __name__ == "__main__":
    main()
