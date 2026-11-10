# -*- coding: utf-8 -*-
"""
21 - Statistics of chapter 5: high versus low pre-stimulus state.

Reads the DFC split into high and low LZC trials (synchrony_master_stato.py) and the
trial assignment of script 20; computes, for each selective electrode, the difference
between the category effect in the high and in the low state, runs the cluster test
as in chapter 4 on the four sets, then the patient-level check, the alpha control and
the check for contamination from the previous trial. Saves the results.

Cells to run in order in Spyder. Created on 29 October 2026.
"""

# %% Cell 1: paths and loading
from pathlib import Path
import numpy as np
import pandas as pd
import mne
from scipy import stats

CARTELLA = Path(r"E:\raw\ieeg_bids\derivatives\synchrony_analysis\sub-super\ses-1\ieeg\results"
                r"\category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"
                r"\desbadcharej_notfil_lapref")
INIZIO = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_stato_"
N_PERMUTAZIONI = 1024
P_CLUSTER = 0.05
SEME = 0

dati = {}
for regione in ["iit", "gnw"]:
    dati[regione] = np.load(CARTELLA / (INIZIO + regione + "_dfc_tfr_alto_basso.npz"), allow_pickle=True)

print(list(dati["gnw"].keys()))
print(dati["gnw"]["categories"])

# %% Cell 2: difference between high and low state in the category effect
def differenza_alto_basso(d, cat):
    """cat = "1" (face-selective electrodes) or "2" (object-selective).
    Returns electrodes x frequencies x time."""
    effetto_alto = d["alto_cat" + cat + "_to_cat1"] - d["alto_cat" + cat + "_to_cat2"]
    effetto_basso = d["basso_cat" + cat + "_to_cat1"] - d["basso_cat" + cat + "_to_cat2"]
    return effetto_alto - effetto_basso

prova = differenza_alto_basso(dati["gnw"], "1")
print(prova.shape)

# %% Cell 3: cluster test (as in chapter 4, with a fixed seed)
def test_cluster(differenza, nome, tempi, frequenze):
    n = differenza.shape[0]
    soglia = stats.t.ppf(1 - P_CLUSTER / 2, df=n - 1)
    t_oss, cluster, p_cluster, _ = mne.stats.permutation_cluster_1samp_test(
        differenza, n_permutations=N_PERMUTAZIONI, threshold=soglia,
        tail=0, seed=SEME, verbose=False)
    p_caselle = np.ones_like(t_oss)
    for c, p in zip(cluster, p_cluster):
        p_caselle[c] = p
    significative = p_caselle < 0.05
    print(f"{nome}: {n} elettrodi, p minimo {p_caselle.min():.5f}, "
          f"celle significative {100 * significative.mean():.1f}%")
    if significative.any():
        righe, colonne = np.where(significative)
        print(f"   frequenze {frequenze[righe].min():.0f}-{frequenze[righe].max():.0f} Hz, "
              f"tempo {tempi[colonne].min():.2f}-{tempi[colonne].max():.2f} s")
    return p_caselle

tempi = dati["gnw"]["analysis_time"]
frequenze = dati["gnw"]["freqs"]

# %% Cell 4: main test, four sets
risultati = {}
for regione, nome_regione in [("iit", "V1/V2"), ("gnw", "prefrontale")]:
    for cat, nome_cat in [("1", "volti"), ("2", "oggetti")]:
        nome = nome_regione + ", elettrodi selettivi per " + nome_cat
        differenza = differenza_alto_basso(dati[regione], cat)
        risultati[(regione, cat)] = test_cluster(differenza, nome, tempi, frequenze)
        
        # %% Cell 5: sign of the cluster (V1/V2, object-selective electrodes)
d = dati["iit"]
cluster = risultati[("iit", "2")] < 0.05          # cells of the cluster
effetto_alto = d["alto_cat2_to_cat1"] - d["alto_cat2_to_cat2"]
effetto_basso = d["basso_cat2_to_cat1"] - d["basso_cat2_to_cat2"]

media_alto = effetto_alto[:, cluster].mean()       # mean over electrodes and cells
media_basso = effetto_basso[:, cluster].mean()
per_elettrodo = (effetto_alto - effetto_basso)[:, cluster].mean(axis=1)

print(f"effetto (volti - oggetti) nel cluster: alto {media_alto:.4f}, basso {media_basso:.4f}")
print(f"differenza alto - basso: {media_alto - media_basso:.4f}")
print(f"elettrodi con differenza negativa: {(per_elettrodo < 0).sum()} su {len(per_elettrodo)}")

