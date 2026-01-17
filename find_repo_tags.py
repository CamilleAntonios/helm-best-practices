import subprocess
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

def git(cmd):
    return subprocess.check_output(cmd, text=True).strip()

def find_tags(months_range: int, repo_path: str):
    current_dir = os.getcwd()
    os.chdir(repo_path)
    log = git([
        "git", "log", "--reverse",
        "--format=%H %ad", "--date=iso"
    ]).splitlines()

    selected = []
    last_date = None

    for line in log:
        sha, date_str = line.split(maxsplit=1)
        commit_date = datetime.fromisoformat(date_str)

        if last_date is None or commit_date >= last_date + relativedelta(months=6):
            selected.append((sha, commit_date.date()))
            last_date = commit_date

    os.chdir(current_dir)
    print("selected tags: ", selected)
    return selected # List of tuples (sha, date)