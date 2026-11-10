# -*- coding: utf-8 -*-
"""
04_schema_predizioni.py

Stylized diagram of COGITATE prediction 2 (maintenance of conscious content
over time), redrawn from Fig. 1a (central panel) of Cogitate Consortium (2025):

- IIT, posterior cortex: sustained activation for the whole duration of the
  stimulus, return to baseline after offset;
- GNWT, prefrontal cortex: brief ignition 0.3-0.5 s after onset and
  0.3-0.5 s after offset, independent of duration, activity practically
  absent in between (Methods, "Duration analysis").

The curves are stylized predictions, not data: the vertical axis has no unit.
Three stimulus durations (0.5 / 1.0 / 1.5 s), as in the paradigm: one row
per duration, as in the original figure, so that each offset ignition can be
attributed unambiguously to its own stimulus.

Legend at the bottom: grey band = stimulus on; pink band = preregistered
ignition windows. That the vertical axis has no unit is stated in the
caption.

Only matplotlib/numpy: runs in any environment (e.g. the MNE one).

Output (in figure_tesi\\output\\schemi\\):
    schema_predizione2.png (300 dpi) and schema_predizione2.pdf (vector)

Usage:
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\04_schema_predizioni.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# text magnification factor: in the PDF the figure is shrunk to the
# page width, so the text must be enlarged accordingly
SCALA = 1.3

from stile_tesi import COLORI, GRIGIO_SCURO, applica_stile, lettera, salva

OUTPUT_DIR = Path(r"D:\TESI\manoscritto\figure_tesi\output\schemi")

DURATE = (0.5, 1.0, 1.5)
FINESTRA_IGNIZIONE = (0.3, 0.5)  # s after onset and after offset (preregistered)

t = np.linspace(-0.4, 2.5, 3000)


def sigmoide(x, tau=0.03):
    return 1.0 / (1.0 + np.exp(-x / tau))


def curva_iit(durata):
    """Plateau: rises at onset, stays high for the duration, returns to baseline."""
    return sigmoide(t - 0.1) * (1.0 - sigmoide(t - durata - 0.1))


def curva_gnw(durata):
    """Two brief ignitions, centred in the 0.3-0.5 s window after onset and offset."""
    centro = np.mean(FINESTRA_IGNIZIONE)
    ampiezza = 0.045
    return (np.exp(-0.5 * ((t - centro) / ampiezza) ** 2)
            + np.exp(-0.5 * ((t - durata - centro) / ampiezza) ** 2))


def disegna_riga(asse, teoria, durata, prima_riga, ultima_riga):
    colore = COLORI[teoria]

    # stimulus on: light grey band for its whole duration
    asse.axvspan(0, durata, color="0.93", zorder=0, linewidth=0)

    if teoria == "gnw":
        # preregistered ignition windows: 0.3-0.5 s after onset and after offset
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
