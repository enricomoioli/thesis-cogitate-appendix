# -*- coding: utf-8 -*-
"""
06_mappa_3d_elettrodi.py

Figura 4.2 della tesi: mappa 3D, sulla superficie piale di fsaverage, dei
contatti usati nell'analisi di sincronia del cap. 4 (serie definitiva
category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d):
- destinazioni nella regione visiva V1/V2 (approssimata con le etichette
  Destrieux S_calcarine, G_cuneus, G_oc-temp_med-Lingual, Pole_occipital) e
  nella regione prefrontale (12 etichette Destrieux), con i colori delle teorie;
- elettrodi selettivi per i volti e per gli oggetti (sorgenti), in grigio.

Fonte dei contatti: i file "_electrodes.tar.gz" salvati da synchrony_master.py
per le due ROI (colonne channels, x, y, z, roi_pick, face, object), cioe'
esattamente i contatti entrati nell'analisi (72 destinazioni V1/V2 in 12
pazienti, 585 prefrontali in 24, 183 elettrodi selettivi in 26).
Coordinate gia' in spazio fsaverage, in metri.

Versione precedente (29 ottobre rinominata da 08_mappa_3d_elettrodi_mne.py):
leggeva il manifest delle ROI del vecchio cap. 5.

Ambiente: quello creato dall'installer ufficiale MNE, che include lo stack
3D (pyvista, VTK, Qt). fsaverage in D:\\MNE_data. Richiede il disco E:.

Output (in figure_tesi\\output\\mappe_elettrodi\\):
    vista_<nome>.png       -- una immagine per angolazione
    mappa_3d_elettrodi.png / .pdf -- composizione delle viste con legenda

Uso (dal prompt MNE):
    python D:\\TESI\\manoscritto\\figure_tesi\\scripts\\06_mappa_3d_elettrodi.py
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import mne

from stile_tesi import applica_stile, lettera, salva

BIDS_ROOT = Path(r"E:\raw\ieeg_bids")  # verificare la lettera del disco esterno
RISULTATI = (BIDS_ROOT / "derivatives" / "synchrony_analysis" / "sub-super" / "ses-1" / "ieeg" / "results"
             / "category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"
             / "desbadcharej_notfil_lapref")
PREFISSO = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_"
SUBJECTS_DIR = Path(r"D:\MNE_data")
OUTPUT_DIR = Path(r"D:\TESI\manoscritto\figure_tesi\output\mappe_elettrodi")

# colori delle teorie per le destinazioni (stile_tesi.py), grigi per gli elettrodi selettivi
COLORI = {"iit": (0.12, 0.47, 0.71), "gnw": (0.84, 0.15, 0.16),
          "volti": (0.15, 0.15, 0.15), "oggetti": (0.5, 0.5, 0.5)}
ETICHETTE = {"iit": "Destinazioni V1/V2 (IIT)", "gnw": "Destinazioni prefrontali (GNWT)",
             "volti": "Elettrodi selettivi per i volti", "oggetti": "Elettrodi selettivi per gli oggetti"}
ORDINE = ("iit", "gnw", "volti", "oggetti")
ALPHA_PIALE = 0.25
DIMENSIONE_FINESTRA = (900, 900)
# fattore di ingrandimento del testo della composizione: nel PDF la figura viene
# ridotta all'80% della larghezza della pagina, quindi il testo va ingrandito
SCALA = 1.3
# Viste sezionate: si mostra solo cio' che sta da un lato di un piano.
# - laterali: piano sagittale mediano (x = 0), ogni vista mostra solo il proprio
#   emisfero, cosi' i contatti dell'emisfero opposto non compaiono in trasparenza;
# - anteriore/posteriore: piano coronale, soglie scelte sulla diagnostica 02
#   (le due ROI si sovrappongono tra -31 e -28.5 mm):
#   posteriore, y < -25 mm: tutti i contatti IIT, esclusi tutti i GNW tranne 2;
#   anteriore,  y > -20 mm: nessun contatto IIT, esclusi 7 GNW su 585.
# valore = (asse, verso, soglia in mm): verso +1 mantiene > soglia, -1 mantiene < soglia
SEZIONI = {
    "laterale_sinistra": ("x", -1, 0),
    "laterale_destra": ("x", 1, 0),
    "posteriore": ("y", -1, -25),
    "anteriore": ("y", 1, -20),
}

# Telecamera impostata direttamente su pyvista (set_3d_view veniva ignorato:
# nella prima esecuzione le quattro viste uscivano identiche, tutte frontali).
# Coordinate fsaverage in metri: x = destra, y = anteriore, z = superiore.
FUOCO = (0.0, -0.02, 0.01)
DISTANZA = 0.40
# nome: (direzione da cui guarda la telecamera, vettore "alto" dell'immagine)
VISTE = {
    "laterale_sinistra": ((-1, 0, 0), (0, 0, 1)),
    "laterale_destra": ((1, 0, 0), (0, 0, 1)),
    "anteriore": ((0, 1, 0), (0, 0, 1)),
    "posteriore": ((0, -1, 0), (0, 0, 1)),
    "ventrale": ((0, 0, -1), (0, 1, 0)),
}
TITOLI = {
    "laterale_sinistra": "Vista laterale, emisfero sinistro",
    "laterale_destra": "Vista laterale, emisfero destro",
    "anteriore": "Vista anteriore (sezione, y > {0} mm)".format(SEZIONI["anteriore"][2]),
    "posteriore": "Vista posteriore (sezione, y < {0} mm)".format(SEZIONI["posteriore"][2]),
    "ventrale": "Vista ventrale",
}
# lato dell'immagine (sinistra, destra) -> emisfero del cervello mostrato
# (nelle viste anteriore e ventrale destra e sinistra dell'immagine si invertono)
ORIENTAMENTO = {
    "anteriore": ("Dx", "Sx"),
    "posteriore": ("Sx", "Dx"),
    "ventrale": ("Dx", "Sx"),
}


def ritaglia_bianco(img, margine=10):
    """Toglie il bordo bianco attorno al cervello nello screenshot."""
    non_bianco = np.where(img[..., :3].min(axis=2) < 250)
    if len(non_bianco[0]) == 0:
        return img
    r0, r1 = non_bianco[0].min(), non_bianco[0].max()
    c0, c1 = non_bianco[1].min(), non_bianco[1].max()
    return img[max(r0 - margine, 0):r1 + margine, max(c0 - margine, 0):c1 + margine]


def uniforma_dimensioni(immagini):
    """Porta tutte le immagini alla stessa dimensione (bordo bianco centrato),
    cosi' i pannelli della figura composta restano allineati."""
    h = max(img.shape[0] for img in immagini.values())
    w = max(img.shape[1] for img in immagini.values())
    uniformate = {}
    for nome, img in immagini.items():
        tela = np.full((h, w, img.shape[2]), 255, dtype=img.dtype)
        r = (h - img.shape[0]) // 2
        c = (w - img.shape[1]) // 2
        tela[r:r + img.shape[0], c:c + img.shape[1]] = img
        uniformate[nome] = tela
    return uniformate


