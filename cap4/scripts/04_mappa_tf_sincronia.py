#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mappa tempo-frequenza dei contrasti di connettivita' (dfc_tfr).

Mediare sulle frequenze per disegnare una curva va bene per dfc a banda
singola, ma con dfc_tfr
(104 frequenze da 2 a 180 Hz) diluisce qualunque effetto confinato a una banda
stretta. Il paper riporta l'effetto nella gamma: mediando su tutto lo spettro lo si
annacqua fino a renderlo invisibile.

Questo script mostra invece il piano tempo-frequenza completo, senza mediare:
  - riga 1: connettivita' media per le prove della categoria preferita
  - riga 2: connettivita' media per le prove dell'altra categoria
  - riga 3: la differenza fra le due, con il contorno delle finestre significative
Piu' un profilo spettrale che indica in quale banda (se in una) la differenza si
concentra, mediata sulla sola finestra post-stimolo.

Uso, dalla cartella coglib\\ieeg con l'ambiente cogitate_ecog attivo:

    python D:\\TESI\\manoscritto\\cap4\\scripts\\04_mappa_tf_sincronia.py NOME_ANALISI [roi]

Esempio:
    python D:\\TESI\\manoscritto\\cap4\\scripts\\04_mappa_tf_sincronia.py category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act gnw

Se la roi non e' indicata, le elabora entrambe.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(r"E:\raw\ieeg_bids\derivatives\synchrony_analysis\sub-super\ses-1\ieeg\results")
PREPROC = "desbadcharej_notfil_lapref"
PREFIX = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_"
OUT_DIR = Path(r"D:\TESI\manoscritto\cap4\figure_lavoro")

# Finestra su cui calcolare il profilo spettrale (post-stimolo, escludendo i bordi
# dove la finestra scorrevole sporge oltre i dati e produce artefatti).
FINESTRA_PROFILO = (0.0, 1.5)
# Margine da escludere a ciascun estremo per gli artefatti di bordo.
MARGINE_BORDI = 0.15
# Basale per le due mappe in alto: ogni frequenza e' espressa come variazione
# percentuale rispetto alla propria media in questa finestra pre-stimolo. Senza
# normalizzazione la scala e' dominata dalle basse frequenze (connettivita' ~10 volte
# piu' alta sotto i 10 Hz) e il resto del piano risulta piatto.
FINESTRA_BASALE = (-0.5, -0.1)


def carica(nome_analisi, roi):
    cartella = BASE / nome_analisi / PREPROC
    candidati = sorted(cartella.glob("{0}{1}_*.npz".format(PREFIX, roi)))
    if not candidati:
        print("Nessun file trovato per la ROI {0} in {1}".format(roi, cartella))
        return None
    return np.load(candidati[0], allow_pickle=True)


def maschera_senza_bordi(tempi):
    """Esclude i primi e ultimi MARGINE_BORDI secondi (artefatti della finestra scorrevole)."""
    return (tempi > tempi.min() + MARGINE_BORDI) & (tempi < tempi.max() - MARGINE_BORDI)


