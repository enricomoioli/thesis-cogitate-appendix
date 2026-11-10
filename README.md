# Appendice digitale della tesi

**Adversarial collaboration, open science e riproducibilità nelle neuroscienze della coscienza.**
**Il caso COGITATE: riproduzione della connettività interareale ed estensione allo stato pre-stimolo**

Enrico Moioli, tesi di laurea magistrale in Processi Cognitivi e Tecnologie (LM-51), Università Telematica Internazionale Uninettuno, anno accademico 2025/2026.

Questo repository è l'appendice della tesi: raccoglie gli script, le preregistrazioni e i risultati leggeri delle analisi descritte nei capitoli 4 e 5, e gli script di tutte le figure. Il testo della tesi non è incluso.

La tesi parte dall'adversarial collaboration COGITATE, che ha messo a confronto la teoria dell'informazione integrata (IIT) e la teoria dello spazio di lavoro neuronale globale (GNWT) su dati fMRI, MEG e iEEG (Cogitate Consortium, *Nature*, 2025, doi:10.1038/s41586-025-08888-1), e si chiede che cosa diventi possibile quando dati e codice sono pubblici e li usa una persona esterna, con mezzi ordinari: un portatile con 8 GB di memoria.

## Che cosa contiene, capitolo per capitolo

| Capitolo della tesi | Materiale in questo repository |
|---|---|
| 4, riproduzione dell'analisi di connettività (predizione 3) sui dati iEEG pubblici | `cap4/` |
| 5, estensione originale: stato pre-stimolo (complessità di Lempel-Ziv) e connettività selettiva | `extension/` |
| Tutte le figure, capitoli 1-7 | `figure_tesi/` |

## Struttura

```
cap4/
  scripts/            download, preprocessing di tutti i pazienti, tabelle e mappe della sincronia (01-04)
  log/                riepilogo del preprocessing dei 38 pazienti
  soggetti_ieeg.md    elenco dei soggetti del rilascio pubblico
extension/
  preregistrazione_cap5_stato_prestimolo.md
  preregistrazione_cap5_pendenza.md
  scripts/analisi/            esplorazione della LZC, assegnazione dello stato, statistica (19a-21)
  scripts/analisi_pendenza/   versione di controllo con la LZC continua (22-23)
  results/                    tabelle e risultati leggeri
figure_tesi/
  scripts/            uno script per figura, più stile_tesi.py (stile comune)
  output/             figure in PNG e PDF
  stimoli_cogitate/   stimoli originali usati nello schema del paradigma (vedi FONTE.txt)
ambienti/             ricette conda degli ambienti usati
```

## Il codice del consorzio

Le analisi di connettività girano con il codice del consorzio (`cogitate-msp1`, licenza MIT), corretto come descritto nel capitolo 4. La versione modificata sta in un repository separato, un fork dell'originale: [collegamento da aggiungere]. Lì si trovano anche i due script derivati per il capitolo 5, `coglib/ieeg/synchrony/synchrony_master_stato.py` e `synchrony_master_pendenza.py`.

## Dati

Non inclusi. Sono i dati iEEG pubblici del consorzio COGITATE: 38 pazienti, formato BIDS, licenza CC BY 4.0, descritti in Seedat et al., *Scientific Data*, 2025, doi:10.1038/s41597-025-04833-z. Lo script `cap4/scripts/01_scarica_soggetti.py` li scarica, con le credenziali del proprio account.

