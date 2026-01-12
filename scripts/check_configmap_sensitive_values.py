import re


def check(yaml_files, chart):
    """
    Detecte un code smell lorsque :
    - le fichier contient 'kind: ConfigMap'
    - ET contient une clé YAML contenant 'password' ou 'token' (case-insensitive)
    - ET la clé ne contient pas 'file', 'url' ou 'path'
    - ET la valeur de cette clé :
        - ne contient pas '.Values'
        - n'est pas vide
        - n'est pas une chaîne vide ("", '')
        - ne contient pas 'true', 'false' ou 'file' (case-insensitive)
        - ne contient pas de template {{ ... }}
    """

    violations = []

    # Regex pour détecter les clés sensibles (password/token)
    sensitive_key_pattern = re.compile(
        r'^\s*([A-Za-z0-9_-]*(password|token)[A-Za-z0-9_-]*)\s*:\s*(.*)$',
        re.IGNORECASE
    )

    # Regex pour détecter les templates Helm / Go
    template_pattern = re.compile(r'{{.*?}}')

    for file in yaml_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split('\n')

            # Condition 1 : kind: ConfigMap présent
            if not any("kind: ConfigMap" in line for line in lines):
                continue

            # Chercher les clés sensibles
            for i, line in enumerate(lines):
                match = sensitive_key_pattern.match(line)
                if not match:
                    continue

                key = match.group(1)
                value = match.group(3).strip()

                key_lower = key.lower()
                value_lower = value.lower()

                # Ignorer les clés liées aux fichiers, URLs ou chemins
                if any(word in key_lower for word in ("file", "url", "path")):
                    continue

                # Ignorer les valeurs provenant de Helm (.Values)
                if ".Values" in value:
                    continue

                # Ignorer les valeurs vides ou chaînes vides
                if value in ("", "''", '""'):
                    continue

                # Ignorer les booléens, fichiers, etc.
                if any(word in value_lower for word in ("true", "false", "file")):
                    continue

                # Ignorer les valeurs templatisées {{ ... }}
                if template_pattern.search(value):
                    continue

                message = (
                    f"{file}:{i+1} → Clé sensible '{key}' "
                    "définie en clair dans un ConfigMap."
                )

                # Affichage immédiat du problème détecté
                print(message)

                violations.append(message)

        except Exception:
            # Ignorer les fichiers illisibles
            continue

    return {
        "name": "configmap_sensitive_values",
        "success": len(violations) == 0,
        "code_smells": len(violations),
        "details": (
            f"{len(violations)} ConfigMap(s) contiennent des secrets en clair"
            if violations else
            "Aucune valeur sensible en clair trouvée dans les ConfigMaps."
        ),
    }
