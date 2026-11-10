# Preregistration for chapter 5: pre-stimulus state and selective connectivity

> **English translation**, added on 10 November 2026 for the public repository. The binding document is the Italian original, `preregistrazione_cap5_stato_prestimolo.md`, committed on 27 October 2026 and left unchanged. In case of discrepancy, the original prevails.

*Written on 27 October 2026. The commit of this file precedes any computation of connectivity on the two halves of the trials.*

## 1. Question and hypothesis

**Question.** Does the complexity of activity in the 500 ms before the stimulus (Lempel-Ziv complexity, LZC), measured in the category-selective electrode, modulate the selective connectivity found in chapter 4 between the selective electrodes and the V1/V2 and prefrontal regions?

**Main hypothesis.** The difference between categories in connectivity (DFC) differs between trials with high and low pre-stimulus LZC. Two-tailed test: the literature points to different directions (Waschke et al. 2017; Wolff et al. 2021; Li et al. 2020).

**Exploratory analysis.** Descriptive comparison of the effect between V1/V2 and prefrontal cortex.

The chapter is exploratory: it does not test IIT or GNWT.

## 2. Data and trials

- Public COGITATE iEEG dataset, consortium preprocessing (broadband epochs, -1.0/+2.5 s, 512 Hz).
- Trials: the same as in the chapter 4 DFC, i.e. stimulus onset, task-irrelevant, faces and objects, durations 1.0 and 1.5 s.
- Selective electrodes (sources), target regions and DFC parameters: those of the final chapter 4 series (`category_faces_objects_synchrony_dfc_tfr_irrelevant_no_act_catsel_textaligned_v1v2d`): 183 selective electrodes in 26 patients.

## 3. The pre-stimulus state

- **Window:** -500/0 ms relative to onset (Wolff et al. 2019 and 2021; Iemi et al. 2019). The broadband signal has only the notch filter of the preprocessing: the last 100 ms are not excluded.
- **LZC:** for each trial and each selective electrode, the signal in the window is binarized on its own median (1 above, 0 below; Aboy et al. 2006), the number of Lempel-Ziv words is computed with the Kaspar and Schuster algorithm and normalized by length, c(n) / (n / log2 n) (Wolff et al. 2019).
- **Exclusion based on the previous trial:** trials in which the offset of the previous stimulus occurred less than 1.0 s before onset are excluded, because the offset response (0.3-0.5 s later) would fall in the window. Trials without a previous stimulus (the first of the recording) are kept. No check with different thresholds is planned.
- **Split:** for each selective electrode and separately for each category, the remaining trials are split on the median LZC: above = high state, below = low state. Trials with LZC equal to the median are excluded (LZC on 256 samples takes discrete values, in steps of 1/32).
- The assignment is produced by the script `extension/scripts/analisi/20_assegna_stato_prestimolo.py` and saved in `extension/results/stato_prestimolo/assegnazione_prove.csv`, committed together with this document.

## 4. Connectivity in the two halves

- DFC identical to chapter 4 (consortium code, `synchrony_master.py`, same configuration), computed once on all trials. Since frites `conn_dfc` computes DFC trial by trial, for each source-target pair two means are computed: over the high and over the low trials of that source, in its category. The regression of the evoked response remains that of chapter 4, estimated on all trials.
- For each selective electrode and each state, the category effect is computed as in chapter 4 (faces minus objects, averaged over the targets of the region).

## 5. Statistics

- **Measure:** for each selective electrode, the difference between the category effect in the high state and in the low state, in each time-frequency cell.
- **Main test:** one-sample cluster test against zero, two-tailed, with the same function and parameters as chapter 4 (1024 permutations, cluster-forming and significance threshold 0.05). Statistical unit: the selective electrode, as in chapter 4 and in the paper ("super participant", motivated by sparse and variable iEEG coverage). Four sets, as in chapter 4: V1/V2 and prefrontal, for face-selective and object-selective electrodes.
- **Patient-level check:** same test on the mean of each patient's electrodes. Read for direction and consistency across patients, not as confirmation of significance.
- **Spectral control (descriptive):** for each electrode and category, difference in alpha power (8-13 Hz, same window) between high and low trials; the median and the share of electrodes with lower alpha in the high state are reported.

## 6. Interpretation of results, fixed in advance

- At least one significant cluster in a set: the pre-stimulus state, measured with LZC, modulates selective connectivity in that set; sign, frequencies and times are reported.
- No cluster: no evidence of modulation with this design.
- If alpha power differs systematically between the two halves, any effect will be read as the effect of a partly spectral state, not of complexity as such.
- The comparison between V1/V2 and prefrontal remains descriptive.

## 7. What was already known before this document

- The results of the DFC on all trials (chapter 4).
- An exploration of pre-stimulus LZC alone (scripts 19b and 19c, then 20), never of the split DFC: distribution of LZC, absence of drift across the session, relation to alpha power, correlation between electrodes of the same patient (low, median 0.11), frequency of ties at the median (11%). This exploration informed the choice of splitting by electrode and the rule on ties.

## 8. Deviations

Any deviation from this document will be declared in the text of the thesis, distinguishing corrections of code errors from changes of design.
