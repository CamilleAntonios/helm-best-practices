# Nettoyage des anciens fichiers
rm graphs/*
rm graphs_with_peaks_excluded/*
rm code_smells_report.csv
rm final_report.csv

# Calcul des codes smells (ça écrit dans le fichier 'code_smells_report.csv')
python code_smells_calculator.py

# Join entre le fichier 'chart_infos.csv' et 'code_smells_report.csv' pour obtenir 'final_report.csv'
python aggregate_csv.py

# Création des graphs
python compute_graphs.py
python compute_graphs_peaks_excluded.py
python compute_graphs_ratio_per_file.py