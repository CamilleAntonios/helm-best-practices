import yaml
import os
import re


def check(chart_path):
    """
    Vérifie que le champ 'name' dans Chart.yaml respecte la bonne pratique :
    - seulement lettres minuscules, chiffres, tirets : ^[a-z0-9-]+$
    
    Retourne un dictionnaire :
      - name: nom du check
      - success: True/False
      - details: informations supplémentaires
    """

    chart_file = os.path.join(chart_path, "Chart.yaml")

    if not os.path.exists(chart_file):
        return {
            "name": "chart_name_format",
            "success": True,
            "details": "Aucun Chart.yaml trouvé, check ignoré."
        }

    try:
        with open(chart_file, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            return {
                "name": "chart_name_format",
                "success": False,
                "details": "Le fichier Chart.yaml n'est pas un dictionnaire YAML."
            }

        name = data.get("name")

        if not name:
            return {
                "name": "chart_name_format",
                "success": False,
                "details": "Aucun champ 'name' trouvé dans Chart.yaml."
            }

        # Regex correcte imposée par Helm
        pattern = r"^[a-z0-9-]+$"

        if re.fullmatch(pattern, name):
            return {
                "name": "chart_name_format",
                "success": True,
                "details": f"Le nom '{name}' est conforme."
            }

        # Mauvaise pratique : nom invalide
        return {
            "name": "chart_name_format",
            "success": False,
            "details": (
                f"Le nom '{name}' est invalide. "
                f"Il doit respecter le regex : {pattern}"
            )
        }

    except yaml.YAMLError as e:
        return {
            "name": "chart_name_format",
            "success": False,
            "details": f"Erreur YAML : {e}"
        }
