''' In sostanza se noi importiamo dei file txt per definire il profilo, in questo modo si
può ottenere un dataframe con le coordinate e non un file di testo, in modo che se le coordinate
siano scritte con misure troppo piccole, come decimi di millimetro, si possa operare un
riscalamento globale del profilo, per non avere problemi su VSP.
Il nuovo file .dat viene salvato nella stessa cartella in cui tu lanci lo script python.
Il codice, tra le altre cose, prende anche i file .txt e li trasforma in .dat, quindi può
essere usato anche per quello, se non si vuole riscalare, si mette solo 1
È importante come il file che venga dato in input abbia soltanto numeri dentro, colonne coi
dati e non titoli o altre cose strane dentro, quelli vanno cancellati a priori.
Dato che su airfoiltools a volte i punti vanno dal bordo d'attacco al bordo d'uscita sul dorso 
e poi dal bordo d'attacco a quello d'uscita anche sul ventre, mentre altre volte invece seguono
una linea unica, devo mettere manualmente una richiesta all'utilizzatore se è il caso di
aggiustare questa cosa a mano oppure no.'''

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename

# Richiedi all'utilizzatore il percorso del file .txt
percorso = askopenfilename(title="Seleziona il file .txt", filetypes=[("Text files", "*.txt"), ("DAT files", "*.dat")])

# Mi salvo il nome del file, in modo da poterlo usare dopo
nomeProfilo = os.path.basename(percorso)
nomeProfilo, ext = os.path.splitext(nomeProfilo)

# Leggi il file .txt e trasformalo in un df
df = pd.read_csv(percorso, delim_whitespace=True, header=None, names=["x", "y", "z"])

# Elimino eventuali colonne di coordinate z che non servono
del df["z"]

# Chiedi all'utilizzatore di quanto vuole riscalare il profilo
riscalamento = float(input("Inserire riscalatura del profilo: "))

# Riscalamento effettivo del dataFrame
df = df*riscalamento

# Chiede all'utilizzatore se intende capovolgere il profilo
capovolgimento = input ("Vuoi capovolgere il profilo? [Y/n]: ")
if capovolgimento == "Y" or capovolgimento == "y":
    df["y"] = df["y"]*(-1)

# Verifica la lunghezza del file: deve essere pari
if len(df) % 2 != 0:
    raise ValueError("Il numero di righe nel file non è pari: controlla il file!")

# Parametri di rotazione
x0 = float(input("Inserisci x del polo di rotazione: "))
y0 = float(input("Inserisci y del polo di rotazione: "))
theta_deg = float(input("Inserisci angolo di rotazione in gradi (positivo = antiorario): "))
theta_rad = np.radians(theta_deg)

# Applica la rotazione a tutti i punti
x_shifted = df["x"] - x0
y_shifted = df["y"] - y0

x_rot = x0 + x_shifted * np.cos(theta_rad) - y_shifted * np.sin(theta_rad)
y_rot = y0 + x_shifted * np.sin(theta_rad) + y_shifted * np.cos(theta_rad)

# Aggiorna il dataframe
df["x"] = x_rot
df["y"] = y_rot

# Chiedo se è necessario fare il flip nel dizionario
necessaryFlip = int(input("Il profilo è definito con una linea ininterrotta di punti (1) oppure " \
    "dorso e ventre con due linee separate PARTENDO DAL LE AL TE (2)? :"))

if necessaryFlip == 2:
    # Divide in due metà
    n = len(df) // 2

    # Arrivato quì posso forzare la chiusura del profilo nel caso in cui debba flippare il dataframe
    if df.iloc[-1, 1] != df.iloc[n-1, 1]:
        df.iloc[-1, 1] = (df.iloc[n-1, 1] + df.iloc[-1, 1]) / 2
        df.iloc[-1, 0] = max(df.iloc[n-1, 0], df.iloc[-1, 0]) + 0.005*df.iloc[-1, 0]

    dorso = df.iloc[:n].copy()
    #ventre = ventre.iloc[::-1].reset_index(drop=True)
    ventre = df.iloc[n:].iloc[::-1].copy()  # inversione del ventre

    # Ricombina in un unico dataframe
    df_flipped = pd.concat([dorso, ventre], ignore_index=True)

# Se non dovessi flippare, perchè il file è già ordinato, comunque genero il df_flipped, perchè
# è un nome importante
if necessaryFlip == 1:
    df_flipped = df.copy()

# Chiede all'utilizzatore se intende effettuare una traslazione nello spazio del profilo
traslazione = input("Vuoi traslare il profilo nello spazio? [Y/n]: ")
if traslazione == "Y" or traslazione == "y":
    
    traslazione_X = float(input("Inserire la traslazione in x in metri (I.E. 160 mm = 0.160): "))
    traslazione_Y = float(input("Inserire la traslazione in y in metri: "))

    df_flipped["x"] = df_flipped["x"] + traslazione_X
    df_flipped["y"] = df_flipped["y"] + traslazione_Y

if traslazione == "n" or traslazione == "N":

    traslazione_X = 0
    traslazione_Y = 0

# Chiedo all'utilizzatore se vuole usare il file di output per xfoil oppure per gmsh, perchè se
# lo usa per gmsh devo aggiungere una colonna z
input_gmsh = input("Vuoi usare il file di output per xfoil o per gmsh? (xfoil/gmsh): ")
if input_gmsh.lower() == "gmsh":
    # Aggiungo una colonna z con valore 0.0
    df_flipped["z"] = 0.0

plt.plot(df_flipped["x"], df_flipped["y"], 'b-', label='Punti Originali')
plt.axis('equal')
plt.show()

# Chiede all'utilizzatore cosa intenda fare per il nome
ask4Name = input("Intendi usare lo stesso nome per il profilo? [Y/n] :")

if ask4Name == "Y" or ask4Name == "y":
    nuovoNome = nomeProfilo
else:
    nuovoNome = input("Inserire nuovo nome del file .txt, senza scrivere .txt, " \
                    "solo il nome: ")

# Riporta il file in .dat
df_flipped.to_csv(f"{nuovoNome}_ruotato.txt", sep=" ", index=False, header=False)
