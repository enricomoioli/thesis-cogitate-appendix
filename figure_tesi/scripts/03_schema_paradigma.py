# -*- coding: utf-8 -*-
"""
03_schema_paradigma.py

Diagram of the COGITATE experimental paradigm for chapter 3, with the common
style (stile_tesi.py). Contents from the Methods and from Fig. 1c-d of
Cogitate Consortium (2025):

- four stimulus categories (faces, objects, letters, false fonts),
  20 identities each, three orientations (left, front, right), three
  durations (0.5, 1.0, 1.5 s);
- trial of 2.0 s in total (stimulus + blank screen), then, for MEG and iEEG,
  a random interval of 0.2-2.0 s (mean 0.4 s);
- blocks: the targets belong to two categories (face-object or
  letter-false font), which become task-relevant; the other two are
  task-irrelevant. The irrelevant trials are those used in the analyses of
  this thesis.

Panel A: original stimuli of the experiment (same source as Fig. 1c),
copied to figure_tesi\\stimoli_cogitate\\ from the consortium repository
cogitate-experiment-code, branch ECOG-Exp1 (file-by-file provenance in
FONTE.txt). Credits, as in the legend of Fig. 1 of the article: objects
courtesy of Michael J. Tarr (Carnegie Mellon University,
http://www.tarrlab.org/); faces created with FaceGen Modeler 3.1.
Greys only (red and blue are reserved for the theories).

Output: figure_tesi\\output\\schemi\\schema_paradigma.png / .pdf

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\03_schema_paradigma.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch, Rectangle

from stile_tesi import GRIGIO_SCURO, GRIGIO_MEDIO, GRIGIO_CHIARO, applica_stile, lettera, salva

USCITA = Path(r"D:\TESI\manoscritto\figure_tesi\output\schemi\schema_paradigma")
STIMOLI = Path(r"D:\TESI\manoscritto\figure_tesi\stimoli_cogitate")

# text magnification factor: the figure is 13 inches wide and in the PDF
# it is shrunk to about half, so the text must be enlarged accordingly
SCALA = 1.5

DURATE = (0.5, 1.0, 1.5)
DURATA_PROVA = 2.0
ITI = (0.2, 2.0)  # MEG and iEEG; mean 0.4 s


# --- original stimuli, each in a unit box centred at (x, y) ---

def cornice(asse, x, y, lato=1.0):
    asse.add_patch(FancyBboxPatch((x - lato / 2, y - lato / 2), lato, lato,
                                  boxstyle="round,pad=0.0,rounding_size=0.06",
                                  facecolor="white", edgecolor=GRIGIO_MEDIO, linewidth=0.9))


def stimolo(asse, x, y, nome_file, lato=0.9):
    """Original image (PNG with transparency) inside the box."""
    immagine = mpimg.imread(str(STIMOLI / nome_file))
    asse.imshow(immagine, extent=(x - lato / 2, x + lato / 2, y - lato / 2, y + lato / 2),
                interpolation="lanczos", zorder=3)


def pannello_stimoli(asse):
    nomi = ["volti", "oggetti", "lettere", "falsi\ncaratteri"]
    file_ = ["volto_fronte.png", "oggetto_fronte.png", "lettera_fronte.png", "falso_carattere_fronte.png"]
    for k, (nome, nome_file) in enumerate(zip(nomi, file_)):
        x = 0.8 + k * 1.45
        cornice(asse, x, 3.0)
        stimolo(asse, x, 3.0, nome_file)
        asse.text(x, 2.3, nome, ha="center", va="top", fontsize=9*SCALA, linespacing=1.1)
    asse.text(0.1, 3.85, "Quattro categorie", ha="left", va="center",
              fontsize=9*SCALA, color=GRIGIO_SCURO)

    asse.text(0.1, 1.55, "Tre orientamenti", ha="left", va="center", fontsize=9*SCALA, color=GRIGIO_SCURO)
    for k, (nome_file, nome) in enumerate((("volto_sinistra.png", "sinistra"), ("volto_fronte.png", "fronte"),
                                           ("volto_destra.png", "destra"))):
        x = 0.8 + k * 1.45
        cornice(asse, x, 0.75)
        stimolo(asse, x, 0.75, nome_file)
        asse.text(x, 0.05, nome, ha="center", va="top", fontsize=9*SCALA)
    asse.set_xlim(0, 5.8)
    asse.set_ylim(-0.4, 4.1)
    asse.set_aspect("equal")
    asse.axis("off")


def pannello_prova(asse):
    for riga, durata in enumerate(DURATE):
        y = 2 - riga
        asse.add_patch(Rectangle((0, y - 0.3), durata, 0.6, facecolor="0.55", edgecolor="none"))
        asse.add_patch(Rectangle((durata, y - 0.3), DURATA_PROVA - durata, 0.6, facecolor="0.92",
                                 edgecolor="none"))
        # random interval: at least ITI[0] (solid, light), then variable up to ITI[1] (dashed)
        asse.add_patch(Rectangle((DURATA_PROVA, y - 0.3), ITI[0], 0.6, facecolor="0.92", edgecolor="none"))
        asse.add_patch(Rectangle((DURATA_PROVA + ITI[0], y - 0.3), ITI[1] - ITI[0], 0.6, facecolor="white",
                                 edgecolor=GRIGIO_CHIARO, hatch="////", linewidth=0.6))
        asse.text(-0.08, y, "{0} s".format(str(durata).replace(".", ",")), ha="right", va="center", fontsize=9*SCALA)
    asse.axvline(DURATA_PROVA, color=GRIGIO_SCURO, linestyle="--", linewidth=0.8)
    asse.text(0.02, 2.55, "stimolo", ha="left", va="bottom", fontsize=8.5*SCALA, color=GRIGIO_SCURO)
    asse.text(1.4, 2.55, "schermo vuoto", ha="center", va="bottom", fontsize=8.5*SCALA, color=GRIGIO_SCURO)
    asse.text(DURATA_PROVA + ITI[1] / 2, 2.55, "intervallo casuale\nda 0,2 a 2,0 s\nmedia 0,4 s",
              ha="center", va="bottom", fontsize=8.5*SCALA, color=GRIGIO_SCURO)
    asse.set_xlim(-0.45, DURATA_PROVA + ITI[1] + 0.1)
    asse.set_ylim(-0.6, 3.75)
    asse.set_yticks([])
    asse.spines["left"].set_visible(False)
    asse.set_xticks([0, 0.5, 1.0, 1.5, 2.0, 2.2, 4.0])
    asse.set_xticklabels(["0", "0,5", "1,0", "1,5", "2,0", "", "4,0"])
    asse.set_xlabel("Tempo dall'accensione dello stimolo (s)")


def pannello_blocchi(asse):
    colonne = ["bersagli", "rilevanti\nper il compito", "irrilevanti\nper il compito"]
    righe = [("blocco con bersagli\nvolto e oggetto", ["un volto e un oggetto\nspecifici",
                                                         "gli altri volti\ne oggetti",
                                                         "lettere e\nfalsi caratteri"]),
             ("blocco con bersagli\nlettera e falso carattere", ["una lettera e un falso\ncarattere specifici",
                                                                  "le altre lettere\ne falsi caratteri",
                                                                  "volti e oggetti"])]
    x_col = [3.75, 6.3, 8.85]
    for x, nome in zip(x_col, colonne):
        asse.text(x, 2.35, nome, ha="center", va="center", fontsize=9*SCALA, fontweight="bold", linespacing=1.1)
    for r, (nome, celle) in enumerate(righe):
        y = 1.4 - r * 1.15
        asse.text(0.0, y, nome, ha="left", va="center", fontsize=9*SCALA, linespacing=1.2)
        for c, (x, testo) in enumerate(zip(x_col, celle)):
            evidenziata = c == 2
            asse.add_patch(FancyBboxPatch((x - 1.2, y - 0.45), 2.4, 0.9,
                                          boxstyle="round,pad=0.0,rounding_size=0.08",
                                          facecolor="0.85" if evidenziata else "white",
                                          edgecolor=GRIGIO_SCURO if evidenziata else GRIGIO_MEDIO,
                                          linewidth=1.2 if evidenziata else 0.8))
            asse.text(x, y, testo, ha="center", va="center", fontsize=8.6*SCALA, linespacing=1.2)
    asse.text(8.85, -0.42, "prove analizzate in questa tesi", ha="center", va="center", fontsize=8.5*SCALA,
              style="italic", color=GRIGIO_SCURO)
    asse.set_xlim(-0.1, 10.1)
    asse.set_ylim(-0.65, 2.85)
    asse.axis("off")


def main():
    applica_stile()
    matplotlib.rcParams.update({"axes.titlesize": 11 * SCALA, "axes.labelsize": 10 * SCALA,
                                "xtick.labelsize": 9 * SCALA, "ytick.labelsize": 9 * SCALA})
    fig = plt.figure(figsize=(13, 7.6))
    griglia = fig.add_gridspec(2, 2, width_ratios=[1, 1.25], height_ratios=[1, 0.7], hspace=0.35, wspace=0.12)
    a = fig.add_subplot(griglia[0, 0])
    b = fig.add_subplot(griglia[0, 1])
    c = fig.add_subplot(griglia[1, :])
    pannello_stimoli(a)
    lettera(a, "A", "Stimoli")
    pannello_prova(b)
    lettera(b, "B", "Struttura di una prova")
    pannello_blocchi(c)
    lettera(c, "C", "Blocchi e rilevanza per il compito")
    salva(fig, USCITA)


if __name__ == "__main__":
    main()