def imposta_sezione(plotter, sezione):
    """Applica (sezione = (asse, verso, soglia_mm)) o rimuove (sezione None) un
    piano di taglio a tutti gli oggetti della scena."""
    from vtkmodules.vtkCommonDataModel import vtkPlane
    piano = None
    if sezione is not None:
        asse, verso, soglia_mm = sezione
        i = "xyz".index(asse)
        origine = [0.0, 0.0, 0.0]
        normale = [0.0, 0.0, 0.0]
        origine[i] = soglia_mm / 1000.0
        normale[i] = float(verso)  # la parte mantenuta e' quella verso cui punta la normale
        piano = vtkPlane()
        piano.SetOrigin(*origine)
        piano.SetNormal(*normale)
    for attore in plotter.renderer.actors.values():
        mapper = getattr(attore, "mapper", None)
        if mapper is None:
            continue
        mapper.RemoveAllClippingPlanes()
        if piano is not None:
            mapper.AddClippingPlane(piano)


def carica_coordinate():
    """Ritorna (nomi, coordinate_m, gruppo_di_ogni_contatto) per i contatti dell'analisi
    di sincronia: destinazioni delle due ROI ed elettrodi selettivi (senza duplicati)."""
    tabelle = {}
    for roi in ("iit", "gnw"):
        file_name = RISULTATI / (PREFISSO + roi + "_dfc_tfr_electrodes.tar.gz")
        # salvato con DataFrame.to_pickle: e' un pickle compresso gzip, non un archivio tar
        tabelle[roi] = pd.read_pickle(file_name, compression="gzip")

    nomi, coords, gruppi = [], [], []
    def aggiungi(tabella, gruppo):
        for _, riga in tabella.iterrows():
            xyz = riga[["x", "y", "z"]].astype(float).values
            if not np.all(np.isfinite(xyz)):
                print("  coordinate non valide:", riga["channels"])
                continue
            nomi.append("{0}-{1}".format(gruppo, riga["channels"]))
            coords.append(xyz)
            gruppi.append(gruppo)

    for roi in ("iit", "gnw"):
        t = tabelle[roi]
        aggiungi(t[t["roi_pick"] == True], roi)
    tutti = pd.concat([tabelle["iit"], tabelle["gnw"]]).drop_duplicates("channels")
    aggiungi(tutti[tutti["face"] == True], "volti")
    aggiungi(tutti[tutti["object"] == True], "oggetti")
    for g in ORDINE:
        print("{0}: {1} contatti".format(g, gruppi.count(g)))
    return nomi, np.array(coords), gruppi


