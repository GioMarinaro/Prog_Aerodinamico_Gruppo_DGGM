import pandas as pd 
import matplotlib.pyplot as plt 
from tkinter import Tk, filedialog 
import numpy as np
from matplotlib.lines import Line2D


# selezione del file .csv 
Tk().withdraw()
df = filedialog.askopenfilename(title="Seleziona il CSV con cui lavorare", filetypes=[("CSV file", "*.csv")])

if not df:
    raise ValueError("\n Nessun file selezionato. Uscita.")

print(f"\n File selezionato: {df}")

dfRisultati = pd.read_csv(df, usecols=["Configurazione", "CL", "Cd"], index_col="Configurazione") #usiamo Configurazione come indice

#separiamo i casi con e senza naso 

filt_naso = dfRisultati.index.str.contains(r'(?:_si_naso|_naso)$', case=False) & \
            (~dfRisultati.index.str.contains(r'(?:_no_naso)$', case=False))

df_naso = dfRisultati.loc[filt_naso].copy()
df_nonaso = dfRisultati.loc[~filt_naso].copy()

#manipolazione dei dati: 

df_naso["CL"] = df_naso["CL"]
df_naso = df_naso[df_naso["Cd"]>0]

df_nonaso["CL"] = df_nonaso["CL"]
df_nonaso = df_nonaso[ (df_nonaso["Cd"]>0) & (df_nonaso["CL"]<2)] 
# nella configurazione senza naso usiamo un filtro più stringete per eliminare i dati spuri che alterano il risultato della funzione


print("\n anteprima del dataframe con il naso:")
print(df_naso.head())

print("\n anteprima del dataframe senza naso: ")
print(df_nonaso.head())

def funzione_multi_obj(df, N_alpha):
    Cd = df["Cd"]
    Cl = df["CL"]

    # Normalizzazione con direzioni corrette
    Cd_norm = 1 - (Cd - Cd.min()) / (Cd.max() - Cd.min())  # più basso = meglio
    Cl_eff = -Cl   # deportanza: CL negativo → positivo
    Cl_norm = (Cl_eff - Cl_eff.min()) / (Cl_eff.max() - Cl_eff.min())  # più grande = meglio

    pick = []
    alphas = np.linspace(0, 1, N_alpha)

    for a in alphas:
        J = a * Cl_norm + (1 - a) * Cd_norm
        J_opt = J.idxmax()  # ora restituisce il massimo "buono"
        pick.append((J_opt, a, df.loc[J_opt, "Cd"], df.loc[J_opt, "CL"], J.loc[J_opt]))

    Pareto = (
        pd.DataFrame(pick, columns=["Configurazione", "alpha", "Cd", "CL", "J"])
        .set_index("Configurazione")
        .sort_values(by=["Cd", "CL"], ascending=[True, False])
    )
    return Pareto

Fronte_Pareto_naso = funzione_multi_obj(df_naso,20)
Fronte_Pareto_nonaso = funzione_multi_obj(df_nonaso,20)

def plot_con_numeri_e_legenda(df_all, fronte, titolo,
                              punto_all_color="blue", punto_all_edge="k",
                              punto_front_color="red", punto_front_edge="k"):
    """
    df_all: dataframe con tutti i punti (index = Configurazione, colonne Cd, CL)
    fronte: dataframe risultato della funzione_multi_obj (index = Configurazione, colonne Cd, CL, ...)
    titolo: titolo del grafico
    """

    plt.figure(figsize=(12, 7))

    # scatter veloce di tutti i punti (senza etichetta per non duplicare la legenda)
    plt.scatter(df_all["Cd"], df_all["CL"], color=punto_all_color,
                edgecolor=punto_all_edge, s=40, alpha=0.4, label="_nolegend_")

    # evidenzio i punti che fanno parte del fronte (sopra allo scatter)
    if not fronte.empty:
        plt.scatter(fronte["Cd"], fronte["CL"], color=punto_front_color,
                    edgecolor=punto_front_edge, s=80, zorder=5, label="_nolegend_")
        plt.plot(fronte["Cd"], fronte["CL"], '-', color=punto_front_color, linewidth=2, zorder=4)

    # calcolo piccoli offset per posizionare i numeri (proporzionale all'intervallo)
    dx = (df_all["Cd"].max() - df_all["Cd"].min()) * 0.005
    dy = (df_all["CL"].max() - df_all["CL"].min()) * 0.015

    # enumerazione e annotazione dei punti (numero vicino al punto)
    # uso l'ordine di df_all per il numbering
    labels_map = []   # lista (i, config) per costruire la legenda
    for i, (config, row) in enumerate(df_all.iterrows(), start=1):
        x = row["Cd"]
        y = row["CL"]
        # posiziona il numero con un piccolo offset
        plt.text(x + dx, y + dy, str(i), fontsize=8, ha="left", va="bottom")
        labels_map.append((i, config))

    # Costruisco i manici (handles) per la legenda: prima la linea del fronte, poi i mapping numero->config
    legend_handles = []

    # handle per la linea del fronte
    if not fronte.empty:
        legend_handles.append(Line2D([0], [0], color=punto_front_color, lw=2, label="Fronte di Pareto"))

    # creo handles per ogni punto (mappa numero -> configurazione)
    # i punti appartenenti al fronte avranno il marker rosso, gli altri grigio
    fronte_set = set(fronte.index) if not fronte.empty else set()
    for i, config in labels_map:
        color = punto_front_color if config in fronte_set else punto_all_color
        handle = Line2D([0], [0], marker='o', color='w',
                        markerfacecolor=color, markeredgecolor='k', markersize=6,
                        label=f"{i}: {config}")
        legend_handles.append(handle)

    # mostro la legenda a destra (puoi regolare fontsize o ncol)
    plt.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
               fontsize=8, frameon=True)

    plt.xlabel("$C_D$")
    plt.ylabel("$C_L$")
    plt.title(titolo)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# --- Esempio di utilizzo per il Naso ---
plot_con_numeri_e_legenda(df_naso, Fronte_Pareto_naso, "Fronte di Pareto - Configurazioni con Naso")

# --- E per il No Naso (se vuoi mostrarlo dopo) ---
plot_con_numeri_e_legenda(df_nonaso, Fronte_Pareto_nonaso, "Fronte di Pareto - Configurazioni senza Naso")


#esportazione dei dati 
df_naso.to_csv("DataFrame_muso.csv")
df_nonaso.to_csv("DataFrame_Nomuso.csv")
Fronte_Pareto_naso.to_csv("Fronte_Pareto_muso.csv")
Fronte_Pareto_nonaso.to_csv("Fronte_Pareto_nomuso.csv")