# %% Cell 6: patient-level check
def media_per_paziente(differenza, pazienti):
    pazienti = np.asarray(pazienti)
    elenco = np.unique(pazienti)
    return np.stack([differenza[pazienti == p].mean(axis=0) for p in elenco]), elenco

for regione, nome_regione in [("iit", "V1/V2"), ("gnw", "prefrontale")]:
    for cat, nome_cat in [("1", "volti"), ("2", "oggetti")]:
        d = dati[regione]
        differenza = differenza_alto_basso(d, cat)
        per_paziente, elenco = media_per_paziente(differenza, d["category_" + cat + "_selective"])
        nome = nome_regione + ", " + nome_cat + " (per paziente)"
        test_cluster(per_paziente, nome, tempi, frequenze)
        if (regione, cat) == ("iit", "2"):
            nel_cluster = per_paziente[:, risultati[("iit", "2")] < 0.05].mean(axis=1)
            print("   nel cluster degli elettrodi:", dict(zip(elenco, np.round(nel_cluster, 4))))
            print(f"   pazienti con differenza positiva: {(nel_cluster > 0).sum()} su {len(elenco)}")
            
            # %% Cell 7: alpha control (descriptive)
tabella = pd.read_csv(r"D:\TESI\manoscritto\extension\results\stato_prestimolo\assegnazione_prove.csv")
tabella = tabella[tabella["stato"].isin(["alto", "basso"])]

alfa = tabella.groupby(["canale", "categoria", "stato"])["alfa_log10"].mean().unstack("stato")
alfa["differenza"] = alfa["alto"] - alfa["basso"]

def riassunto_alfa(differenze, nome):
    print(f"{nome}: {len(differenze)} elettrodo x categoria, "
          f"mediana alto - basso {differenze.median():.3f} (log10), "
          f"alfa piu' bassa nello stato alto: {100 * (differenze < 0).mean():.0f}%")

riassunto_alfa(alfa["differenza"], "tutti")
oggetti_v1v2 = alfa.loc[alfa.index.get_level_values("canale").isin(dati["iit"]["seed_cat2"]), "differenza"]
riassunto_alfa(oggetti_v1v2, "V1/V2, selettivi per oggetti")

# %% Cell 8: exploratory check, contamination from the previous trial
tenute = tabella[np.isfinite(tabella["distanza_spegnimento"])]
gruppi = tenute.groupby(["canale", "categoria"])
rho = gruppi.apply(lambda x: stats.spearmanr(x["distanza_spegnimento"], x["lzc"])[0]).dropna()
print(f"Spearman LZC ~ distanza dallo spegnimento: mediana {rho.median():.3f}, "
      f"negativi {100 * (rho < 0).mean():.0f}%, Wilcoxon p {stats.wilcoxon(rho).pvalue:.2f}")
for stato in ["alto", "basso"]:
    print(f"distanza mediana, stato {stato}: "
          f"{tenute.loc[tenute['stato'] == stato, 'distanza_spegnimento'].median():.2f} s")
    
    # %% Cell 9: saving the results
USCITA = Path(r"D:\TESI\manoscritto\extension\results\stato_prestimolo")
da_salvare = {"tempi": tempi, "frequenze": frequenze}
riepilogo = []
for regione in ["iit", "gnw"]:
    for cat in ["1", "2"]:
        d = dati[regione]
        alto = d["alto_cat" + cat + "_to_cat1"] - d["alto_cat" + cat + "_to_cat2"]
        basso = d["basso_cat" + cat + "_to_cat1"] - d["basso_cat" + cat + "_to_cat2"]
        chiave = regione + "_cat" + cat
        da_salvare[chiave + "_alto"] = alto.mean(axis=0)
        da_salvare[chiave + "_basso"] = basso.mean(axis=0)
        da_salvare[chiave + "_differenza"] = (alto - basso).mean(axis=0)
        da_salvare[chiave + "_p"] = risultati[(regione, cat)]
        riepilogo.append({"regione": regione, "selettivi_per": d["categories"][int(cat) - 1],
                          "elettrodi": alto.shape[0],
                          "pazienti": len(np.unique(d["category_" + cat + "_selective"])),
                          "p_minimo": risultati[(regione, cat)].min(),
                          "celle_significative_pct": 100 * (risultati[(regione, cat)] < 0.05).mean()})
np.savez(USCITA / "statistica_alto_basso.npz", **da_salvare)
pd.DataFrame(riepilogo).to_csv(USCITA / "statistica_alto_basso_riepilogo.csv", index=False)
print(pd.DataFrame(riepilogo))