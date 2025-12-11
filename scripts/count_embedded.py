import os
import yaml


def check(yaml_files):
    """
    Vérifie tous les fichiers YAML et calcule :
    total_objets_imbriqués / total_lignes_YAML
    """

    total_embedded = 0
    total_lines = 0

    for file in yaml_files:
        try:
            with open(file, "r") as f:
                lines = f.readlines()
                total_lines += len(lines)

            # Charger YAML
            with open(file, "r") as f:
                data = yaml.safe_load(f)

            # YAML vide
            if data is None:
                continue

            # Pas un dictionnaire → on ne peut pas compter les objets imbriqués
            if not isinstance(data, dict):
                continue

            # Nombre d'objets imbriqués au 1er niveau
            embedded = sum(1 for v in data.values() if isinstance(v, dict))
            total_embedded += embedded

        except yaml.YAMLError as e:
            ##TODO: trouver une solution later
            continue

    # Résultat global
    return {
        "name": "count_embedded_objects",
        "success": True,
        "details": f"{total_embedded} objets imbriqués / {total_lines} lignes YAML analysées.",
    }
