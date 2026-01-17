import os
import re


def check(yaml_files, chart):
    """
    Vérifie la présence d'un fichier helper dans les charts Helm.
    Vérifie aussi que ce fichier contient le motif 'define "*.labels"'.
    Retourne :
      - 'name'
      - 'success'
      - 'details'
    """

    helper_file_found = False
    labels_define_found = False
    helper_file_path = None

    # Chercher le fichier _helpers.tpl
    for root, dirs, files in os.walk(chart):
        for file in files:
            if file == "_helpers.tpl":
                helper_file_found = True
                helper_file_path = os.path.join(root, file)
                break
        if helper_file_found:
            break

    # Vérifier le contenu du fichier _helpers.tpl
    if helper_file_found and helper_file_path:
        try:
            with open(helper_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Chercher le motif 'define "*.labels"'
                if re.search(r'define\s+"[^"]+\.labels"', content):
                    labels_define_found = True
        except Exception as e:
            return {
                "name": "has_helper_file",
                "success": False,
                "details": f"Erreur lors de la lecture du fichier: {str(e)}",
            }

    success = helper_file_found and labels_define_found
   
    if not helper_file_found:
        details = "_helpers.tpl non trouvé."
    elif not labels_define_found:
        details = '_helpers.tpl trouvé mais ne contient pas le motif define "*.labels".'
    else:
        details = '_helpers.tpl trouvé et contient le motif define "*.labels".'

    return {
        "name": "has_helper_file",
        "success": success,
        "details": details,
        "code_smells": 0 if success else 1
    }