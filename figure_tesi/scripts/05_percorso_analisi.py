# -*- coding: utf-8 -*-
"""
05_percorso_analisi.py

Diagramma del percorso di analisi della parte empirica: dai dati pubblici del
consorzio al tentativo MEG (interrotto), alla riproduzione iEEG del cap. 4 e
all'estensione del cap. 5, che parte dagli elettrodi selettivi del cap. 4,
divide le prove secondo la LZC pre-stimolo e ricalcola la DFC sulle due meta'.
Contenuti presi dal testo del cap. 4 e dalla preregistrazione del cap. 5.

I cerchi numerati segnano la fase in cui emerge ciascuno dei sei difetti
oggettivi della tabella tab:difetti del cap. 4 (stessa numerazione: 1, 2 e 3
nel preprocessing, 4 nella selettivita', 5 e 6 nella sincronia).
Aggiornato il 3 novembre: tolti la fase di responsivita' visiva (filtro di
attivazione disattivato nella configurazione finale) e la robustezza; testi piu' grandi.
Aggiornato il 4 novembre: figura piu' stretta (10 pollici) perche' nel PDF il
testo restasse leggibile; etichette di corsia sopra le corsie, testi a capo.

Solo grigi: rosso e blu sono riservati alle teorie (stile_tesi.py).

Output: figure_tesi\\output\\schemi\\percorso_analisi.png / .pdf

Uso:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\05_percorso_analisi.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from stile_tesi import GRIGIO_SCURO, GRIGIO_MEDIO, applica_stile, salva

USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\schemi\percorso_analisi")

L, H = 3.15, 1.4        # larghezza e altezza dei riquadri
PASSO = 3.5             # distanza orizzontale fra riquadri
X0 = L / 2 + 0.05       # centro della prima colonna
RAGGIO_DIFETTO = 0.27
Y = {"meg": 6.2, "cap4": 3.2, "cap5": 0.7}
TESTO = 10.5            # corpo del testo nei riquadri

STILI = {
    "meg": dict(fc="0.97", ec="0.65", ls="--"),
    "cap4": dict(fc="0.93", ec=GRIGIO_SCURO, ls="-"),
    "cap5": dict(fc="0.86", ec=GRIGIO_SCURO, ls="-"),
    "dati": dict(fc="white", ec=GRIGIO_SCURO, ls="-"),
}


def riquadro(asse, colonna, corsia, testo, stile=None):
    x = X0 + colonna * PASSO
    y = Y[corsia]
    s = STILI[stile or corsia]
    asse.add_patch(FancyBboxPatch((x - L / 2, y - H / 2), L, H,
                                  boxstyle="round,pad=0.02,rounding_size=0.12",
                                  facecolor=s["fc"], edgecolor=s["ec"], linestyle=s["ls"], linewidth=1.1))
    asse.text(x, y, testo, ha="center", va="center", fontsize=TESTO, linespacing=1.2,
              color="0.1" if corsia != "meg" else "0.35")
    return x, y


def etichetta_corsia(asse, corsia, testo):
    """Nome della corsia sopra il primo riquadro, allineato a sinistra."""
    asse.text(X0 - L / 2, Y[corsia] + H / 2 + 0.2, testo, ha="left", va="bottom", fontsize=11,
              fontweight="bold", linespacing=1.15, color=GRIGIO_SCURO if corsia != "meg" else GRIGIO_MEDIO)


def difetti(asse, colonna, corsia, numeri):
    """Cerchi numerati appena sopra il riquadro, allineati a destra."""
    x = X0 + colonna * PASSO + L / 2 - 0.3
    y = Y[corsia] + H / 2 + RAGGIO_DIFETTO + 0.04  # appena sopra il riquadro, senza coprire il testo
    for k, numero in enumerate(reversed(numeri)):
        xc = x - k * (2 * RAGGIO_DIFETTO + 0.1)
        asse.add_patch(plt.Circle((xc, y), RAGGIO_DIFETTO, facecolor=GRIGIO_SCURO, edgecolor="white",
                                  linewidth=1.0, zorder=5))
        asse.text(xc, y, str(numero), ha="center", va="center", fontsize=9, fontweight="bold",
                  color="white", zorder=6)


def freccia(asse, da, a, colore=GRIGIO_SCURO, tratteggio="-", curva=0.0):
    asse.annotate("", xy=a, xytext=da,
                  arrowprops=dict(arrowstyle="-|>", color=colore, linewidth=1.1, linestyle=tratteggio,
                                  shrinkA=0, shrinkB=0, mutation_scale=12,
                                  connectionstyle="arc3,rad={0}".format(curva)))


def orizzontale(asse, col_da, col_a, corsia, **kw):
    y = Y[corsia]
    freccia(asse, (X0 + col_da * PASSO + L / 2, y), (X0 + col_a * PASSO - L / 2, y), **kw)


def main():
    applica_stile()
    fig, asse = plt.subplots(figsize=(10, 5.0))

    # etichette di corsia
    etichetta_corsia(asse, "meg", "Tentativo MEG (cap. 4)")
    etichetta_corsia(asse, "cap4", "Riproduzione\n(cap. 4)")
    etichetta_corsia(asse, "cap5", "Estensione (cap. 5)")

    # corsia MEG
    riquadro(asse, 0, "meg", "Dati MEG\ndel consorzio")
    riquadro(asse, 1, "meg", "Preprocessing\nriprodotto\n(3 soggetti)")
    riquadro(asse, 2, "meg", "Ricostruzione\ndelle sorgenti\ne GED")
    orizzontale(asse, 0, 1, "meg", colore="0.6", tratteggio="--")
    orizzontale(asse, 1, 2, "meg", colore="0.6", tratteggio="--")
    asse.text(X0 + 3 * PASSO - L / 2, Y["meg"], "interrotto: memoria insufficiente\nsu portatile (8 GB),\nColab e Kaggle",
              ha="left", va="center", fontsize=TESTO, linespacing=1.2, color="0.35", style="italic")

    # corsia cap. 4
    riquadro(asse, 0, "cap4", "Dati iEEG\n38 pazienti, 3 siti\ncodice e Methods", stile="dati")
    riquadro(asse, 1, "cap4", "Preprocessing\n38 pazienti")
    riquadro(asse, 2, "cap4", "Selettivit\u00e0\ndi categoria\n(criterio del testo)")
    riquadro(asse, 3, "cap4", "Sincronia DFC\n(configurazione\ndal testo)")
    riquadro(asse, 4, "cap4", "Test a cluster")
    for c in range(4):
        orizzontale(asse, c, c + 1, "cap4")
    difetti(asse, 1, "cap4", [1, 2, 3])
    difetti(asse, 2, "cap4", [4])
    difetti(asse, 3, "cap4", [5, 6])

    # corsia cap. 5: dagli elettrodi selettivi del cap. 4
    riquadro(asse, 2, "cap5", "LZC pre-stimolo\n(\u22120,5\u20130 s) negli\nelettrodi selettivi")
    riquadro(asse, 3, "cap5", "Prove divise\nin LZC alta\ne bassa (mediana)")
    riquadro(asse, 4, "cap5", "DFC in ogni met\u00e0,\ntest a cluster\nalta contro bassa")
    for c in range(2, 4):
        orizzontale(asse, c, c + 1, "cap5")
    x_sel = X0 + 2 * PASSO
    freccia(asse, (x_sel, Y["cap4"] - H / 2), (x_sel, Y["cap5"] + H / 2))

    # dal MEG all'iEEG: il cambio di dataset (a destra dell'etichetta della corsia)
    x_cambio = X0 + L / 2 - 0.35
    freccia(asse, (x_cambio, Y["meg"] - H / 2), (x_cambio, Y["cap4"] + H / 2 + 0.02), colore="0.6",
            tratteggio="--")
    asse.text(x_cambio + 0.15, Y["meg"] - H / 2 - 0.45, "cambio di dataset", ha="left", va="center",
              fontsize=TESTO, color="0.35", style="italic")

    asse.set_xlim(-0.05, X0 + 4 * PASSO + L / 2 + 0.1)
    asse.set_ylim(-0.1, Y["meg"] + H / 2 + 0.75)
    asse.set_aspect("equal")
    asse.axis("off")
    salva(fig, USCITA)


if __name__ == "__main__":
    main()
