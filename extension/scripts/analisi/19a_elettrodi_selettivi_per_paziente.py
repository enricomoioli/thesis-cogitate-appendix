# -*- coding: utf-8 -*-
"""
19a - Selective electrodes per patient (final _v1v2d series of chapter 4).

Read only. Used to choose the patient on which to explore pre-stimulus LZC.
Reads the two *_electrodes.tar.gz files (ROI iit and gnw) saved by synchrony_master.py:
they are pandas DataFrames in gzip pickle, with columns
channels, ch_types, x, y, z, roi_pick, face, object
(roi_pick = targets; face/object = selective sources).

Usage (prompt with the cogitate_ecog environment or the MNE installer):
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
# the patient is the prefix of the channel name (format to be checked in the output above)
tutti["paziente"] = tutti["channels"].astype(str).str.split("-").str[0]

sorgenti = tutti[(tutti["face"] == True) | (tutti["object"] == True)]
sorgenti = sorgenti.drop_duplicates(subset=["channels"])
tab = sorgenti.groupby("paziente").agg(volti=("face", "sum"), oggetti=("object", "sum"))
tab["totale"] = tab["volti"] + tab["oggetti"]
print("\n=== Elettrodi selettivi (sorgenti) per paziente, ordinati ===")
print(tab.sort_values("totale", ascending=False).to_string())
