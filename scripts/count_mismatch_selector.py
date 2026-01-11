import os
import re

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_services(text):
    """Retourne True si le fichier contient un Service Kubernetes natif."""
    return (
        re.search(r'(?m)^kind:\s*Service\s*$', text) and 
        re.search(r'(?m)^apiVersion:\s*v1\s*$', text)
    )


def extract_pods(text):
    """Détecte un Pod."""
    return re.search(r'(?m)^kind:\s*Pod\s*$', text) is not None


def extract_deployments(text):
    """Détecte un Deployment."""
    return re.search(r'(?m)^kind:\s*Deployment\s*$', text) is not None


# ============================================================
# SELECTOR EXTRACTION (robuste, sensible à l'indentation)
# ============================================================

def extract_selector_block(text):
    """
    Extrait un bloc YAML après `selector:` en respectant l'indentation.
    Le bloc ne contient que les vrais champs du selector.
    """
    lines = text.splitlines()
    selectors = {}

    for i, line in enumerate(lines):
        # Trouver "selector:"
        if re.match(r'\s*selector:\s*$', line):
            base_indent = len(line) - len(line.lstrip())
            block = []

            # Lire les lignes suivantes tant qu'elles sont + indentées
            for j in range(i + 1, len(lines)):
                ln = lines[j]

                if ln.strip() == "":
                    break

                indent = len(ln) - len(ln.lstrip())

                # Fin du bloc dès que l'indentation est <= base
                if indent <= base_indent:
                    break

                block.append(ln)

            # Parser les lignes du bloc selector
            for ln in block:
                clean = ln.strip()
                if ":" in clean:
                    k, v = clean.split(":", 1)
                    selectors[k.strip()] = v.strip()

            return selectors

    return None


# ============================================================
# LABEL EXTRACTION
# ============================================================

def extract_labels_from_block(block):
    """Transforme un bloc YAML labels en dict."""
    labels = {}
    for line in block.splitlines():
        clean = line.strip()
        if ":" in clean:
            k, v = clean.split(":", 1)
            labels[k.strip()] = v.strip()
    return labels


def extract_labels(text):
    """
    Extrait les labels pour :
    - Pod: metadata.labels
    - Deployment: spec.template.metadata.labels
    """

    # Déploiement : labels dans spec.template.metadata.labels
    match = re.search(
        r'template:\s*\n(?:\s{2,}.*\n)*?\s*labels:\s*\n((\s{6,}.*\n)+)',
        text
    )
    if match:
        return extract_labels_from_block(match.group(1))

    # Pod : metadata.labels
    match = re.search(
        r'metadata:\s*\n(?:\s{2,}.*\n)*?\s*labels:\s*\n((\s{4,}.*\n)+)',
        text
    )
    if match:
        return extract_labels_from_block(match.group(1))

    return None


# ============================================================
# MAIN CHECK FUNCTION
# ============================================================

def check(yaml_files, chart):
    """
    Vérifie que les selectors des Services matchent les labels
    des Pods ou Deployments du chart.
    """

    service_selectors = []
    workloads_labels = []

    for filepath in yaml_files:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        # -----------------------------------------
        # ignorer ServiceMonitor, PodMonitor, CRDs, etc.
        # -----------------------------------------
        if "ServiceMonitor" in text or "PodMonitor" in text:
            continue
        if re.search(r'(?m)^apiVersion:\s*monitoring\.coreos\.com', text):
            continue
        if re.search(r'(?m)^kind:\s*CustomResourceDefinition', text):
            continue

        # -----------------------------------------
        # SERVICE → extraire selector
        # -----------------------------------------
        if extract_services(text):
            selectors = extract_selector_block(text)
            if selectors:
                service_selectors.append((filepath, selectors))

        # -----------------------------------------
        # WORKLOADS → Pods / Deployments
        # -----------------------------------------
        if extract_pods(text) or extract_deployments(text):
            labels = extract_labels(text)
            if labels:
                workloads_labels.append(labels)

    # -----------------------------------------
    # Aucun workload trouvé
    # ---------------------------------------
    if not workloads_labels:
        return {
            "name": "selector_mismatch",
            "success": True,
            "code_smells": 1,
            "details": "Aucun Pod/Deployment trouvé dans la chart."
        }

    # -----------------------------------------
    # COMPARAISON SELECTORS ↔ LABELS
    # -----------------------------------------
    violations = []

    for filepath, selectors in service_selectors:
        for key, val in selectors.items():

            matched = any(lbls.get(key) == val for lbls in workloads_labels)

            if not matched:
                violations.append(
                    f"{filepath} → selector {key}: {val} ne correspond à aucun Pod/Deployment."
                )

    return {
        "name": "selector_mismatch",
        "success": len(violations) == 0,
        "code_smells": len(violations),
        "details": (
            "Aucune violation détectée."
            if not violations
            else " / ".join(violations)
        )
    }
