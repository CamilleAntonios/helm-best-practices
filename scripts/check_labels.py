import re
import os

RECOMMENDED = [
    "app.kubernetes.io/name",
    "app.kubernetes.io/instance",
    "helm.sh/chart",
    "app.kubernetes.io/managed-by",
]

NON_MANIFEST_FILES = [
    "Chart.yaml",
    "values.yaml",
]

LABEL_HELPER_PATTERN = re.compile(r'include\s+"[^"]*labels"')


def check(yaml_files, chart):
    """
    Vérifie que chaque manifest YAML applique les labels recommandés,
    soit via un helper, soit via les labels présents directement.
    """

    failures = []

    for file in yaml_files:
        if os.path.basename(file) in NON_MANIFEST_FILES:
            continue  # skip non-manifest files
        with open(file, "r") as f:
            content = f.read()
            lines = content.splitlines()

        # 1) Helper detected ?
        if LABEL_HELPER_PATTERN.search(content):
            continue  # this file is OK

        # 2) Otherwise check for direct labels
        present = set()

        for line in lines:
            stripped = line.strip()
            for label in RECOMMENDED:
                if stripped.startswith(label + ":"):
                    present.add(label)

        if len(present) != len(RECOMMENDED):
            missing = [l for l in RECOMMENDED if l not in present]
            failures.append((file, missing))

    # Final result
    if not failures:
        return {
            "name": "standard_labels",
            "success": True,
            "code_smells": 0,
            "details": "Tous les manifests appliquent les labels recommandés (via helper ou labels directs).",
        }

    detail_lines = []
    for file, missing in failures:
        detail_lines.append(f"{file}: missing {missing}")

    return {
        "name": "standard_labels",
        "success": False,
        "code_smells": len(failures),
        "details": f"labels missing for {len(failures)} files"
    }
