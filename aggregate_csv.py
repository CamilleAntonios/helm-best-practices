"""
Fichier pour relier les infos de "code_smells_report.csv" et "chart-infos.csv"
dans un fichier unique final "final_report.csv".
"""
import csv

CODE_SMELLS_FILE = "code_smells_report.csv"
CHART_INFOS_FILE = "chart_infos.csv"
OUTPUT_FILE = "final_report.csv"

# --- Read chart_infos.csv into a dict keyed by Nom ---
chart_infos = {}

with open(CHART_INFOS_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        chart_name = row.get("Nom")
        if chart_name:
            chart_infos[chart_name] = {
                "stars": row.get("Etoiles"),
                "days_ago": row.get("Days Ago"),
                "origin": row.get("Provenance"),
            }

# --- Read code_smells_report.csv and join ---
final_rows = []

with open(CODE_SMELLS_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        chart = row.get("Chart")

        if chart in chart_infos:
            info = chart_infos[chart]
            final_rows.append({
                "Chart": chart,
                "stars": info["stars"],
                "days_ago": info["days_ago"],
                "origin": info["origin"],
                "code_smells": row.get("Code Smells"),
                "total_lines": row.get("Total Lines"),
                "total_files": row.get("Total Files"),
                "ratio": row.get("Ratio"),
            })

# --- Write final_report.csv ---
fieldnames = [
    "Chart",
    "stars",
    "days_ago",
    "origin",
    "code_smells",
    "total_lines",
    "total_files",
    "ratio"
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_rows)

print(f"Final report written to {OUTPUT_FILE}")
