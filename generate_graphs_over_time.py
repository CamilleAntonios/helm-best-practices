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

    for repo in repositories:
        repository_folder = repo["repository_folder"]
        chart_folder_path = repo["chart_folder_path"]

        tags_to_checkout = find_tags(1, repository_folder)

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
                f"files={results['files']}"
            )

        # plot
        # horizontal axis: tags
        # vertical axis : code smells per lines

        # in tags_to_checkout, keep only those tags present in results_per_tag
        tags_to_checkout = [
            tag for tag in tags_to_checkout if tag[0] in results_per_tag.keys()
        ]

        code_smells_per_k_lines = [
            (results_per_tag[tag[0]]["code_smells"] / results_per_tag[tag[0]]["lines"] * 1000)
            if results_per_tag[tag[0]]["lines"] > 0 else 0
            for tag in tags_to_checkout
        ]

        plt.figure(figsize=(10, 6))
        plt.plot([tag[1] for tag in tags_to_checkout], code_smells_per_k_lines, marker='o')
        plt.title(f"Code Smells per 1000 Lines over Tags\nRepository: {repository_folder}, Chart: {chart_folder_path}")
        plt.xlabel("Git Tags")
        plt.ylabel("Code Smells per 1000 Lines")
        plt.xticks(rotation=45)
        plt.autoscale("y")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{repository_folder.replace('/', '_')}_{chart_folder_path.replace('/', '_')}_code_smells_over_time.png")
        plt.close()
        print(f"Plot saved as '{repository_folder.replace('/', '_')}_{chart_folder_path.replace('/', '_')}_code_smells_over_time.png'")

        # plot
        # horizontal axis: tags
        # vertical axis : code smells per files

        code_smells_per_100_files = [
            (results_per_tag[tag[0]]["code_smells"] / results_per_tag[tag[0]]["files"] * 100)
            if results_per_tag[tag[0]]["files"] > 0 else 0
            for tag in tags_to_checkout
        ]
        plt.figure(figsize=(10, 6))
        plt.plot([tag[1] for tag in tags_to_checkout], code_smells_per_100_files, marker='o', color='orange')
        plt.title(f"Code Smells per 100 Files over Tags\nRepository: {repository_folder}, Chart: {chart_folder_path}")
        plt.xlabel("Git Tags")
        plt.ylabel("Code Smells per 100 Files")
        plt.xticks(rotation=45)
        plt.autoscale("y")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{repository_folder.replace('/', '_')}_{chart_folder_path.replace('/', '_')}_code_smells_per_files_over_time.png")
        plt.close()
        print(f"Plot saved as '{repository_folder.replace('/', '_')}_{chart_folder_path.replace('/', '_')}_code_smells_per_files_over_time.png'")



if __name__ == "__main__":
    main(Path("graph-over-time.toml"))