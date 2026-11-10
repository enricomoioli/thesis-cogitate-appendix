# -*- coding: utf-8 -*-
"""
stile_tesi.py

Stile comune per tutte le figure della tesi. Si importa dagli script in
figure_tesi\\scripts\\ (stessa cartella):

    from stile_tesi import COLORI, applica_stile, virgola_decimale, lettera, salva

Regole:
- colori delle teorie fissi in tutta la tesi: IIT blu, GNW rosso
  (gli stessi della mappa degli elettrodi e dello schema delle predizioni);
  per tutto cio' che non e' una teoria si usano grigi, mai rosso o blu;
- decimali con la virgola;
- lettere di pannello (A, B, C...) in grassetto in alto a sinistra, niente
  titolo generale con identificativi interni: il contesto sta in didascalia;
- niente bordi superiore e destro;
- salvataggio in PNG a 300 dpi e in PDF vettoriale.
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

COLORI = {"iit": (0.12, 0.47, 0.71), "gnw": (0.84, 0.15, 0.16)}
GRIGIO_SCURO = "0.25"
GRIGIO_MEDIO = "0.55"
GRIGIO_CHIARO = "0.88"

# mappe di colore: sequenziale per valori assoluti, divergente per differenze
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
    if "e" in testo:  # notazione scientifica: la si lascia com'e', solo la virgola
        testo = "{0:.2g}".format(valore)
    return testo.replace("-", "\u2212").replace(".", ",")


def virgola_decimale(asse, x=True, y=True):
    """Etichette degli assi con la virgola decimale."""
    formattatore = FuncFormatter(_con_virgola)
    if x:
        asse.xaxis.set_major_formatter(formattatore)
    if y:
        asse.yaxis.set_major_formatter(formattatore)


def virgola_barra_colore(barra):
    barra.ax.yaxis.set_major_formatter(FuncFormatter(_con_virgola))


def lettera(asse, testo, titolo=None):
    """Titolo di pannello: lettera in grassetto, eventuale descrizione breve."""
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
