import os
import pandas as pd
import re
from  tkinter import Tk, filedialog

# Percorso della cartella principale
Tk().withdraw()
root_dir = filedialog.askdirectory(title="seleziona la cartella CFD")

if not root_dir:
    raise ValueError("Nessuna cartella selezionata. Uscita.")

print(f"Cartella CFD selezionata: {root_dir}")

# Lista per salvare i dati
data = []

# Funzione per estrarre CL e Cd dal file
def estrai_cl_cd(filepath):
    cl, cd = None, None
    with open(filepath, 'r') as f:
        for line in f:
            if "CL" in line.upper():
                cl = float(re.search(r"[-+]?\d*\.\d+|\d+", line).group())
            elif "CD" in line.upper():
                cd = float(re.search(r"[-+]?\d*\.\d+|\d+", line).group())
    return cl, cd

# Cammina nella directory ricorsivamente
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.lower() in ["result.txt", "results.txt"]:
            full_path = os.path.join(dirpath, filename)
            cl, cd = estrai_cl_cd(full_path)

            # Info strutturali
            relative_path = os.path.relpath(full_path, root_dir)
            parts = relative_path.split(os.sep)

            sim = parts[0] if len(parts) > 0 else "Unknown"
            tipo_naso = parts[1] if len(parts) > 2 else "No_info"  # gestisce caso SIM2
            configurazione = parts[-2]  # nome della cartella profilo

            # Salva i dati
            data.append({
                "SIM": sim,
                "Tipo": tipo_naso,
                "Configurazione": configurazione,
                "CL": cl,
                "Cd": cd,
                "Path": relative_path
            })

# Crea il dataframe
df = pd.DataFrame(data)

# Mostra il risultato
print(df.head())

# Salva su file
df.to_csv("Risultati.csv", index=False)
