# -*- coding: utf-8 -*-
"""
07_figura_sincronia_sintesi.py

Figura 4.3 della tesi: equivalente della figura 4a dell'articolo COGITATE
(Nature 2025), ridisegnata con i dati di questa riproduzione e con lo stile
comune (stile_tesi.py).

Allineata al paper (21 ottobre):
- disposizione 2 x 2: riga in alto regione V1/V2 (iit), in basso regione
  prefrontale (gnw); colonna a sinistra elettrodi selettivi per i volti, a
  destra selettivi per gli oggetti;
- segno come nel paper e nel codice del consorzio: per entrambe le colonne
  la differenza e' prove con volti MENO prove con oggetti. Per gli elettrodi
  selettivi per gli oggetti un effetto a favore della categoria preferita
  compare quindi negativo (blu);
- scala di colore fissa e comune a tutti i pannelli, da -0,05 a +0,05
  (come nel paper); i valori oltre sono saturati;
- asse del tempo da -0,5 a 2,0 s, come nel paper;
- celle significative (p < 0,05, dal file del consorzio, test di cluster
  sulla differenza) contornate. Il test non dipende dal segno.

Sola lettura dei .npz prodotti da synchrony_master.py. Richiede il disco E:.

Output: figure_tesi\\output\\cap4\\sincronia_sintesi.png / .pdf

Uso:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\07_figura_sincronia_sintesi.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stile_tesi import (GRIGIO_SCURO, MAPPA_DIVERGENTE, applica_stile, virgola_decimale,
                        virgola_barra_colore, lettera, salva)

ANALISI = "category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"  # ROI iit V1/V2 Destrieux: calcarino, cuneo, linguale, polo occipitale (20 ottobre)
CARTELLA_DATI = (Path(r"E:\raw\ieeg_bids\derivatives\synchrony_analysis\sub-super\ses-1\ieeg\results")
                 / ANALISI / "desbadcharej_notfil_lapref")
PREFISSO = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_"
USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\cap4\sincronia_sintesi")

FINESTRA_TEMPO = (-0.5, 2.0)   # come nel paper
LIMITE_SCALA = 0.05            # scala fissa comune, come nel paper

# (riga, colonna, roi, categoria degli elettrodi, titolo)
PANNELLI = [(0, 0, "iit", "volti", "V1/V2, selettivi per i volti"),
            (0, 1, "iit", "oggetti", "V1/V2, selettivi per gli oggetti"),
            (1, 0, "gnw", "volti", "Prefrontale, selettivi per i volti"),
            (1, 1, "gnw", "oggetti", "Prefrontale, selettivi per gli oggetti")]
# fattore di ingrandimento del testo: nel PDF la figura viene ridotta alla
# larghezza della pagina, quindi il testo va ingrandito di conseguenza
SCALA = 1.25
DIMENSIONE_TITOLI = 10 * SCALA


def carica(roi):
    candidati = sorted(CARTELLA_DATI.glob("{0}{1}_*.npz".format(PREFISSO, roi)))
    if not candidati:
        raise FileNotFoundError("Nessun file per la ROI {0} in {1}".format(roi, CARTELLA_DATI))
    return np.load(candidati[0], allow_pickle=True)


def volti_meno_oggetti(dati, categoria):
    """Indici del consorzio: secondo indice = categoria del trial (1 = volti, 2 = oggetti).
    Per entrambe le categorie di elettrodi restituisce prove con volti meno prove con oggetti."""
    if categoria == "volti":
        diff = np.asarray(dati["cat1_to_cat1"]) - np.asarray(dati["cat1_to_cat2"])
        p = np.asarray(dati["p_values_fac_selective"])
        pazienti = np.asarray(dati["category_1_selective"])
    else:
        diff = np.asarray(dati["cat2_to_cat1"]) - np.asarray(dati["cat2_to_cat2"])
        p = np.asarray(dati["p_values_obj_selective"])
        pazienti = np.asarray(dati["category_2_selective"])
    return diff, p, len({str(x) for x in pazienti})


def main():
    dati = {roi: carica(roi) for roi in ("iit", "gnw")}
    applica_stile()
    matplotlib.rcParams.update({"font.size": 10 * SCALA, "axes.labelsize": 10 * SCALA, "xtick.labelsize": 9 * SCALA,
                                "ytick.labelsize": 9 * SCALA, "legend.fontsize": 9 * SCALA})
    fig, assi = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    lettere = iter("ABCD")
    mappa = None

    for riga, colonna, roi, categoria, titolo in PANNELLI:
        d = dati[roi]
        tempi = np.asarray(d["analysis_time"])
        freqs = np.asarray(d["freqs"])
        diff, p, n_pazienti = volti_meno_oggetti(d, categoria)
        n_elettrodi = diff.shape[0]
        finestra = (tempi >= FINESTRA_TEMPO[0]) & (tempi <= FINESTRA_TEMPO[1])
        t = tempi[finestra]
        media = diff.mean(0)[:, finestra]
        sig = (p < 0.05)[:, finestra]

        asse = assi[riga, colonna]
        mappa = asse.pcolormesh(t, freqs, media, cmap=MAPPA_DIVERGENTE, vmin=-LIMITE_SCALA,
                                vmax=LIMITE_SCALA, shading="auto", rasterized=True)
        if sig.any():
            asse.contour(t, freqs, sig, levels=[0.5], colors=GRIGIO_SCURO, linewidths=0.7)
        asse.axvline(0, color=GRIGIO_SCURO, linestyle="--", linewidth=0.8)
        for lato in ("top", "right"):
            asse.spines[lato].set_visible(True)  # le mappe restano incorniciate
        lettera(asse, next(lettere), "{0}\n{1} elettrodi, {2} pazienti".format(titolo, n_elettrodi, n_pazienti))
        asse.title.set_fontsize(DIMENSIONE_TITOLI)
        if riga == 1:
            asse.set_xlabel("Tempo dall'accensione (s)")
        if colonna == 0:
            asse.set_ylabel("Frequenza (Hz)")
        virgola_decimale(asse)

    fig.tight_layout(rect=(0, 0, 0.88, 1), h_pad=2.0, w_pad=1.5)
    asse_barra = fig.add_axes((0.91, 0.25, 0.02, 0.5))
    barra = fig.colorbar(mappa, cax=asse_barra)
    barra.set_label("\u0394DFC (volti \u2212 oggetti)")
    virgola_barra_colore(barra)
    salva(fig, USCITA)


if __name__ == "__main__":
    main()
