# -*- coding: utf-8 -*-
"""
09_figure_stato_prestimolo.py

Figure del cap. 5 (stato pre-stimolo e connettivita' selettiva), con lo stesso
stile e la stessa convenzione della figura 4.3 (07_figura_sincronia_sintesi.py).

Figura 5.1: differenza fra prove con LZC pre-stimolo alta e bassa nell'effetto
di categoria (volti meno oggetti) sul piano tempo-frequenza, media fra
elettrodi selettivi; disposizione 2 x 2 come la figura 4.3 (righe: V1/V2 e
prefrontale; colonne: selettivi per volti e per oggetti). Celle del cluster
significativo (p < 0,05) contornate.

Figura 5.2: solo V1/V2, elettrodi selettivi per gli oggetti: effetto di
categoria con LZC bassa, con LZC alta e loro differenza, con il cluster
contornato in tutti e tre i pannelli.

Scala fissa da -0,05 a +0,05 come nella figura 4.3 (valori oltre saturati);
asse del tempo da -0,5 a 2,0 s.

Sola lettura dei risultati dello script 21
(extension\\results\\stato_prestimolo\\statistica_alto_basso.npz e
statistica_alto_basso_riepilogo.csv).

Output: figure_tesi\\output\\cap5\\stato_differenza.png/.pdf e
        figure_tesi\\output\\cap5\\stato_v1v2_oggetti.png/.pdf

Uso:
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

FINESTRA_TEMPO = (-0.5, 2.0)   # come la figura 4.3
LIMITE_SCALA = 0.05            # come la figura 4.3
# fattore di ingrandimento del testo: nel PDF la figura viene ridotta alla
# larghezza della pagina, quindi il testo va ingrandito di conseguenza
SCALA = 1.25
DIMENSIONE_TITOLI = 10 * SCALA

# (riga, colonna, chiave nel file, regione, categoria nel riepilogo, titolo)
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
        asse.spines[lato].set_visible(True)  # le mappe restano incorniciate
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

    # Figura 5.1: differenza alto - basso, quattro insiemi
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

    # Figura 5.2: V1/V2, selettivi per gli oggetti: bassa, alta, differenza
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
