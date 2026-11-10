# -*- coding: utf-8 -*-
"""
01_mappa_teorie.py

Map of the theories of consciousness for chapter 1 ("Troppe teorie, poco
confronto" and "Il resto del panorama in breve"), with the common style
(stile_tesi.py).

- The four families are those of Seth and Bayne (2022), as reported in the
  text of chapter 1. The examples within each family are NOT Seth and Bayne's
  classification: they are the theories discussed in this thesis, placed
  where the text places them (chapters 2 and 6).
- Below, in dashed grey, the more speculative proposals that chapter 1
  mentions and declares it will not cover.
- IIT and GNWT in the theory colours; everything else in grey.

Output: figure_tesi\\output\\schemi\\mappa_teorie.png / .pdf

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\01_mappa_teorie.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import to_rgb

from stile_tesi import COLORI, GRIGIO_SCURO, GRIGIO_MEDIO, applica_stile, salva

USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\schemi\mappa_teorie")

# (family name, [(theory, colour key or None)])
FAMIGLIE = [
    ("Teorie di\nordine superiore", [("HOROR", None), ("perceptual reality\nmonitoring", None)]),
    ("Teorie del\nglobal workspace", [("GNWT", "gnw")]),
    ("Teorie del re-entry\ne del processamento\npredittivo", [("recurrent processing\ntheory", None),
                                                          ("active inference", None),
                                                          ("neurorepresenta-\ntionalism", None)]),
    ("Teoria\ndell'informazione\nintegrata", [("IIT", "iit")]),
]
SPECULATIVE = ["panpsichismo", "Orch OR\n(microtubuli)", "campo elettro-\nmagnetico (cemi)"]

# grey of the speculative proposals: darker than GRIGIO_MEDIO (0.55) for readability
GRIGIO_SPECULATIVE = "0.40"

L, H = 3.6, 3.9
PASSO = 4.0


def schiarisci(colore, quanto):
    r, g, b = to_rgb(colore)
    return (r + (1 - r) * quanto, g + (1 - g) * quanto, b + (1 - b) * quanto)


def scatola(asse, x, y, l, h, fc, ec, ls="-", lw=1.1):
    asse.add_patch(FancyBboxPatch((x, y), l, h, boxstyle="round,pad=0.0,rounding_size=0.12",
                                  facecolor=fc, edgecolor=ec, linestyle=ls, linewidth=lw))


def main():
    applica_stile()
    fig, asse = plt.subplots(figsize=(13, 6.6))

    for k, (famiglia, teorie) in enumerate(FAMIGLIE):
        x = k * PASSO
        scatola(asse, x, 0, L, H, "0.95", GRIGIO_SCURO)
        asse.text(x + L / 2, H - 0.62, famiglia, ha="center", va="center", fontsize=13, fontweight="bold",
                  linespacing=1.2)
        n = len(teorie)
        altezza_t = 0.72
        spazio = (H - 1.45 - n * altezza_t) / (n + 1)
        for i, (teoria, chiave) in enumerate(teorie):
            y = H - 1.3 - (i + 1) * spazio - (i + 1) * altezza_t
            if chiave:
                fc, ec, peso = schiarisci(COLORI[chiave], 0.75), COLORI[chiave], "bold"
            else:
                fc, ec, peso = "white", GRIGIO_MEDIO, "normal"
            scatola(asse, x + 0.3, y, L - 0.6, altezza_t, fc, ec, lw=1.3 if chiave else 0.8)
            asse.text(x + L / 2, y + altezza_t / 2, teoria, ha="center", va="center",
                      fontsize=14 if chiave else 12.5, fontweight=peso, linespacing=1.1)

    asse.text(0, H + 0.35, "Le quattro famiglie di Seth e Bayne, con le teorie discusse in questa tesi",
              ha="left", va="bottom", fontsize=13, color=GRIGIO_SCURO)

    # speculative proposals
    larghezza = 3 * PASSO + L
    y0 = -2.0
    asse.text(0, y0 + 1.05, "Proposte pi\u00f9 speculative, nominate ma non trattate", ha="left", va="bottom",
              fontsize=13, color=GRIGIO_SPECULATIVE)
    l_spec = 3.4
    passo_spec = (larghezza - l_spec) / (len(SPECULATIVE) - 1)
    for k, nome in enumerate(SPECULATIVE):
        x = k * passo_spec
        scatola(asse, x, y0, l_spec, 0.9, "white", GRIGIO_SPECULATIVE, ls="--", lw=0.9)
        asse.text(x + l_spec / 2, y0 + 0.45, nome, ha="center", va="center", fontsize=12.5, color=GRIGIO_SPECULATIVE,
                  linespacing=1.1)

    asse.set_xlim(-0.2, larghezza + 0.2)
    asse.set_ylim(y0 - 0.25, H + 0.9)
    asse.set_aspect("equal")
    asse.axis("off")
    salva(fig, USCITA)


if __name__ == "__main__":
    main()
