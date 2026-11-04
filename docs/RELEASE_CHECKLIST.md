# Public repository readiness

## Confirmed locally on 2026-11-04

- [x] Python modules compile.
- [x] CLI doctor runs offline.
- [x] Synthetic gaze and expression visualisations generate image files.
- [x] Research CSV.gz recordings load, list stimuli and support time matching.
- [x] All available regression tests pass locally.
- [x] The original 2023 research notebooks are preserved without stored outputs.
- [x] Absolute personal file paths were removed from the historical notebooks.
- [x] Public data excludes original CSV preambles containing age, gender, recording calendar dates and named study metadata.
- [x] Original raw sensor ZIP and proprietary stimulus images are absent from the rebuilt working tree.

## Before pushing to a public GitHub remote

- [ ] Verify participant consent, research governance and licence permissions for **public release of individual-level sensor traces**; see `docs/PUBLICATION_AND_ETHICS.md`.
- [ ] Check repository history: the previously committed `raw_data.zip` may remain accessible in old commits even if deleted from the latest version.
- [ ] Confirm software licences and any third-party stimulus-image ownership.
- [ ] Run GitHub Actions on a real public branch; the Windows/macOS runners have not yet been independently executed.
- [ ] Review licence wording for the dataset: MIT only covers the source code; no explicit downstream reuse licence is granted for participant measurements by this repository.
- [ ] If unable to confirm permission, publish only the synthetic demonstration and omit `data/public_recordings`.
