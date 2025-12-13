def count_embedded_objects_from_text(yaml_content):
    """
    Compte les objets imbriqués dans un contenu YAML sans utiliser le module yaml.
    Un objet imbriqué est détecté comme une clé ayant une valeur indentée (non-commentaire).
    """
    embedded_count = 0
    lines = yaml_content.split('\n')
    
    for i, line in enumerate(lines):
        # Ignorer les lignes vides et les commentaires
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            continue
        
        # Vérifier si c'est une clé au niveau racine (pas indentée ou indentation = 0)
        if not line.startswith(' ') and not line.startswith('\t'):
            # C'est une clé potentielle
            if ':' in line and not stripped.startswith('-'):
                # Chercher la première ligne indentée non-vide après cette clé
                # (en ignorant les commentaires)
                for j in range(i + 1, len(lines)):
                    next_line = lines[j]
                    next_stripped = next_line.lstrip()
                    
                    # Ignorer les lignes vides
                    if not next_stripped:
                        continue
                    
                    # Si on trouve une ligne indentée (pas un commentaire), c'est un objet imbriqué
                    if len(next_line) - len(next_line.lstrip()) > 0:
                        # Mais on doit vérifier que ce n'est pas une clé au niveau racine
                        if next_stripped.startswith('#'):
                            # C'est un commentaire, on continue
                            continue
                        else:
                            # C'est du contenu imbriqué
                            embedded_count += 1
                            break
                    else:
                        # Ligne sans indentation trouvée = pas d'objet imbriqué
                        break
    
    return embedded_count


def check(yaml_files, chart):
    """
    Vérifie les objets imbriqués dans les fichiers YAML.
    
    Dans une chart Helm, values.yaml est le seul fichier qui DOIT contenir 
    les définitions de variables. On vérifie donc uniquement celui-ci.
    """
    
    # Chercher le fichier values.yaml
    values_file = None
    for file in yaml_files:
        if file.endswith("values.yaml"):
            values_file = file
            break
    
    total_embedded = 0
    total_lines = 0
    files_checked = []
    
    # Vérifier uniquement values.yaml (seul fichier définissant les variables)
    files_to_check = [values_file] if values_file else []
    
    # Analyser les fichiers
    for file in files_to_check:
        try:
            with open(file, "r", encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                total_lines += len(lines)
            
            # Compter les objets imbriqués
            embedded = count_embedded_objects_from_text(content)
            if embedded > 0:
                total_embedded += embedded
                files_checked.append(f"{file}: {embedded} objet(s) imbriqué(s)")
        
        except Exception as e:
            # Ignorer les fichiers qui ne peuvent pas être lus
            continue
    
    # Résultat global
    details_msg = f"{total_embedded} objet(s) imbriqué(s) / {total_lines} lignes YAML analysées"
    if files_checked:
        details_msg += " - " + "; ".join(files_checked)
    
    return {
        "name": "count_embedded_objects",
        "success": total_embedded == 0,
        "code_smells": total_embedded,
        "details": details_msg,
    }
