# -*- coding: utf-8 -*-
"""
01_mappa_teorie.py

Mappa delle teorie della coscienza per il cap. 1 ("Troppe teorie, poco
confronto" e "Il resto del panorama in breve"), con lo stile comune
(stile_tesi.py).

- Le quattro famiglie sono quelle di Seth e Bayne (2022), come riportate nel
  testo del cap. 1. Gli esempi dentro ciascuna famiglia NON sono la
  classificazione di Seth e Bayne: sono le teorie che questa tesi discute,
  collocate dove il testo le colloca (cap. 2 e cap. 6).
- Sotto, in grigio tratteggiato, le proposte piu' speculative che il cap. 1
  nomina e dichiara di non trattare.
- IIT e GNWT nei colori delle teorie; tutto il resto in grigio.

Output: figure_tesi\\output\\schemi\\mappa_teorie.png / .pdf

Uso:
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

# (nome della famiglia, [(teoria, chiave colore o None)])
FAMIGLIE = [
    ("Teorie di\nordine superiore", [("HOROR", None), ("perceptual reality\nmonitoring", None)]),
    ("Teorie del\nglobal workspace", [("GNWT", "gnw")]),
    ("Teorie del re-entry\ne del processamento\npredittivo", [("recurrent processing\ntheory", None),
                                                          ("active inference", None),
                                                          ("neurorepresenta-\ntionalism", None)]),
    ("Teoria\ndell'informazione\nintegrata", [("IIT", "iit")]),
]
SPECULATIVE = ["panpsichismo", "Orch OR\n(microtubuli)", "campo elettro-\nmagnetico (cemi)"]

# grigio delle proposte speculative: piu' scuro di GRIGIO_MEDIO (0.55) per leggibilita'
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

    # proposte speculative
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
