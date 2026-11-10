# -*- coding: utf-8 -*-
"""
11_schema_stati_alterati.py

Diagram for the discussion chapter (section on future directions: beyond
meditation, a range of altered states): the eight states discussed, in the
order in which the text presents them, which the text itself declares to be
a gradient of evidential weight, from the universal and best documented case
(sleep) to an anomaly reported in a few cases (tukdam).

For each: what it offers to the dispute and what it rests on, paraphrased
from the text. No numerical quantity and no position on axes: the order is
the only information, and it is that of the text. The intensity of the grey
follows the order, only as a visual guide.

Output: figure_tesi\\output\\schemi\\schema_stati_alterati.png / .pdf

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\11_schema_stati_alterati.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from stile_tesi import GRIGIO_SCURO, GRIGIO_MEDIO, applica_stile, salva

USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\schemi\schema_stati_alterati")

STATI = [
    ("Sonno e sogno", "nel sogno l'esperienza c'\u00e8,\nma senza accesso n\u00e9 report",
     "universale, studiato\nda decenni"),
    ("Stati psichedelici", "la complessit\u00e0 del segnale\nsale con l'intensit\u00e0 riferita",
     "pi\u00f9 sostanze e tecniche,\nrisultati replicati"),
    ("Meditazione\na lungo termine", "connettivit\u00e0 efficace modulata\ndall'esperienza di pratica",
     "studio su monaci di\nSera Jey, EEG a riposo"),
    ("Yoga nidra", "fenomenologia alterata senza\nle firme EEG del sonno",
     "6 volontari, analisi\nspettrale su 1 solo"),
    ("Ipnosi", "attivit\u00e0 sostenuta senza\nignition frontoparietale",
     "un solo soggetto"),
    ("Esperienze\ndi pre-morte", "aumento gamma nel cervello\nmorente, origine contesa",
     "pochi pazienti,\ninterpretazione criticata"),
    ("Esperienze\nfuori dal corpo", "esperienza che prosegue senza\nun s\u00e9 corporeo localizzato",
     "una rassegna, contesto\nda vagliare con cura"),
    ("Tukdam", "nessuna attivit\u00e0 EEG residua\nrilevata", "pochi casi,\nanomalia presunta"),
]

PER_RIGA = 4
L, H = 3.3, 2.55
PASSO_X, PASSO_Y = 3.65, 3.25


def main():
    applica_stile()
    fig, asse = plt.subplots(figsize=(13, 7.4))
    toni = np.linspace(0.70, 0.97, len(STATI))

    for k, (nome, offre, base) in enumerate(STATI):
        riga, colonna = divmod(k, PER_RIGA)
        x = colonna * PASSO_X
        y = -riga * PASSO_Y
        asse.add_patch(FancyBboxPatch((x, y - H), L, H, boxstyle="round,pad=0.0,rounding_size=0.1",
                                      facecolor=str(toni[k]), edgecolor=GRIGIO_SCURO, linewidth=1.0))
        asse.text(x + 0.18, y - 0.2, str(k + 1), ha="left", va="top", fontsize=9, color=GRIGIO_MEDIO,
                  fontweight="bold")
        asse.text(x + L / 2, y - 0.5, nome, ha="center", va="center", fontsize=10, fontweight="bold",
                  linespacing=1.15)
        asse.text(x + L / 2, y - 1.3, offre, ha="center", va="center", fontsize=8.6, linespacing=1.25)
        asse.plot([x + 0.35, x + L - 0.35], [y - 1.82, y - 1.82], color=GRIGIO_MEDIO, linewidth=0.6)
        asse.text(x + L / 2, y - 2.17, base, ha="center", va="center", fontsize=8.2, style="italic",
                  color=GRIGIO_SCURO, linespacing=1.2)

    # gradient: arrow below the two rows
    y_freccia = -PASSO_Y - H - 0.45
    larghezza = (PER_RIGA - 1) * PASSO_X + L
    asse.annotate("", xy=(larghezza, y_freccia), xytext=(0, y_freccia),
                  arrowprops=dict(arrowstyle="-|>", color=GRIGIO_SCURO, linewidth=1.2, mutation_scale=14))
    asse.text(0, y_freccia - 0.22, "evidenza pi\u00f9 solida", ha="left", va="top", fontsize=8.8,
              color=GRIGIO_SCURO)
    asse.text(larghezza, y_freccia - 0.22, "evidenza pi\u00f9 fragile", ha="right", va="top", fontsize=8.8,
              color=GRIGIO_SCURO)
    asse.text(larghezza / 2, y_freccia - 0.22, "nell'ordine del testo, da 1 a 8", ha="center", va="top",
              fontsize=8.8, style="italic", color=GRIGIO_MEDIO)

    asse.set_xlim(-0.2, larghezza + 0.2)
    asse.set_ylim(y_freccia - 0.75, 0.2)
    asse.set_aspect("equal")
    asse.axis("off")
    salva(fig, USCITA)


if __name__ == "__main__":
    main()
