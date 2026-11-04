# Release notes: 2026 research-software refresh (v1.1.0)

## Original project

University of Essex MSc Computer Science final research work, 2022-2023. The original notebooks, procedural GUI and experimental browser-scrolling scripts were deposited in the public repository in December 2023.

## Changes

- Rebuilt the iMotions CSV cleaning and eye-gaze analysis as reusable Python modules.
- Added a simple desktop Tkinter interface and testable command-line commands.
- Replaced fixed-display `1920 × 1080` coordinate assumptions with explicit viewport calibration fields.
- Added temporal matching of gaze and facial-expression scores, within recording and stimulus.
- Preserved missing measurements instead of filling them with artificial zero values.
- Added 12 derived research recordings with new recording labels, excluding source file demographics and metadata. Original raw ZIP is intentionally omitted.
- Added a reproducible synthetic example, package metadata, CLI documentation, tests, data statement and research-ethics checklist.
- Preserved original code/notebooks as an historical archive, with notebook outputs and personal paths scrubbed.

## Limitations

The original stimulus image collection was not supplied; the public research recordings cannot be accurately laid over their original images without their actual media position. The historical machine-learning findings were not independently replicated. Publisher must verify rights for public sensor-data release before posting to a public remote.
