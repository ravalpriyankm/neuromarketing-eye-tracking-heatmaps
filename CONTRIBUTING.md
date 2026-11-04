# Contributing

This repository is a 2026 maintenance refresh of the author's University of Essex 2022-2023 MSc research project. Contributions are welcome for reproducibility, portability and documentation.

## Development workflow

1. Fork the repository and create a focused branch.
2. Use Python 3.10 or later and `pip install -e .`.
3. Run `python -m unittest discover -s tests -v` and `python -m neuromarketing_heatmaps demo --output examples/generated` before opening a pull request.
4. Explain sensor units, display calibration and how a proposed change affects scientific interpretation.
5. Use synthetic examples in tests. Do not commit identifiable participant data, unpublished datasets, raw calibration metadata, proprietary experiment images or institutional credentials.
6. Keep the `legacy/` folder as an historical record; apply fixes to maintained modules instead.

Claims of improved accuracy or emotional validity require a clearly documented and independently reproducible evaluation, not only visual examples.
