import subprocess
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta


def git(cmd):
    return subprocess.check_output(cmd, text=True).strip()


def find_tags(months_range: int, repo_path: str):
    repo_path = Path(repo_path).resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    log = git(
        [
            "git",
            "-C",
            str(repo_path),
            "log",
            "--reverse",
            "--format=%H %ad",
            "--date=iso",
        ]
    ).splitlines()

    selected = []
    last_date = None

    for line in log:
        sha, date_str = line.split(maxsplit=1)
        commit_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")

        if last_date is None or commit_date >= last_date + relativedelta(
            months=months_range
        ):
            selected.append((sha, commit_date.date()))
            last_date = commit_date

    print("Selected commits:", selected)
    return selected  # List[(sha, date)]
