#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_sintesi_tabella_sincronia.py

Estrae dai file .npz del consorzio, per ciascuna regione e categoria, tutto cio'
che serve alle tabelle del cap. 4: elettrodi selettivi, pazienti, p minimo,
percentuale di celle significative, banda di frequenza e finestre temporali
dei cluster (tempi in cui almeno una frequenza e' significativa), e direzione
dell'effetto (preferita - altra) dentro le celle significative.

Convenzione degli indici (synchrony_master.py): secondo indice = categoria
letterale del trial (1 = volti, 2 = oggetti). Trial preferiti: cat1_to_cat1 per
gli elettrodi-volti, cat2_to_cat2 per gli elettrodi-oggetti.

Uso (ambiente cogitate_ecog):
    python D:\\TESI\\manoscritto\\cap4\\scripts\\03_sintesi_tabella_sincronia.py NOME_ANALISI
"""
import sys
from pathlib import Path
import numpy as np

BASE = Path(r"E:\raw\ieeg_bids\derivatives\synchrony_analysis\sub-super\ses-1\ieeg\results")
PREPROC = "desbadcharej_notfil_lapref"
PREFIX = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_"


def finestre_contigue(tempi, attive):
    finestre, inizio = [], None
    for i, a in enumerate(attive):
        if a and inizio is None:
            inizio = i
        if (not a or i == len(attive) - 1) and inizio is not None:
            fine = i if a else i - 1
            finestre.append((tempi[inizio], tempi[fine]))
            inizio = None
    return finestre


def main():
    nome = sys.argv[1]
    for roi, nome_roi in (("gnw", "Prefrontale"), ("iit", "Visiva")):
        percorso = sorted((BASE / nome / PREPROC).glob("{0}{1}_*.npz".format(PREFIX, roi)))[0]
        d = np.load(percorso, allow_pickle=True)
        tempi = np.asarray(d["analysis_time"])
        freqs = np.asarray(d["freqs"])
        pannelli = [
            ("volti", d["cat1_to_cat1"], d["cat1_to_cat2"], d["p_values_fac_selective"], d["category_1_selective"]),
            ("oggetti", d["cat2_to_cat2"], d["cat2_to_cat1"], d["p_values_obj_selective"], d["category_2_selective"]),
        ]
        for cat, a, b, p, elenco in pannelli:
            a, b, p = np.asarray(a), np.asarray(b), np.asarray(p)
            nomi = [str(x) for x in np.asarray(elenco)]
            pazienti = len({x.split("-")[0] for x in nomi})
            sig = p < 0.05
            print("\n{0}, {1}: {2} elettrodi, {3} pazienti".format(nome_roi, cat, a.shape[0], pazienti))
            if not sig.any():
                print("   nessuna cella significativa")
                continue
            diff = a.mean(0) - b.mean(0)
            f_sig = freqs[sig.any(axis=1)]
            fin = finestre_contigue(tempi, sig.any(axis=0))
            print("   p minimo {0:.5f} | celle sig. {1}/{2} ({3:.1f}%) | banda {4:.0f}-{5:.0f} Hz".format(
                p.min(), sig.sum(), sig.size, 100 * sig.mean(), f_sig.min(), f_sig.max()))
            print("   finestre: " + "; ".join("{0:.2f}-{1:.2f} s".format(x, y) for x, y in fin))
            print("   direzione nelle celle sig.: media {0:+.5f}, celle positive {1:.1f}%".format(
                diff[sig].mean(), 100 * (diff[sig] > 0).mean()))


if __name__ == "__main__":
    main()
