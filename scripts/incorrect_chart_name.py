import yaml
import os
import re

def check(yaml_files, chart):
    """
    Compatible avec main() qui fournit une liste de fichiers YAML d'une chart.

    Vérifie que le champ 'name' dans Chart.yaml respecte le regex Helm :
        ^[a-z0-9-]+$
    """

    if not yaml_files:
        return {
            "name": "chart_name_format",
            "success": True,
            "code_smells": 0,
            "details": "Aucun fichier YAML fourni, check ignoré."
        }

    # On retrouve le chemin racine de la chart
    # Exemple : charts/mychart/templates/deployment.yaml → charts/mychart
    chart_path = os.path.dirname(yaml_files[0])
    while chart_path and os.path.basename(chart_path) not in ("charts", ""):
        parent = os.path.dirname(chart_path)
        if os.path.basename(parent) == "charts":
            break
        chart_path = parent

    chart_file = os.path.join(chart_path, "Chart.yaml")

    if not os.path.exists(chart_file):
        return {
            "name": "chart_name_format",
            "success": True,
            "code_smells": 0,
            "details": "Aucun Chart.yaml trouvé, check ignoré."
        }

    try:
        with open(chart_file, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            return {
                "name": "chart_name_format",
                "success": False,
                "code_smells": 1,
                "details": "Le fichier Chart.yaml n'est pas un dictionnaire YAML."
            }

        name = data.get("name")

        if not name:
            return {
                "name": "chart_name_format",
                "success": False,
                "code_smells": 1,
                "details": "Aucun champ 'name' trouvé dans Chart.yaml."
            }

        # Regex conforme aux exigences Helm
        pattern = r"^[a-z0-9-]+$"

        if re.fullmatch(pattern, name):
            return {
                "name": "chart_name_format",
                "success": True,
                "code_smells": 0,
                "details": f"Le nom '{name}' est conforme."
            }

        # Nom invalide
        return {
            "name": "chart_name_format",
            "success": False,
            "code_smells": 1,
            "details": (
                f"Le nom '{name}' est invalide. "
                f"Il doit respecter le regex : {pattern}"
            )
        }

    except yaml.YAMLError as e:
        return {
            "name": "chart_name_format",
            "success": False,
            "code_smells": 1,
            "details": f"Erreur YAML : {e}"
        }
