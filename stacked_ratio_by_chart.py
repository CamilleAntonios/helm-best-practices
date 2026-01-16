import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------
# Setup
# -------------------------
OUTPUT_DIR = "graphs_stacked"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# Load data
# -------------------------
df = pd.read_csv("code_smells_by_practice.csv")

# Convert ratio "x.xx%" -> float
df["Ratio"] = df["Ratio"].str.replace("%", "", regex=False).astype(float)

# -------------------------
# Pivot: Chart x Practice
# -------------------------
pivot = df.pivot_table(index="Chart", columns="Practice", values="Ratio", fill_value=0)

# Optional: sort charts by total ratio (descending)
pivot["TOTAL"] = pivot.sum(axis=1)
pivot = pivot.sort_values("TOTAL", ascending=False)
pivot = pivot.drop(columns="TOTAL")

# -------------------------
# Plot stacked bar chart
# -------------------------
plt.figure(figsize=(14, 8))

bottom = None
for practice in pivot.columns:
    if bottom is None:
        plt.bar(pivot.index, pivot[practice], label=practice)
        bottom = pivot[practice]
    else:
        plt.bar(pivot.index, pivot[practice], bottom=bottom, label=practice)
        bottom = bottom + pivot[practice]

# -------------------------
# Styling
# -------------------------
plt.ylabel("% de mauvaises pratiques par ligne")
plt.xlabel("Charts Helm")
plt.title("Répartition des mauvaises pratiques par chart (ratios empilés)")
plt.xticks(rotation=90)
plt.legend(title="Mauvaise pratique", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()

# -------------------------
# Save
# -------------------------
plt.savefig(os.path.join(OUTPUT_DIR, "stacked_ratio_by_chart.png"))
plt.close()

print("Graph generated in graphs_stacked/stacked_ratio_by_chart.png")
# ============================================================
# Statistical summaries for analysis
# ============================================================

print("\n================ ANALYSE STATISTIQUE ================\n")

# ------------------------------------------------------------
# 1. Charts avec le MOINS de mauvaises pratiques (top 10)
# ------------------------------------------------------------
total_ratio_per_chart = pivot.sum(axis=1)

print("📉 Charts avec le moins de mauvaises pratiques (Top 10) :")
for chart, ratio in total_ratio_per_chart.sort_values().head(10).items():
    print(f"  - {chart:<35} → {ratio:.2f}%")
print("")

# ------------------------------------------------------------
# 2. Charts avec le PLUS de mauvaises pratiques (Top 10)
# ------------------------------------------------------------
print("📈 Charts avec le plus de mauvaises pratiques (Top 10) :")
for chart, ratio in total_ratio_per_chart.sort_values(ascending=False).head(10).items():
    print(f"  - {chart:<35} → {ratio:.2f}%")
print("")

# ------------------------------------------------------------
# 3. Pratique JAMAIS détectée
# ------------------------------------------------------------
practice_totals = pivot.sum(axis=0)

never_detected = practice_totals[practice_totals == 0].index.tolist()

if never_detected:
    print("✅ Mauvaises pratiques jamais détectées sur l’ensemble des charts :")
    for p in never_detected:
        print(f"  - {p}")
else:
    print("⚠️ Toutes les mauvaises pratiques ont été détectées au moins une fois.")
print("")

# ------------------------------
# ============================================================
# Additional global statistics on practices
# ============================================================

print("\n================ ANALYSE GLOBALE DES MAUVAISES PRATIQUES ================\n")

# Total number of charts
nb_charts = pivot.shape[0]
print(f"Nombre total de charts analysées : {nb_charts}\n")

# ------------------------------------------------------------
# 1. Nombre de charts où chaque pratique est détectée
# ------------------------------------------------------------
# Une pratique est considérée détectée si son ratio > 0
practice_presence = (pivot > 0).sum(axis=0)

practice_presence_sorted = practice_presence.sort_values(ascending=False)

print("📊 Classement des mauvaises pratiques par nombre de charts impactées :")
for practice, count in practice_presence_sorted.items():
    percentage = (count / nb_charts) * 100
    print(f"  - {practice:<30} → {count:>3} charts ({percentage:5.1f}%)")
print("")

# ------------------------------------------------------------
# 2. Pratiques quasi systématiques vs rares
# ------------------------------------------------------------
systematic = practice_presence_sorted[practice_presence_sorted >= nb_charts * 0.75]
rare = practice_presence_sorted[practice_presence_sorted <= nb_charts * 0.10]

print("🔥 Mauvaises pratiques très fréquentes (≥ 75% des charts) :")
if not systematic.empty:
    for practice, count in systematic.items():
        print(f"  - {practice} ({count}/{nb_charts})")
else:
    print("  Aucune pratique n'est quasi systématique.")
print("")

print("🧊 Mauvaises pratiques rares (≤ 10% des charts) :")
if not rare.empty:
    for practice, count in rare.items():
        print(f"  - {practice} ({count}/{nb_charts})")
else:
    print("  Aucune pratique strictement rare.")
print("")

# ------------------------------------------------------------
# 3. Intensité moyenne quand la pratique est présente
# ------------------------------------------------------------
# Moyenne uniquement sur les charts où la pratique existe
mean_when_present = pivot.where(pivot > 0).mean(axis=0)

print("📈 Intensité moyenne des pratiques (uniquement quand détectées) :")
for practice, value in mean_when_present.sort_values(ascending=False).items():
    if pd.notna(value):
        print(f"  - {practice:<30} → {value:.2f}%")
print("")

# ------------------------------------------------------------
# 4. Couverture cumulée (Pareto)
# ------------------------------------------------------------
total_contribution = pivot.sum(axis=0)
total_all = total_contribution.sum()

pareto = total_contribution.sort_values(ascending=False).cumsum() / total_all * 100

print("📐 Analyse de Pareto (contribution cumulée des pratiques) :")
for practice, cum_pct in pareto.items():
    print(f"  - {practice:<30} → {cum_pct:5.1f}% cumulé")
print("")

# ------------------------------------------------------------
# 5. Nombre moyen de pratiques par chart
# ------------------------------------------------------------
nb_practices_per_chart = (pivot > 0).sum(axis=1)

print("📦 Diversité des mauvaises pratiques par chart :")
print(f"  - Moyenne  : {nb_practices_per_chart.mean():.2f} pratiques / chart")
print(f"  - Médiane  : {nb_practices_per_chart.median():.0f}")
print(f"  - Min / Max: {nb_practices_per_chart.min()} / {nb_practices_per_chart.max()}")
print("")

print("================ FIN ANALYSE GLOBALE =================\n")
