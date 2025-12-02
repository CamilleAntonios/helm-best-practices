import os
import importlib.util

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


def main():
    print("Chargement des checks...")
    checks = load_check_functions()
    print(f"{len(checks)} checks chargés.")

    charts = get_charts_list()
    print(f"{len(charts)} charts trouvées.")

    print("\n--- Résultats ---\n")

    for chart in charts:
        print(f"Chart : {chart}")
        for check in checks:
            result = check(chart)
            status = "✔️ OK" if result["success"] else "❌ FAIL"
            print(f"  - {result['name']}: {status} ({result['details']})")
        print("")


if __name__ == "__main__":
    main()
