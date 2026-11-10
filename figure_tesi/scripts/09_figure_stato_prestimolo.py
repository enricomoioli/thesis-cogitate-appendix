# -*- coding: utf-8 -*-
"""
09_figure_stato_prestimolo.py

Figures of chapter 5 (pre-stimulus state and selective connectivity), with the
same style and convention as figure 4.3 (07_figura_sincronia_sintesi.py).

Figure 5.1: difference between trials with high and low pre-stimulus LZC in the
category effect (faces minus objects) on the time-frequency plane, averaged
across selective electrodes; 2 x 2 layout as in figure 4.3 (rows: V1/V2 and
prefrontal; columns: face-selective and object-selective). Cells of the
significant cluster (p < 0.05) outlined.

Figure 5.2: V1/V2 only, object-selective electrodes: category effect with
low LZC, with high LZC and their difference, with the cluster outlined in all
three panels.

Fixed scale from -0.05 to +0.05 as in figure 4.3 (values beyond saturated);
time axis from -0.5 to 2.0 s.

Reads only the results of script 21
(extension\\results\\stato_prestimolo\\statistica_alto_basso.npz and
statistica_alto_basso_riepilogo.csv).

Output: figure_tesi\\output\\cap5\\stato_differenza.png/.pdf and
        figure_tesi\\output\\cap5\\stato_v1v2_oggetti.png/.pdf

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\09_figure_stato_prestimolo.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stile_tesi import (GRIGIO_SCURO, MAPPA_DIVERGENTE, applica_stile, virgola_decimale,
                        virgola_barra_colore, lettera, salva)

RISULTATI = Path(r"D:\TESI\manoscritto\extension\results\stato_prestimolo")
USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\cap5")

FINESTRA_TEMPO = (-0.5, 2.0)   # as in figure 4.3
LIMITE_SCALA = 0.05            # as in figure 4.3
# text magnification factor: in the PDF the figure is shrunk to the
# page width, so the text must be enlarged accordingly
SCALA = 1.25
DIMENSIONE_TITOLI = 10 * SCALA

# (row, column, key in the file, region, category in the summary, title)
PANNELLI = [(0, 0, "iit_cat1", "iit", "face", "V1/V2, selettivi per i volti"),
            (0, 1, "iit_cat2", "iit", "object", "V1/V2, selettivi per gli oggetti"),
            (1, 0, "gnw_cat1", "gnw", "face", "Prefrontale, selettivi per i volti"),
            (1, 1, "gnw_cat2", "gnw", "object", "Prefrontale, selettivi per gli oggetti")]


def mappa(asse, t, freqs, valori, significative):
    m = asse.pcolormesh(t, freqs, valori, cmap=MAPPA_DIVERGENTE, vmin=-LIMITE_SCALA,
                        vmax=LIMITE_SCALA, shading="auto", rasterized=True)
    if significative.any():
        asse.contour(t, freqs, significative, levels=[0.5], colors=GRIGIO_SCURO, linewidths=0.9)
    asse.axvline(0, color=GRIGIO_SCURO, linestyle="--", linewidth=0.8)
    for lato in ("top", "right"):
        asse.spines[lato].set_visible(True)  # the maps keep their frame
    virgola_decimale(asse)
    return m


def barra_colore(fig, m, etichetta):
    asse_barra = fig.add_axes((0.91, 0.25, 0.02, 0.5))
    barra = fig.colorbar(m, cax=asse_barra)
    barra.set_label(etichetta)
    virgola_barra_colore(barra)


def main():
    d = np.load(RISULTATI / "statistica_alto_basso.npz")
    riepilogo = pd.read_csv(RISULTATI / "statistica_alto_basso_riepilogo.csv")
    tempi = d["tempi"]
    freqs = d["frequenze"]
    finestra = (tempi >= FINESTRA_TEMPO[0]) & (tempi <= FINESTRA_TEMPO[1])
    t = tempi[finestra]
    applica_stile()
    matplotlib.rcParams.update({"font.size": 10 * SCALA, "axes.labelsize": 10 * SCALA, "xtick.labelsize": 9 * SCALA,
                                "ytick.labelsize": 9 * SCALA, "legend.fontsize": 9 * SCALA})

    # Figure 5.1: high - low difference, four sets
    fig, assi = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    lettere = iter("ABCD")
    for riga, colonna, chiave, regione, categoria, titolo in PANNELLI:
        info = riepilogo[(riepilogo["regione"] == regione) & (riepilogo["selettivi_per"] == categoria)].iloc[0]
        asse = assi[riga, colonna]
        m = mappa(asse, t, freqs, d[chiave + "_differenza"][:, finestra],
                  (d[chiave + "_p"] < 0.05)[:, finestra])
        lettera(asse, next(lettere), "{0}\n{1} elettrodi, {2} pazienti".format(
            titolo, int(info["elettrodi"]), int(info["pazienti"])))
        asse.title.set_fontsize(DIMENSIONE_TITOLI)
        if riga == 1:
            asse.set_xlabel("Tempo dall'accensione (s)")
        if colonna == 0:
            asse.set_ylabel("Frequenza (Hz)")
    fig.tight_layout(rect=(0, 0, 0.88, 1), h_pad=2.0, w_pad=1.5)
    barra_colore(fig, m, "\u0394DFC (volti \u2212 oggetti), alta \u2212 bassa")
    salva(fig, USCITA / "stato_differenza")

    # Figure 5.2: V1/V2, object-selective: low, high, difference
    fig, assi = plt.subplots(1, 3, figsize=(10.5, 3.8), sharex=True, sharey=True)
    cluster = (d["iit_cat2_p"] < 0.05)[:, finestra]
    for asse, lett, chiave, titolo in zip(
            assi, "ABC",
            ["iit_cat2_basso", "iit_cat2_alto", "iit_cat2_differenza"],
            ["LZC pre-stimolo bassa", "LZC pre-stimolo alta", "Alta \u2212 bassa"]):
        m = mappa(asse, t, freqs, d[chiave][:, finestra], cluster)
        lettera(asse, lett, titolo)
        asse.title.set_fontsize(DIMENSIONE_TITOLI)
        asse.set_xlabel("Tempo dall'accensione (s)")
    assi[0].set_ylabel("Frequenza (Hz)")
    fig.tight_layout(rect=(0, 0, 0.89, 1), w_pad=1.5)
    barra_colore(fig, m, "\u0394DFC (volti \u2212 oggetti)")
    salva(fig, USCITA / "stato_v1v2_oggetti")


if __name__ == "__main__":
    main()
