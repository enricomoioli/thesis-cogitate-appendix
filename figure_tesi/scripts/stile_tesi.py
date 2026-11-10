# -*- coding: utf-8 -*-
"""
stile_tesi.py

Common style for all the figures of the thesis. Imported by the scripts in
figure_tesi\\scripts\\ (same folder):

    from stile_tesi import COLORI, applica_stile, virgola_decimale, lettera, salva

Rules:
- theory colours fixed throughout the thesis: IIT blue, GNW red
  (the same as in the electrode map and in the predictions diagram);
  anything that is not a theory uses greys, never red or blue;
- comma as decimal separator (Italian convention of the thesis);
- panel letters (A, B, C...) in bold at the top left, no general title with
  internal identifiers: the context goes in the caption;
- no top and right spines;
- saved as PNG at 300 dpi and as vector PDF.
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

COLORI = {"iit": (0.12, 0.47, 0.71), "gnw": (0.84, 0.15, 0.16)}
GRIGIO_SCURO = "0.25"
GRIGIO_MEDIO = "0.55"
GRIGIO_CHIARO = "0.88"

# colour maps: sequential for absolute values, diverging for differences
MAPPA_SEQUENZIALE = "viridis"
MAPPA_DIVERGENTE = "RdBu_r"


def applica_stile():
    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titlelocation": "left",
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.bbox": "tight",
    })


def _con_virgola(valore, _pos):
    testo = "{0:g}".format(valore)
    if "e" in testo:  # scientific notation: left as it is, only the comma
        testo = "{0:.2g}".format(valore)
    return testo.replace("-", "\u2212").replace(".", ",")


def virgola_decimale(asse, x=True, y=True):
    """Axis labels with the decimal comma."""
    formattatore = FuncFormatter(_con_virgola)
    if x:
        asse.xaxis.set_major_formatter(formattatore)
    if y:
        asse.yaxis.set_major_formatter(formattatore)


def virgola_barra_colore(barra):
    barra.ax.yaxis.set_major_formatter(FuncFormatter(_con_virgola))


def lettera(asse, testo, titolo=None):
    """Panel title: letter in bold, optional short description."""
    if titolo:
        asse.set_title(r"$\bf{" + testo + r"}$   " + titolo)
    else:
        asse.set_title(r"$\bf{" + testo + r"}$")


def salva(fig, percorso_senza_estensione):
    percorso = Path(percorso_senza_estensione)
    percorso.parent.mkdir(parents=True, exist_ok=True)
    for estensione, dpi in (("png", 300), ("pdf", None)):
        uscita = percorso.with_suffix("." + estensione)
        fig.savefig(str(uscita), dpi=dpi)
        print("Salvato:", uscita)
    plt.close(fig)
