import os
import re

def check(chart_path):
    """
    Vérifie que chaque '{{ include ... }}' est suivi d'un '| indent N' ou '| nindent N'.
    
    Retourne :
      - name: nom du check
      - success: True/False
      - details: liste des violations détectées
    """

    templates_dir = os.path.join(chart_path, "templates")

    if not os.path.exists(templates_dir):
        return {
            "name": "include_indent_required",
            "success": True,
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

                # Cas 1 : pas de pipe du tout → erreur
                if "|" not in pipe_section:
                    violations.append(
                        f"{filepath}:{i+1} → include sans '| indent N' ou '| nindent N'."
                    )
                    continue

                # Cas 2 : pipe mais pas indent/nindent → erreur
                if not indent_pattern.search(pipe_section):
                    violations.append(
                        f"{filepath}:{i+1} → include utilise un pipe mais sans indent/nindent valide."
                    )
                    continue

    return {
        "name": "include_indent_required",
        "success": len(violations) == 0,
        "details": (
            "Aucune violation détectée."
            if not violations
            else f"{len(violations)} problèmes trouvés"
        )
    }
