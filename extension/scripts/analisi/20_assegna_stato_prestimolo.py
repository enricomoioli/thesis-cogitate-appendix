# -*- coding: utf-8 -*-
"""
20 - Assegnazione delle prove a "stato alto" e "stato basso" (cap. 5).

Per ogni paziente, elettrodo selettivo e categoria (volti, oggetti):
  1. prove del cap. 4: accensione, irrilevanti, volti e oggetti, 1,0 e 1,5 s;
  2. LZC pre-stimolo (-500/0 ms): binarizzazione sulla mediana della finestra,
     conteggio di Lempel-Ziv, normalizzazione per lunghezza (Wolff et al. 2019);
  3. potenza alfa (8-13 Hz) nella stessa finestra, per il controllo spettrale;
  4. esclusione delle prove con lo spegnimento dello stimolo precedente a meno di 1,0 s;
  5. divisione per mediana della LZC: sopra = "alto", sotto = "basso",
     pari alla mediana = esclusa.

Guarda solo la LZC, non la DFC. Uscita: una tabella con una riga per prova ed elettrodo,
in D:/TESI/manoscritto/extension/results/stato_prestimolo/assegnazione_prove.csv

Celle:
  1. librerie, parametri e funzioni di base
  2. la funzione che elabora UN paziente (stessi passaggi costruiti in Spyder)
  3. prova su un paziente, con controlli
  4. tutti i pazienti e salvataggio
"""

# %% 1. Librerie, parametri e funzioni di base

from pathlib import Path
import mne
import numpy as np
import pandas as pd

PAZIENTE_DI_PROVA = "CE120"
BIDS = Path("E:/raw/ieeg_bids")
FINESTRA_INIZIO, FINESTRA_FINE = -0.5, 0.0          # secondi
SOGLIA_SPEGNIMENTO = 1.0                            # secondi dallo spegnimento precedente
CARTELLA_USCITA = Path("D:/TESI/manoscritto/extension/results/stato_prestimolo")

CARTELLA_ELETTRODI = (BIDS / "derivatives" / "synchrony_analysis" / "sub-super" / "ses-1" / "ieeg"
                      / "results" / "category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d"
                      / "desbadcharej_notfil_lapref")


def conta_parole_nuove_lz(sequenza):
    """Lempel-Ziv (1976), algoritmo di Kaspar e Schuster (1987).
    Riceve una sequenza di 0 e 1; restituisce quante "parole nuove" si incontrano
    leggendola da sinistra a destra. Verificata sull'esempio classico 0001101001000101 -> 6."""
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
    """LZC di un segnale: binarizzazione sulla mediana, conteggio, normalizzazione per lunghezza."""
    sequenza_binaria = (segnale >= np.median(segnale)).astype(int)
    lunghezza = len(sequenza_binaria)
    return conta_parole_nuove_lz(sequenza_binaria) / (lunghezza / np.log2(lunghezza))


# tabella degli elettrodi selettivi della serie _v1v2d (uguale per tutti i pazienti: si legge una volta)
elettrodi = pd.concat([
    pd.read_pickle(CARTELLA_ELETTRODI / "sub-super_ses-1_task-Dur_ana-synchrony_analysis_iit_dfc_tfr_electrodes.tar.gz",
                   compression="gzip"),
    pd.read_pickle(CARTELLA_ELETTRODI / "sub-super_ses-1_task-Dur_ana-synchrony_analysis_gnw_dfc_tfr_electrodes.tar.gz",
                   compression="gzip"),
])
elettrodi = elettrodi[elettrodi["face"] | elettrodi["object"]].drop_duplicates(subset=["channels"])


# %% 2. La funzione che elabora un paziente

