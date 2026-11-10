"""
Scarica tutti i soggetti iEEG del consorzio Cogitate da XNAT.

AMBIENTE: ieeg_release  (NON cogitate_ecog: xnat_download vive in cog_ieeg,
                         installato solo in ieeg_release)

USO:
    conda activate ieeg_release
    python D:\\TESI\\manoscritto\\cap4\\scripts\\01_scarica_soggetti.py

Chiede username e password XNAT UNA VOLTA all'inizio, poi procede da solo.
E' ripartibile: i soggetti gia' presenti vengono saltati.

ATTENZIONE: se l'esecuzione si interrompe a meta' di un soggetto, resta una
cartella parziale che al riavvio verra' saltata come se fosse completa.
In quel caso cancellare a mano la cartella del soggetto interrotto prima
di rilanciare (l'ultimo soggetto nominato a schermo prima dell'interruzione).
"""

from cog_ieeg.utils import set_bids_root, get_bids_root
from cog_ieeg.xnat_utilities import xnat_download

BIDS_ROOT = "E:/raw/ieeg_bids"

set_bids_root(BIDS_ROOT)
print("bids_root impostato su:", get_bids_root())
print()
print("Sto per scaricare TUTTI i soggetti del progetto.")
print("Il bundle completo e' circa 98 GB: verifica lo spazio libero su E: prima di procedere.")
print("I soggetti gia' scaricati verranno saltati automaticamente.")
print()

# subjects_to_download=None  ->  scarica tutti i soggetti presenti nel progetto
# overwrite=False            ->  salta quelli gia' presenti in locale
xnat_download(None, overwrite=False)

print()
print("Download concluso.")
