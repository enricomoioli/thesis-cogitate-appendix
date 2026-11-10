# -*- coding: utf-8 -*-
"""
06_mappa_3d_elettrodi.py

Figure 4.2 of the thesis: 3D map, on the pial surface of fsaverage, of the
contacts used in the synchrony analysis of chapter 4 (final series
category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d):
- targets in the visual region V1/V2 (approximated with the Destrieux labels
  S_calcarine, G_cuneus, G_oc-temp_med-Lingual, Pole_occipital) and in the
  prefrontal region (12 Destrieux labels), in the theory colours;
- face-selective and object-selective electrodes (sources), in grey.

Source of the contacts: the "_electrodes.tar.gz" files saved by synchrony_master.py
for the two ROIs (columns channels, x, y, z, roi_pick, face, object), i.e.
exactly the contacts that entered the analysis (72 V1/V2 targets in 12
patients, 585 prefrontal in 24, 183 selective electrodes in 26).
Coordinates already in fsaverage space, in metres.

Previous version (renamed on 29 October from 08_mappa_3d_elettrodi_mne.py):
it read the ROI manifest of the old chapter 5.

Environment: the one created by the official MNE installer, which includes the
3D stack (pyvista, VTK, Qt). fsaverage in D:\\MNE_data. Requires drive E:.

Output (in figure_tesi\\output\\mappe_elettrodi\\):
    vista_<nome>.png       -- one image per view
    mappa_3d_elettrodi.png / .pdf -- composition of the views with legend

Usage (from the MNE prompt):
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

BIDS_ROOT = Path(r"E:\raw\ieeg_bids")  # check the drive letter of the external disk
RISULTATI = (BIDS_ROOT / "derivatives" / "synchrony_analysis" / "sub-super" / "ses-1" / "ieeg" / "results"
             / "category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"
             / "desbadcharej_notfil_lapref")
PREFISSO = "sub-super_ses-1_task-Dur_ana-synchrony_analysis_"
SUBJECTS_DIR = Path(r"D:\MNE_data")
OUTPUT_DIR = Path(r"D:\TESI\manoscritto\figure_tesi\output\mappe_elettrodi")

# theory colours for the targets (stile_tesi.py), greys for the selective electrodes
COLORI = {"iit": (0.12, 0.47, 0.71), "gnw": (0.84, 0.15, 0.16),
          "volti": (0.15, 0.15, 0.15), "oggetti": (0.5, 0.5, 0.5)}
ETICHETTE = {"iit": "Destinazioni V1/V2 (IIT)", "gnw": "Destinazioni prefrontali (GNWT)",
             "volti": "Elettrodi selettivi per i volti", "oggetti": "Elettrodi selettivi per gli oggetti"}
ORDINE = ("iit", "gnw", "volti", "oggetti")
ALPHA_PIALE = 0.25
DIMENSIONE_FINESTRA = (900, 900)
# text magnification factor of the composition: in the PDF the figure is
# shrunk to 80% of the page width, so the text must be enlarged
SCALA = 1.3
# Sectioned views: only what lies on one side of a plane is shown.
# - lateral: mid-sagittal plane (x = 0), each view shows only its own
#   hemisphere, so contacts of the opposite hemisphere do not show through;
# - anterior/posterior: coronal plane, thresholds chosen on diagnostic 02
#   (the two ROIs overlap between -31 and -28.5 mm):
#   posterior, y < -25 mm: all IIT contacts, all GNW excluded except 2;
#   anterior,  y > -20 mm: no IIT contact, 7 GNW out of 585 excluded.
# value = (axis, direction, threshold in mm): direction +1 keeps > threshold, -1 keeps < threshold
SEZIONI = {
    "laterale_sinistra": ("x", -1, 0),
    "laterale_destra": ("x", 1, 0),
    "posteriore": ("y", -1, -25),
    "anteriore": ("y", 1, -20),
}

# Camera set directly through pyvista (set_3d_view was ignored:
# in the first run the four views came out identical, all frontal).
# fsaverage coordinates in metres: x = right, y = anterior, z = superior.
FUOCO = (0.0, -0.02, 0.01)
DISTANZA = 0.40
# name: (direction the camera looks from, "up" vector of the image)
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
# side of the image (left, right) -> hemisphere of the brain shown
# (in the anterior and ventral views left and right of the image are swapped)
ORIENTAMENTO = {
    "anteriore": ("Dx", "Sx"),
    "posteriore": ("Sx", "Dx"),
    "ventrale": ("Dx", "Sx"),
}


def ritaglia_bianco(img, margine=10):
    """Remove the white border around the brain in the screenshot."""
    non_bianco = np.where(img[..., :3].min(axis=2) < 250)
    if len(non_bianco[0]) == 0:
        return img
    r0, r1 = non_bianco[0].min(), non_bianco[0].max()
    c0, c1 = non_bianco[1].min(), non_bianco[1].max()
    return img[max(r0 - margine, 0):r1 + margine, max(c0 - margine, 0):c1 + margine]


def uniforma_dimensioni(immagini):
    """Bring all images to the same size (centred white border),
    so that the panels of the composite figure stay aligned."""
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
    """Apply (sezione = (axis, direction, threshold_mm)) or remove (sezione None) a
    clipping plane on all the objects in the scene."""
    from vtkmodules.vtkCommonDataModel import vtkPlane
    piano = None
    if sezione is not None:
        asse, verso, soglia_mm = sezione
        i = "xyz".index(asse)
        origine = [0.0, 0.0, 0.0]
        normale = [0.0, 0.0, 0.0]
        origine[i] = soglia_mm / 1000.0
        normale[i] = float(verso)  # the part kept is the one the normal points to
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
    """Return (names, coordinates_m, group_of_each_contact) for the contacts of the
    synchrony analysis: targets of the two ROIs and selective electrodes (no duplicates)."""
    tabelle = {}
    for roi in ("iit", "gnw"):
        file_name = RISULTATI / (PREFISSO + roi + "_dfc_tfr_electrodes.tar.gz")
        # saved with DataFrame.to_pickle: it is a gzip-compressed pickle, not a tar archive
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

    # 5 panels: two rows of two, ventral centred at the bottom
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
            # labels just below the brain, at its edges (pixel coordinates of the image)
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
