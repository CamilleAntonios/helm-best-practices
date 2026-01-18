import subprocess
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta


def git(cmd, fault_on_error=True):
    """Execute a git command and return its output as a string."""
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if fault_on_error and result.returncode != 0:
        raise RuntimeError(
            f"Git command {' '.join(cmd)} failed with error: {result.stderr}"
        )
    return result.stdout


def find_tags(months_range: int, repo_path: str):
    current_dir = os.getcwd()
    os.chdir(repo_path)

    git(["git", "checkout", "master"], fault_on_error=False) # make sure to have access to one of the tags
    git(["git", "checkout", "main"], fault_on_error=False) #one of these commands will fail, it is not a problem as the other one will have worked

    log = git([
        "git", "log", "--reverse",
        "--format=%H %ad", "--date=iso"
    ]).splitlines()

    selected = []
    last_date = None

    for line in log:
        sha, date_str = line.split(maxsplit=1)
        commit_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")

        if last_date is None or commit_date >= last_date + relativedelta(months=months_range):
            selected.append((sha, commit_date.date()))
            last_date = commit_date

    print("Selected commits:", selected)
    return selected  # List[(sha, date)]
