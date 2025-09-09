import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import os

# Percorso dei file
base_path = os.path.dirname(__file__)
csv_path = os.path.join(base_path, "risultati_deviazione.csv")
stallo_path = os.path.join(base_path, "Stallo.txt")

# Leggi i CSV
df = pd.read_csv(csv_path)
import re
df_stallo = pd.read_csv(stallo_path, sep=r"\t|\s+", engine="python", names=["cartella", "stallo"], header=None)

# Unisci i due dataframe sulla colonna 'cartella'
df_merged = pd.merge(df, df_stallo, on="cartella", how="inner")

# Sostituzioni dei nomi
df_merged['cartella'] = df_merged['cartella'].str.replace('be092075', 'Be 092-075', regex=False)
df_merged['cartella'] = df_merged['cartella'].str.replace('be122125', 'Be 122-125', regex=False)
df_merged['cartella'] = df_merged['cartella'].str.replace('be122155', 'Be 122-155', regex=False)

# Converti i nomi dei profili in maiuscolo
df_merged['cartella'] = df_merged['cartella'].str.upper()

# Aggiungi spazio dopo NACA
df_merged['cartella'] = df_merged['cartella'].str.replace('NACA', 'NACA ', regex=False)
df_merged['cartella'] = df_merged['cartella'].str.replace('NACA  ', 'NACA ', regex=False)  # Rimuovi doppi spazi

# Sostituisci underscore con " + " tra i profili
df_merged['cartella'] = df_merged['cartella'].str.replace('_', ' + ', regex=False)

# Riordina in modo alfabetico per cartella
df_merged = df_merged.sort_values('cartella')



# Filtra solo dove stallo == "no" (case insensitive) e crea una copia per evitare SettingWithCopyWarning
df_plot = df_merged[df_merged["stallo"].str.lower() == "no"].copy()

# Controlla che le colonne esistano
if "Cd.csv" not in df_merged.columns or "min_theta" not in df_merged.columns or "cartella" not in df_merged.columns:
    raise ValueError("Il file CSV deve contenere le colonne 'Cd.csv', 'min_theta' e 'cartella'.")

# Normalizza rispetto al massimo di 1/Cd.csv e al valore assoluto del minimo di min_theta (sul dataframe completo)
cd_inv_max_all = (1 / df_merged["Cd.csv"]).max()
theta_min_abs_all = abs(df_merged["min_theta"].min())
df_merged["Cd_inv_norm"] = (1 / df_merged["Cd.csv"]) / cd_inv_max_all if cd_inv_max_all != 0 else (1 / df_merged["Cd.csv"])
df_merged["min_theta_norm"] = df_merged["min_theta"] / theta_min_abs_all if theta_min_abs_all != 0 else df_merged["min_theta"]

# Plot TUTTI I DATI (senza filtro stallo)
fig, ax = plt.subplots(figsize=(15, 8))
ax.scatter(df_merged["Cd.csv"], df_merged["min_theta"], color='blue', marker='o', s=60, edgecolors='black', linewidths=1)

# Numerazione punti in grassetto
num_labels = list(range(1, len(df_merged) + 1))
for i, (idx, row) in enumerate(df_merged.iterrows()):
    ax.annotate(str(num_labels[i]), (row["Cd.csv"], row["min_theta"]), 
                xytext=(3, 3), textcoords='offset points',
                fontsize=7, color='black', weight='bold', ha='left', va='bottom')

ax.set_xlabel("$C_D$")
ax.set_ylabel("$\\theta_{min}$ (°)")
ax.set_title("$\\theta_{min}$ vs $C_D$")
ax.grid(True)

# Legenda numerica a lato in più colonne per compattezza
labels_data = [(num_labels[i], row['cartella']) for i, (idx, row) in enumerate(df_merged.iterrows())]
# Dividi in 2 colonne
n_cols = 2
n_rows = len(labels_data) // n_cols + (1 if len(labels_data) % n_cols > 0 else 0)
legend_lines = []
for row in range(n_rows):
    line_parts = []
    for col in range(n_cols):
        idx = row * n_cols + col
        if idx < len(labels_data):
            line_parts.append(f"$\\mathbf{{{labels_data[idx][0]}}}$: {labels_data[idx][1]}")
        else:
            line_parts.append("")  # Riempi celle vuote
    legend_lines.append("  |  ".join(line_parts))

legend_text = "\n".join(legend_lines)
ax.text(1.05, 0.5, legend_text, transform=ax.transAxes, fontsize=9, verticalalignment='center', 
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="black"), family='sans-serif')

plt.tight_layout()
plt.show()



# Normalizza e calcola funzione obiettivo solo per i non stallo (come prima)
cd_inv_max = (1 / df_plot["Cd.csv"]).max()
theta_min_abs = abs(df_plot["min_theta"].min())
df_plot["Cd_inv_norm"] = (1 / df_plot["Cd.csv"]) / cd_inv_max if cd_inv_max != 0 else (1 / df_plot["Cd.csv"])
df_plot["min_theta_norm"] = df_plot["min_theta"] / theta_min_abs if theta_min_abs != 0 else df_plot["min_theta"]

