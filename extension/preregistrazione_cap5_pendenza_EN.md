# Preregistration for chapter 5: pre-stimulus state and selective connectivity (continuous LZC)

> **English translation**, added on 10 November 2026 for the public repository. The binding document is the Italian original, `preregistrazione_cap5_pendenza.md`, committed on 29 October 2026 and left unchanged. In case of discrepancy, the original prevails. The original carries the same title as the first preregistration; the words in parentheses are added here to tell them apart.

*Written on 29 October 2026. The commit of this file precedes any computation of the slopes of connectivity on LZC.*

## 1. Question and hypothesis

**Question.** Does the complexity of activity in the 500 ms before the stimulus (Lempel-Ziv complexity, LZC), measured in the category-selective electrode, modulate the selective connectivity found in chapter 4 between the selective electrodes and the V1/V2 and prefrontal regions?

**Hypothesis.** The relation between pre-stimulus LZC and DFC differs between trials with faces and trials with objects, i.e. LZC modulates the category effect. Two-tailed test: the literature points to different directions (Waschke et al. 2017; Wolff et al. 2021; Li et al. 2020).

The chapter is exploratory: it does not test IIT or GNWT.

## 2. Data and trials

- Public COGITATE iEEG dataset, consortium preprocessing (broadband epochs, -1.0/+2.5 s, 512 Hz).
- Trials: the same as in the chapter 4 DFC, i.e. stimulus onset, task-irrelevant, faces and objects, durations 1.0 and 1.5 s.
- Selective electrodes (sources), target regions and DFC parameters: those of the final chapter 4 series (`category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d`): 183 selective electrodes in 26 patients.
- Exclusion: trials in which the offset of the previous stimulus occurred less than 1.0 s before onset are excluded, because the offset response (0.3-0.5 s later) would fall in the window. Trials without a previous stimulus (the first of the recording) are kept. All other trials are used.

## 3. The pre-stimulus state

- **Window:** -500/0 ms relative to onset (Wolff et al. 2019 and 2021; Iemi et al. 2019), on the broadband signal.
- **LZC:** for each trial and each selective electrode, the signal in the window is binarized on its own median (1 above, 0 below; Aboy et al. 2006), the number of Lempel-Ziv words is computed with the Kaspar and Schuster algorithm and normalized by length, c(n) / (n / log2 n) (Wolff et al. 2019).
- Trial-level LZC is produced by the script `extension/scripts/analisi/20_assegna_stato_prestimolo.py` and saved in `extension/results/stato_prestimolo/assegnazione_prove.csv` (columns `lzc`, `distanza_spegnimento`).
- **Standardization:** for each selective electrode and separately for face and object trials, LZC is converted to z-scores (mean 0, standard deviation 1), so that slopes are comparable across electrodes with different LZC variability.

## 4. Slopes

- DFC identical to chapter 4 (consortium code, `synchrony_master.py`, same configuration), computed trial by trial by frites `conn_dfc`. The regression of the evoked response remains that of chapter 4, estimated on all trials.
- For each source-target pair, each frequency and each window: slope of the linear regression (least squares) of DFC on standardized LZC, over the trials of the category. Mean of the slopes over the targets of the region.
- For each selective electrode: slope in face trials minus slope in object trials (same sign convention as chapter 4).

## 5. Statistics

- **Test:** one-sample cluster test against zero, two-tailed, with the same function and parameters as chapter 4 (1024 permutations, cluster-forming and significance threshold 0.05), `seed=0`. Statistical unit: the selective electrode, as in chapter 4 and in the paper ("super participant", motivated by sparse and variable iEEG coverage). Four sets (V1/V2 and prefrontal, for face-selective and object-selective electrodes).
- **Patient-level check:** same test on the mean of each patient's electrodes. Read for direction and consistency across patients, not as confirmation of significance.

## 6. Interpretation of results, fixed in advance

- At least one cluster: pre-stimulus LZC modulates selective connectivity in that set; sign, frequencies and times are reported.
- No cluster: no evidence of modulation with this design.
- The comparison between V1/V2 and prefrontal remains descriptive.

## 7. What was already known before this document

- The results of the DFC on all trials (chapter 4).
- An exploration of pre-stimulus LZC alone (scripts 19b, 19c and 20): distribution of LZC, absence of drift across the session, relation to alpha power, correlation between electrodes of the same patient (low, median 0.11). This exploration informed the choice of standardizing LZC by electrode.

## 8. Deviations

Any deviation from this document will be declared in the text of the thesis, distinguishing corrections of code errors from changes of design.
