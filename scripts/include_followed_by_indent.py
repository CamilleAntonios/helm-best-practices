import os
import re

def check(yaml_files, chart):
    """
    Compatible avec main() :
    main() envoie une liste de chemins YAML provenant d'une chart.

    Ce check doit alors :
    - retrouver le chemin racine de la chart
    - analyser les fichiers dans <chart>/templates/
    """

    if not yaml_files:
        return {
            "name": "include_indent_required",
            "success": True,
            "code_smells": 0,
            "details": "Aucun fichier YAML fourni, check ignoré."
        }

    # On déduit la chart à partir du premier fichier YAML
    # Exemple : charts/mychart/values.yaml → charts/mychart
    chart_path = os.path.dirname(yaml_files[0])
    while chart_path and os.path.basename(chart_path) not in ("charts", ""):
        parent = os.path.dirname(chart_path)
        # On s'arrête lorsque parent == "charts"
        if os.path.basename(parent) == "charts":
            break
        chart_path = parent

    # Le dossier templates est à l'intérieur de la chart
    templates_dir = os.path.join(chart_path, "templates")

    if not os.path.exists(templates_dir):
        return {
            "name": "include_indent_required",
            "success": True,
            "code_smells": 0,
            "details": "Aucun dossier templates/ trouvé, check ignoré."
        }

    violations = []

    # Détecte un include
    include_pattern = re.compile(r"{{\s*include\s+\"[^\"]+\"\s*\.\s*([^}]*)}}")

    # Détecte indent / nindent avec nombre
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

                match = include_pattern.search(line)
                if not match:
                    continue

                pipe_section = match.group(1)

                # Cas 1 : pas de pipe → erreur
                if "|" not in pipe_section:
                    violations.append(
                        f"{filepath}:{i+1} → include sans '| indent N' ou '| nindent N'."
                    )
                    continue

                # Cas 2 : pipe mais sans indent/nindent → erreur
                if not indent_pattern.search(pipe_section):
                    violations.append(
                        f"{filepath}:{i+1} → include utilise un pipe mais sans indent/nindent valide."
                    )
                    continue

    return {
        "name": "include_indent_required",
        "success": len(violations) == 0,
        "code_smells": len(violations),
        "details": (
            "Aucune violation détectée."
            if not violations
            else f"{len(violations)} problèmes trouvés. "
        )
    }