# Definisci i pesi (modifica a piacere)
w_theta = -0.55
w_cd = 0.45

# Calcola la funzione obiettivo come somma pesata
df_plot["obiettivo"] = w_theta * df_plot["min_theta_norm"] + w_cd * df_plot["Cd_inv_norm"]

# Plot SOLO NON STALLO (senza ordinamento)
fig, ax = plt.subplots(figsize=(15, 8))
ax.scatter(df_plot["Cd.csv"], df_plot["min_theta"], color='blue', marker='o', s=60, edgecolors='black', linewidths=1)

# Numerazione punti in grassetto
num_labels_2 = list(range(1, len(df_plot) + 1))
for i, (idx, row) in enumerate(df_plot.iterrows()):
    ax.annotate(str(num_labels_2[i]), (row["Cd.csv"], row["min_theta"]), 
                xytext=(3, 3), textcoords='offset points',
                fontsize=7, color='black', weight='bold', ha='left', va='bottom')

ax.set_xlabel("$C_D$")
ax.set_ylabel("$\\theta_{min}$ (°)")
ax.set_title("$\\theta_{min}$ vs $C_D$")
ax.grid(True)

# Legenda numerica a lato in più colonne per compattezza
labels_data_2 = [(num_labels_2[i], row['cartella']) for i, (idx, row) in enumerate(df_plot.iterrows())]
# Dividi in 1 colonna
n_cols_2 = 1
n_rows_2 = len(labels_data_2) // n_cols_2 + (1 if len(labels_data_2) % n_cols_2 > 0 else 0)
legend_lines_2 = []
for row in range(n_rows_2):
    line_parts = []
    for col in range(n_cols_2):
        idx = row * n_cols_2 + col
        if idx < len(labels_data_2):
            line_parts.append(f"$\\mathbf{{{labels_data_2[idx][0]}}}$: {labels_data_2[idx][1]}")
        else:
            line_parts.append("")  # Riempi celle vuote
    legend_lines_2.append("  |  ".join(line_parts))

legend_text_2 = "\n".join(legend_lines_2)
ax.text(1.05, 0.5, legend_text_2, transform=ax.transAxes, fontsize=12, verticalalignment='center', 
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="black"), family='sans-serif')

plt.tight_layout()
plt.show()

# Plot funzione obiettivo
# Ordina per funzione obiettivo in modo decrescente per il grafico colorato
df_plot_sorted = df_plot.sort_values("obiettivo", ascending=False)

fig, ax = plt.subplots(figsize=(15, 8))
scatter = ax.scatter(df_plot_sorted["Cd.csv"], df_plot_sorted["min_theta"], c=df_plot_sorted["obiettivo"], cmap="viridis", marker='o', s=60, edgecolors='black', linewidths=1)

# Numerazione punti in grassetto (ordinati per funzione obiettivo)
num_labels_3 = list(range(1, len(df_plot_sorted) + 1))
for i, (idx, row) in enumerate(df_plot_sorted.iterrows()):
    ax.annotate(str(num_labels_3[i]), (row["Cd.csv"], row["min_theta"]), 
                xytext=(3, 3), textcoords='offset points',
                fontsize=7, color='black', weight='bold', ha='left', va='bottom')

ax.set_xlabel("$C_D$")
ax.set_ylabel("$\\theta_{min}$ (°)")
ax.set_title("$\\theta_{min}$ vs $C_D$")
plt.colorbar(scatter, label="Funzione obiettivo")
ax.grid(True)

# Legenda numerica a lato in più colonne per compattezza
labels_data_3 = [(num_labels_3[i], row['cartella']) for i, (idx, row) in enumerate(df_plot_sorted.iterrows())]
# Dividi in 1 colonna
n_cols_3 = 1
n_rows_3 = len(labels_data_3) // n_cols_3 + (1 if len(labels_data_3) % n_cols_3 > 0 else 0)
legend_lines_3 = []
for row in range(n_rows_3):
    line_parts = []
    for col in range(n_cols_3):
        idx = row * n_cols_3 + col
        if idx < len(labels_data_3):
            line_parts.append(f"$\\mathbf{{{labels_data_3[idx][0]}}}$: {labels_data_3[idx][1]}")
        else:
            line_parts.append("")  # Riempi celle vuote
    legend_lines_3.append("  |  ".join(line_parts))

legend_text_3 = "\n".join(legend_lines_3)
ax.text(1.25, 0.5, legend_text_3, transform=ax.transAxes, fontsize=12, verticalalignment='center', 
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="black"), family='sans-serif')

plt.tight_layout()
plt.show()

# Stampa i cinque migliori risultati della funzione obiettivo con colonne e nomi richiesti
print("Cinque migliori risultati (funzione obiettivo più alta):")
df_print = df_plot_sorted[["cartella", "Cd.csv", "min_theta", "obiettivo"]].head(5).copy()
df_print = df_print.rename(columns={"cartella": "Accoppiamento", "Cd.csv": "Cd", "min_theta": "Theta", "obiettivo": "f_obiettivo"})
print(df_print[["Accoppiamento", "Cd", "Theta", "f_obiettivo"]].to_string(index=False))