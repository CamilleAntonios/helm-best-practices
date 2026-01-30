import os
import importlib.util
import csv

SCRIPTS_FOLDER = "scripts"
CHARTS_FOLDER = "charts"

def load_check_functions():
    check_functions = []

    for filename in os.listdir(SCRIPTS_FOLDER):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue

        module_name = filename[:-3]
        module_path = os.path.join(SCRIPTS_FOLDER, filename)

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)

        if hasattr(module, "check"):
            check_functions.append(module.check)

    return check_functions


def get_charts_list():
    return [
        os.path.join(CHARTS_FOLDER, d)
        for d in os.listdir(CHARTS_FOLDER)
        if os.path.isdir(os.path.join(CHARTS_FOLDER, d))
    ]


def get_yaml_files(chart_path):
    """
    Retourne tous les fichiers .yaml ou .yml d'une chart Helm,
    en ignorant les templates Go (.tpl).
    """
    yaml_files = []

    for root, dirs, files in os.walk(chart_path):
        for file in files:
            if file.endswith((".yaml", ".yml")):  # Only YAML
                yaml_files.append(os.path.join(root, file))

    return yaml_files

def computeLinesOfChart(chart_path):
    total_lines = 0

    print("path for lines computation:", chart_path)
    print("from :" + os.getcwd())

    for root, dirs, files in os.walk(chart_path):
        for file in files:
            if file.endswith((".yaml", ".yml", ".tpl")):  # Only Useful Files
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {file_path} : {e}")

    return total_lines

def process_single_chart(chart, checks=None):
    if checks is None:
        print("Checks were not provided, loading them...")
        checks = load_check_functions()
    print(f"Chart : {chart}")
    codeSmells = 0
    lines = computeLinesOfChart(chart)    
    yaml_files = get_yaml_files(chart)
    files = len(yaml_files)

    for check in checks:
        result = check(yaml_files, chart)
        status = "✔️ OK" if result["success"] else "❌ FAIL"
        codeSmells += result["code_smells"]
        print(f"  - {result['name']}: {status} ({result['details']})")
    print("")
    print("total code smells for chart", chart, ":", codeSmells)
    print("")

    return codeSmells, lines, files

def main():
    print("Chargement des checks...")
    checks = load_check_functions()
    print(f"{len(checks)} checks chargés.")

    charts = get_charts_list()
    print(f"{len(charts)} charts trouvées.")

    print("\n--- Résultats ---\n")
    codeSmellsPerChart = {}
    linesPerChart = {}
    filesPerChart = {}
    for chart in charts:
        code_smells, total_lines, total_files = process_single_chart(chart, checks)
        codeSmellsPerChart[chart] = code_smells
        linesPerChart[chart] = total_lines
        filesPerChart[chart] = total_files
        
    print("--- Résumé des code smells par chart ---")
    for chart, code_smells in codeSmellsPerChart.items():
        print(f"Chart: {chart} → Code Smells: {code_smells}, Total Lines: {linesPerChart[chart]}, Total Files: {filesPerChart[chart]}, ratio: {code_smells/linesPerChart[chart] if linesPerChart[chart]>0 else 0}")

    with open("code_smells_report.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Chart", "Code Smells", "Total Lines", "Total Files", "Ratio"])
        for chart, code_smells in codeSmellsPerChart.items():
            ratio = code_smells / linesPerChart[chart] if linesPerChart[chart] > 0 else 0
            chart_name_without_charts_prefix = chart.split("/")[1] # remove the "charts/" prefix
            writer.writerow([chart_name_without_charts_prefix, code_smells, linesPerChart[chart], filesPerChart[chart], ratio])
if __name__ == "__main__":
    main()