def elabora_paziente(paziente):

    # --- a. caricare le epoche (come la cella 2 costruita in Spyder)
    file_epoche = (BIDS / "derivatives" / "preprocessing" / f"sub-{paziente}" / "ses-1" / "ieeg"
                   / "epoching" / "broadband" / "desbadcharej_notfil_lapref"
                   / f"sub-{paziente}_ses-1_task-Dur_desc-epoching_ieeg-epo.fif")
    epoche_tutte = mne.read_epochs(file_epoche, preload=False, verbose="ERROR")
    metadati = epoche_tutte.metadata

    # --- b. selezionare le prove del cap. 4 (cella 3)
    cond_accensione = metadati["event type"] == "stimulus onset"
    cond_irrilevante = metadati["task_relevance"] == "Irrelevant"
    cond_categoria = metadati["category"].isin(["face", "object"])
    cond_durata = metadati["duration"].isin(["1000ms", "1500ms"])
    prove_scelte = cond_accensione & cond_irrilevante & cond_categoria & cond_durata

    # --- c. elettrodi selettivi del paziente (cella 4)
    elettrodi_selettivi = elettrodi[elettrodi["channels"].str.startswith(paziente + "-")]
    nomi_con_prefisso = elettrodi_selettivi["channels"].tolist()
    nomi_canali = [nome.replace(paziente + "-", "", 1) for nome in nomi_con_prefisso]
    preferenza = ["volti" if volti else "oggetti" for volti in elettrodi_selettivi["face"]]

    # --- d. dati della finestra pre-stimolo (cella 5)
    epoche_scelte = epoche_tutte[prove_scelte.values]
    epoche_scelte.load_data()
    epoche_scelte.pick(nomi_canali)
    epoche_scelte.crop(tmin=FINESTRA_INIZIO, tmax=FINESTRA_FINE, include_tmax=False)
    dati_prestimolo = epoche_scelte.get_data()             # prove x elettrodi x campioni
    numero_prove, numero_elettrodi, numero_campioni = dati_prestimolo.shape
    frequenza_campionamento = epoche_scelte.info["sfreq"]

    # --- e. LZC per ogni prova ed elettrodo (celle 6-7)
    lzc_tutte = np.zeros((numero_prove, numero_elettrodi))
    for prova in range(numero_prove):
        for elettrodo in range(numero_elettrodi):
            lzc_tutte[prova, elettrodo] = lzc_normalizzata(dati_prestimolo[prova, elettrodo, :])

    # --- f. potenza alfa (8-13 Hz) nella stessa finestra, per il controllo spettrale
    densita, frequenze = mne.time_frequency.psd_array_welch(
        dati_prestimolo, frequenza_campionamento, fmin=8, fmax=13, n_fft=numero_campioni, verbose="ERROR")
    alfa_log10 = np.log10(densita.mean(axis=-1))            # prove x elettrodi

    # --- g. distanza dallo spegnimento dello stimolo precedente (dagli eventi BIDS)
    eventi = pd.read_csv(BIDS / f"sub-{paziente}" / "ses-1" / "ieeg" / f"sub-{paziente}_ses-1_task-Dur_events.tsv",
                         sep="\t", encoding="utf-8-sig").sort_values("onset").reset_index(drop=True)
    parti = eventi["trial_type"].str.split("/", expand=True)
    eventi["tipo"] = parti[0]
    chiavi = ["block", "miniblock", "category", "identity", "orientation", "duration", "task_relevance"]
    for posizione, chiave in enumerate(chiavi, start=1):
        eventi[chiave] = parti[posizione]
    # tempo dell'ultimo spegnimento PRIMA di ogni evento
    ultimo_spegnimento = eventi["onset"].where(eventi["tipo"] == "stimulus offset").ffill().shift(1)
    accensioni = eventi[eventi["tipo"] == "stimulus onset"].copy()
    accensioni["distanza_spegnimento"] = accensioni["onset"] - ultimo_spegnimento[accensioni.index]

    # abbinare epoche ed eventi: stesse chiavi; le ripetizioni si abbinano nel loro ordine temporale
    accensioni["occorrenza"] = accensioni.groupby(chiavi).cumcount()
    prove_tabella = metadati[prove_scelte][chiavi].astype(str).reset_index(drop=True)
    prove_tabella["tempo_epoca"] = epoche_scelte.events[:, 0] / frequenza_campionamento
    prove_tabella["campione_evento"] = epoche_scelte.events[:, 0]
    prove_tabella["occorrenza"] = prove_tabella.groupby(chiavi).cumcount()
    prove_tabella = prove_tabella.merge(accensioni[chiavi + ["occorrenza", "onset", "distanza_spegnimento"]],
                                        on=chiavi + ["occorrenza"], how="left")
    # controllo: se l'abbinamento e' giusto, eventi ed epoche hanno lo stesso tempo (scarto ~0)
    assert prove_tabella["onset"].notna().all(), f"{paziente}: prove non abbinate agli eventi"
    scarto = (prove_tabella["onset"] - prove_tabella["tempo_epoca"]).abs().max()
    assert scarto < 0.01, f"{paziente}: abbinamento epoche-eventi non affidabile (scarto {scarto:.3f} s)"
    # una prova senza spegnimento precedente (la prima della registrazione) e' preceduta solo da pausa:
    # distanza infinita, quindi non viene esclusa
    senza_precedente = prove_tabella["distanza_spegnimento"].isna()
    if senza_precedente.any():
        print(f"  {paziente}: {senza_precedente.sum()} prova/e senza stimolo precedente (tenute)")
    prove_tabella["distanza_spegnimento"] = prove_tabella["distanza_spegnimento"].fillna(np.inf)

    # --- h. tabella lunga: una riga per prova ed elettrodo
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

    # --- i. esclusioni e divisione per mediana (per elettrodo e categoria)
    tabella["stato"] = "da_assegnare"
    tabella.loc[tabella["distanza_spegnimento"] < SOGLIA_SPEGNIMENTO, "stato"] = "escluso_spegnimento"
    tenute = tabella["stato"] == "da_assegnare"
    mediana = tabella[tenute].groupby(["canale", "categoria"])["lzc"].transform("median")
    tabella.loc[tenute & (tabella["lzc"] > mediana.reindex(tabella.index)), "stato"] = "alto"
    tabella.loc[tenute & (tabella["lzc"] < mediana.reindex(tabella.index)), "stato"] = "basso"
    tabella.loc[tenute & (tabella["lzc"] == mediana.reindex(tabella.index)), "stato"] = "escluso_pareggio"
    assert not (tabella["stato"] == "da_assegnare").any(), f"{paziente}: prove non assegnate"

    return tabella


# %% 3. Prova su un paziente, con controlli

tabella_prova = elabora_paziente(PAZIENTE_DI_PROVA)
print(tabella_prova.head())
print(tabella_prova["stato"].value_counts())
# per ogni elettrodo e categoria: quante prove alte e quante basse (devono essere simili)
print(tabella_prova.groupby(["canale", "categoria"])["stato"].value_counts().unstack(fill_value=0).head(10))

# %% 4. Tutti i pazienti e salvataggio

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
