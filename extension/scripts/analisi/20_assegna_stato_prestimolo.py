# -*- coding: utf-8 -*-
"""
20 - Assignment of trials to "high state" and "low state" (chapter 5).

For each patient, selective electrode and category (faces, objects):
  1. chapter 4 trials: onset, task-irrelevant, faces and objects, 1.0 and 1.5 s;
  2. pre-stimulus LZC (-500/0 ms): binarization on the median of the window,
     Lempel-Ziv count, length normalization (Wolff et al. 2019);
  3. alpha power (8-13 Hz) in the same window, for the spectral control;
  4. exclusion of the trials whose previous stimulus went off less than 1.0 s before;
  5. median split of LZC: above = "alto" (high), below = "basso" (low),
     equal to the median = excluded.

Looks only at LZC, not at the DFC. Output: a table with one row per trial and
electrode, in D:/TESI/manoscritto/extension/results/stato_prestimolo/assegnazione_prove.csv

Cells:
  1. libraries, parameters and basic functions
  2. the function that processes ONE patient (same steps built in Spyder)
  3. test on one patient, with checks
  4. all patients and saving
"""

# %% 1. Libraries, parameters and basic functions

from pathlib import Path
import mne
import numpy as np
import pandas as pd

PAZIENTE_DI_PROVA = "CE120"
BIDS = Path("E:/raw/ieeg_bids")
FINESTRA_INIZIO, FINESTRA_FINE = -0.5, 0.0          # seconds
SOGLIA_SPEGNIMENTO = 1.0                            # seconds since the previous offset
CARTELLA_USCITA = Path("D:/TESI/manoscritto/extension/results/stato_prestimolo")

CARTELLA_ELETTRODI = (BIDS / "derivatives" / "synchrony_analysis" / "sub-super" / "ses-1" / "ieeg"
                      / "results" / "category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"
                      / "desbadcharej_notfil_lapref")


def conta_parole_nuove_lz(sequenza):
    """Lempel-Ziv (1976), Kaspar and Schuster algorithm (1987).
    Takes a sequence of 0s and 1s; returns how many "new words" are met
    reading it from left to right. Checked on the classic example 0001101001000101 -> 6."""
    n = len(sequenza)
    i, k, l, conteggio, k_max = 0, 1, 1, 1, 1
    while True:
        if sequenza[i + k - 1] == sequenza[l + k - 1]:
            k += 1
            if l + k > n:
                conteggio += 1
                break
        else:
            if k > k_max:
                k_max = k
            i += 1
            if i == l:
                conteggio += 1
                l += k_max
                if l + 1 > n:
                    break
                i, k, k_max = 0, 1, 1
            else:
                k = 1
    return conteggio


def lzc_normalizzata(segnale):
    """LZC of a signal: binarization on the median, count, length normalization."""
    sequenza_binaria = (segnale >= np.median(segnale)).astype(int)
    lunghezza = len(sequenza_binaria)
    return conta_parole_nuove_lz(sequenza_binaria) / (lunghezza / np.log2(lunghezza))


# table of the selective electrodes of the _v1v2d series (same for all patients: read once)
elettrodi = pd.concat([
    pd.read_pickle(CARTELLA_ELETTRODI / "sub-super_ses-1_task-Dur_ana-synchrony_analysis_iit_dfc_tfr_electrodes.tar.gz",
                   compression="gzip"),
    pd.read_pickle(CARTELLA_ELETTRODI / "sub-super_ses-1_task-Dur_ana-synchrony_analysis_gnw_dfc_tfr_electrodes.tar.gz",
                   compression="gzip"),
])
elettrodi = elettrodi[elettrodi["face"] | elettrodi["object"]].drop_duplicates(subset=["channels"])


# %% 2. The function that processes one patient

