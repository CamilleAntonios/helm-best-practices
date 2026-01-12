# Fichiers
# Pour générer automatiquement les graphs
Avec WSl: 
`./make_graphs.sh`
va tout faire.

# Fichiers de calculs de graphs
## `compute_graphs` 
Le fichier fait les graphs au sens qu'on avait prévu : faire varier le ratio de code smells par lignes de code, sur toutes nos variables.

## `compute_graphs_peak_excluded`
Même chose qu'avant, mais exclue les valeurs qui dépassent le 95% des autres, que ce soit en ordonnée ou en abscisse.

## `compute_graphs_ratio_per_file`
Comme `compute_graphs`, mais au lieu d'utiliser le pourcentage de codes smells par lignes de code, utilise le ratio de code smells par fichiers YAML.

# Fichiers CSV
## `chart_infos.csv`
Contient les infos qu'on a noté sur Google Drive : dernières deliveries, provenance de la chart ...

## `code_smells_report.csv` (généré par les scripts)
Résultat des codes smells

## `final_report.csv` (généré par `aggregate_csv.py`)
Fait le lien entre `chart_infos.csv` et `code_smells_report.csv`, pour mettre dans un unique fichier toutes les infos nécessaires pour calculer les graphs. Le join se fait sur le nom de la chart, et ce doit donc être STRICTEMENT le même dans les deux fichiers CSV sources.