import os

"""
Verification de la mauvaise pratique :
'Il ne faut pas utiliser des repositories en HTTP uniquement (sans HTTPS)'
"""

def check(yaml_files, chart):
    """
    Vérifie toutes les YAML d'une chart pour compter les lignes contenant
    des tabulations. Retourne :
      - 'name'
      - 'success'
      - 'details'
    """

    total_http_repositories = 0
    total_lines = 0

    for file in yaml_files:
        try:
            with open(file, "r") as f:
                lines = f.readlines()

            total_lines += len(lines)
            total_http_repositories += sum(1 for l in lines if "http://" in l and "repository" in l)

        except Exception as e:
            return {
                "name": "count_http_only_repositories",
                "success": False,
                "details": f"Erreur lors de la lecture du fichier {file} : {e}",
            }

    return {
        "name": "count_http_only_repositories",
        "success": total_http_repositories == 0,
        "details": f"{total_http_repositories} lignes / {total_lines} contiennent des repositories qui sont en HTTP uniquement.",
    }