def elabora_paziente(paziente):

    # --- a. load the epochs (as in cell 2 built in Spyder)
    file_epoche = (BIDS / "derivatives" / "preprocessing" / f"sub-{paziente}" / "ses-1" / "ieeg"
                   / "epoching" / "broadband" / "desbadcharej_notfil_lapref"
                   / f"sub-{paziente}_ses-1_task-Dur_desc-epoching_ieeg-epo.fif")
    epoche_tutte = mne.read_epochs(file_epoche, preload=False, verbose="ERROR")
    metadati = epoche_tutte.metadata

    # --- b. select the chapter 4 trials (cell 3)
    cond_accensione = metadati["event type"] == "stimulus onset"
    cond_irrilevante = metadati["task_relevance"] == "Irrelevant"
    cond_categoria = metadati["category"].isin(["face", "object"])
    cond_durata = metadati["duration"].isin(["1000ms", "1500ms"])
    prove_scelte = cond_accensione & cond_irrilevante & cond_categoria & cond_durata

    # --- c. the patient's selective electrodes (cell 4)
    elettrodi_selettivi = elettrodi[elettrodi["channels"].str.startswith(paziente + "-")]
    nomi_con_prefisso = elettrodi_selettivi["channels"].tolist()
    nomi_canali = [nome.replace(paziente + "-", "", 1) for nome in nomi_con_prefisso]
    preferenza = ["volti" if volti else "oggetti" for volti in elettrodi_selettivi["face"]]

    # --- d. data of the pre-stimulus window (cell 5)
    epoche_scelte = epoche_tutte[prove_scelte.values]
    epoche_scelte.load_data()
    epoche_scelte.pick(nomi_canali)
    epoche_scelte.crop(tmin=FINESTRA_INIZIO, tmax=FINESTRA_FINE, include_tmax=False)
    dati_prestimolo = epoche_scelte.get_data()             # trials x electrodes x samples
    numero_prove, numero_elettrodi, numero_campioni = dati_prestimolo.shape
    frequenza_campionamento = epoche_scelte.info["sfreq"]

    # --- e. LZC for each trial and electrode (cells 6-7)
    lzc_tutte = np.zeros((numero_prove, numero_elettrodi))
    for prova in range(numero_prove):
        for elettrodo in range(numero_elettrodi):
            lzc_tutte[prova, elettrodo] = lzc_normalizzata(dati_prestimolo[prova, elettrodo, :])

    # --- f. alpha power (8-13 Hz) in the same window, for the spectral control
    densita, frequenze = mne.time_frequency.psd_array_welch(
        dati_prestimolo, frequenza_campionamento, fmin=8, fmax=13, n_fft=numero_campioni, verbose="ERROR")
    alfa_log10 = np.log10(densita.mean(axis=-1))            # trials x electrodes

    # --- g. distance from the offset of the previous stimulus (from the BIDS events)
    eventi = pd.read_csv(BIDS / f"sub-{paziente}" / "ses-1" / "ieeg" / f"sub-{paziente}_ses-1_task-Dur_events.tsv",
                         sep="\t", encoding="utf-8-sig").sort_values("onset").reset_index(drop=True)
    parti = eventi["trial_type"].str.split("/", expand=True)
    eventi["tipo"] = parti[0]
    chiavi = ["block", "miniblock", "category", "identity", "orientation", "duration", "task_relevance"]
    for posizione, chiave in enumerate(chiavi, start=1):
        eventi[chiave] = parti[posizione]
    # time of the last offset BEFORE each event
    ultimo_spegnimento = eventi["onset"].where(eventi["tipo"] == "stimulus offset").ffill().shift(1)
    accensioni = eventi[eventi["tipo"] == "stimulus onset"].copy()
    accensioni["distanza_spegnimento"] = accensioni["onset"] - ultimo_spegnimento[accensioni.index]

    # match epochs and events: same keys; repetitions are matched in their temporal order
    accensioni["occorrenza"] = accensioni.groupby(chiavi).cumcount()
    prove_tabella = metadati[prove_scelte][chiavi].astype(str).reset_index(drop=True)
    prove_tabella["tempo_epoca"] = epoche_scelte.events[:, 0] / frequenza_campionamento
    prove_tabella["campione_evento"] = epoche_scelte.events[:, 0]
    prove_tabella["occorrenza"] = prove_tabella.groupby(chiavi).cumcount()
    prove_tabella = prove_tabella.merge(accensioni[chiavi + ["occorrenza", "onset", "distanza_spegnimento"]],
                                        on=chiavi + ["occorrenza"], how="left")
    # check: if the matching is right, events and epochs have the same time (difference ~0)
    assert prove_tabella["onset"].notna().all(), f"{paziente}: prove non abbinate agli eventi"
    scarto = (prove_tabella["onset"] - prove_tabella["tempo_epoca"]).abs().max()
    assert scarto < 0.01, f"{paziente}: abbinamento epoche-eventi non affidabile (scarto {scarto:.3f} s)"
    # a trial with no previous offset (the first of the recording) is preceded only by a pause:
    # infinite distance, so it is not excluded
    senza_precedente = prove_tabella["distanza_spegnimento"].isna()
    if senza_precedente.any():
        print(f"  {paziente}: {senza_precedente.sum()} prova/e senza stimolo precedente (tenute)")
    prove_tabella["distanza_spegnimento"] = prove_tabella["distanza_spegnimento"].fillna(np.inf)

    # --- h. long table: one row per trial and electrode
    righe = []
    for prova in range(numero_prove):
        for elettrodo in range(numero_elettrodi):
            righe.append({
                "paziente": paziente,
                "canale": nomi_con_prefisso[elettrodo],
                "preferenza": preferenza[elettrodo],
                "campione_evento": int(prove_tabella.loc[prova, "campione_evento"]),
                "blocco": prove_tabella.loc[prova, "block"],
                "categoria": prove_tabella.loc[prova, "category"],
                "durata": prove_tabella.loc[prova, "duration"],
                "distanza_spegnimento": prove_tabella.loc[prova, "distanza_spegnimento"],
                "lzc": lzc_tutte[prova, elettrodo],
                "alfa_log10": alfa_log10[prova, elettrodo],
            })
    tabella = pd.DataFrame(righe)

    # --- i. exclusions and median split (per electrode and category)
    tabella["stato"] = "da_assegnare"
    tabella.loc[tabella["distanza_spegnimento"] < SOGLIA_SPEGNIMENTO, "stato"] = "escluso_spegnimento"
    tenute = tabella["stato"] == "da_assegnare"
    mediana = tabella[tenute].groupby(["canale", "categoria"])["lzc"].transform("median")
    tabella.loc[tenute & (tabella["lzc"] > mediana.reindex(tabella.index)), "stato"] = "alto"
    tabella.loc[tenute & (tabella["lzc"] < mediana.reindex(tabella.index)), "stato"] = "basso"
    tabella.loc[tenute & (tabella["lzc"] == mediana.reindex(tabella.index)), "stato"] = "escluso_pareggio"
    assert not (tabella["stato"] == "da_assegnare").any(), f"{paziente}: prove non assegnate"

    return tabella


