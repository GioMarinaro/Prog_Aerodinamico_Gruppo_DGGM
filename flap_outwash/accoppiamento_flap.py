
import numpy as np
import matplotlib.pyplot as plt
import os
import csv

# --- Funzioni di utilità ---
def calculate_tangent(x, y, idx, window=3):
    start_idx = max(0, idx - window)
    end_idx = min(len(x), idx + window + 1)
    coeffs = np.polyfit(x[start_idx:end_idx], y[start_idx:end_idx], 1)
    return coeffs[0]

def plot_tangent_line(x_point, y_point, slope, length=0.1):
    x_line = np.array([x_point - length/2, x_point + length/2])
    y_line = slope * (x_line - x_point) + y_point
    return x_line, y_line

def rotate_profile(x, y, angle_rad, center_x=0, center_y=0):
    x = np.asarray(x)
    y = np.asarray(y)
    x_translated = x - center_x
    y_translated = y - center_y
    cos_theta = np.cos(angle_rad)
    sin_theta = np.sin(angle_rad)
    x_rot = x_translated * cos_theta - y_translated * sin_theta
    y_rot = x_translated * sin_theta + y_translated * cos_theta
    return x_rot + center_x, y_rot + center_y


# --- Parametri principali ---
scale_factor = 0.7  # Fattore di scala per il secondo flap

# --- Caricamento file profilo ---
profili_path = os.path.join(os.path.dirname(__file__), 'Profili')
if not os.path.exists(profili_path):
    os.makedirs(profili_path)
    print(f"Cartella 'Profili' creata in: {profili_path}")
    print("Inserisci i tuoi file .dat nella cartella appena creata")
    exit()

# Selezione del file profilo
dat_files = [f for f in os.listdir(profili_path) if f.endswith('.dat')]
if not dat_files:
    print("Nessun file .dat trovato nella cartella 'Profili'")
    exit()

print("File disponibili:")
for i, file in enumerate(dat_files):
    print(f"{i+1}. {file}")

# Input selezione file
while True:
    try:
        selection = int(input("\nSeleziona il numero del file da analizzare: ")) - 1
        if 0 <= selection < len(dat_files):
            selected_file = dat_files[selection]
            break
        print("Selezione non valida. Riprova.")
    except ValueError:
        print("Inserisci un numero valido.")

# Caricamento dati profilo 1
data1 = np.loadtxt(os.path.join(profili_path, selected_file))
x, y = data1[:, 0], data1[:, 1]

# --- Divisione dorso/ventre profilo 1 ---
idx_min = np.argmin(x)
x_us, y_us = x[:idx_min], y[:idx_min]  # Upper surface (dorso)
x_ls, y_ls = x[idx_min:], y[idx_min:]  # Lower surface (ventre)

# --- Selezione secondo file profilo ---
print("\nSeleziona il secondo file profilo (flap):")
for i, file in enumerate(dat_files):
    print(f"{i+1}. {file}")

while True:
    try:
        selection2 = int(input("\nSeleziona il numero del secondo file da analizzare: ")) - 1
        if 0 <= selection2 < len(dat_files):
            selected_file2 = dat_files[selection2]
            break
        print("Selezione non valida. Riprova.")
    except ValueError:
        print("Inserisci un numero valido.")

# Caricamento dati profilo 2 (flap)
data2 = np.loadtxt(os.path.join(profili_path, selected_file2))
x2, y2 = data2[:, 0], data2[:, 1]

# --- Divisione dorso/ventre profilo 2 ---
idx_min2 = np.argmin(x2)
x_us2, y_us2 = x2[:idx_min2], y2[:idx_min2]  # Upper surface (dorso)
x_ls2, y_ls2 = x2[idx_min2:], y2[idx_min2:]  # Lower surface (ventre)

# Profilo 2 scalato
x_us_scaled = x_us2 * scale_factor
y_us_scaled = y_us2 * scale_factor
x_ls_scaled = x_ls2 * scale_factor
y_ls_scaled = y_ls2 * scale_factor

# --- Input angolo di attacco ---
while True:
    try:
        alpha_deg = float(input("\nInserisci l'angolo di attacco del profilo originale (in gradi): "))
        alpha_rad = np.deg2rad(alpha_deg)
        break
    except ValueError:
        print("Inserisci un numero valido.")

# --- Rotazione profilo originale ---
x_rotated_orig, y_rotated_orig = rotate_profile(x, y, alpha_rad)
te_x, te_y = x_rotated_orig[0], y_rotated_orig[0]

# Ruota solo il dorso e il ventre separatamente
x_us_rotated, y_us_rotated = rotate_profile(x_us, y_us, alpha_rad)
x_ls_rotated, y_ls_rotated = rotate_profile(x_ls, y_ls, alpha_rad)

# --- Scegli il punto di riferimento a x = 20% della corda sul profilo scalato ---
x_ref_point_scaled = 0.2 * scale_factor
idx_us_ref_scaled = np.argmin(np.abs(x_us_scaled - x_ref_point_scaled))
x_us_ref_scaled = x_us_scaled[idx_us_ref_scaled]
y_us_ref_scaled = y_us_scaled[idx_us_ref_scaled]

