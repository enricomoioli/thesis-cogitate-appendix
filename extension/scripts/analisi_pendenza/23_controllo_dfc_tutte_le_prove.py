# -*- coding: utf-8 -*-
"""
23_controllo_dfc_tutte_le_prove.py

Controllo di correttezza (non un'analisi): la DFC media su tutte le prove calcolata
da synchrony_master_pendenza.py deve coincidere con quella del capitolo 4.
Confronta, per le due regioni, le quattro matrici cat1_to_cat1 ... cat2_to_cat2
e gli elenchi dei pazienti.
"""

from pathlib import Path
import numpy as np

CARTELLA = Path(r"E:\raw\ieeg_bids\derivatives\synchrony_analysis\sub-super\ses-1\ieeg\results"
                r"\category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"
                r"\desbadcharej_notfil_lapref")
BASE = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_"

for regione in ["iit", "gnw"]:
    cap4 = np.load(CARTELLA / (BASE + regione + "_dfc_tfr.npz"), allow_pickle=True)
    nuova = np.load(CARTELLA / (BASE + "pendenza_" + regione + "_dfc_tfr.npz"), allow_pickle=True)
    for chiave in ["cat1_to_cat1", "cat1_to_cat2", "cat2_to_cat1", "cat2_to_cat2"]:
        a, b = cap4[chiave], nuova[chiave]
        uguali = a.shape == b.shape and np.allclose(a, b, rtol=0, atol=1e-10)
        massima = np.abs(a - b).max() if a.shape == b.shape else np.nan
        print(f"{regione} {chiave}: forma {a.shape} contro {b.shape}, "
              f"differenza massima {massima:.2e}, uguali: {uguali}")
    for chiave in ["category_1_selective", "category_2_selective"]:
        print(f"{regione} {chiave}: stessi pazienti nello stesso ordine: "
              f"{list(cap4[chiave]) == list(nuova[chiave])}")