# %% 3. Test on one patient, with checks

tabella_prova = elabora_paziente(PAZIENTE_DI_PROVA)
print(tabella_prova.head())
print(tabella_prova["stato"].value_counts())
# for each electrode and category: how many high and how many low trials (they should be similar)
print(tabella_prova.groupby(["canale", "categoria"])["stato"].value_counts().unstack(fill_value=0).head(10))

# %% 4. All patients and saving

pazienti = sorted(elettrodi["channels"].str.split("-").str[0].unique())
tabelle = []
for numero, paziente in enumerate(pazienti, start=1):
    print(f"[{numero}/{len(pazienti)}] {paziente}")
    tabelle.append(elabora_paziente(paziente))
assegnazione = pd.concat(tabelle, ignore_index=True)

CARTELLA_USCITA.mkdir(parents=True, exist_ok=True)
assegnazione.to_csv(CARTELLA_USCITA / "assegnazione_prove.csv", index=False)

riepilogo = (assegnazione.drop_duplicates(["paziente", "canale", "campione_evento"])
             .groupby("paziente")["stato"].value_counts().unstack(fill_value=0))
print(riepilogo)
print(f"Elettrodi: {assegnazione['canale'].nunique()}, pazienti: {assegnazione['paziente'].nunique()}")
print(f"Salvato in {CARTELLA_USCITA / 'assegnazione_prove.csv'}")
