# Soggetti iEEG Cogitate — dataset pubblico

Elenco completo dei 38 soggetti presenti nel rilascio pubblico BIDS
(`E:\raw\ieeg_bids`), verificato il 6 settembre 2026 sui nomi delle cartelle
scaricate e coerente con il conteggio di `participants.tsv`.

Tre siti di raccolta, riconoscibili dal prefisso: CE (13), CF (19), CG (6).

Attenzione: la numerazione ha buchi (non esistono CE104, CE105, CE111, CF108,
CF111, CF114, CF115, CF118, CF123). Sono soggetti scartati a monte dal
consorzio: non usare i numeri per stimare l'avanzamento, usare la posizione
nell'elenco.

Nota sulla numerosita': l'articolo principale dichiara 34 pazienti iEEG
reclutati, 32 analizzati dopo due esclusioni per dati incompleti, 29 confluiti
nel "super partecipante" delle analisi multivariate. Il rilascio pubblico ne
distribuisce 38, quindi include anche registrazioni non confluite nelle analisi
pubblicate. Quali siano effettivamente utilizzabili va verificato soggetto per
soggetto: il `participants.tsv` pubblico NON contiene le colonne di inclusione
per analisi (`visual_responsiveness`, `category_selectivity`, `synchrony`) che
gli script del consorzio si aspetterebbero.

---

## Elenco in ordine alfabetico (ordine di elaborazione degli script)

CE103
CE106
CE107
CE108
CE109
CE110
CE112
CE113
CE115
CE118
CE119
CE120
CE121
CF102
CF103
CF104
CF105
CF106
CF107
CF109
CF110
CF112
CF113
CF116
CF117
CF119
CF120
CF121
CF122
CF124
CF125
CF126
CG101
CG102
CG103
CG104
CG105
CG106

---

## Lista Python pronta per i tre script master

Da incollare in `visual_responsiveness_master.py`, `category_selectivity_master.py`
e `synchrony_master.py`, al posto dell'attuale `["CF102"]` hardcoded nel blocco
`if __name__ == "__main__":`.

ATTENZIONE: prima di usarla, rimuovere i soggetti risultati falliti nel
preprocessing (vedi `log_preprocessing.txt`). Uno script master fallisce sul
primo soggetto per cui non trova i dati preprocessati.

```python
subjects_list = [
    "CE103", "CE106", "CE107", "CE108", "CE109", "CE110", "CE112",
    "CE113", "CE115", "CE118", "CE119", "CE120", "CE121",
    "CF102", "CF103", "CF104", "CF105", "CF106", "CF107", "CF109",
    "CF110", "CF112", "CF113", "CF116", "CF117", "CF119", "CF120",
    "CF121", "CF122", "CF124", "CF125", "CF126",
    "CG101", "CG102", "CG103", "CG104", "CG105", "CG106",
]
```

---

## Dimensioni osservate durante il preprocessing

Utili per stimare i tempi: il costo dipende da numero di canali e durata
della registrazione, non dal soggetto in se'.

- CF102: 136 canali (110 ECoG, 24 sEEG, 2 ECG), 2471 s di registrazione,
  93 canali validi dopo scarto, ~13 minuti di preprocessing
- CE110: 188 canali, 4704 s
- CE119: 161 canali

CF102 risulta finora tra i piu' piccoli: la stima di 13 minuti a soggetto
e' quindi ottimistica, i soggetti piu' grandi richiedono sensibilmente di piu'.
