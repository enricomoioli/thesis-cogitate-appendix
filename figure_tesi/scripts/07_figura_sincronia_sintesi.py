# -*- coding: utf-8 -*-
"""
07_figura_sincronia_sintesi.py

Figure 4.3 of the thesis: equivalent of figure 4a of the COGITATE article
(Nature 2025), redrawn with the data of this reproduction and with the common
style (stile_tesi.py).

Aligned with the paper (21 October):
- 2 x 2 layout: top row V1/V2 region (iit), bottom row prefrontal region
  (gnw); left column face-selective electrodes, right column
  object-selective;
- sign as in the paper and in the consortium code: for both columns the
  difference is face trials MINUS object trials. For object-selective
  electrodes an effect in favour of the preferred category therefore
  appears negative (blue);
- fixed colour scale, common to all panels, from -0.05 to +0.05
  (as in the paper); values beyond are saturated;
- time axis from -0.5 to 2.0 s, as in the paper;
- significant cells (p < 0.05, from the consortium file, cluster test on
  the difference) outlined. The test does not depend on the sign.

Reads only the .npz files produced by synchrony_master.py. Requires drive E:.

Output: figure_tesi\\output\\cap4\\sincronia_sintesi.png / .pdf

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\07_figura_sincronia_sintesi.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stile_tesi import (GRIGIO_SCURO, MAPPA_DIVERGENTE, applica_stile, virgola_decimale,
                        virgola_barra_colore, lettera, salva)

ANALISI = "category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"  # iit ROI V1/V2 Destrieux: calcarine, cuneus, lingual, occipital pole (20 October)
CARTELLA_DATI = (Path(r"E:\raw\ieeg_bids\derivatives\synchrony_analysis\sub-super\ses-1\ieeg\results")
                 / ANALISI / "desbadcharej_notfil_lapref")
PREFISSO = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_"
USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\cap4\sincronia_sintesi")

FINESTRA_TEMPO = (-0.5, 2.0)   # as in the paper
LIMITE_SCALA = 0.05            # fixed common scale, as in the paper

# (row, column, roi, electrode category, title)
PANNELLI = [(0, 0, "iit", "volti", "V1/V2, selettivi per i volti"),
            (0, 1, "iit", "oggetti", "V1/V2, selettivi per gli oggetti"),
            (1, 0, "gnw", "volti", "Prefrontale, selettivi per i volti"),
            (1, 1, "gnw", "oggetti", "Prefrontale, selettivi per gli oggetti")]
# text magnification factor: in the PDF the figure is shrunk to the
# page width, so the text must be enlarged accordingly
SCALA = 1.25
DIMENSIONE_TITOLI = 10 * SCALA


def carica(roi):
    candidati = sorted(CARTELLA_DATI.glob("{0}{1}_*.npz".format(PREFISSO, roi)))
    if not candidati:
        raise FileNotFoundError("Nessun file per la ROI {0} in {1}".format(roi, CARTELLA_DATI))
    return np.load(candidati[0], allow_pickle=True)


def volti_meno_oggetti(dati, categoria):
    """Consortium indices: second index = trial category (1 = faces, 2 = objects).
    For both electrode categories returns face trials minus object trials."""
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
            asse.spines[lato].set_visible(True)  # the maps keep their frame
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
