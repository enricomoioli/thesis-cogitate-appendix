# -*- coding: utf-8 -*-
"""
22_statistica_pendenza.py

Chapter 5, version with continuous LZC (preregistration
extension/preregistrazione_cap5_pendenza.md, 29 October 2026).

Reads the slopes of DFC on standardized pre-stimulus LZC produced by
synchrony_master_pendenza.py (files ..._pendenza.npz) and, for each selective
electrode, computes the slope in face trials minus the slope in object trials.
On this difference: cluster test as in chapter 4 (with a fixed seed) in the
four sets, then the same with the patient as unit.

Cells to run in order in Spyder.
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
INIZIO = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_pendenza_"
USCITA = Path(r"D:\TESI\manoscritto\extension\results\pendenza")
N_PERMUTAZIONI = 1024
P_CLUSTER = 0.05
SEME = 0

dati = {}
for regione in ["iit", "gnw"]:
    dati[regione] = np.load(CARTELLA / (INIZIO + regione + "_dfc_tfr_pendenza.npz"), allow_pickle=True)

print(list(dati["gnw"].keys()))
print(dati["gnw"]["categories"])          # expected: ['face' 'object']

# %% Cell 2: modulation of the category effect
def modulazione(d, cat):
    """cat = "1" (face-selective electrodes) or "2" (object-selective).
    Slope in face trials minus slope in object trials.
    Returns electrodes x frequencies x time."""
    return d["pendenza_cat" + cat + "_to_cat1"] - d["pendenza_cat" + cat + "_to_cat2"]

prova = modulazione(dati["gnw"], "1")
print(prova.shape, "nan:", np.isnan(prova).sum())

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
    print(f"{nome}: {n} unita', p minimo {p_caselle.min():.5f}, "
          f"celle significative {100 * significative.mean():.2f}%")
    if significative.any():
        righe, colonne = np.where(significative)
        print(f"   frequenze {frequenze[righe].min():.0f}-{frequenze[righe].max():.0f} Hz, "
              f"tempo {tempi[colonne].min():.2f}-{tempi[colonne].max():.2f} s")
    return p_caselle

tempi = dati["gnw"]["analysis_time"]
frequenze = dati["gnw"]["freqs"]

INSIEMI = [("iit", "V1/V2", "1", "volti"), ("iit", "V1/V2", "2", "oggetti"),
           ("gnw", "prefrontale", "1", "volti"), ("gnw", "prefrontale", "2", "oggetti")]

# %% Cell 4: main test, four sets (unit = electrode)
risultati = {}
for regione, nome_regione, cat, nome_cat in INSIEMI:
    nome = nome_regione + ", elettrodi selettivi per " + nome_cat
    risultati[(regione, cat)] = test_cluster(modulazione(dati[regione], cat), nome, tempi, frequenze)

# %% Cell 5: sign in the sets with a cluster (descriptive)
# Values computed inside the cluster, so they describe the direction, they do not confirm it.
for regione, nome_regione, cat, nome_cat in INSIEMI:
    cluster = risultati[(regione, cat)] < 0.05
    if not cluster.any():
        continue
    d = dati[regione]
    pend_volti = d["pendenza_cat" + cat + "_to_cat1"][:, cluster].mean()
    pend_oggetti = d["pendenza_cat" + cat + "_to_cat2"][:, cluster].mean()
    per_elettrodo = modulazione(d, cat)[:, cluster].mean(axis=1)
    print(f"{nome_regione}, selettivi per {nome_cat}: pendenza nelle prove con volti {pend_volti:.4f}, "
          f"con oggetti {pend_oggetti:.4f}, differenza {pend_volti - pend_oggetti:.4f}")
    print(f"   elettrodi con differenza positiva: {(per_elettrodo > 0).sum()} su {len(per_elettrodo)}")

# %% Cell 6: patient-level check (direction and consistency)
def media_per_paziente(differenza, pazienti):
    pazienti = np.asarray(pazienti)
    elenco = np.unique(pazienti)
    return np.stack([differenza[pazienti == p].mean(axis=0) for p in elenco]), elenco

for regione, nome_regione, cat, nome_cat in INSIEMI:
    d = dati[regione]
    per_paziente, elenco = media_per_paziente(modulazione(d, cat), d["category_" + cat + "_selective"])
    test_cluster(per_paziente, nome_regione + ", " + nome_cat + " (per paziente)", tempi, frequenze)
    cluster = risultati[(regione, cat)] < 0.05
    if cluster.any():
        nel_cluster = per_paziente[:, cluster].mean(axis=1)
        print("   nel cluster degli elettrodi:", dict(zip(elenco, np.round(nel_cluster, 4))))
        print(f"   pazienti con differenza positiva: {(nel_cluster > 0).sum()} su {len(elenco)}")

# %% Cell 7: saving the results
da_salvare = {"tempi": tempi, "frequenze": frequenze}
riepilogo = []
for regione, nome_regione, cat, nome_cat in INSIEMI:
    d = dati[regione]
    chiave = regione + "_cat" + cat
    da_salvare[chiave + "_pendenza_volti"] = d["pendenza_cat" + cat + "_to_cat1"].mean(axis=0)
    da_salvare[chiave + "_pendenza_oggetti"] = d["pendenza_cat" + cat + "_to_cat2"].mean(axis=0)
    da_salvare[chiave + "_modulazione"] = modulazione(d, cat).mean(axis=0)
    da_salvare[chiave + "_p"] = risultati[(regione, cat)]
    riepilogo.append({"regione": regione, "selettivi_per": d["categories"][int(cat) - 1],
                      "elettrodi": d["pendenza_cat" + cat + "_to_cat1"].shape[0],
                      "pazienti": len(np.unique(d["category_" + cat + "_selective"])),
                      "p_minimo": risultati[(regione, cat)].min(),
                      "celle_significative_pct": 100 * (risultati[(regione, cat)] < 0.05).mean()})
np.savez(USCITA / "statistica_pendenza.npz", **da_salvare)
pd.DataFrame(riepilogo).to_csv(USCITA / "statistica_pendenza_riepilogo.csv", index=False)
print(pd.DataFrame(riepilogo))
