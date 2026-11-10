# -*- coding: utf-8 -*-
"""
10_schema_lakatos_cogitate.py

Lo schema del modello di Lakatos del cap. 2 (02_schema_lakatos.py),
applicato alle due teorie di COGITATE per il cap. 6 (sezione "La replica
di GNWT, e cosa insegna sulla cintura protettiva"): due programmi
affiancati, ciascuno con l'anomalia che lo studio gli ha opposto e la
risposta dei proponenti, come riportate nel testo.

- IIT: anomalia sulla terza predizione (nessuna sincronizzazione sostenuta
  nella corteccia posteriore con la misura preregistrata); risposta: troppo
  pochi elettrodi sulle aree posteriori (cap. 2, da Negro 2024), cioe' una
  modifica di un'ipotesi ausiliaria sul disegno.
- GNWT: anomalia sulla seconda predizione (nessuna ignition allo
  spegnimento dello stimolo); risposta: l'ignition all'offset non sarebbe
  mai stata una predizione del nucleo (cap. 6, da Naccache et al. 2025),
  cioe' un nuovo confine fra nucleo e cintura.

Testi parafrasati dal testo della tesi, non citazioni. Colori delle teorie
da stile_tesi.py; tutto il resto in grigio.

Output: figure_tesi\\output\\schemi\\schema_lakatos_cogitate.png / .pdf

Uso:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\10_schema_lakatos_cogitate.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.colors import to_rgb

from stile_tesi import COLORI, GRIGIO_SCURO, applica_stile, salva

USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\schemi\schema_lakatos_cogitate")

R_NUCLEO, R_CINTURA = 1.0, 2.2
ANGOLI_PREDIZIONI = (150, 200, 250, 290, 340)
ANGOLO_ANOMALIA = 50

PROGRAMMI = [
    dict(teoria="iit", x=0.0, nome="IIT",
         anomalia="Predizione 3\nnessuna sincronia sostenuta\nnella corteccia posteriore",
         risposta="Troppo pochi elettrodi\nsulle aree posteriori",
         mossa="si modifica un'ipotesi ausiliaria\nsul disegno sperimentale"),
    dict(teoria="gnw", x=9.0, nome="GNWT",
         anomalia="Predizione 2\nnessuna ignition allo\nspegnimento dello stimolo",
         risposta="L'ignition allo spegnimento\nnon apparteneva al nucleo",
         mossa="si ridisegna il confine\nfra nucleo e cintura"),
]


def schiarisci(colore, quanto):
    r, g, b = to_rgb(colore)
    return (r + (1 - r) * quanto, g + (1 - g) * quanto, b + (1 - b) * quanto)


def polare(cx, r, gradi):
    a = np.deg2rad(gradi)
    return cx + r * np.cos(a), r * np.sin(a)


def riquadro(asse, x, y, titolo, testo, larghezza=5.0, altezza=2.1):
    asse.add_patch(FancyBboxPatch((x - larghezza / 2, y - altezza / 2), larghezza, altezza,
                                  boxstyle="round,pad=0.02,rounding_size=0.12",
                                  facecolor="white", edgecolor=GRIGIO_SCURO, linewidth=1.1))
    asse.text(x, y + 0.72, "risposta dei proponenti", ha="center", va="center", fontsize=8.2,
              color=GRIGIO_SCURO)
    asse.text(x, y + 0.17, titolo, ha="center", va="center", fontsize=9.2, fontweight="bold",
              linespacing=1.25)
    asse.text(x, y - 0.55, testo, ha="center", va="center", fontsize=8.6, style="italic",
              color=GRIGIO_SCURO, linespacing=1.25)


def programma(asse, p):
    colore = COLORI[p["teoria"]]
    cx = p["x"]
    asse.add_patch(Circle((cx, 0), R_CINTURA, facecolor=schiarisci(colore, 0.88), edgecolor=colore, linewidth=1.2))
    asse.add_patch(Circle((cx, 0), R_NUCLEO, facecolor=schiarisci(colore, 0.55), edgecolor=colore, linewidth=1.2))
    asse.text(cx, 0.15, "Nucleo", ha="center", va="center", fontsize=10.5, fontweight="bold")
    asse.text(cx, -0.25, p["nome"], ha="center", va="center", fontsize=9.5)
    asse.text(cx, -(R_NUCLEO + R_CINTURA) / 2 - 0.05, "cintura protettiva", ha="center", va="center",
              fontsize=8.6, style="italic", color=GRIGIO_SCURO)
    for gradi in ANGOLI_PREDIZIONI:
        x, y = polare(cx, R_CINTURA, gradi)
        asse.plot(x, y, "o", markersize=7, markerfacecolor="white", markeredgecolor=colore,
                  markeredgewidth=1.3, zorder=3)

    # anomalia: colpisce una predizione sul bordo, non raggiunge il nucleo
    xc, yc = polare(cx, R_CINTURA, ANGOLO_ANOMALIA)
    asse.plot(xc, yc, "o", markersize=8.5, color="k", zorder=4)
    inizio = (xc + 1.7, yc + 1.55)
    asse.annotate("", xy=(xc + 0.1, yc + 0.1), xytext=inizio,
                  arrowprops=dict(arrowstyle="-|>", color="k", linewidth=1.8, mutation_scale=15))
    asse.text(inizio[0] + 0.1, inizio[1] + 0.08, p["anomalia"], ha="left", va="bottom", fontsize=8.8,
              linespacing=1.25)
    asse.text(inizio[0] + 0.1, inizio[1] + 1.12, "anomalia", ha="left", va="bottom", fontsize=9.5,
              fontweight="bold")

    # risposta dei proponenti, sotto il programma
    y_risposta = -R_CINTURA - 1.85
    riquadro(asse, cx, y_risposta, p["risposta"], p["mossa"])
    asse.annotate("", xy=(cx, y_risposta + 1.07), xytext=(cx, -R_CINTURA),
                  arrowprops=dict(arrowstyle="-|>", color=GRIGIO_SCURO, linewidth=1.1, mutation_scale=12))


def main():
    applica_stile()
    fig, asse = plt.subplots(figsize=(13, 7.2))
    for p in PROGRAMMI:
        programma(asse, p)
    asse.text(5.6, -5.85, "In entrambi i casi l'anomalia viene assorbita dalla cintura protettiva e il nucleo resta intatto.",
              ha="center", va="center", fontsize=9.5, color=GRIGIO_SCURO)
    asse.set_xlim(-2.8, 14.2)
    asse.set_ylim(-6.2, 5.0)
    asse.set_aspect("equal")
    asse.axis("off")
    salva(fig, USCITA)


if __name__ == "__main__":
    main()
