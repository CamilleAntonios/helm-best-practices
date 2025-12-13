import os
import yaml

"""
Vérifie la mauvaise pratique du lien suivant : https://helm.sh/docs/chart_best_practices/dependencies#versions

'Il ne faut jamais fixer la version d'une dépendance précisèment, mais toujours utiliser des plages de versions.'
"""

def is_the_dependency_version_nonrange(version):
    """
    Vérifie si une version est non-range (ex: '1.2.3') ou range (ex: '^1.2.3', '~1.2.3', '>=1.2.3', '<=1.2.3', '*')
    """
    nonrange_indicators = ["~", "^", ">=", "<=", "*"]
    return not any(indicator in version for indicator in nonrange_indicators)

def check(yaml_files, chart):
    """
    Vérifie toutes les YAML d'une chart pour compter les lignes contenant
    des versions non-range. Retourne :
      - 'name'
      - 'success'
      - 'details'
    """

    total_nonrange_versions_lines = 0
    total_lines = 0

    for file in yaml_files:
        try:
            with open(file, "r") as f:
                lines = f.readlines()
                total_lines += len(lines)

            if "Chart.yaml" not in file:
                continue # on ne traite que les Chart.yaml

            # Charger YAML
            with open(file, "r") as f:
                data = yaml.safe_load(f)

            # YAML vide
            if data is None:
                continue

            try:
                total_nonrange_versions_lines += sum(1 for l in data["dependencies"] if "version" in l and is_the_dependency_version_nonrange(l["version"]))
            except KeyError:
                # le fichier n'a pas de dépendances
                # soit ce n'est pas un Chart.yml valide, soit la chart n'a pas de dépendances
                continue

        except Exception as e:
            return {
                "name": "count_nonrange_versions",
                "success": False,
                "details": f"Erreur lors de la lecture du fichier {file} : {e}",
            }

    return {
        "name": "count_nonrange_versions",
        "success": total_nonrange_versions_lines == 0,
        "code_smells": total_nonrange_versions_lines,
        "details": f"{total_nonrange_versions_lines} lignes / {total_lines} contiennent des versions non-range.",
    }
