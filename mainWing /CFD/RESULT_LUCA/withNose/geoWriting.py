'''Questo script è pensato per usare python per scrivere un file .geo, in modo tale che la non abbia più
problemi a passare da un file .msh ad un .su2 e andare da un .geo ad un .su2 in modo più corretto.
Dato che voglio scrivere un file .geo, ha senso che prima di tutto tu ti assicuri che il nome che darai
al file non sia già in uso, altrimenti lo script non funzionerà, o meglio, darà errore.'''

import numpy as np
import os
import sys
import pandas as pd
from tkinter.filedialog import askopenfilename

# Richiedo all'utilizzatore il file .txt del profilo main e secondario
main = askopenfilename(title="Seleziona il file .txt del main", filetypes=[("Text files", "*.txt")])
secondary = askopenfilename(title="Seleziona il file .txt dell'ala secondaria",
                            filetypes=[("Text files", "*.txt")])
nose = askopenfilename(title="Seleziona il file .txt del naso",
                       filetypes=[("Text files", "*.txt")])

# Vado in dataframe per comodità nella manipolazione, dato che askopenfilename salva una tupla
dfMain = pd.read_csv(main, delim_whitespace=True, header=None, names=["x", "y", "z"])
dfSecondary = pd.read_csv(secondary, delim_whitespace=True, header=None, names=["x", "y", "z"])
dfNose = pd.read_csv(nose, delim_whitespace=True, header=None, names=["x", "y"])

# Chiedo all'utilizzatore il nome del file .geo da creare
nomeFileGeo = input("Inserisci il nome del file .geo da creare (senza estensione): ")

# Creo il file .geo
fileGeo = open(f"{nomeFileGeo}.geo", "x")

# Chiedo all'utilizzatore quanto vuole la rifinutura attorno al profilo
cl__1 = float(input("Inserisci la rifinutura attorno al profilo (cl__1): "))

# Stampo le info sulla grandezza della mesh nella prima riga del file .geo. Nota bene: il \n alla fine
# della stringa ti dice che dopo quello andrai a capo
with open(f"{nomeFileGeo}.geo", "w") as file:
    file.write("// Contenuto generato automaticamente da Python\n")

    file.write("\n")

    file.write(f"cl__1 = {cl__1};\n")

# Scrivo le coordinate del profilo principale, ma prima mi creo una variabile di servizio
servizio = 0
for i in range(len(dfMain)):

    x = dfMain["x"][i]
    y = dfMain["y"][i]

    # Incremento il valore della variabile di servizio
    servizio = servizio + 1

    # Scrivo le coordinate nel file .geo
    with open(f"{nomeFileGeo}.geo", "a") as file:
        file.write(f"Point({i+1}) = {{{x}, {y}, 0, cl__1}};\n")

servizio1 = 0
# Scrivo le coordinate del profilo secondario sfruttando la variabile di servizio
for i in range(len(dfSecondary)):

    x = dfSecondary["x"][i]
    y = dfSecondary["y"][i]

    # Incremento il valore della variabile di servizio
    servizio1 = servizio1 + 1

    # Scrivo le coordinate nel file .geo
    with open(f"{nomeFileGeo}.geo", "a") as file:
        file.write(f"Point({i+1+len(dfMain)}) = {{{x}, {y}, 0, cl__1}};\n")

for i in range(len(dfNose)):
    x = dfNose["x"][i]
    y = dfNose["y"][i]

    # Scrivo le coordinate nel file .geo
    with open(f"{nomeFileGeo}.geo", "a") as file:
        file.write(f"Point({i+1+len(dfSecondary)+len(dfMain)}) = {{{x}, {y}, 0, cl__1}};\n")

with open(f"{nomeFileGeo}.geo", "a") as file:
    file.write("\n")

# Scrivo con quali spline compongo i due profili e il naso
with open(f"{nomeFileGeo}.geo", "a") as file:
    file.write("Spline(1) = {")
    for i in range(len(dfMain) - 1):
        file.write(f"{i+1}, ")
    file.write(f"{len(dfMain)}, ")
    file.write("1")
    file.write("};\n")

with open(f"{nomeFileGeo}.geo", "a") as file:
    file.write("Spline(2) = {")
    for i in range(len(dfSecondary)):
        file.write(f"{i+1+len(dfMain)}, ")
    file.write(f"{servizio + 1}")
    file.write("};\n")

    file.write("\n")

with open(f"{nomeFileGeo}.geo", "a") as file:
    file.write("Spline(3) = {")
    for i in range(len(dfNose)):
        file.write(f"{i+1+len(dfMain)+len(dfSecondary)}, ")
    file.write(f"{servizio + servizio1 + 1}")
    file.write("};\n")

    file.write("\n") 

with open(f"{nomeFileGeo}.geo", "a") as file:
    file.write("Curve Loop(1) = {1};\n")
    file.write("Curve Loop(2) = {2};\n")
    file.write("Curve Loop(3) = {3};\n")

    file.write("\n")

# Definisco le dimensioni della galleria
# Lx = 4
# Ly = 1.25
# x0 = -0.5
# y0 = 0
# cl_far = 0.03
Lx, Ly = 10, 3
x0, y0 = -1.5, 0
cl_far = 0.3

