# -*- coding: utf-8 -*-
"""
19a - Elettrodi selettivi per paziente (serie definitiva _v1v2d del cap. 4).

Solo lettura. Serve a scegliere il paziente su cui esplorare la LZC pre-stimolo.
Legge i due file *_electrodes.tar.gz (ROI iit e gnw) salvati da synchrony_master.py:
sono DataFrame pandas in pickle gzip, con colonne
channels, ch_types, x, y, z, roi_pick, face, object
(roi_pick = destinazioni; face/object = sorgenti selettive).

Uso (prompt con l'ambiente cogitate_ecog o l'installer MNE):
    python 19a_elettrodi_selettivi_per_paziente.py
"""
from pathlib import Path
import pandas as pd

CARTELLA = Path(r"E:/raw/ieeg_bids/derivatives/synchrony_analysis/sub-super/ses-1/ieeg/results/"
                r"category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d/"
                r"desbadcharej_notfil_lapref")

righe = []
for roi in ["iit", "gnw"]:
    f = CARTELLA / f"sub-super_ses-1_task-Dur_ana-synchrony_analysis_{roi}_dfc_tfr_electrodes.tar.gz"
    df = pd.read_pickle(f, compression="gzip")
    print(f"\n=== {roi}: {len(df)} righe; colonne: {list(df.columns)}")
    print("Esempi di nomi di canale:", df["channels"].head(5).tolist())
    df["roi"] = roi
    righe.append(df)

tutti = pd.concat(righe, ignore_index=True)
# il paziente e' il prefisso del nome di canale (formato da verificare nell'output sopra)
tutti["paziente"] = tutti["channels"].astype(str).str.split("-").str[0]

sorgenti = tutti[(tutti["face"] == True) | (tutti["object"] == True)]
sorgenti = sorgenti.drop_duplicates(subset=["channels"])
tab = sorgenti.groupby("paziente").agg(volti=("face", "sum"), oggetti=("object", "sum"))
tab["totale"] = tab["volti"] + tab["oggetti"]
print("\n=== Elettrodi selettivi (sorgenti) per paziente, ordinati ===")
print(tab.sort_values("totale", ascending=False).to_string())
