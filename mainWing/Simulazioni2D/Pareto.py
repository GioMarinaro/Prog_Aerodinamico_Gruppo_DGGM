import pandas as pd 
import matplotlib.pyplot as plt 
from tkinter import Tk, filedialog 
import numpy as np
plt.style.use('fivethirtyeight')

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

def funzione_multi_obj(df, N_alpha=20):
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


Fronte_Pareto_naso = funzione_multi_obj(df_naso,100)
Fronte_Pareto_nonaso = funzione_multi_obj(df_nonaso,100)

# plot naso

plt.figure()
plt.scatter(df_naso["Cd"], df_naso["CL"], alpha=0.3, label='tutte le configurazioni')
plt.plot(Fronte_Pareto_naso["Cd"], Fronte_Pareto_naso["CL"], 'o-', label='Fronte di pareto')
plt.xlabel('Cd')
plt.ylabel('Cl')
plt.title('Fronte di pareto con funzione multi-obiettivo J = alpha*f1 + (1-alpha)*f2')
#plt.gca().invert_yaxis()
plt.grid(True)
plt.legend()
plt.show()

# plot no naso

plt.figure()
plt.scatter(df_nonaso["Cd"], df_nonaso["CL"], alpha=0.3, label='tutte le configurazioni')
plt.plot(Fronte_Pareto_nonaso["Cd"], Fronte_Pareto_nonaso["CL"], 'o-', label='Fronte di pareto')
plt.xlabel('Cd')
plt.ylabel('Cl')
plt.title('Fronte di pareto con funzione multi-obiettivo J = alpha*f1 + (1-alpha)*f2 (No Naso)')
#plt.gca().invert_yaxis()
plt.grid(True)
plt.legend()
plt.show()

#esportazione dei dati 
df_naso.to_csv("DataFrame_Naso.csv")
df_nonaso.to_csv("DataFrame_NoNaso.csv")
Fronte_Pareto_naso.to_csv("Fronte_Pareto_naso.csv")
Fronte_Pareto_nonaso.to_csv("Fronte_Pareto_nonaso.csv")
















