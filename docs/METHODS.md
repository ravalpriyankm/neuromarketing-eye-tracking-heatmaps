# Methods and interpretation

## Context and design

The original 2022-2023 MSc project explored visualising iMotions eye-tracking and facial-expression outputs for image-based neuromarketing/perception research. The 2026 refresh supplies a reproducible, offline, descriptive visualisation workflow, not a clinical or commercial predictive model.

## Pipeline

1. Detect the actual iMotions `Row,Timestamp,...` header after its metadata preamble.
2. Forward-fill `SlideEvent` and keep media-on samples between `StartMedia` and the following event. Distinguish this from a formal fixation/saccade segmentation.
3. Keep relative timestamps, stimulus identifiers, gaze coordinates and expression scores. Do **not** replace missing signal values with zero.
4. Replace invalid gaze coordinates such as `-1` with missing values. Average the left and right gaze point only if both are present, otherwise use the valid eye.
5. Match eye-gaze samples to the temporally nearest expression-score sample **within the same recording and stimulus**; require the separation to be within `--tolerance-ms` (default 100 ms). Timing fields are assumed to be milliseconds and must be checked against the export configuration.
6. Map gaze coordinates into the **actual display rectangle occupied by the stimulus**, explicitly supplied as left, top, width and height. There is no universal `1920 × 1080` assumption.
7. Render a binned and Gaussian-smoothed **sample-density** map on top of the stimulus image. In expression-weighted mode, multiply sample counts by non-negative classifier scores. Output a descriptive overlay.

## Limits and failure modes

- Raw sample density can overrepresent higher sample rates and slow movements. It does **not** measure fixation duration, attention, interest or task success.
- Facial-expression estimates can be unreliable across participants, faces, lighting and cultural contexts. They are **not direct readouts of emotional states**.
- A weighted heatmap does not establish that a stimulus **caused** an emotional response.
- Original stimulus images/viewport telemetry are absent from this archive. Default dimensions in examples are illustrative only; otherwise the spatial overlay may be invalid.
- Nearest-neighbour time matching is not physical sensor synchronisation. Inspect timing offsets and missed matches before drawing conclusions.
- The 2023 notebook's historical R² = 0.644 is not recalculated here and does not prove generalisation to new participants.
- Multi-participant statistics or model training require participant-separated validation and a documented data collection/evaluation protocol.

## Reproducibility

Run `python -m neuromarketing_heatmaps demo --output examples/generated`, then `python -m unittest discover -s tests -v`. This demo is fully synthetic and checks that code paths and plotting execute; it does not validate research findings.

Sources: https://imotions.com/products/imotions-online/data-export/ ; https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/special-category-data/what-is-special-category-data/
