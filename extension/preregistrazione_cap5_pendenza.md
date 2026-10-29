# Preregistrazione del capitolo 5: lo stato pre-stimolo e la connettivita' selettiva

*Data di stesura: 29 ottobre 2026. Il commit di questo file precede qualunque calcolo delle pendenze della connettivita' sulla LZC.*

## 1. Domanda e ipotesi

**Domanda.** La complessita' dell'attivita' nei 500 ms prima dello stimolo (Lempel-Ziv complexity, LZC), misurata nell'elettrodo selettivo per categoria, modula la connettivita' selettiva trovata nel capitolo 4 fra gli elettrodi selettivi e le regioni V1/V2 e prefrontale?

**Ipotesi.** La relazione fra LZC pre-stimolo e DFC e' diversa nelle prove con volti e in quelle con oggetti, cioe' la LZC modula l'effetto di categoria. Test a due code: la letteratura indica direzioni diverse (Waschke et al. 2017; Wolff et al. 2021; Li et al. 2020).

Il capitolo e' esplorativo: non mette alla prova IIT o GNWT.

## 2. Dati e prove

- Dataset iEEG pubblico di COGITATE, preprocessing del consorzio (epoche broadband, -1,0/+2,5 s, 512 Hz).
- Prove: le stesse della DFC del capitolo 4, cioe' accensione dello stimolo, irrilevanti per il compito, volti e oggetti, durate 1,0 e 1,5 s.
- Elettrodi selettivi (sorgenti), regioni di destinazione e parametri della DFC: quelli della serie definitiva del capitolo 4 (`category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d`): 183 elettrodi selettivi in 26 pazienti.
- Esclusione: sono escluse le prove in cui lo spegnimento dello stimolo precedente e' avvenuto meno di 1,0 s prima dell'accensione, perche' la risposta allo spegnimento (0,3-0,5 s dopo) cadrebbe nella finestra. Le prove senza stimolo precedente (la prima della registrazione) sono tenute. Tutte le altre prove sono usate.

## 3. Lo stato pre-stimolo

- **Finestra:** -500/0 ms rispetto all'accensione (Wolff et al. 2019 e 2021; Iemi et al. 2019), sul segnale broadband.
- **LZC:** per ogni prova e ogni elettrodo selettivo, il segnale della finestra e' binarizzato sulla propria mediana (1 sopra, 0 sotto; Aboy et al. 2006), il numero di parole di Lempel-Ziv e' calcolato con l'algoritmo di Kaspar e Schuster ed e' normalizzato per la lunghezza, c(n) / (n / log2 n) (Wolff et al. 2019).
- La LZC per prova e' prodotta dallo script `extension/scripts/analisi/20_assegna_stato_prestimolo.py` e salvata in `extension/results/stato_prestimolo/assegnazione_prove.csv` (colonne `lzc`, `distanza_spegnimento`).
- **Standardizzazione:** per ogni elettrodo selettivo e separatamente per le prove con volti e con oggetti, la LZC e' trasformata in z-score (media 0, deviazione standard 1), cosi' che la pendenza sia confrontabile fra elettrodi con variabilita' diversa della LZC.

## 4. Pendenze

- DFC identica al capitolo 4 (codice del consorzio, `synchrony_master.py`, stessa configurazione), calcolata prova per prova da `conn_dfc` di frites. La regressione della risposta evocata resta quella del capitolo 4, stimata su tutte le prove.
- Per ogni coppia sorgente-destinazione, ogni frequenza e ogni finestra: pendenza della regressione lineare (minimi quadrati) della DFC sulla LZC standardizzata, sulle prove della categoria. Media delle pendenze sulle destinazioni della regione.
- Per ogni elettrodo selettivo: pendenza nelle prove con volti meno pendenza nelle prove con oggetti (stessa convenzione di segno del capitolo 4).

## 5. Statistica

- **Test:** cluster test one-sample contro zero, a due code, con la stessa funzione e gli stessi parametri del capitolo 4 (1024 permutazioni, soglia di formazione e di significativita' del cluster 0,05), `seed=0`. Unita' statistica: l'elettrodo selettivo, come nel capitolo 4 e nel paper ("super participant", motivato dalla copertura iEEG scarsa e variabile). Quattro insiemi (V1/V2 e prefrontale, per elettrodi selettivi ai volti e agli oggetti).
- **Verifica per paziente:** stesso test sulla media degli elettrodi di ciascun paziente. Letta per la direzione e la coerenza fra pazienti, non come conferma della significativita'.

## 6. Lettura dei risultati, fissata prima

- Almeno un cluster: la LZC pre-stimolo modula la connettivita' selettiva in quell'insieme; si riportano segno, frequenze e tempi.
- Nessun cluster: nessuna evidenza di modulazione con questo disegno.
- Il confronto fra V1/V2 e prefrontale resta descrittivo.

## 7. Che cosa era gia' noto prima di questo documento

- I risultati della DFC su tutte le prove (capitolo 4).
- Un'esplorazione della sola LZC pre-stimolo (script 19b, 19c e 20): distribuzione della LZC, assenza di deriva lungo la sessione, legame con la potenza alfa, correlazione fra elettrodi dello stesso paziente (bassa, mediana 0,11). Questa esplorazione ha informato la scelta di standardizzare la LZC per elettrodo.

## 8. Deviazioni

Qualunque deviazione da questo documento sara' dichiarata nel testo della tesi, distinguendo le correzioni di errori di codice dai cambi di disegno.