Gli script contengono percorsi fissi: `D:\TESI\manoscritto\` per questo repository, `D:\TESI\cogitate-msp1\` per il codice del consorzio, `E:\raw\ieeg_bids\` per i dati. Chi li riusa deve cambiarli all'inizio di ciascuno script. I nomi delle cartelle dei risultati sotto `derivatives\` sono generati dal codice del consorzio.

## Ambienti

Le ricette sono in `ambienti/` (`conda env create -f nome.yml`).

| Ambiente | Uso |
|---|---|
| `ieeg_release` | download dei dati |
| `cogitate_ecog` | codice del consorzio, analisi dei capitoli 4 e 5 |
| installer MNE (`mne_installer.yml`) | mappa 3D degli elettrodi e figure |

## Capitolo 4: ordine di esecuzione

1. `01_scarica_soggetti.py`: download dei 38 pazienti;
2. `02_preprocessing_tutti_soggetti.py`: preprocessing del consorzio in ciclo, un processo per paziente, con riepilogo in `cap4/log/`;
3. selettività di categoria e sincronia (DFC) con il codice del consorzio, nel fork;
4. `03_sintesi_tabella_sincronia.py`: valori delle tabelle del capitolo 4;
5. `04_mappa_tf_sincronia.py`: mappe tempo-frequenza di lavoro.

## Capitolo 5: ordine di esecuzione

1. `19a`, `19b`, `19c`: esplorazione della LZC pre-stimolo, fatta prima della preregistrazione e senza guardare la connettività;
2. `20_assegna_stato_prestimolo.py`: divisione delle prove in LZC alta e bassa, per elettrodo;
3. `synchrony_master_stato.py` (nel fork): connettività ricalcolata sulle due metà;
4. `21_statistica_alto_basso.py`: test a cluster e controllo spettrale;
5. versione di controllo con la LZC continua: `synchrony_master_pendenza.py` (nel fork), poi `22_statistica_pendenza.py` e `23_controllo_dfc_tutte_le_prove.py`.

Il seme delle permutazioni è fisso (0).

## Preregistrazione

Criteri, parametri e regole di lettura del capitolo 5 sono stati fissati prima di eseguire i calcoli, in due documenti: `preregistrazione_cap5_stato_prestimolo.md` (27 ottobre 2026) e `preregistrazione_cap5_pendenza.md` (29 ottobre 2026). I primi due commit di questo repository li riproducono con le date originali. La cronologia pubblica è stata ricostruita da un repository di lavoro locale, che resta disponibile su richiesta.

## Figure

Ogni figura della tesi esce da uno script in `figure_tesi/scripts/`, numerato nell'ordine di comparsa, con lo stile comune di `stile_tesi.py` (IIT in blu, GNWT in rosso, grigi per il resto, virgola decimale).

| Script | Figura |
|---|---|
| `01_mappa_teorie.py` | mappa delle teorie della coscienza (cap. 1) |
| `02_schema_lakatos.py` | schema del modello di Lakatos (cap. 2) |
| `03_schema_paradigma.py` | paradigma sperimentale di COGITATE (cap. 3) |
| `04_schema_predizioni.py` | andamento atteso per la predizione 2 (cap. 3) |
| `05_percorso_analisi.py` | percorso della parte empirica (cap. 4) |
| `06_mappa_3d_elettrodi.py` | mappa 3D degli elettrodi (cap. 4) |
| `07_figura_sincronia_sintesi.py` | sintesi della connettività (cap. 4) |
| `08_figura_profili_spettrali.py` | profili spettrali (cap. 4) |
| `09_figure_stato_prestimolo.py` | stato pre-stimolo e connettività (cap. 5) |
| `10_schema_lakatos_cogitate.py` | Lakatos applicato alle due teorie (cap. 6) |
| `11_schema_stati_alterati.py` | schema degli stati alterati (cap. 7) |
| `12_figure_pendenza.py`, `13_figura_confronto_alto_basso_pendenza.py` | versione di controllo con la LZC continua (cap. 5) |

Le figure 06, 07 e 08 richiedono i risultati di sincronia sul disco dei dati; le figure del capitolo 5 leggono i file in `extension/results/`.

## Licenza

Il codice di questo repository è distribuito con licenza MIT (file `LICENSE`). I dati e il codice originale del consorzio restano soggetti alle rispettive licenze (CC BY 4.0 per i dati, MIT per il codice).

## Crediti

Dati e codice originali: Cogitate Consortium. Gli stimoli in `figure_tesi/stimoli_cogitate/` vengono dal repository `cogitate-experiment-code` del consorzio (licenza MIT): immagini degli oggetti per cortesia di Michael J. Tarr, Carnegie Mellon University, http://www.tarrlab.org/; volti creati con FaceGen Modeler 3.1.
