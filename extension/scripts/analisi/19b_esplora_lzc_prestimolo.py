# -*- coding: utf-8 -*-
"""
19b - Exploration of pre-stimulus LZC in ONE patient (chapter 5, new direction).

Purpose: get familiar with the data BEFORE the preregistration. It does not touch
the DFC, so it does not show the result that is still to be preregistered.

For the chosen patient:
  1. loads the broadband epochs (consortium preprocessing, -1.0/+2.5 s);
  2. keeps the chapter 4 trials: task-irrelevant, faces and objects, durations
     1.0 and 1.5 s, event "stimulus onset";
  3. keeps the patient's selective electrodes (sources) of the _v1v2d series;
  4. for each trial and each electrode, on the -500/0 ms window computes:
       - LZC: signal binarized on the median of the window (1 above, 0 below;
         Aboy et al. 2006), Lempel-Ziv count (Kaspar and Schuster algorithm),
         normalized by length c / (n / log2 n) (Wolff et al. 2019);
       - alpha power (8-13 Hz, log10, Welch over the whole window);
  5. from the BIDS events derives the distance between the offset of the previous
     stimulus and the onset of the trial, and flags the trials below 1.0 s;
  6. saves a table (one row per trial and electrode) and three figures:
       a) LZC by trial number, one panel per electrode, colours by block;
       b) mean LZC (z per electrode) by trial number, with the blocks;
       c) LZC against alpha power.

Usage (cogitate_ecog prompt, from the script folder):
    python 19b_esplora_lzc_prestimolo.py            (patient CE120)
    python 19b_esplora_lzc_prestimolo.py CF124      (another patient)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import mne
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

PAZIENTE = sys.argv[1] if len(sys.argv) > 1 else "CE120"
BIDS = Path(r"E:/raw/ieeg_bids")
SERIE = ("category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d")
FINESTRA = (-0.5, 0.0)
SOGLIA_SPEGNIMENTO = 1.0   # s
USCITA = Path(r"D:/TESI/manoscritto/extension/results/esplorazione_lzc") / PAZIENTE
USCITA.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- LZC
def lz76(s):
    """Number of Lempel-Ziv 'new words' (1976), Kaspar and Schuster algorithm (1987)."""
    n = len(s)
    i, k, l, c, k_max = 0, 1, 1, 1, 1
    while True:
        if s[i + k - 1] == s[l + k - 1]:
            k += 1
            if l + k > n:
                c += 1
                break
        else:
            if k > k_max:
                k_max = k
            i += 1
            if i == l:
                c += 1
                l += k_max
                if l + 1 > n:
                    break
                i, k, k_max = 0, 1, 1
            else:
                k = 1
    return c


def lzc(x):
    """Length-normalized LZC, binarization on the median of the window."""
    b = (x >= np.median(x)).astype(np.int8)
    n = len(b)
    return lz76(b) / (n / np.log2(n))


# ---------------------------------------------------------------- 1. epochs
f_epo = (BIDS / "derivatives" / "preprocessing" / f"sub-{PAZIENTE}" / "ses-1" / "ieeg" / "epoching"
         / "broadband" / "desbadcharej_notfil_lapref"
         / f"sub-{PAZIENTE}_ses-1_task-Dur_desc-epoching_ieeg-epo.fif")
epochs = mne.read_epochs(f_epo, preload=False, verbose="ERROR")
md = epochs.metadata.copy()
print(f"Epoche: {len(epochs)}, sfreq {epochs.info['sfreq']} Hz, {len(epochs.ch_names)} canali")
for col in ["event type", "category", "task_relevance", "duration"]:
    print(f"  {col}: {sorted(md[col].astype(str).unique())[:10]}")

# ---------------------------------------------------------------- 2. chapter 4 trials
dur = md["duration"].astype(str)
sel = ((md["event type"].astype(str) == "stimulus onset")
       & (md["task_relevance"].astype(str) == "Irrelevant")
       & (md["category"].astype(str).isin(["face", "object"]))
       & (dur.str.contains("1000") | dur.str.contains("1500") | dur.isin(["1.0", "1.5"])))
idx = np.where(sel.values)[0]
print(f"Prove selezionate: {len(idx)}")

# ---------------------------------------------------------------- 3. selective electrodes
cartella = (BIDS / "derivatives" / "synchrony_analysis" / "sub-super" / "ses-1" / "ieeg" / "results"
            / SERIE / "desbadcharej_notfil_lapref")
el = pd.concat([pd.read_pickle(cartella / f"sub-super_ses-1_task-Dur_ana-synchrony_analysis_{r}_dfc_tfr_electrodes.tar.gz",
                               compression="gzip") for r in ["iit", "gnw"]])
el = el[((el["face"] == True) | (el["object"] == True)) & el["channels"].astype(str).str.startswith(PAZIENTE + "-")]
el = el.drop_duplicates(subset=["channels"])
nomi = el["channels"].astype(str).tolist()
# in the epochs the channels may lack the patient prefix
if not set(nomi) <= set(epochs.ch_names):
    nomi_senza = [n.split("-", 1)[1] for n in nomi]
    if set(nomi_senza) <= set(epochs.ch_names):
        mappa = dict(zip(nomi_senza, nomi))
        nomi = nomi_senza
    else:
        mancanti = sorted(set(nomi) - set(epochs.ch_names))
        raise SystemExit(f"Canali non trovati nelle epoche: {mancanti[:10]} ... (esempi epoche: {epochs.ch_names[:5]})")
else:
    mappa = {n: n for n in nomi}
pref = {mappa[n]: ("volti" if bool(r.face) else "oggetti") for n, r in zip(nomi, el.itertuples())}
print(f"Elettrodi selettivi trovati: {len(nomi)}")

# ---------------------------------------------------------------- 4. LZC and alpha
# mandatory order in MNE (documented quirk): index, then load_data(), then pick()
ep = epochs[idx]
ep.load_data()
ep.pick(nomi)
ep.crop(*FINESTRA, include_tmax=False)
dati = ep.get_data()                       # trials x channels x samples
n_camp = dati.shape[-1]
print(f"Finestra {FINESTRA}: {n_camp} campioni per prova")
lzc_val = np.array([[lzc(dati[t, c]) for c in range(dati.shape[1])] for t in range(dati.shape[0])])
psd, freqs = mne.time_frequency.psd_array_welch(dati, ep.info["sfreq"], fmin=8, fmax=13,
                                                 n_fft=n_camp, verbose="ERROR")
alfa = np.log10(psd.mean(axis=-1))

# ---------------------------------------------------------------- 5. distance from the previous offset
ev = pd.read_csv(BIDS / f"sub-{PAZIENTE}" / "ses-1" / "ieeg" / f"sub-{PAZIENTE}_ses-1_task-Dur_events.tsv",
                 sep="\t", encoding="utf-8-sig").sort_values("onset").reset_index(drop=True)
parti = ev["trial_type"].str.split("/", expand=True)
ev["tipo"], ev["block"], ev["miniblock"], ev["category"], ev["identity"], ev["orientation"], ev["duration"], ev["task_relevance"] = \
    parti[0], parti[1], parti[2], parti[3], parti[4], parti[5], parti[6], parti[7]
ultimo_spegn = ev["onset"].where(ev["tipo"] == "stimulus offset").ffill().shift(1)
on = ev[ev["tipo"] == "stimulus onset"].copy()
on["dist_spegnimento"] = on["onset"] - ultimo_spegn[on.index]
on["ordine"] = np.arange(len(on))

chiavi = ["block", "miniblock", "category", "identity", "orientation", "duration", "task_relevance"]
mdsel = md.iloc[idx].reset_index(drop=True)
mdsel_str = mdsel[chiavi].astype(str)
print("Esempio metadati:", mdsel_str.iloc[0].tolist(), "| esempio eventi:", on[chiavi].iloc[0].tolist())
on_k = on[chiavi + ["dist_spegnimento", "ordine", "onset"]].astype({k: str for k in chiavi})
# key combinations can repeat: repetitions are matched in their temporal order
# (n-th occurrence in the events with n-th occurrence in the epochs)
on_k["occorrenza"] = on_k.groupby(chiavi).cumcount()
mdsel_str["t_epoca"] = epochs.events[idx, 0] / epochs.info["sfreq"]
mdsel_str = mdsel_str.sort_values("t_epoca").reset_index()
mdsel_str["occorrenza"] = mdsel_str.groupby(chiavi).cumcount()
abb = mdsel_str.merge(on_k, on=chiavi + ["occorrenza"], how="left").sort_values("index").reset_index(drop=True)
mdsel_str = mdsel_str.sort_values("index").reset_index(drop=True)
print(f"Prove abbinate agli eventi: {abb['dist_spegnimento'].notna().sum()} su {len(abb)}")
# check: if the matching is right, the difference between event time and epoch time is constant
scarto = abb["onset"] - abb["t_epoca"]
print(f"Verifica abbinamento: scarto eventi-epoche, mediana {scarto.median():.3f} s, "
      f"max deviazione {np.nanmax(np.abs(scarto - scarto.median())):.3f} s (deve essere circa 0)")

# ---------------------------------------------------------------- 6. table and figures
righe = []
for t in range(len(idx)):
    for c, nome in enumerate(nomi):
        righe.append(dict(paziente=PAZIENTE, canale=mappa[nome], preferenza=pref[mappa[nome]],
                          prova=int(idx[t]), ordine=abb.loc[t, "ordine"], blocco=mdsel_str.loc[t, "block"],
                          categoria=mdsel_str.loc[t, "category"], durata=mdsel_str.loc[t, "duration"],
                          dist_spegnimento=abb.loc[t, "dist_spegnimento"],
                          esclusa=bool(abb.loc[t, "dist_spegnimento"] < SOGLIA_SPEGNIMENTO),
                          lzc=lzc_val[t, c], alfa_log10=alfa[t, c]))
tab = pd.DataFrame(righe)
tab.to_csv(USCITA / f"{PAZIENTE}_lzc_prestimolo.csv", index=False)
print(f"Prove con spegnimento precedente < {SOGLIA_SPEGNIMENTO} s: "
      f"{tab.drop_duplicates('prova')['esclusa'].mean():.0%}")

blocchi = sorted(tab["blocco"].unique())
colori = dict(zip(blocchi, plt.cm.tab10(np.arange(len(blocchi)))))

# a) one panel per electrode
n = len(nomi)
ncol = 6
nrig = int(np.ceil(n / ncol))
fig, axs = plt.subplots(nrig, ncol, figsize=(3 * ncol, 2.2 * nrig), sharex=True, squeeze=False)
for ax, nome in zip(axs.flat, nomi):
    d = tab[tab["canale"] == mappa[nome]]
    for b in blocchi:
        db = d[d["blocco"] == b]
        ax.scatter(db["ordine"], db["lzc"], s=6, color=colori[b])
    ax.set_title(f"{mappa[nome]} ({pref[mappa[nome]]})", fontsize=7)
for ax in axs.flat[n:]:
    ax.axis("off")
fig.supxlabel("Numero d'ordine della prova nella sessione")
fig.supylabel("LZC pre-stimolo (-500/0 ms)")
fig.tight_layout()
fig.savefig(str(USCITA / f"{PAZIENTE}_a_lzc_per_elettrodo.png"), dpi=150)
plt.close(fig)

# b) mean of the electrodes (z per electrode)
tab["lzc_z"] = tab.groupby("canale")["lzc"].transform(lambda v: (v - v.mean()) / v.std())
media = tab.groupby(["ordine", "blocco"], as_index=False)["lzc_z"].mean()
fig, ax = plt.subplots(figsize=(10, 3.5))
for b in blocchi:
    mb = media[media["blocco"] == b]
    ax.scatter(mb["ordine"], mb["lzc_z"], s=10, color=colori[b], label=b)
ax.set_xlabel("Numero d'ordine della prova nella sessione")
ax.set_ylabel("LZC media (z per elettrodo)")
ax.legend(fontsize=7, ncol=len(blocchi))
fig.tight_layout()
fig.savefig(str(USCITA / f"{PAZIENTE}_b_lzc_media_sessione.png"), dpi=150)
plt.close(fig)

# c) LZC against alpha
fig, ax = plt.subplots(figsize=(4.5, 4))
ax.scatter(tab["alfa_log10"], tab["lzc"], s=3, alpha=0.4, color="grey")
ax.set_xlabel("Potenza alfa 8-13 Hz (log10)")
ax.set_ylabel("LZC pre-stimolo")
fig.tight_layout()
fig.savefig(str(USCITA / f"{PAZIENTE}_c_lzc_vs_alfa.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------- numerical summary
print("\n=== Riepilogo per elettrodo ===")
ries = []
for nome in nomi:
    d = tab[tab["canale"] == mappa[nome]].dropna(subset=["ordine"])
    r_ord = stats.spearmanr(d["ordine"], d["lzc"])[0]
    r_alfa = stats.spearmanr(d["alfa_log10"], d["lzc"])[0]
    ries.append(dict(canale=mappa[nome], preferenza=pref[mappa[nome]],
                     lzc_mediana=d["lzc"].median(), lzc_iqr=d["lzc"].quantile(.75) - d["lzc"].quantile(.25),
                     rho_lzc_ordine=r_ord, rho_lzc_alfa=r_alfa))
ries = pd.DataFrame(ries)
# ties at the median: LZC on 256 samples moves in steps of 1/32
pareggi = tab[~tab["esclusa"]].groupby("canale")["lzc"].apply(lambda v: np.mean(v == v.median()))
ries["quota_pareggi_mediana"] = ries["canale"].map(pareggi)
ries.to_csv(USCITA / f"{PAZIENTE}_riepilogo_elettrodi.csv", index=False)
print(ries.round(3).to_string(index=False))
print(f"\nMediana fra elettrodi: rho(LZC, ordine) = {ries['rho_lzc_ordine'].median():.2f}; "
      f"rho(LZC, alfa) = {ries['rho_lzc_alfa'].median():.2f}; "
      f"prove pari alla mediana (dopo esclusione) = {ries['quota_pareggi_mediana'].median():.0%} "
      f"(min {ries['quota_pareggi_mediana'].min():.0%}, max {ries['quota_pareggi_mediana'].max():.0%})")
print(f"Uscite in {USCITA}")
