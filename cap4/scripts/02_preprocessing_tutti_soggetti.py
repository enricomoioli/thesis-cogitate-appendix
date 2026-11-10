"""
Preprocessing in a loop over all iEEG subjects already downloaded.

ENVIRONMENT: cogitate_ecog  (NOT ieeg_release)

USAGE:
    conda activate cogitate_ecog
    python D:\\TESI\\manoscritto\\cap4\\scripts\\02_preprocessing_tutti_soggetti.py

Each subject is launched as a separate process: if one fails, the loop moves
on to the next ones instead of stopping. At the end it prints a summary and
also writes it to a log file.

It can be restarted: subjects already preprocessed are skipped (the high_gamma
epoching file is used as proof of completion).

Expected time: about 13 minutes per subject on the laptop, measured on CF102.
With 38 subjects that is about 8 hours.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Paths: adapt them if the drive letter of the external disk changes
# --------------------------------------------------------------------------
BIDS_ROOT = Path("E:/raw/ieeg_bids")
IEEG_CODE = Path("D:/TESI/cogitate-msp1/coglib/ieeg")
CONFIG = IEEG_CODE / "Preprocessing" / "configs_locali" / "config_preprocessing_locale.json"
MASTER = IEEG_CODE / "Preprocessing" / "PreprocessingMaster.py"
LOG = Path("D:/TESI/manoscritto/cap4/log") / "log_preprocessing.txt"

SESSION = "1"
TASK = "Dur"
PREPROC_STEPS = "desbadcharej_notfil_lapref"

# --------------------------------------------------------------------------
# PYTHONPATH: the local modules of the repository are not pip packages,
# so it must be set or the imports fail. It is set here instead of
# relying on the user to remember it.
# --------------------------------------------------------------------------
env = os.environ.copy()
env["PYTHONPATH"] = str(IEEG_CODE)


def gia_preprocessato(subject):
    """True if the high_gamma epoching file already exists for this subject."""
    atteso = (BIDS_ROOT / "derivatives" / "preprocessing" / f"sub-{subject}" /
              f"ses-{SESSION}" / "ieeg" / "epoching" / "high_gamma" / PREPROC_STEPS /
              f"sub-{subject}_ses-{SESSION}_task-{TASK}_desc-epoching_ieeg-epo.fif")
    return atteso.is_file()


def trova_soggetti():
    """List the downloaded subjects, from the names of the sub-* folders in the BIDS root."""
    if not BIDS_ROOT.is_dir():
        print(f"ERRORE: {BIDS_ROOT} non esiste. Il disco esterno e' collegato?")
        sys.exit(1)
    soggetti = sorted(d.name.replace("sub-", "")
                      for d in BIDS_ROOT.iterdir()
                      if d.is_dir() and d.name.startswith("sub-"))
    return soggetti


def main():
    # Preliminary checks: better to fail now than in the middle of the night
    for percorso, descrizione in [(CONFIG, "file di configurazione"),
                                  (MASTER, "script di preprocessing")]:
        if not percorso.is_file():
            print(f"ERRORE: {descrizione} non trovato in {percorso}")
            sys.exit(1)

    soggetti = trova_soggetti()
    if not soggetti:
        print(f"Nessun soggetto trovato in {BIDS_ROOT}. Scaricarli prima.")
        sys.exit(1)

    da_fare = [s for s in soggetti if not gia_preprocessato(s)]
    gia_fatti = [s for s in soggetti if gia_preprocessato(s)]

    print(f"Soggetti trovati:        {len(soggetti)}")
    print(f"Gia' preprocessati:      {len(gia_fatti)}  {gia_fatti if gia_fatti else ''}")
    print(f"Da preprocessare adesso: {len(da_fare)}")
    print(f"Tempo stimato:           circa {len(da_fare) * 13} minuti "
          f"({len(da_fare) * 13 / 60:.1f} ore)")
    print()

    if not da_fare:
        print("Niente da fare, tutti i soggetti risultano gia' preprocessati.")
        return

    riusciti, falliti = [], []
    inizio_totale = datetime.now()

    for i, subject in enumerate(da_fare, start=1):
        print("=" * 70)
        print(f"[{i}/{len(da_fare)}] {subject} - avvio alle {datetime.now():%H:%M:%S}")
        print("=" * 70)
        inizio = datetime.now()
        # Folder for the full output of each subject: without it, a failure
        # leaves only the returncode and no way to understand what happened.
        # (lesson of 6 September: 33 subjects failed, all with returncode 1,
        #  and no trace of the reason)
        cartella_output = LOG.parent / "output_preprocessing"
        cartella_output.mkdir(exist_ok=True)
        file_output = cartella_output / f"{subject}.txt"
        try:
            with open(file_output, "w", encoding="utf-8", errors="replace") as fout:
                esito = subprocess.run(
                    [sys.executable, str(MASTER), str(CONFIG), "--subject", subject],
                    cwd=str(IEEG_CODE),
                    env=env,
                    stdout=fout,
                    stderr=subprocess.STDOUT,
                )
            durata = (datetime.now() - inizio).total_seconds() / 60
            if esito.returncode == 0 and gia_preprocessato(subject):
                riusciti.append(subject)
                print(f">>> {subject}: RIUSCITO in {durata:.1f} minuti")
            else:
                # Retrieve the last meaningful line of the output, usually the
                # exception message: this way the final summary says right away
                # what kind of error it is, without opening the files one by one.
                motivo = f"returncode {esito.returncode}"
                try:
                    righe_output = file_output.read_text(encoding="utf-8", errors="replace").splitlines()
                    ultime = [r.strip() for r in righe_output if r.strip()]
                    if ultime:
                        motivo += " | " + ultime[-1][:200]
                except Exception:
                    pass
                falliti.append((subject, motivo))
                print(f">>> {subject}: FALLITO dopo {durata:.1f} minuti - si prosegue")
                print(f"    {motivo}")
                print(f"    output completo in {file_output}")
        except Exception as e:
            falliti.append((subject, str(e)))
            print(f">>> {subject}: FALLITO con eccezione: {e} - si prosegue")

    durata_totale = (datetime.now() - inizio_totale).total_seconds() / 60

    # ----------------------------------------------------------------------
    # Summary on screen and in a file
    # ----------------------------------------------------------------------
    righe = []
    righe.append(f"Preprocessing concluso il {datetime.now():%Y-%m-%d %H:%M}")
    righe.append(f"Durata totale: {durata_totale:.0f} minuti ({durata_totale/60:.1f} ore)")
    righe.append(f"Riusciti ({len(riusciti)}): {', '.join(riusciti) if riusciti else '-'}")
    righe.append(f"Falliti ({len(falliti)}):")
    if falliti:
        for s, motivo in falliti:
            righe.append(f"    {s}  ->  {motivo}")
    else:
        righe.append("    nessuno")

    testo = "\n".join(righe)
    print("\n" + "=" * 70)
    print(testo)
    print("=" * 70)

    with open(LOG, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 70 + "\n" + testo + "\n")
    print(f"\nRiepilogo aggiunto anche in {LOG}")


if __name__ == "__main__":
    main()
