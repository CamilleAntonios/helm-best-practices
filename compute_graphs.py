import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# Setup
# -------------------------
OUTPUT_DIR = "graphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# Load & clean data
# -------------------------
df = pd.read_csv("final_report.csv")

# Clean ratio column (e.g. "0.71%")
df["ratio"] = (
    df["ratio"]
    .str.replace("%", "", regex=False)
    .astype(float)
)

# Clean days_ago (handle quoted values with comma decimal)
def parse_days_ago(x):
    if isinstance(x, str):
        x = x.replace(",", ".").replace('"', "")
    return float(x)

df["days_ago"] = df["days_ago"].apply(parse_days_ago)

# Recompute ratio if needed (safety)
df["ratio"] = df["code_smells"] / df["total_lines"] * 100

# -------------------------
# Helper function
# -------------------------
def plot_scatter(x, y, data, label, filename, xlabel, ylabel):
    plt.figure()
    for name, group in data:
        plt.scatter(group[x], group[y], label=name, alpha=0.6)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close()

# -------------------------
# 1. Bad practices vs stars (commu vs entreprise)
# -------------------------
plot_scatter(
    x="stars",
    y="ratio",
    data=df.groupby("origin"),
    label="origin",
    filename="bad_practices_vs_stars_origin.png",
    xlabel="Nombre d'étoiles Artifactory",
    ylabel="% de mauvaises pratiques par ligne"
)

# -------------------------
# 2. Bad practices vs stars with median split
# -------------------------
median_stars = df["stars"].median()

df["stars_group"] = np.where(
    df["stars"] <= median_stars,
    "Sous médiane",
    "Au-dessus médiane"
)

plt.figure()
for (origin, group_name), group in df.groupby(["origin", "stars_group"]):
    label = f"{origin} - {group_name}"
    plt.scatter(group["stars"], group["ratio"], label=label, alpha=0.6)

plt.xlabel("Nombre d'étoiles Artifactory")
plt.ylabel("% de mauvaises pratiques par ligne")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "bad_practices_vs_stars_median_split.png"))
plt.close()

# -------------------------
# 3. Bad practices vs total lines
# -------------------------
plot_scatter(
    x="total_lines",
    y="ratio",
    data=df.groupby("origin"),
    label="origin",
    filename="bad_practices_vs_total_lines.png",
    xlabel="Nombre total de lignes de configuration",
    ylabel="% de mauvaises pratiques par ligne"
)

# -------------------------
# 4. Bad practices vs days ago
# -------------------------
plt.figure()
plt.scatter(df["days_ago"], df["ratio"], alpha=0.6)
plt.xlabel("Dernier commit (days ago)")
plt.ylabel("% de mauvaises pratiques par ligne")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "bad_practices_vs_days_ago.png"))
plt.close()

# -------------------------
# 5. Quartiles of days_ago (bar chart)
# -------------------------
df["days_quartile"] = pd.qcut(
    df["days_ago"],
    q=4,
    labels=["Q1 (plus récent)", "Q2", "Q3", "Q4 (plus ancien)"]
)

quartile_means = df.groupby("days_quartile")["ratio"].mean()

plt.figure()
quartile_means.plot(kind="bar")
plt.ylabel("% moyen de mauvaises pratiques par ligne")
plt.xlabel("Quartiles de Days Ago")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "bad_practices_by_days_ago_quartiles.png"))
plt.close()

# -------------------------
# 6. Mean comparison commu vs entreprise
# -------------------------
mean_ratios = df.groupby("origin")["ratio"].mean()

plt.figure()
mean_ratios.plot(kind="bar")
plt.ylabel("% moyen de mauvaises pratiques par ligne")
plt.xlabel("Origine du chart")
plt.title(
    "ATTENTION : ce chiffre seul n'est PAS représentatif\n"
    "(il exclut les étoiles, la taille et la fraîcheur du projet)"
)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "mean_bad_practices_commu_vs_entreprise.png"))
plt.close()

print("Tous les graphiques ont été générés dans le dossier 'graphs/'")
