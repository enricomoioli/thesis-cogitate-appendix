# -*- coding: utf-8 -*-
"""
19c - Exploration of pre-stimulus LZC in ALL patients with selective electrodes.

Purpose: decide whether to split the trials by electrode (as Li et al. 2020) or by
patient (mean LZC of the patient's selective electrodes). Looks ONLY at LZC, never
at the DFC.

For each patient:
  1. runs script 19b (same LZC, same trials, same exclusions), saving its output
     in a log file;
  2. from the trial-by-trial table of 19b computes the correlation (Spearman) of
     LZC between each pair of the patient's selective electrodes, on the trials
     NOT excluded: if it is high, the electrodes "go up and down together"
     (shared state); if it is low, each electrode has its own state.
     The correlation is also reported separately for pairs with the same
     preference (faces-faces, objects-objects) and with different preference
     (as Li et al. 2020).

At the end it saves and prints a summary table.

Usage (cogitate_ecog prompt, from the script folder):
    python 19c_esplora_lzc_tutti_i_pazienti.py
"""
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

QUI = Path(__file__).resolve().parent
RISULTATI = Path(r"D:/TESI/manoscritto/extension/results/esplorazione_lzc")
CARTELLA_EL = Path(r"E:/raw/ieeg_bids/derivatives/synchrony_analysis/sub-super/ses-1/ieeg/results/"
                   r"category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d/"
                   r"desbadcharej_notfil_lapref")

# ---------------------------------------------------------------- patients with selective electrodes
el = pd.concat([pd.read_pickle(CARTELLA_EL / f"sub-super_ses-1_task-Dur_ana-synchrony_analysis_{r}_dfc_tfr_electrodes.tar.gz",
                               compression="gzip") for r in ["iit", "gnw"]])
el = el[(el["face"] == True) | (el["object"] == True)].drop_duplicates(subset=["channels"])
pazienti = sorted(el["channels"].astype(str).str.split("-").str[0].unique())
print(f"Pazienti con elettrodi selettivi: {len(pazienti)}")

# ---------------------------------------------------------------- 1. 19b on each patient
for i, paz in enumerate(pazienti, 1):
    log = RISULTATI / f"log_19b_{paz}.txt"
    log.parent.mkdir(parents=True, exist_ok=True)
    print(f"[{i}/{len(pazienti)}] {paz} ...", end=" ", flush=True)
    r = subprocess.run([sys.executable, str(QUI / "19b_esplora_lzc_prestimolo.py"), paz],
                       cwd=str(QUI), capture_output=True, text=True)
    log.write_text(r.stdout + "\n" + r.stderr, encoding="utf-8")
    print("ok" if r.returncode == 0 else f"ERRORE (vedi {log.name})")

# ---------------------------------------------------------------- 2. summary and correlations between electrodes
righe = []
for paz in pazienti:
    f_prove = RISULTATI / paz / f"{paz}_lzc_prestimolo.csv"
    f_ries = RISULTATI / paz / f"{paz}_riepilogo_elettrodi.csv"
    if not (f_prove.exists() and f_ries.exists()):
        righe.append(dict(paziente=paz, nota="manca l'uscita del 19b"))
        continue
    prove = pd.read_csv(f_prove)
    ries = pd.read_csv(f_ries)
    tenute = prove[~prove["esclusa"]]
    tab = tenute.pivot_table(index="prova", columns="canale", values="lzc")
    pref = prove.drop_duplicates("canale").set_index("canale")["preferenza"]

    stessa, diversa = [], []
    for a, b in combinations(tab.columns, 2):
        rho = tab[a].corr(tab[b], method="spearman")
        (stessa if pref[a] == pref[b] else diversa).append(rho)
    tutte = stessa + diversa

    righe.append(dict(
        paziente=paz,
        elettrodi=tab.shape[1],
        prove_totali=prove["prova"].nunique(),
        quota_escluse=prove.drop_duplicates("prova")["esclusa"].mean(),
        rho_ordine_mediana=ries["rho_lzc_ordine"].median(),
        rho_alfa_mediana=ries["rho_lzc_alfa"].median(),
        pareggi_mediana=ries["quota_pareggi_mediana"].median(),
        coppie=len(tutte),
        corr_fra_elettrodi=np.median(tutte) if tutte else np.nan,
        corr_stessa_pref=np.median(stessa) if stessa else np.nan,
        corr_pref_diversa=np.median(diversa) if diversa else np.nan,
    ))

R = pd.DataFrame(righe)
R.to_csv(RISULTATI / "riepilogo_tutti_i_pazienti.csv", index=False)
pd.set_option("display.width", 200)
print("\n=== Riepilogo per paziente (correlazioni: mediana fra coppie di elettrodi) ===")
print(R.round(2).to_string(index=False))

conCoppie = R.dropna(subset=["corr_fra_elettrodi"]) if "corr_fra_elettrodi" in R else R
print(f"\nPazienti con almeno due elettrodi: {len(conCoppie)}")
print(f"Correlazione fra elettrodi, mediana fra pazienti: {conCoppie['corr_fra_elettrodi'].median():.2f} "
      f"(min {conCoppie['corr_fra_elettrodi'].min():.2f}, max {conCoppie['corr_fra_elettrodi'].max():.2f})")
print(f"Stessa preferenza: {conCoppie['corr_stessa_pref'].median():.2f}; "
      f"preferenza diversa: {conCoppie['corr_pref_diversa'].median():.2f}")
print(f"Prove escluse (mediana): {R['quota_escluse'].median():.0%}; "
      f"rho con l'ordine (mediana): {R['rho_ordine_mediana'].median():.2f}; "
      f"rho con l'alfa (mediana): {R['rho_alfa_mediana'].median():.2f}; "
      f"pareggi (mediana): {R['pareggi_mediana'].median():.0%}")
print(f"Uscite in {RISULTATI}")
