# -*- coding: utf-8 -*-
"""
04_schema_predizioni.py

Schema stilizzato della predizione 2 del Cogitate (mantenimento del
contenuto cosciente nel tempo), ridisegnato dalla Fig. 1a (pannello centrale)
di Cogitate Consortium (2025):

- IIT, corteccia posteriore: attivazione sostenuta per tutta la durata dello
  stimolo, ritorno al basale dopo lo spegnimento;
- GNWT, corteccia prefrontale: ignition breve 0,3-0,5 s dopo l'accensione e
  0,3-0,5 s dopo lo spegnimento, indipendente dalla durata, attivita'
  praticamente assente nel mezzo (Methods, "Duration analysis").

Le curve sono predizioni stilizzate, non dati: l'asse verticale non ha unita'.
Tre durate dello stimolo (0,5 / 1,0 / 1,5 s), come nel paradigma: una riga
per durata, come nella figura originale, cosi' che ogni ignition allo
spegnimento sia attribuibile senza ambiguita' al proprio stimolo.

Legenda in basso: fascia grigia = stimolo acceso; fascia rosa = finestre di
ignition preregistrate. Che l'asse verticale non abbia unita' e' detto in
didascalia.

Solo matplotlib/numpy: gira in qualunque ambiente (es. quello MNE).

Output (in figure_tesi\\output\\schemi\\):
    schema_predizione2.png (300 dpi) e schema_predizione2.pdf (vettoriale)

Uso:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\04_schema_predizioni.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# fattore di ingrandimento del testo: nel PDF la figura viene ridotta alla
# larghezza della pagina, quindi il testo va ingrandito di conseguenza
SCALA = 1.3

from stile_tesi import COLORI, GRIGIO_SCURO, applica_stile, lettera, salva

OUTPUT_DIR = Path(r"D:\TESI\manoscritto\figure_tesi\output\schemi")

DURATE = (0.5, 1.0, 1.5)
FINESTRA_IGNIZIONE = (0.3, 0.5)  # s dopo accensione e dopo spegnimento (preregistrata)

t = np.linspace(-0.4, 2.5, 3000)


def sigmoide(x, tau=0.03):
    return 1.0 / (1.0 + np.exp(-x / tau))


def curva_iit(durata):
    """Plateau: sale all'accensione, resta alto per la durata, torna al basale."""
    return sigmoide(t - 0.1) * (1.0 - sigmoide(t - durata - 0.1))


def curva_gnw(durata):
    """Due ignition brevi, centrate nella finestra 0,3-0,5 s dopo accensione e spegnimento."""
    centro = np.mean(FINESTRA_IGNIZIONE)
    ampiezza = 0.045
    return (np.exp(-0.5 * ((t - centro) / ampiezza) ** 2)
            + np.exp(-0.5 * ((t - durata - centro) / ampiezza) ** 2))


def disegna_riga(asse, teoria, durata, prima_riga, ultima_riga):
    colore = COLORI[teoria]

    # stimolo acceso: fascia grigia chiara per tutta la sua durata
    asse.axvspan(0, durata, color="0.93", zorder=0, linewidth=0)

    if teoria == "gnw":
        # finestre di ignition preregistrate: 0,3-0,5 s dopo accensione e dopo spegnimento
        for inizio in (0.0, durata):
            asse.axvspan(inizio + FINESTRA_IGNIZIONE[0], inizio + FINESTRA_IGNIZIONE[1],
                         color=colore, alpha=0.15, zorder=1, linewidth=0)

    curva = curva_iit(durata) if teoria == "iit" else curva_gnw(durata)
    asse.plot(t, curva, color=colore, linewidth=2.2, zorder=2)

    asse.set_xlim(t[0], t[-1])
    asse.set_ylim(-0.08, 1.2)
    asse.set_yticks([])
    for lato in ("top", "right", "left"):
        asse.spines[lato].set_visible(False)
    asse.set_xticks([0, 0.5, 1.0, 1.5, 2.0, 2.5])
    if ultima_riga:
        asse.set_xticklabels(["0", "0,5", "1,0", "1,5", "2,0", "2,5"])
        asse.set_xlabel("Tempo dall'accensione dello stimolo (s)")
    else:
        asse.tick_params(labelbottom=False)
    if prima_riga:
        if teoria == "iit":
            lettera(asse, "A", "IIT: corteccia posteriore")
        else:
            lettera(asse, "B", "GNWT: corteccia prefrontale")


def main():
    applica_stile()
    matplotlib.rcParams.update({"font.size": 10 * SCALA, "axes.titlesize": 11 * SCALA, "axes.labelsize": 10 * SCALA,
                                "xtick.labelsize": 9 * SCALA, "ytick.labelsize": 9 * SCALA,
                                "legend.fontsize": 9 * SCALA})
    fig, assi = plt.subplots(len(DURATE), 2, figsize=(11, 5.5), sharex=True)
    for riga, durata in enumerate(DURATE):
        for colonna, teoria in enumerate(("iit", "gnw")):
            disegna_riga(assi[riga, colonna], teoria, durata,
                         prima_riga=(riga == 0), ultima_riga=(riga == len(DURATE) - 1))
        assi[riga, 0].set_ylabel("stimolo\n{0} s".format(str(durata).replace(".", ",")),
                                 rotation=0, ha="right", va="center", fontsize=10 * SCALA)

    legenda = [Patch(color="0.93", label="stimolo acceso"),
               Patch(color=COLORI["gnw"], alpha=0.15,
                     label="finestre di ignition preregistrate (0,3\u20130,5 s dopo accensione e spegnimento)")]
    fig.legend(handles=legenda, loc="lower center", ncol=2)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    salva(fig, OUTPUT_DIR / "schema_predizione2")


if __name__ == "__main__":
    main()
