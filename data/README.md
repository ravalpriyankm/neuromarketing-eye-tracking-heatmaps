# Public research data (derived, de-identified)

The repository includes **12 research recordings**, reconstructed from the uploaded 2023 iMotions CSV exports and provided as `REC001.csv.gz` ... `REC012.csv.gz` (one gzip-compressed CSV per recording).

These are **recording codes, not an asserted number of unique participants**. Some original exports reused respondent labels across different sessions. `data/manifest.json` lists per-recording row and usable-sample counts.

## Disclosure and transformations

**Included columns:** relative `Timestamp`; stimulus identifier `SourceStimuliName`; propagated media boundary `SlideEvent`; pseudonymous `Participant` (recording code); eye-gaze channel columns; and available facial-expression classifier-score columns.

**Removed:** raw `#INFO` preambles, respondent names/IDs, stated ages, gender, calendar dates/times of recordings, study titles, recording metadata, facial-landmark coordinates, raw device identifiers, and other unrelated fields. No original stimulus photographs are included because they were not in the supplied repository ZIP.

Original source CSV files and the original `raw_data.zip` **are not included**. The `.csv.gz` files can be read directly with pandas:

```python
import pandas as pd
recording = pd.read_csv('data/public_recordings/REC001.csv.gz')
print(recording.columns)
```

Or use the packaged CLI:

```bash
python -m neuromarketing_heatmaps summary data/public_recordings/REC001.csv.gz
python -m neuromarketing_heatmaps stimuli data/public_recordings/REC001.csv.gz
```

## Scientific caveats

- Sampling frequencies, missing-data patterns and sensor validity can vary across recordings.
- `Timestamp` is a relative export field; the processing workflow assumes milliseconds when applying matching tolerance. Verify this before interpreting timing.
- Facial-expression scores are classifier outputs, **not validated subjective reports** of emotions.
- Heatmaps created from raw gaze samples describe sample density, **not fixation duration**.
- The actual display viewport and original stimulus images are not bundled, so claims about exact image-region attention require separately verified calibration.
- Individual sensor traces, even with obvious identifiers removed, can retain some **re-identification risk**. This release does not certify mathematical anonymity or ethics compliance.

## Research permissions and reuse

The uploader stated that sharing the research data was permitted. We have not independently inspected original participant consent wording, the University of Essex's research data policy for the relevant project, or the rights in iMotions-derived outputs.

**Software:** MIT (`../LICENSE`). **Dataset:** no separate open-data licence is asserted here. Public visibility does not automatically grant unrestricted reuse. The data rights holder should select a suitable data licence **only if** the necessary permissions cover downstream reuse and redistribution.

Before making a GitHub repository public, review [`../docs/PUBLICATION_AND_ETHICS.md`](../docs/PUBLICATION_AND_ETHICS.md). If permissions do not cover public distribution of individual-level sensor observations, remove `data/public_recordings/` from the published copy and rely on the synthetic demo instead.
