import os
import re


def check(yaml_files, chart):
    """
    Vérifie que chaque définition de template dans les fichiers .tpl
    utilise un nom namespaced (c'est à dire contenant au moins un point).

    Pattern recherché : {{- define "xxxx" }}
    Assertion : xxxx doit contenir au moins un point (par exemple : someChart.someTemplate)

    Retourne :
      - 'name'
      - 'success'
      - 'code_smells' (nombre de violations)
      - 'details'
    """

    # Le dossier templates est à l'intérieur de la chart
    templates_dir = os.path.join(chart, "templates")

    if not os.path.exists(templates_dir):
        return {
            "name": "namespaced_template_definitions",
            "success": True,
            "code_smells": 0,
            "details": "Aucun dossier templates/ trouvé, check ignoré."
        }

    violations = []

    # Pattern pour extraire les définitions : {{- define "xxxx" }}
    define_pattern = re.compile(r'{{-\s*define\s+"([^"]+)"\s*}')

    for root, _, files in os.walk(templates_dir):
        for file in files:
            # Vérifier les fichiers .tpl et .yaml
            if not file.endswith((".tpl", ".yaml")):
                continue

            filepath = os.path.join(root, file)

            try:
                with open(filepath, "r", encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines):
                    match = define_pattern.search(line)
                    if match:
                        template_name = match.group(1)
                        # Vérifier que le nom contient au moins un point (namespaced)
                        if "." not in template_name:
                            violations.append(
                                f"{filepath}:{i+1} → Template '{template_name}' n'est pas namespaced "
                                "(doit contenir un point, ex: chart.name)."
                            )
            except Exception as e:
                violations.append(
                    f"{filepath} → Erreur lors de la lecture: {str(e)}"
                )

    success = len(violations) == 0

    return {
        "name": "namespaced_template_definitions",
        "success": success,
        "code_smells": len(violations),
        "details": f"{len(violations)} definition non namespaced" if violations else "Tous les templates sont correctement namespaced."
    }
