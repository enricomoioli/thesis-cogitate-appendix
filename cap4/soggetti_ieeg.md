# COGITATE iEEG subjects: public dataset

Full list of the 38 subjects in the public BIDS release
(`E:\raw\ieeg_bids`), checked on 6 September 2026 against the names of the
downloaded folders and consistent with the count in `participants.tsv`.

Three recording sites, recognizable from the prefix: CE (13), CF (19), CG (6).

Note: the numbering has gaps (CE104, CE105, CE111, CF108, CF111, CF114,
CF115, CF118 and CF123 do not exist). These subjects were discarded upstream
by the consortium: do not use the numbers to estimate progress, use the
position in the list.

Note on sample size: the main article reports 34 iEEG patients recruited,
32 analysed after two exclusions for incomplete data, and 29 included in the
"super participant" of the multivariate analyses. The public release
distributes 38, so it also includes recordings not used in the published
analyses. Which ones are actually usable must be checked subject by subject:
the public `participants.tsv` does NOT contain the per-analysis inclusion
columns (`visual_responsiveness`, `category_selectivity`, `synchrony`) that
the consortium scripts expect.

---

## List in alphabetical order (processing order of the scripts)

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

## Python list ready for the three master scripts

To paste into `visual_responsiveness_master.py`, `category_selectivity_master.py`
and `synchrony_master.py`, in place of the hardcoded `["CF102"]` in the
`if __name__ == "__main__":` block.

WARNING: before using it, remove the subjects that failed in preprocessing
(see `log_preprocessing.txt`). A master script fails on the first subject for
which it does not find preprocessed data.

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

## Sizes observed during preprocessing

Useful for estimating run times: the cost depends on the number of channels
and on the length of the recording, not on the subject as such.

- CF102: 136 channels (110 ECoG, 24 sEEG, 2 ECG), 2471 s of recording,
  93 valid channels after rejection, ~13 minutes of preprocessing
- CE110: 188 channels, 4704 s
- CE119: 161 channels

CF102 is among the smallest so far: the estimate of 13 minutes per subject
is therefore optimistic, and larger subjects take considerably longer.
