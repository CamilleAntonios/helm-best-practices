import os
import re

def check(yaml_files, chart):
    if not yaml_files:
        return {
            "name": "include_indent_required",
            "success": True,
            "code_smells": 0,
            "details": "Aucun fichier YAML fourni, check ignoré."
        }

    chart_path = os.path.dirname(yaml_files[0])
    while chart_path and os.path.basename(chart_path) not in ("charts", ""):
        parent = os.path.dirname(chart_path)
        if os.path.basename(parent) == "charts":
            break
        chart_path = parent

    templates_dir = os.path.join(chart_path, "templates")

    if not os.path.exists(templates_dir):
        return {
            "name": "include_indent_required",
            "success": True,
            "code_smells": 0,
            "details": "Aucun dossier templates/ trouvé, check ignoré."
        }

    violations = []

    include_pattern = re.compile(r"{{\s*include\s+\"[^\"]+\"\s*\.\s*([^}]*)}}")
    indent_pattern = re.compile(r"\|\s*(nindent|indent)\s+\d+")

    for root, _, files in os.walk(templates_dir):
        for file in files:
            if not file.endswith((".yaml", ".tpl")):
                continue

            filepath = os.path.join(root, file)

            with open(filepath, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if "include" not in line:
                    continue

                stripped = line.strip()

                # 🔹 Include inline → pas de règle d'indentation
                if not (stripped.startswith("{{") and stripped.endswith("}}")):
                    continue

                match = include_pattern.search(line)
                if not match:
                    continue

                pipe_section = match.group(1)

                # Include seul sur sa ligne → indent requis
                if "|" not in pipe_section:
                    violations.append(
                        f"{filepath}:{i+1} → include seul sur sa ligne sans '| indent N' ou '| nindent N'."
                    )
                    continue

                if not indent_pattern.search(pipe_section):
                    violations.append(
                        f"{filepath}:{i+1} → include seul sur sa ligne avec pipe mais sans indent/nindent valide."
                    )

    return {
        "name": "include_indent_required",
        "success": len(violations) == 0,
        "code_smells": len(violations),
        "details": (
            "Aucune violation détectée."
            if not violations
            else f"{len(violations)} problèmes trouvés."
        )
    }
