import os


def check(yaml_files):
    """
    Vérifie toutes les YAML d'une chart pour compter les lignes contenant
    des tabulations. Retourne :
      - 'name'
      - 'success'
      - 'details'
    """

    total_tab_lines = 0
    total_lines = 0

    for file in yaml_files:
        try:
            with open(file, "r") as f:
                lines = f.readlines()

            total_lines += len(lines)
            total_tab_lines += sum(1 for l in lines if "\t" in l)

        except Exception as e:
            return {
                "name": "count_tabs",
                "success": False,
                "details": f"Erreur lors de la lecture du fichier {file} : {e}",
            }

    return {
        "name": "count_tabs",
        "success": total_tab_lines == 0,
        "details": f"{total_tab_lines} lignes / {total_lines} contiennent une tabulation.",
    }
