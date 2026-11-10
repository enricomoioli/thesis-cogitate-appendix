# -*- coding: utf-8 -*-
"""
12_figure_pendenza.py

Figures of chapter 5, version with continuous LZC (slope), with the same style
and layout as 09_figure_stato_prestimolo.py.

Figure A: modulation of the category effect (slope of DFC on standardized LZC in
face trials minus that in object trials), averaged across selective electrodes;
2 x 2 layout as in figure 4.3. Cells of the significant cluster (p < 0.05)
outlined.

Figure B: V1/V2 only, object-selective electrodes: slope in face trials, in object
trials and their difference, with the cluster outlined.

Slopes have a different unit from DFC (change in DFC per standard deviation of
LZC): the scale (LIMITE_SCALA) is set here, not taken from figure 4.3.

It also prints how many separate pieces (connected components on the
time-frequency plane) make up the significant cells of each set.

Reads only the results of script 22 (extension\\results\\pendenza\\).
Output: figure_tesi\\output\\cap5_pendenza\\pendenza_modulazione.png/.pdf and
        figure_tesi\\output\\cap5_pendenza\\pendenza_v1v2_oggetti.png/.pdf

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\12_figure_pendenza.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stile_tesi import (GRIGIO_SCURO, MAPPA_DIVERGENTE, applica_stile, virgola_decimale,
                        virgola_barra_colore, lettera, salva)

RISULTATI = Path(r"D:\TESI\manoscritto\extension\results\pendenza")
USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\cap5_pendenza")

FINESTRA_TEMPO = (-0.5, 2.0)   # as in figure 4.3
LIMITE_SCALA = 0.02            # slopes: own scale, to be reviewed by looking at the figure
DIMENSIONE_TITOLI = 10

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
    d = np.load(RISULTATI / "statistica_pendenza.npz")
    riepilogo = pd.read_csv(RISULTATI / "statistica_pendenza_riepilogo.csv")
    tempi = d["tempi"]
    freqs = d["frequenze"]
    finestra = (tempi >= FINESTRA_TEMPO[0]) & (tempi <= FINESTRA_TEMPO[1])
    t = tempi[finestra]
    applica_stile()

    # how many separate pieces make up the significant cells (whole plane)
    for _, _, chiave, _, _, titolo in PANNELLI:
        significative = d[chiave + "_p"] < 0.05
        etichette, n_pezzi = ndimage.label(significative)
        if n_pezzi:
            print(f"{titolo}: {n_pezzi} pezzi")
            for k in range(1, n_pezzi + 1):
                righe, colonne = np.where(etichette == k)
                print(f"   pezzo {k}: {len(righe)} celle, {freqs[righe].min():.0f}-{freqs[righe].max():.0f} Hz, "
                      f"{tempi[colonne].min():.2f}-{tempi[colonne].max():.2f} s, "
                      f"p {d[chiave + '_p'][righe[0], colonne[0]]:.4f}")

    # Figure A: modulation, four sets
    fig, assi = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    lettere = iter("ABCD")
    for riga, colonna, chiave, regione, categoria, titolo in PANNELLI:
        info = riepilogo[(riepilogo["regione"] == regione) & (riepilogo["selettivi_per"] == categoria)].iloc[0]
        asse = assi[riga, colonna]
        m = mappa(asse, t, freqs, d[chiave + "_modulazione"][:, finestra],
                  (d[chiave + "_p"] < 0.05)[:, finestra])
        lettera(asse, next(lettere), "{0}\n{1} elettrodi, {2} pazienti".format(
            titolo, int(info["elettrodi"]), int(info["pazienti"])))
        asse.title.set_fontsize(DIMENSIONE_TITOLI)
        if riga == 1:
            asse.set_xlabel("Tempo dall'accensione (s)")
        if colonna == 0:
            asse.set_ylabel("Frequenza (Hz)")
    fig.tight_layout(rect=(0, 0, 0.88, 1), h_pad=2.0, w_pad=1.5)
    barra_colore(fig, m, "Pendenza volti \u2212 pendenza oggetti")
    USCITA.mkdir(parents=True, exist_ok=True)
    salva(fig, USCITA / "pendenza_modulazione")

    # Figure B: V1/V2, object-selective: slope faces, objects, difference
    fig, assi = plt.subplots(1, 3, figsize=(14, 4.2), sharex=True, sharey=True)
    cluster = (d["iit_cat2_p"] < 0.05)[:, finestra]
    for asse, lett, chiave, titolo in zip(
            assi, "ABC",
            ["iit_cat2_pendenza_volti", "iit_cat2_pendenza_oggetti", "iit_cat2_modulazione"],
            ["Pendenza, prove con volti", "Pendenza, prove con oggetti", "Volti \u2212 oggetti"]):
        m = mappa(asse, t, freqs, d[chiave][:, finestra], cluster)
        lettera(asse, lett, titolo)
        asse.title.set_fontsize(DIMENSIONE_TITOLI)
        asse.set_xlabel("Tempo dall'accensione (s)")
    assi[0].set_ylabel("Frequenza (Hz)")
    fig.tight_layout(rect=(0, 0, 0.89, 1), w_pad=1.5)
    barra_colore(fig, m, "Pendenza della DFC sulla LZC (per 1 DS)")
    salva(fig, USCITA / "pendenza_v1v2_oggetti")


if __name__ == "__main__":
    main()