# Inserisco nel file .geo i punti del farfield
with open(f"{nomeFileGeo}.geo", "a") as file:
    file.write("// Definizione farfield in senso antiorario\n")
    file.write(f"Point(1001) = {{{x0}, {y0}, 0, {cl_far}/100}}; // Bottom-Left\n")
    file.write(f"Point(1002) = {{{x0 + Lx}, {y0}, 0, {cl_far}/100}}; // Bottom-right\n")
    file.write(f"Point(1003) = {{{x0 + Lx}, {y0 + Ly}, 0, {cl_far}/7}}; // Top-Left\n")
    file.write(f"Point(1004) = {{{x0}, {y0 + Ly}, 0, {cl_far}/7}}; // Top-right\n")

    file.write("\n")

    file.write("// Definizione delle linee del farfield\n")
    file.write("Line(2001) = {1001, 1002};\n")
    file.write("Line(2002) = {1002, 1003};\n")
    file.write("Line(2003) = {1003, 1004};\n")
    file.write("Line(2004) = {1004, 1001};\n")

    file.write("\n")

    file.write("// Line Loop e superficie farfield (chiusa)\n")
    file.write("Curve Loop(3001) = {2001, 2002, 2003, 2004};\n")

    file.write("\n")


    # Definisco su che superficie sono sia i profili che il farfield, che è una superficie per tutti
    # e 3, dato che sono in 2D
    file.write("Plane Surface(1) = {3001, 1, 2, 3}; // Airfoils + Nose + Boundary\n")
    #file.write("Plane Surface(2) = {1, 2}; // Airfoils\n")

    file.write("\n")

    file.write("Physical Surface(1) = {1}; // Airfoils + Nose + Boundary\n")
    #file.write("Physical Surface(2) = {2}; // Farfield\n")

    file.write("\n")

    # Definisco i nomi delle superfici in modo che su2 le legga col config e imponga 
    # le condizioni al contorno

    file.write("// Definizione dei nomi delle superfici\n")
    file.write("Physical Line(\"Airfoil1\") = {1};\n")
    file.write("Physical Line(\"Airfoil2\") = {2};\n")
    file.write("Physical Line(\"Nose\") = {3};\n")
    file.write("Physical Line(\"inlet\") = {2004};\n")
    file.write("Physical Line(\"outlet\") = {2002};\n")
    file.write("Physical Line(\"bottom\") = {2001};\n")
    file.write("Physical Line(\"top\") = {2003};\n")

    file.write("\n")

    file.write("// Refinement box attorno ai profili\n")
    file.write("Field[1] = Distance;\n")
    file.write("Field[1].CurvesList = {1, 2};\n")  # Le curve sono i profili

    file.write("\n")

    file.write("// Threshold per la dimensione della mesh\n")
    file.write("Field[2] = Threshold;\n")
    file.write("Field[2].InField = 1;\n")
    file.write("Field[2].SizeMin = 0.1;\n")  # Dimensione minima della mesh
    file.write("Field[2].SizeMax = 0.3;\n")  # Dimensione massima della mesh
    file.write("Field[2].DistMin = 0.001;\n")  # Distanza minima per il threshold
    file.write("Field[2].DistMax = 0.01;\n")  # Distanza massima per il threshold

    file.write("\n")

    # file.write("// Refinement box grande attorno ai profili\n")
    # file.write("Field[3] = Box;\n")
    # file.write("Field[3].VIn = 0.001;\n")  # Velocità in entrata
    # file.write("Field[3].VOut = 0.01;\n")  # Velocità in uscita
    # file.write("Field[3].XMin = 0.10;\n")  # Coordinate del box
    # file.write("Field[3].XMax = 2.0;\n")  # Coordinate del box
    # file.write("Field[3].YMin = -0.1;\n")  # Coordinate del box
    # file.write("Field[3].YMax = 0.5;\n")  # Coordinate del box
    # file.write("Field[3].ZMin = -1;\n")  # Coordinate del box
    # file.write("Field[3].ZMax = 1;\n")  # Coordinate del box

    file.write("// Refinement box grande attorno ai profili\n")
    file.write("Field[3] = Box;\n")
    file.write("Field[3].VIn = 0.01;\n")  # Velocità in entrata
    file.write("Field[3].VOut = 0.1;\n")  # Velocità in uscita
    file.write("Field[3].XMin = 0;\n")  # Coordinate del box
    file.write("Field[3].XMax = 2.0;\n")  # Coordinate del box
    file.write("Field[3].YMin = 0;\n")  # Coordinate del box
    file.write("Field[3].YMax = 0.35;\n")  # Coordinate del box
    file.write("Field[3].ZMin = -1;\n")  # Coordinate del box
    file.write("Field[3].ZMax = 1;\n")  # Coordinate del box

    file.write("\n")

    file.write("// Background mesh\n")
    file.write("Background Field = 3;\n")

    # Inserisco il tipo di algoritmo per la mesh
    file.write("// Definizione del tipo di algoritmo per la mesh\n")
    file.write("Mesh.Algorithm = 2; // Automatic\n")

