# -*- coding: utf-8 -*-
"""
13_figura_confronto_alto_basso_pendenza.py

Figure 5.3: V1/V2, object-selective electrodes, comparison between the two
versions of the pre-stimulus state analysis.
  A: difference between trials with high and low LZC in the category effect
     (faces minus objects), as in figure 5.1, panel B (scale +-0.05);
  B: slope in face trials minus slope in object trials, with continuous
     standardized LZC (scale +-0.02).
Each panel has its own scale (different units) and the outline of its own cluster.

Reads only the results of scripts 21 and 22.
Output: figure_tesi\\output\\cap5\\confronto_alto_basso_pendenza.png/.pdf

Usage (from the folder figure_tesi\\scripts):
    python 13_figura_confronto_alto_basso_pendenza.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stile_tesi import (GRIGIO_SCURO, MAPPA_DIVERGENTE, applica_stile, virgola_decimale,
                        virgola_barra_colore, lettera, salva)

ALTO_BASSO = Path(r"D:\TESI\manoscritto\extension\results\stato_prestimolo\statistica_alto_basso.npz")
PENDENZA = Path(r"D:\TESI\manoscritto\extension\results\pendenza\statistica_pendenza.npz")
USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\cap5")

FINESTRA_TEMPO = (-0.5, 2.0)   # as in figures 4.3 and 5.1
# text magnification factor: in the PDF the figure is shrunk to the
# page width, so the text must be enlarged accordingly
SCALA = 1.3
DIMENSIONE_TITOLI = 10 * SCALA

# (file, key of the values, scale limit, title, colour bar label)
PANNELLI = [(ALTO_BASSO, "iit_cat2_differenza", 0.05, "LZC divisa sulla mediana: alta \u2212 bassa",
             "\u0394DFC (volti \u2212 oggetti), alta \u2212 bassa"),
            (PENDENZA, "iit_cat2_modulazione", 0.02, "LZC continua: pendenza volti \u2212 oggetti",
             "Pendenza volti \u2212 pendenza oggetti")]


def main():
    applica_stile()
    matplotlib.rcParams.update({"font.size": 10 * SCALA, "axes.labelsize": 10 * SCALA, "xtick.labelsize": 9 * SCALA,
                                "ytick.labelsize": 9 * SCALA, "legend.fontsize": 9 * SCALA})
    fig, assi = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for asse, lett, (file, chiave, limite, titolo, etichetta) in zip(assi, "AB", PANNELLI):
        d = np.load(file)
        tempi, freqs = d["tempi"], d["frequenze"]
        finestra = (tempi >= FINESTRA_TEMPO[0]) & (tempi <= FINESTRA_TEMPO[1])
        t = tempi[finestra]
        valori = d[chiave][:, finestra]
        cluster = (d["iit_cat2_p"] < 0.05)[:, finestra]
        m = asse.pcolormesh(t, freqs, valori, cmap=MAPPA_DIVERGENTE, vmin=-limite, vmax=limite,
                            shading="auto", rasterized=True)
        if cluster.any():
            asse.contour(t, freqs, cluster, levels=[0.5], colors=GRIGIO_SCURO, linewidths=0.9)
        asse.axvline(0, color=GRIGIO_SCURO, linestyle="--", linewidth=0.8)
        for lato in ("top", "right"):
            asse.spines[lato].set_visible(True)
        virgola_decimale(asse)
        lettera(asse, lett, titolo)
        asse.title.set_fontsize(DIMENSIONE_TITOLI)
        asse.set_xlabel("Tempo dall'accensione (s)")
        barra = fig.colorbar(m, ax=asse, fraction=0.046, pad=0.03)
        barra.set_label(etichetta)
        virgola_barra_colore(barra)
    assi[0].set_ylabel("Frequenza (Hz)")
    fig.tight_layout(w_pad=2.0)
    USCITA.mkdir(parents=True, exist_ok=True)
    salva(fig, USCITA / "confronto_alto_basso_pendenza")


if __name__ == "__main__":
    main()
