"""
Download all iEEG subjects of the Cogitate consortium from XNAT.

ENVIRONMENT: ieeg_release  (NOT cogitate_ecog: xnat_download lives in cog_ieeg,
                            installed only in ieeg_release)

USAGE:
    conda activate ieeg_release
    python D:\\TESI\\manoscritto\\cap4\\scripts\\01_scarica_soggetti.py

Asks for the XNAT username and password ONCE at the start, then runs on its own.
It can be restarted: subjects already present are skipped.

WARNING: if the run is interrupted halfway through a subject, a partial folder
is left behind and will be skipped on restart as if it were complete.
In that case delete the folder of the interrupted subject by hand before
restarting (the last subject named on screen before the interruption).
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

# subjects_to_download=None  ->  download all subjects in the project
# overwrite=False            ->  skip those already present locally
xnat_download(None, overwrite=False)

print()
print("Download concluso.")