def disegna(nome_analisi, roi, dati):
    tempi = np.asarray(dati["analysis_time"])
    freqs = np.asarray(dati["freqs"]) if dati["freqs"] is not None else None

    if freqs is None or freqs.size <= 1:
        print("ROI {0}: una sola banda, la mappa tempo-frequenza non si applica.".format(roi))
        return

    pannelli = [
        ("volti", dati["cat1_to_cat1"], dati["cat1_to_cat2"], dati["p_values_fac_selective"]),
        # secondo indice = categoria letterale del trial (1=volti, 2=oggetti):
        # per gli elettrodi-oggetti i trial preferiti sono cat2_to_cat2.
        ("oggetti", dati["cat2_to_cat2"], dati["cat2_to_cat1"], dati["p_values_obj_selective"]),
    ]

    validi = maschera_senza_bordi(tempi)

    for etichetta, a, b, p in pannelli:
        a = np.asarray(a)
        b = np.asarray(b)
        if a.size == 0 or b.size == 0 or a.ndim != 3:
            print("ROI {0}, {1}: nessun dato.".format(roi, etichetta))
            continue

        n = a.shape[0]
        media_a = a.mean(0)          # (n_freqs, n_tempi)
        media_b = b.mean(0)
        differenza = media_a - media_b

        p = np.asarray(p)
        sig = None
        if p.size and p.shape == differenza.shape:
            sig = (p < 0.05)

        fig = plt.figure(figsize=(13, 9))

        # --- tre mappe tempo-frequenza ---
        # in alto: variazione percentuale rispetto al basale pre-stimolo, per frequenza
        basale = (tempi >= FINESTRA_BASALE[0]) & (tempi <= FINESTRA_BASALE[1])
        rel_a = 100 * (media_a / media_a[:, basale].mean(1, keepdims=True) - 1)
        rel_b = 100 * (media_b / media_b[:, basale].mean(1, keepdims=True) - 1)
        lim_rel = np.percentile(np.abs(np.concatenate([rel_a[:, validi], rel_b[:, validi]])), 99)

        ax1 = plt.subplot(2, 2, 1)
        m = ax1.pcolormesh(tempi[validi], freqs, rel_a[:, validi], cmap="RdBu_r",
                           vmin=-lim_rel, vmax=lim_rel, shading="auto")
        ax1.axvline(0, color="k", ls="--", lw=1)
        ax1.set_title("prove {0} (n={1} elettrodi), % rispetto al basale".format(etichetta, n))
        ax1.set_ylabel("frequenza (Hz)")
        plt.colorbar(m, ax=ax1)

        ax2 = plt.subplot(2, 2, 2)
        m = ax2.pcolormesh(tempi[validi], freqs, rel_b[:, validi], cmap="RdBu_r",
                           vmin=-lim_rel, vmax=lim_rel, shading="auto")
        ax2.axvline(0, color="k", ls="--", lw=1)
        ax2.set_title("prove altra categoria, % rispetto al basale")
        plt.colorbar(m, ax=ax2)

        ax3 = plt.subplot(2, 2, 3)
        limite = np.abs(differenza[:, validi]).max()
        m = ax3.pcolormesh(tempi[validi], freqs, differenza[:, validi],
                           cmap="RdBu_r", vmin=-limite, vmax=limite, shading="auto")
        ax3.axvline(0, color="k", ls="--", lw=1)
        ax3.set_title("differenza (preferita - altra)")
        ax3.set_xlabel("tempo dall'onset (s)")
        ax3.set_ylabel("frequenza (Hz)")
        plt.colorbar(m, ax=ax3)
        if sig is not None and sig.any():
            ax3.contour(tempi[validi], freqs, sig[:, validi], levels=[0.5], colors="k", linewidths=1.5)

        # --- profilo spettrale della differenza, finestra post-stimolo ---
        ax4 = plt.subplot(2, 2, 4)
        finestra = (tempi >= FINESTRA_PROFILO[0]) & (tempi <= FINESTRA_PROFILO[1])
        # errore standard fra elettrodi, per banda, mediato sulla finestra post-stimolo
        per_elettrodo = (a - b)[:, :, finestra].mean(2)   # (n_elettrodi, n_freqs)
        profilo = per_elettrodo.mean(0)
        sem = per_elettrodo.std(0) / np.sqrt(max(n - 1, 1))

        ax4.plot(freqs, profilo, color="k")
        ax4.fill_between(freqs, profilo - sem, profilo + sem, alpha=0.3, color="k")
        ax4.axhline(0, color="gray", ls="--", lw=1)
        ax4.set_xlabel("frequenza (Hz)")
        ax4.set_ylabel("differenza media")
        ax4.set_title("profilo spettrale, {0}-{1} s".format(*FINESTRA_PROFILO))
        # bande di riferimento
        for f0, f1, nome in [(8, 13, "alfa"), (13, 30, "beta"), (30, 70, "gamma"), (70, 150, "alta gamma")]:
            if freqs.max() >= f0:
                ax4.axvspan(f0, min(f1, freqs.max()), alpha=0.08, color="C0")
                ax4.text((f0 + min(f1, freqs.max())) / 2, ax4.get_ylim()[1] * 0.92, nome,
                         ha="center", fontsize=8, color="C0")

        plt.suptitle("{0} - {1} - elettrodi selettivi per {2}".format(nome_analisi, roi.upper(), etichetta))
        plt.tight_layout()

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        percorso = OUT_DIR / "{0}_{1}_{2}_tf.png".format(nome_analisi, roi, etichetta)
        plt.savefig(str(percorso), dpi=140)
        plt.close(fig)
        print("Salvato: {0}".format(percorso))

        # --- riepilogo numerico, per non doverlo dedurre a occhio dalla figura ---
        banda_max = freqs[np.argmax(np.abs(profilo))]
        print("    picco della differenza a {0:.0f} Hz (valore {1:+.5f})".format(
            banda_max, profilo[np.argmax(np.abs(profilo))]))
        rapporto = np.abs(profilo).max() / (np.abs(media_a[:, validi]).mean())
        print("    ampiezza del picco rispetto al livello medio di connettivita': {0:.1%}".format(rapporto))
        if sig is not None:
            print("    celle tempo-frequenza significative: {0} su {1}".format(
                int(sig.sum()), sig.size))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    nome_analisi = sys.argv[1]
    rois = [sys.argv[2]] if len(sys.argv) > 2 else ["iit", "gnw"]

    for roi in rois:
        dati = carica(nome_analisi, roi)
        if dati is None:
            continue
        print("\n" + "=" * 60)
        print("ROI: {0}".format(roi))
        print("=" * 60)
        disegna(nome_analisi, roi, dati)


if __name__ == "__main__":
    main()
