import tomli
import os
import sys
from pathlib import Path
from code_smells_calculator import process_single_chart, load_check_functions
import matplotlib.pyplot as plt
from find_repo_tags import find_tags

checks = load_check_functions()

def compute_smells_for_repo(repository_folder: str, chart_folder_path: str, tag_to_checkout: tuple[str, str]):
    print(
        f"Processing repo='{repository_folder}', "
        f"chart='{chart_folder_path}', "
        f"tag='{tag_to_checkout}'"
    )
    print("Current directory: ", Path.cwd())
    current_dir = Path.cwd()


    # chdir to repository folder
    repo_path = Path(repository_folder)
    # chdir
    os.chdir(repo_path)
    # checkout tag
    os.system(f"git checkout {tag_to_checkout[0]}")
    os.chdir(current_dir)

    chart_path = repo_path / chart_folder_path
    if not chart_path.exists():
        print(f"Chart path '{chart_path}' does not exist, from {Path.cwd()}. Skipping.")
        return
    
    # process charts
    codeSmells, lines, files = process_single_chart(str(chart_path), checks)

    os.chdir(current_dir)

    print(
        f"Results for repo='{repository_folder}', "
        f"chart='{chart_folder_path}', "
        f"tag='{tag_to_checkout}': "
        f"Date='{tag_to_checkout[1]}', "
        f"code_smells={codeSmells}, "
        f"lines={lines}, "
        f"files={files}"
    )
    return codeSmells, lines, files


def main(toml_path: Path):
    with toml_path.open("rb") as f:
        config = tomli.load(f)

    repositories = config.get("repositories", [])

    current_dir = Path.cwd()

    global_smells_results = {}
    global_lines_results = {}

    global_ratio_results = {}

    for repo in repositories:
        repository_folder = repo["repository_folder"]
        chart_folder_path = repo["chart_folder_path"]

        tags_to_checkout = find_tags(6, repository_folder)

        print("tags to checkout: ", tags_to_checkout)

        # store results per tag
        results_per_tag = {}

        for tag in tags_to_checkout:
            smells_result = compute_smells_for_repo(repository_folder, chart_folder_path, tag)

            if not smells_result:
                continue
            codeSmells, lines, files = smells_result

            print("Returning to directory: ", current_dir)

            os.chdir(current_dir) # go back to original dir after processing each repo/tag

            results_per_tag[tag[0]] = {
                "code_smells": codeSmells,
                "lines": lines,
                "files": files
            }

        print(f"Summary for repository '{repository_folder}', chart '{chart_folder_path}':")
        for tag, results in results_per_tag.items():
            print(
                f"  Tag: {tag} => "
                f"code_smells={results['code_smells']}, "
                f"lines={results['lines']}, "
                f"files={results['files']}, "
                f"ratio ={results['code_smells'] / results['lines'] if results['lines'] > 0 else 0}"
            )

        # plot
        # horizontal axis: tags
        # vertical axis : code smells per lines

        # in tags_to_checkout, keep only those tags present in results_per_tag
        tags_to_checkout = [
            tag for tag in tags_to_checkout if tag[0] in results_per_tag.keys()
        ]

        if len(tags_to_checkout) < 2:
            print(f"Not enough tags with results for repository '{repository_folder}', chart '{chart_folder_path}'. Skipping plot.")
            continue

        first_smell_result = results_per_tag[tags_to_checkout[0][0]]["code_smells"]
        last_smell_result = results_per_tag[tags_to_checkout[-1][0]]["code_smells"]
        global_smells_results[str(repository_folder) + str(chart_folder_path)] = (last_smell_result - first_smell_result) / first_smell_result

        first_lines_result = results_per_tag[tags_to_checkout[0][0]]["lines"]
        last_lines_result = results_per_tag[tags_to_checkout[-1][0]]["lines"]
        global_lines_results[str(repository_folder) + str(chart_folder_path)] = (last_lines_result - first_lines_result) / first_lines_result

        first_ratio_result = first_smell_result / first_lines_result if first_lines_result > 0 else 0
        last_ratio_result = last_smell_result / last_lines_result if last_lines_result > 0 else 0
        global_ratio_results[str(repository_folder) + str(chart_folder_path)] = (last_ratio_result - first_ratio_result) / first_ratio_result if first_ratio_result > 0 else 0

    plt.figure(figsize=(10, 6))
    plt.plot(global_smells_results.keys(), global_smells_results.values(), marker='o')
    plt.title(f"Code Smells per 1000 Lines over Tags\nRepository: {repository_folder}, Chart: {chart_folder_path}")
    plt.xlabel("Git Tags")
    plt.ylabel("Percentage of evolution between first and last tag")
    plt.xticks(rotation=45)
    plt.autoscale("y")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"code_smells_over_time.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(global_lines_results.keys(), global_lines_results.values(), marker='o')
    plt.title(f"Lines over Tags\nRepository: {repository_folder}, Chart: {chart_folder_path}")
    plt.xlabel("Git Tags")
    plt.ylabel("Percentage of evolution between first and last tag")
    plt.xticks(rotation=45)
    plt.autoscale("y")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"lines_over_time.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(global_ratio_results.keys(), global_ratio_results.values(), marker='o')
    plt.title(f"Code Smells per Lines over Tags\nRepository: {repository_folder}, Chart: {chart_folder_path}")
    plt.xlabel("Git Tags")
    plt.ylabel("Percentage of evolution between first and last tag")
    plt.xticks(rotation=45)
    plt.autoscale("y")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"code_smells_per_lines_over_time.png")
    plt.close()

if __name__ == "__main__":
    main(Path("graph-over-time.toml"))