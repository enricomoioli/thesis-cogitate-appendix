# -*- coding: utf-8 -*-
"""
08_figura_profili_spettrali.py

Figure 4.4 of the thesis: spectral profiles of the connectivity difference
(DFC) between face trials and object trials, for the four sets of figure 4.3
(07_figura_sincronia_sintesi.py). It has no equivalent in the paper: it shows
in which frequency band each effect is concentrated.

Same conventions as figure 4.3:
- 2 x 2 layout: top V1/V2 (iit), bottom prefrontal (gnw);
  left face-selective electrodes, right object-selective;
- sign faces MINUS objects for both columns (as in the paper): for
  object-selective electrodes an effect in favour of the preferred
  category is negative.
For each frequency: mean of the difference between 0 and 1.5 s per electrode,
then mean and standard error across electrodes. Theory colours from the common
style (IIT blue, GNW red); grey lines at the band boundaries
(8, 13, 30, 70, 150 Hz). Same vertical scale in the four panels.

Reads only the .npz files produced by synchrony_master.py. Requires drive E:.

Output: figure_tesi\\output\\cap4\\sincronia_profili.png / .pdf

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\08_figura_profili_spettrali.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stile_tesi import (COLORI, GRIGIO_MEDIO, GRIGIO_CHIARO, applica_stile, virgola_decimale,
                        lettera, salva)

ANALISI = "category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"
CARTELLA_DATI = (Path(r"E:\raw\ieeg_bids\derivatives\synchrony_analysis\sub-super\ses-1\ieeg\results")
                 / ANALISI / "desbadcharej_notfil_lapref")
PREFISSO = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_"
USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\cap4\sincronia_profili")

FINESTRA_PROFILO = (0.0, 1.5)
CONFINI_BANDE = (8, 13, 30, 70, 150)
# text magnification factor: in the PDF the figure is shrunk to the
# page width, so the text must be enlarged accordingly
SCALA = 1.25
DIMENSIONE_TITOLI = 10 * SCALA
# Vertical scale computed on frequencies >= 8 Hz only: below that, estimates are
# unstable (large standard error) and would squash the rest. The low stretch
# that goes off scale is cut and declared in the caption.
FREQ_MIN_SCALA = 8

PANNELLI = [(0, 0, "iit", "volti", "V1/V2, selettivi per i volti"),
            (0, 1, "iit", "oggetti", "V1/V2, selettivi per gli oggetti"),
            (1, 0, "gnw", "volti", "Prefrontale, selettivi per i volti"),
            (1, 1, "gnw", "oggetti", "Prefrontale, selettivi per gli oggetti")]


def carica(roi):
    candidati = sorted(CARTELLA_DATI.glob("{0}{1}_*.npz".format(PREFISSO, roi)))
    if not candidati:
        raise FileNotFoundError("Nessun file per la ROI {0} in {1}".format(roi, CARTELLA_DATI))
    return np.load(candidati[0], allow_pickle=True)


def volti_meno_oggetti(dati, categoria):
    """Consortium indices: second index = trial category (1 = faces, 2 = objects)."""
    if categoria == "volti":
        return np.asarray(dati["cat1_to_cat1"]) - np.asarray(dati["cat1_to_cat2"])
    return np.asarray(dati["cat2_to_cat1"]) - np.asarray(dati["cat2_to_cat2"])


def main():
    dati = {roi: carica(roi) for roi in ("iit", "gnw")}
    applica_stile()
    matplotlib.rcParams.update({"font.size": 10 * SCALA, "axes.labelsize": 10 * SCALA, "xtick.labelsize": 9 * SCALA,
                                "ytick.labelsize": 9 * SCALA, "legend.fontsize": 9 * SCALA})
    fig, assi = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True, sharey=True)
    lettere = iter("ABCD")
    massimo = 0.0

    for riga, colonna, roi, categoria, titolo in PANNELLI:
        d = dati[roi]
        tempi = np.asarray(d["analysis_time"])
        freqs = np.asarray(d["freqs"])
        diff = volti_meno_oggetti(d, categoria)
        n = diff.shape[0]
        finestra = (tempi >= FINESTRA_PROFILO[0]) & (tempi <= FINESTRA_PROFILO[1])
        per_elettrodo = diff[:, :, finestra].mean(2)          # electrodes x frequencies
        profilo = per_elettrodo.mean(0)
        sem = per_elettrodo.std(0, ddof=1) / np.sqrt(n)

        asse = assi[riga, colonna]
        for f in CONFINI_BANDE:
            asse.axvline(f, color=GRIGIO_CHIARO, linewidth=0.8, zorder=0)
        asse.axhline(0, color=GRIGIO_MEDIO, linestyle="--", linewidth=0.8)
        asse.fill_between(freqs, profilo - sem, profilo + sem, color=COLORI[roi], alpha=0.25, linewidth=0)
        asse.plot(freqs, profilo, color=COLORI[roi], linewidth=1.5)
        sopra = freqs >= FREQ_MIN_SCALA
        massimo = max(massimo, np.abs(profilo[sopra]).max() + sem[sopra].max())
        lettera(asse, next(lettere), "{0}\n{1} elettrodi".format(titolo, n))
        asse.title.set_fontsize(DIMENSIONE_TITOLI)
        if riga == 1:
            asse.set_xlabel("Frequenza (Hz)")
        if colonna == 0:
            asse.set_ylabel("\u0394DFC (volti \u2212 oggetti), 0\u20131,5 s")
        virgola_decimale(asse)

    limite = np.ceil(massimo * 1.1 * 1000) / 1000
    assi[0, 0].set_ylim(-limite, limite)  # shared axes: applies to all panels
    fig.tight_layout(h_pad=2.0, w_pad=1.5)
    salva(fig, USCITA)


if __name__ == "__main__":
    main()
