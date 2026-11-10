# -*- coding: utf-8 -*-
"""
02_schema_lakatos.py

Didactic diagram of Lakatos's model for chapter 2 (section on sophisticated
falsificationism), on a hypothetical research programme: hard core,
protective belt of auxiliary hypotheses, predictions on the edge.
An anomaly hits a prediction without reaching the core; an auxiliary
hypothesis is modified, and the two possible responses are those defined in
the text of chapter 2:
- progressive: the modification predicts novel facts;
- degenerating: the modification only accommodates the anomaly.

Hypothetical programme, hence greys only (red and blue are reserved for the theories).

Output: figure_tesi\\output\\schemi\\schema_lakatos.png / .pdf

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\02_schema_lakatos.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

# text magnification factor: in the PDF the figure is shrunk to the
# page width, so the text must be enlarged accordingly
SCALA = 1.4

from stile_tesi import GRIGIO_SCURO, applica_stile, salva

USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\schemi\schema_lakatos")

R_NUCLEO, R_CINTURA = 1.25, 3.0
ANGOLI_PREDIZIONI = (110, 150, 200, 250, 290)
ANGOLO_ANOMALIA = 20


def polare(r, gradi):
    a = np.deg2rad(gradi)
    return r * np.cos(a), r * np.sin(a)


def riquadro(asse, x, y, testo, larghezza=4.7, altezza=1.3, tratteggio="-"):
    asse.add_patch(FancyBboxPatch((x - larghezza / 2, y - altezza / 2), larghezza, altezza,
                                  boxstyle="round,pad=0.02,rounding_size=0.12",
                                  facecolor="white", edgecolor=GRIGIO_SCURO, linewidth=1.1,
                                  linestyle=tratteggio))
    asse.text(x, y, testo, ha="center", va="center", fontsize=8.8 * SCALA, linespacing=1.3)


def freccia(asse, da, a, tratteggio="-"):
    asse.annotate("", xy=a, xytext=da,
                  arrowprops=dict(arrowstyle="-|>", color=GRIGIO_SCURO, linewidth=1.3,
                                  linestyle=tratteggio, mutation_scale=13, shrinkA=2, shrinkB=2))


def main():
    applica_stile()
    matplotlib.rcParams.update({"font.size": 10 * SCALA, "axes.titlesize": 11 * SCALA, "axes.labelsize": 10 * SCALA,
                                "xtick.labelsize": 9 * SCALA, "ytick.labelsize": 9 * SCALA,
                                "legend.fontsize": 9 * SCALA})
    fig, asse = plt.subplots(figsize=(12, 6.2))

    # research programme
    asse.add_patch(Circle((0, 0), R_CINTURA, facecolor="0.93", edgecolor=GRIGIO_SCURO, linewidth=1.2))
    asse.add_patch(Circle((0, 0), R_NUCLEO, facecolor="0.72", edgecolor=GRIGIO_SCURO, linewidth=1.2))
    asse.text(0, 0.12, "Nucleo", ha="center", va="center", fontsize=11 * SCALA, fontweight="bold")
    asse.text(0, -0.32, "non si abbandona", ha="center", va="center", fontsize=8.8 * SCALA, style="italic")
    asse.text(0, 2.05, "Cintura protettiva", ha="center", va="center",
              fontsize=10 * SCALA, fontweight="bold", color=GRIGIO_SCURO)
    asse.text(0, 1.62, "ipotesi ausiliarie modificabili", ha="center",
              va="center", fontsize=7.8 * SCALA, style="italic", color=GRIGIO_SCURO)

    for gradi in ANGOLI_PREDIZIONI:
        x, y = polare(R_CINTURA, gradi)
        asse.plot(x, y, "o", markersize=8, markerfacecolor="white", markeredgecolor=GRIGIO_SCURO,
                  markeredgewidth=1.4, zorder=3)
    x, y = polare(R_CINTURA, 150)
    asse.annotate("predizioni", xy=(x - 0.12, y), xytext=(x - 0.9, y + 0.55), ha="right", va="center",
                  fontsize=9 * SCALA, color=GRIGIO_SCURO,
                  arrowprops=dict(arrowstyle="-", color=GRIGIO_SCURO, linewidth=0.8))

    # anomaly: comes from outside and hits a prediction (filled dot), without reaching the core
    x_colpita, y_colpita = polare(R_CINTURA, ANGOLO_ANOMALIA)
    asse.plot(x_colpita, y_colpita, "o", markersize=9, color="k", zorder=4)
    inizio = (x_colpita + 0.9, y_colpita + 2.0)
    asse.annotate("", xy=(x_colpita + 0.06, y_colpita + 0.14), xytext=inizio,
                  arrowprops=dict(arrowstyle="-|>", color="k", linewidth=2, mutation_scale=16))
    asse.text(inizio[0], inizio[1] + 0.1, "anomalia", ha="center", va="bottom",
              fontsize=10 * SCALA, fontweight="bold")

    # two possible responses
    x_bivio, y_bivio = 7.0, 0
    riquadro(asse, x_bivio, y_bivio, "si modifica\nun'ipotesi ausiliaria", larghezza=3.7)
    freccia(asse, (x_colpita + 0.2, y_colpita - 0.1), (x_bivio - 1.85, y_bivio))
    riquadro(asse, 12.3, 1.5, "Progressiva\nla modifica predice\nfatti nuovi", altezza=1.75)
    riquadro(asse, 12.3, -1.5, "Degenerativa\nla modifica accomoda\nsolo l'anomalia", altezza=1.75,
             tratteggio="--")
    freccia(asse, (x_bivio + 1.85, y_bivio + 0.2), (12.3 - 2.35, 1.5))
    freccia(asse, (x_bivio + 1.85, y_bivio - 0.2), (12.3 - 2.35, -1.5), tratteggio="--")

    asse.set_xlim(-4.8, 14.8)
    asse.set_ylim(-3.3, 4.0)
    asse.set_aspect("equal")
    asse.axis("off")
    salva(fig, USCITA)


if __name__ == "__main__":
    main()
