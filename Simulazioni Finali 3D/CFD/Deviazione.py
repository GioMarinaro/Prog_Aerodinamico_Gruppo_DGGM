import os
import pandas as pd
import numpy as np
import math
import csv

def scegli_cartella(percorso):
    cartelle = [d for d in os.listdir(percorso) if os.path.isdir(os.path.join(percorso, d))]
    if not cartelle:
        print("Nessuna cartella trovata.")
        return None
    print("Cartelle disponibili:")
    for i, nome in enumerate(cartelle):
        print(f"{i+1}: {nome}")
    scelta = input("Seleziona il numero della cartella da analizzare: ")
    try:
        idx = int(scelta) - 1
        if 0 <= idx < len(cartelle):
            return cartelle[idx]
    except ValueError:
        pass
    print("Scelta non valida.")
    return None

def analizza_plot_csv(cartella_base):
    plot_path = os.path.join(cartella_base, "Plot")
    x_csv = os.path.join(plot_path, "X_Direction.csv")
    y_csv = os.path.join(plot_path, "Y_Direction.csv")
    if os.path.isfile(x_csv) and os.path.isfile(y_csv):
        try:
            x_df = pd.read_csv(x_csv)
            y_df = pd.read_csv(y_csv)
            y_pos = x_df.iloc[:, 0]
            vx = x_df.iloc[:, 1]
            vy = y_df.iloc[:, 1]
            theta = np.degrees(np.arctan2(vy, vx))
            min_idx = np.argmin(theta)
            min_theta = theta[min_idx]
            y_min = y_pos.iloc[min_idx]
            return {
                "tipo": "CSV",
                "min_theta": min_theta,
                "y_min": y_min,
                "dettaglio": ""
            }
        except Exception as e:
            return {
                "tipo": "CSV",
                "min_theta": "",
                "y_min": "",
                "dettaglio": f"Errore CSV: {e}"
            }
    return None

def analizza_plot_txt(cartella_base):
    plot_path = os.path.join(cartella_base, "Plot")
    x_file = os.path.join(plot_path, "X_Direction")
    y_file = os.path.join(plot_path, "Y_Direction")
    if os.path.isfile(x_file) and os.path.isfile(y_file):
        angoli = []
        with open(x_file) as xf, open(y_file) as yf:
            x_lines = xf.readlines()
            y_lines = yf.readlines()
            for i, (x, y) in enumerate(zip(x_lines, y_lines)):
                try:
                    x_val = float(x.strip())
                    y_val = float(y.strip())
                    angle_rad = math.atan2(y_val, x_val)
                    angle_deg = math.degrees(angle_rad)
                    angoli.append(angle_deg)
                except ValueError:
                    continue
        if angoli:
            min_theta = min(angoli)
            return {
                "tipo": "TXT",
                "min_theta": min_theta,
                "y_min": "",
                "dettaglio": ""
            }
    return None

def analizza_reports_txt(cartella_base):
    report_path = os.path.join(cartella_base, "Plot", "Reports.txt")
    if os.path.isfile(report_path):
        valori = {}
        with open(report_path, "r") as f:
            for line in f:
                if ":" in line:
                    key, value = line.split(":", 1)
                    valori[key.strip()] = value.strip()
        return valori
    return None

def analizza_tutte_cartelle(base_dir):
    risultati = []
    all_report_keys = set()
    temp_risultati = []

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        plot_path = os.path.join(folder_path, "Plot")
        if os.path.isdir(folder_path):
            risultato = None
            tipo = ""
            if os.path.isdir(plot_path):
                risultato = analizza_plot_csv(folder_path)
                if risultato:
                    tipo = risultato["tipo"]
                else:
                    risultato = analizza_plot_txt(folder_path)
                    if risultato:
                        tipo = risultato["tipo"]
            report_valori = analizza_reports_txt(folder_path)
            if risultato:
                r = {
                    "cartella": folder,
                    "min_theta": risultato["min_theta"],
                    "y_min": risultato["y_min"]
                }
            else:
                r = {
                    "cartella": folder,
                    "min_theta": "",
                    "y_min": ""
                }
            if report_valori:
                r.update(report_valori)
                all_report_keys.update(report_valori.keys())
            temp_risultati.append(r)
    # Ordina le colonne: fisse + tutte quelle trovate nei report
    fieldnames = ["cartella", "min_theta", "y_min"] + sorted(all_report_keys)
    for r in temp_risultati:
        for k in all_report_keys:
            if k not in r:
                r[k] = ""
        risultati.append(r)
    return risultati, fieldnames

if __name__ == "__main__":
    percorso = os.path.dirname(os.path.abspath(__file__))
    risultati, fieldnames = analizza_tutte_cartelle(percorso)
    output_csv = os.path.join(percorso, "risultati_deviazione.csv")
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in risultati:
            writer.writerow(r)
    print(f"\nRisultati salvati in '{output_csv}'.")