# Calcola la tangente nel punto di riferimento sul profilo scalato
slope_at_us_ref_scaled = calculate_tangent(x_us_scaled, y_us_scaled, idx_us_ref_scaled)
x_tangent_ref_scaled, y_tangent_ref_scaled = plot_tangent_line(x_us_ref_scaled, y_us_ref_scaled, slope_at_us_ref_scaled, length=0.2)

# --- Calcola la tangente al dorso al TE del profilo originale ruotato ---
idx_te_us_rot = np.argmax(x_us_rotated)
slope_at_us_te_rotated = calculate_tangent(x_us_rotated, y_us_rotated, idx_te_us_rot)
x_te_us_rot = x_us_rotated[idx_te_us_rot]
y_te_us_rot = y_us_rotated[idx_te_us_rot]
x_tangent_us_te_rotated, y_tangent_us_te_rotated = plot_tangent_line(x_te_us_rot, y_te_us_rot, slope_at_us_te_rotated, length=0.2)

# --- Rendi le tangenti parallele ---
angle_ref_scaled = np.arctan(slope_at_us_ref_scaled)
angle_te_us_rotated = np.arctan(slope_at_us_te_rotated)
angle_between = angle_te_us_rotated - angle_ref_scaled

# Ruota tutto il profilo scalato e la sua tangente per rendere le tangenti parallele
x_us_scaled_rot, y_us_scaled_rot = rotate_profile(x_us_scaled, y_us_scaled, angle_between)
x_ls_scaled_rot, y_ls_scaled_rot = rotate_profile(x_ls_scaled, y_ls_scaled, angle_between)
x_tangent_ref_scaled_rot, y_tangent_ref_scaled_rot = rotate_profile(x_tangent_ref_scaled, y_tangent_ref_scaled, angle_between)
x_us_ref_scaled_rot, y_us_ref_scaled_rot = rotate_profile([x_us_ref_scaled], [y_us_ref_scaled], angle_between)

y_translation = y_te_us_rot - y_us_ref_scaled_rot[0]

# Applica la traslazione verticale al profilo scalato ruotato e ai relativi elementi
y_us_scaled_rot_aligned = y_us_scaled_rot + y_translation
y_ls_scaled_rot_aligned = y_ls_scaled_rot + y_translation
y_us_ref_scaled_rot_aligned = y_us_ref_scaled_rot[0] + y_translation
y_tangent_ref_scaled_rot_aligned = y_tangent_ref_scaled_rot + y_translation

# Le x restano invariate
x_us_scaled_rot_aligned = x_us_scaled_rot
x_ls_scaled_rot_aligned = x_ls_scaled_rot
x_us_ref_scaled_rot_aligned = x_us_ref_scaled_rot[0]
x_tangent_ref_scaled_rot_aligned = x_tangent_ref_scaled_rot

# --- Allineamento orizzontale: x del punto a 20% corda = x del TE originale ---
delta_x = x_te_us_rot - x_us_ref_scaled_rot[0]

# Applica la traslazione orizzontale al profilo scalato ruotato e ai relativi elementi
x_us_scaled_rot_aligned = x_us_scaled_rot_aligned + delta_x
x_ls_scaled_rot_aligned = x_ls_scaled_rot_aligned + delta_x
x_us_ref_scaled_rot_aligned = x_us_ref_scaled_rot_aligned + delta_x
x_tangent_ref_scaled_rot_aligned = x_tangent_ref_scaled_rot_aligned + delta_x

# Le y restano invariate dopo la traslazione verticale

# --- Allineamento verticale  per il secondo profilo ---
offset_y = -0.04 # scegli tu il valore, negativo = verso il basso

y_us_scaled_rot_aligned = y_us_scaled_rot_aligned + offset_y
y_ls_scaled_rot_aligned = y_ls_scaled_rot_aligned + offset_y
y_us_ref_scaled_rot_aligned = y_us_ref_scaled_rot_aligned + offset_y
y_tangent_ref_scaled_rot_aligned = y_tangent_ref_scaled_rot_aligned + offset_y

# --- Calcolo linea media del flap scalato, ruotato e traslato
if len(x_us_scaled_rot_aligned) == len(x_ls_scaled_rot_aligned):
    x_camber = (x_us_scaled_rot_aligned + x_ls_scaled_rot_aligned[::-1]) / 2
    y_camber = (y_us_scaled_rot_aligned + y_ls_scaled_rot_aligned[::-1]) / 2
else:
    # Interpola il ventre per avere lo stesso numero di punti del dorso
    from scipy.interpolate import interp1d
    f_x_ls = interp1d(np.linspace(0,1,len(x_ls_scaled_rot_aligned)), x_ls_scaled_rot_aligned, kind='linear')
    f_y_ls = interp1d(np.linspace(0,1,len(y_ls_scaled_rot_aligned)), y_ls_scaled_rot_aligned, kind='linear')
    s_us = np.linspace(0,1,len(x_us_scaled_rot_aligned))
    x_ls_interp = f_x_ls(s_us)
    y_ls_interp = f_y_ls(s_us)
    x_camber = (x_us_scaled_rot_aligned + x_ls_interp[::-1]) / 2
    y_camber = (y_us_scaled_rot_aligned + y_ls_interp[::-1]) / 2