def main():
    nomi, coords, gruppi = carica_coordinate()
    print("Range x (metri attesi, ordine di grandezza 0.0x): [{0:.3f}, {1:.3f}]".format(
        coords[:, 0].min(), coords[:, 0].max()))

    SUBJECTS_DIR.mkdir(parents=True, exist_ok=True)
    mne.datasets.fetch_fsaverage(subjects_dir=SUBJECTS_DIR, verbose=True)

    montage = mne.channels.make_dig_montage(ch_pos=dict(zip(nomi, coords)), coord_frame="mri")
    montage.add_estimated_fiducials("fsaverage", SUBJECTS_DIR)
    trans = mne.channels.compute_native_head_t(montage)

    info = mne.create_info(ch_names=nomi, sfreq=1.0, ch_types="seeg")
    info.set_montage(montage)

    colori_contatti = np.array([COLORI[g] for g in gruppi])

    mne.viz.set_3d_backend("pyvistaqt")
    fig = mne.viz.create_3d_figure(size=DIMENSIONE_FINESTRA, bgcolor="white")
    mne.viz.plot_alignment(
        info, trans=trans, subject="fsaverage", subjects_dir=SUBJECTS_DIR,
        surfaces={"pial": ALPHA_PIALE}, coord_frame="mri",
        sensor_colors=colori_contatti, show_axes=False, fig=fig)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    immagini = {}
    plotter = fig.plotter
    for nome, (direzione, alto) in VISTE.items():
        posizione = tuple(f + DISTANZA * d for f, d in zip(FUOCO, direzione))
        plotter.camera_position = [posizione, FUOCO, alto]
        imposta_sezione(plotter, SEZIONI.get(nome))
        plotter.reset_camera_clipping_range()
        plotter.render()
        img = ritaglia_bianco(plotter.screenshot())
        immagini[nome] = img
        plt.imsave(str(OUTPUT_DIR / "vista_{0}.png".format(nome)), img)
        print("  salvata vista:", nome)
    imposta_sezione(plotter, None)
    immagini = uniforma_dimensioni(immagini)

    # 5 pannelli: due righe da due, ventrale centrata in basso
    applica_stile()
    matplotlib.rcParams.update({"axes.titlesize": 11 * SCALA})
    composta = plt.figure(figsize=(10, 15))
    griglia = composta.add_gridspec(3, 4)
    posizioni = [griglia[0, 0:2], griglia[0, 2:4], griglia[1, 0:2], griglia[1, 2:4], griglia[2, 1:3]]
    for lett, posizione, (nome, img) in zip("ABCDE", posizioni, immagini.items()):
        asse = composta.add_subplot(posizione)
        asse.imshow(img)
        lettera(asse, lett, TITOLI[nome])
        if nome in ORIENTAMENTO:
            sx, dx = ORIENTAMENTO[nome]
            # etichette appena sotto il cervello, ai suoi bordi (coordinate in pixel dell'immagine)
            righe, colonne = np.where(img[..., :3].min(axis=2) < 250)
            basso, bordo_sx, bordo_dx = righe.max(), colonne.min(), colonne.max()
            asse.text(bordo_sx, basso + 15, sx, fontsize=11 * SCALA, color="0.3", va="top", ha="left")
            asse.text(bordo_dx, basso + 15, dx, fontsize=11 * SCALA, color="0.3", va="top", ha="right")
        asse.axis("off")
    legenda = [Line2D([0], [0], marker="o", linestyle="", markersize=9 * SCALA,
                      markerfacecolor=COLORI[g], markeredgecolor="none",
                      label="{0} (n = {1})".format(ETICHETTE[g], gruppi.count(g)))
               for g in ORDINE]
    composta.legend(handles=legenda, loc="lower center", ncol=2, frameon=False, fontsize=11 * SCALA)
    composta.tight_layout(rect=(0, 0.06, 1, 1))
    salva(composta, OUTPUT_DIR / "mappa_3d_elettrodi")


if __name__ == "__main__":
    main()
