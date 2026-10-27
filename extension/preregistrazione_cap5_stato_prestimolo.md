# Preregistrazione del capitolo 5: lo stato pre-stimolo e la connettivita' selettiva

*Data di stesura: 27 ottobre 2026. Il commit di questo file precede qualunque calcolo della connettivita' sulle due meta' delle prove.*

## 1. Domanda e ipotesi

**Domanda.** La complessita' dell'attivita' nei 500 ms prima dello stimolo (Lempel-Ziv complexity, LZC), misurata nell'elettrodo selettivo per categoria, modula la connettivita' selettiva trovata nel capitolo 4 fra gli elettrodi selettivi e le regioni V1/V2 e prefrontale?

**Ipotesi principale.** La differenza fra categorie nella connettivita' (DFC) e' diversa nelle prove con LZC pre-stimolo alta rispetto a quelle con LZC bassa. Test a due code: la letteratura indica direzioni diverse (Waschke et al. 2017; Wolff et al. 2021; Li et al. 2020).

**Analisi esplorativa.** Confronto descrittivo dell'effetto fra V1/V2 e prefrontale.

Il capitolo e' esplorativo: non mette alla prova IIT o GNWT.

## 2. Dati e prove

- Dataset iEEG pubblico di COGITATE, preprocessing del consorzio (epoche broadband, -1,0/+2,5 s, 512 Hz).
- Prove: le stesse della DFC del capitolo 4, cioe' accensione dello stimolo, irrilevanti per il compito, volti e oggetti, durate 1,0 e 1,5 s.
- Elettrodi selettivi (sorgenti), regioni di destinazione e parametri della DFC: quelli della serie definitiva del capitolo 4 (`category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d`): 183 elettrodi selettivi in 26 pazienti.

## 3. Lo stato pre-stimolo

- **Finestra:** -500/0 ms rispetto all'accensione (Wolff et al. 2019 e 2021; Iemi et al. 2019). Sul segnale broadband c'e' solo il filtro notch del preprocessing: non si escludono gli ultimi 100 ms.
- **LZC:** per ogni prova e ogni elettrodo selettivo, il segnale della finestra e' binarizzato sulla propria mediana (1 sopra, 0 sotto; Aboy et al. 2006), il numero di parole di Lempel-Ziv e' calcolato con l'algoritmo di Kaspar e Schuster ed e' normalizzato per la lunghezza, c(n) / (n / log2 n) (Wolff et al. 2019).
- **Esclusione per la prova precedente:** sono escluse le prove in cui lo spegnimento dello stimolo precedente e' avvenuto meno di 1,0 s prima dell'accensione, perche' la risposta allo spegnimento (0,3-0,5 s dopo) cadrebbe nella finestra. Le prove senza stimolo precedente (la prima della registrazione) sono tenute. Non e' prevista una verifica con soglie diverse.
- **Divisione:** per ogni elettrodo selettivo e separatamente per categoria, le prove rimaste sono divise sulla mediana della LZC: sopra = stato alto, sotto = stato basso. Le prove con LZC pari alla mediana sono escluse (la LZC su 256 campioni ha valori discreti, a passi di 1/32).
- L'assegnazione e' prodotta dallo script `extension/scripts/analisi/20_assegna_stato_prestimolo.py` ed e' salvata in `extension/results/stato_prestimolo/assegnazione_prove.csv`, committati insieme a questo documento.

## 4. Connettivita' nelle due meta'

- DFC identica al capitolo 4 (codice del consorzio, `synchrony_master.py`, stessa configurazione), calcolata una volta su tutte le prove. Poiche' `conn_dfc` di frites calcola la DFC prova per prova, per ogni coppia sorgente-destinazione si calcolano due medie: sulle prove alte e sulle prove basse di quella sorgente, nella sua categoria. La regressione della risposta evocata resta quella del capitolo 4, stimata su tutte le prove.
- Per ogni elettrodo selettivo e ogni stato si calcola l'effetto di categoria come nel capitolo 4 (volti meno oggetti, media sulle destinazioni della regione).

## 5. Statistica

- **Misura:** per ogni elettrodo selettivo, la differenza fra l'effetto di categoria nello stato alto e quello nello stato basso, in ogni cella tempo-frequenza.
- **Test principale:** cluster test one-sample contro zero, a due code, con la stessa funzione e gli stessi parametri del capitolo 4 (1024 permutazioni, soglia di formazione e di significativita' del cluster 0,05). Unita' statistica: l'elettrodo selettivo, come nel capitolo 4 e nel paper ("super participant", motivato dalla copertura iEEG scarsa e variabile). Quattro insiemi, come nel capitolo 4: V1/V2 e prefrontale, per elettrodi selettivi ai volti e agli oggetti.
- **Verifica per paziente:** stesso test sulla media degli elettrodi di ciascun paziente. Letta per la direzione e la coerenza fra pazienti, non come conferma della significativita'.
- **Controllo spettrale (descrittivo):** per ogni elettrodo e categoria, differenza di potenza alfa (8-13 Hz, stessa finestra) fra prove alte e basse; si riportano la mediana e la quota di elettrodi con alfa piu' bassa nello stato alto.

## 6. Lettura dei risultati, fissata prima

- Almeno un cluster significativo in un insieme: lo stato pre-stimolo, misurato con la LZC, modula la connettivita' selettiva in quell'insieme; si riportano segno, frequenze e tempi.
- Nessun cluster: nessuna evidenza di modulazione con questo disegno.
- Se la potenza alfa e' sistematicamente diversa fra le due meta', un eventuale effetto sara' letto come effetto di uno stato in parte spettrale, non della complessita' in se'.
- Il confronto fra V1/V2 e prefrontale resta descrittivo.

## 7. Che cosa era gia' noto prima di questo documento

- I risultati della DFC su tutte le prove (capitolo 4).
- Un'esplorazione della sola LZC pre-stimolo (script 19b e 19c, poi 20), mai della DFC divisa: distribuzione della LZC, assenza di deriva lungo la sessione, legame con la potenza alfa, correlazione fra elettrodi dello stesso paziente (bassa, mediana 0,11), frequenza dei pareggi alla mediana (11%). Questa esplorazione ha informato la scelta di dividere per elettrodo e la regola sui pareggi.

## 8. Deviazioni

Qualunque deviazione da questo documento sara' dichiarata nel testo della tesi, distinguendo le correzioni di errori di codice dai cambi di disegno.