# Calcola la derivata prima della linea media
dy_dx = np.gradient(y_camber, x_camber)


# 1. Trova l'indice della x massima (TE) sulla linea media
idx_te_camber = np.argmax(x_camber)
x_te_camber = x_camber[idx_te_camber]
y_te_camber = y_camber[idx_te_camber]

# 2. Calcola la derivata locale (tangente) in quel punto
if idx_te_camber == 0:
    # Se il TE è il primo punto, usa il secondo
    idx_next = 1
else:
    idx_next = idx_te_camber - 1

dx = x_camber[idx_te_camber] - x_camber[idx_next]
dy = y_camber[idx_te_camber] - y_camber[idx_next]
slope_te_camber = dy / dx if dx != 0 else np.sign(dy) * 1e6  # Evita divisione per zero

# 3. Calcola l'angolo rispetto all'orizzontale globale
angle_te_camber_rad = np.arctan(slope_te_camber)
angle_te_camber_deg = np.degrees(angle_te_camber_rad)
print(f"Angolo tangente linea media al TE rispetto all'orizzontale globale: {angle_te_camber_deg:.2f} gradi")


# Nel plot finale dei profili, aggiungi:
plt.figure(figsize=(10, 6))
plt.plot(np.concatenate([x_us_rotated, x_ls_rotated]), 
         np.concatenate([y_us_rotated, y_ls_rotated]), 
         'b-', label='Primo flap')
plt.plot(x_tangent_us_te_rotated, y_tangent_us_te_rotated, 'r--', 
         label='Tangente al dorso (TE)')
plt.plot(np.concatenate([x_us_scaled_rot_aligned, x_ls_scaled_rot_aligned]), 
         np.concatenate([y_us_scaled_rot_aligned, y_ls_scaled_rot_aligned]), 
         'c-', label='Secondo Flap')
plt.plot(x_us_ref_scaled_rot_aligned, y_us_ref_scaled_rot_aligned, 'mo', label='Punto a 20% corda')
plt.plot(x_tangent_ref_scaled_rot_aligned, y_tangent_ref_scaled_rot_aligned, 'm--', label='Tangente a 20%')
plt.axis('equal')
plt.grid(True)
plt.xlabel('x/c')
plt.ylabel('y/c')
plt.title(f'Accoppiamento Flap - Allineamento verticale su 20% corda')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# --- Salvataggio profili accoppiati ---
# Crea la cartella "CSV per simulazioni" dentro la cartella Sim_files (non più in profili)
simulazioni_path = os.path.join(os.path.dirname(profili_path), 'Sim_files')
csv_sim_folder = os.path.join(simulazioni_path, "CSV_txt_per_simulazioni")
os.makedirs(csv_sim_folder, exist_ok=True)

# Usa i nomi dei file .dat selezionati (senza estensione)
base1 = os.path.splitext(selected_file)[0]
base2 = os.path.splitext(selected_file2)[0]
output_folder = os.path.join(csv_sim_folder, f"{base1}__{base2}")
os.makedirs(output_folder, exist_ok=True)

# File di testo
output_file = os.path.join(output_folder, "profili_accoppiati.txt")
points = []

# Primo airfoil (profilo originale ruotato)
for xi, yi in zip(np.concatenate([x_us_rotated, x_ls_rotated]), np.concatenate([y_us_rotated, y_ls_rotated])):
    points.append(f"{xi:.8f},{yi:.8f},0.0")

# Secondo airfoil (profilo flap scalato, ruotato, traslato)
for xi, yi in zip(np.concatenate([x_us_scaled_rot_aligned, x_ls_scaled_rot_aligned]), np.concatenate([y_us_scaled_rot_aligned, y_ls_scaled_rot_aligned])):
    points.append(f"{xi:.8f},{yi:.8f},0.0")

# Salva il file di testo
with open(output_file, "w") as f:
    for line in points:
        f.write(line + "\n")

print(f"Punti dei due profili salvati in: {output_file}")

# File CSV senza intestazione
output_csv = os.path.join(output_folder, "profili_accoppiati.csv")
with open(output_csv, "w", newline='') as f_csv:
    writer = csv.writer(f_csv)
    for xi, yi in zip(np.concatenate([x_us_rotated, x_ls_rotated]), np.concatenate([y_us_rotated, y_ls_rotated])):
        writer.writerow([f"{xi:.8f}", f"{yi:.8f}", "0.0"])
    for xi, yi in zip(np.concatenate([x_us_scaled_rot_aligned, x_ls_scaled_rot_aligned]), np.concatenate([y_us_scaled_rot_aligned, y_ls_scaled_rot_aligned])):
        writer.writerow([f"{xi:.8f}", f"{yi:.8f}", "0.0"])

print(f"Punti dei due profili salvati anche in: {output_csv}")




