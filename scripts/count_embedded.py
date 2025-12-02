import yaml
import os

def check(chart_path):
    """
    Vérifie le fichier values.yaml d'une chart et renvoie un résultat.
    Retourne un dictionnaire contenant :
      - 'name': nom du check
      - 'success': True/False
      - 'details': informations supplémentaires
    """

    values_file = os.path.join(chart_path, "values.yaml")

    if not os.path.exists(values_file):
        return {
            "name": "count_embedded_objects",
            "success": True,
            "details": "Aucun values.yaml trouvé, check ignoré."
        }

    try:
        with open(values_file, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            return {
                "name": "count_embedded_objects",
                "success": False,
                "details": "Le fichier values.yaml n'est pas un dictionnaire YAML."
            }

        # On considère que plus de X objets imbriqués = mauvaise pratique
        # (seuil ajustable : ici 0 = strict, aucun objet imbriqué accepté)
        count = sum(1 for v in data.values() if isinstance(v, dict))

        return {
            "name": "count_embedded_objects",
            "success": count == 0,
            "details": f"{count} objets imbriqués trouvés."
        }

    except yaml.YAMLError as e:
        return {
            "name": "count_embedded_objects",
            "success": False,
            "details": f"Erreur YAML : {e}"
        }
