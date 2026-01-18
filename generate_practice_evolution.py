import tomli
import os
from pathlib import Path
import matplotlib.pyplot as plt
from code_smells_calculator import process_single_chart_detailed, load_check_functions
from find_repo_tags import find_tags


REPO_BASE = Path("target-repo").resolve()


checks = load_check_functions()


def get_output_dir(repo_name: str, chart_name: str) -> Path:
    out = Path("graphs_practices_over_time") / repo_name / chart_name
    out.mkdir(parents=True, exist_ok=True)
    return out


def analyze_repo(repo_path: str, chart_path: str, months_range: int = 6):
    repo_path = Path(repo_path).resolve()
    chart_path = repo_path / chart_path

    tags = find_tags(months_range, str(repo_path))

    results = []

    for sha, date in tags:
        os.system(f"git -C {repo_path} checkout {sha}")

        if not chart_path.exists():
            continue

        res = process_single_chart_detailed(str(chart_path), checks)

        results.append({
            "sha": sha,
            "date": date,
            "lines": res["lines"],
            "by_practice": res["by_practice"]
        })

    return results


def build_time_series(results):
    all_practices = set()
    for r in results:
        all_practices.update(r["by_practice"].keys())

    series = {p: [] for p in all_practices}
    dates = []

    for r in results:
        dates.append(r["date"])
        lines = r["lines"]

        for p in all_practices:
            count = r["by_practice"].get(p, 0)
            ratio = (count / lines * 1000) if lines > 0 else 0
            series[p].append(ratio)

    return dates, series


def plot_per_practice(dates, series, output_dir, repo_name, chart_name):
    for practice, values in series.items():
        plt.figure(figsize=(8, 5))
        plt.plot(dates, values, marker="o")
        plt.title(f"{practice}\n{repo_name} / {chart_name}")
        plt.xlabel("Date")
        plt.ylabel("Code smells / 1000 lignes")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        fname = f"{repo_name}_{chart_name}_{practice}.png".replace("/", "_")
        plt.savefig(output_dir / fname)
        plt.close()


def plot_stacked(dates, series, output_dir, repo_name, chart_name):
    labels = list(series.keys())
    values = [series[p] for p in labels]

    plt.figure(figsize=(12, 7))
    plt.stackplot(dates, values, labels=labels)
    plt.title(f"Évolution des mauvaises pratiques\n{repo_name} / {chart_name}")
    plt.xlabel("Date")
    plt.ylabel("Code smells / 1000 lignes")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    plt.xticks(rotation=45)
    plt.tight_layout()

    fname = f"{repo_name}_{chart_name}_STACKED.png".replace("/", "_")
    plt.savefig(output_dir / fname)
    plt.close()


def save_practice_stats(dates, series, output_dir):
    output_file = output_dir / "ANALYSE_PRACTICES.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== ANALYSE DES PRATIQUES ===\n\n")

        for practice, values in series.items():
            introduced = None
            for i in range(1, len(values)):
                if values[i - 1] == 0 and values[i] > 0:
                    introduced = (dates[i - 1], dates[i])
                    break

            trend_value = values[-1] - values[0]
            if trend_value > 0:
                trend = "↗"
            elif trend_value < 0:
                trend = "↘"
            else:
                trend = "="

            f.write(f"- {practice}\n")
            f.write(f"  • début: {values[0]:.2f}\n")
            f.write(f"  • fin  : {values[-1]:.2f}\n")
            f.write(f"  • tendance: {trend}\n")

            if introduced:
                f.write(f"  ⚠️ introduite entre {introduced[0]} → {introduced[1]}\n")

            f.write("\n")


def main(toml_path: Path):
    with toml_path.open("rb") as f:
        config = tomli.load(f)

    repo_cfg = config["repository"]

    repo_path = REPO_BASE
    chart_path = repo_cfg["chart_folder_path"]
    months_range = repo_cfg["months_range"]

    results = analyze_repo(repo_path, chart_path, months_range)
    dates, series = build_time_series(results)

    repo_name = repo_path.name
    chart_name = Path(chart_path).name

    output_dir = get_output_dir(repo_name, chart_name)

    plot_per_practice(dates, series, output_dir, repo_name, chart_name)
    plot_stacked(dates, series, output_dir, repo_name, chart_name)
    save_practice_stats(dates, series, output_dir)


if __name__ == "__main__":
    main(Path("graph-over-time.toml"))
