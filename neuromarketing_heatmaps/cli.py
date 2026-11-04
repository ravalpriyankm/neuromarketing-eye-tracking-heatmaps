"""Command-line entry point for headless local research workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, NONNEGATIVE_EXPRESSIONS
from .demo import build_demo
from .processing import DataError, clean_folder, dataset_summary, load_cleaned, read_export, workbook_from_cleaned
from .visualisation import render_heatmap


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="neuromarketing-heatmaps",
                                 description="Offline gaze and expression analysis; University of Essex MSc research refresh.")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check local libraries and platform capabilities")
    demo = sub.add_parser("demo", help="Generate a fully synthetic stimulus, raw export and two heatmaps")
    demo.add_argument("--output", required=True, type=Path)
    clean = sub.add_parser("clean", help="Clean an iMotions raw CSV file or directory")
    clean.add_argument("source", type=Path)
    clean.add_argument("--output", type=Path, required=True)
    workbook = sub.add_parser("workbook", help="Split cleaned samples into stimulus-named Excel sheets")
    workbook.add_argument("cleaned_csv", type=Path)
    workbook.add_argument("--output", type=Path, required=True)
    summ = sub.add_parser("summary", help="Print non-identifying sample counts from a cleaned CSV")
    summ.add_argument("cleaned_csv", type=Path)
    stimuli = sub.add_parser("stimuli", help="List available stimulus identifiers and row counts")
    stimuli.add_argument("cleaned_csv", type=Path)
    heatmap = sub.add_parser("heatmap", help="Render gaze-density or time-matched expression-weighted overlay")
    heatmap.add_argument("cleaned_csv", type=Path)
    heatmap.add_argument("--image", type=Path, required=True)
    heatmap.add_argument("--stimulus", required=True, help="Exact SourceStimuliName")
    heatmap.add_argument("--display-width", type=int, required=True, help="Displayed stimulus width in gaze pixels")
    heatmap.add_argument("--display-height", type=int, required=True, help="Displayed stimulus height in gaze pixels")
    heatmap.add_argument("--display-left", type=float, default=0)
    heatmap.add_argument("--display-top", type=float, default=0)
    heatmap.add_argument("--expression", choices=NONNEGATIVE_EXPRESSIONS)
    heatmap.add_argument("--tolerance-ms", type=float, default=100)
    heatmap.add_argument("--output", type=Path, required=True)
    heatmap.add_argument("--bins", type=int, default=200)
    return ap


def run(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "doctor":
            import pandas, numpy, matplotlib, PIL, openpyxl
            print(json.dumps({"project": __version__, "python": sys.version.split()[0],
                              "numpy": numpy.__version__, "pandas": pandas.__version__,
                              "matplotlib": matplotlib.__version__, "pillow": PIL.__version__,
                              "openpyxl": openpyxl.__version__, "offline": True}, indent=2))
        elif args.command == "clean":
            if args.source.is_dir():
                result = clean_folder(args.source, args.output)
                print(json.dumps({"files_cleaned": len(result), "output": str(args.output)}, indent=2))
            else:
                data = read_export(args.source)
                args.output.parent.mkdir(parents=True, exist_ok=True)
                if args.output.is_dir():
                    raise DataError("For a single input CSV, --output must be a CSV filename")
                data.to_csv(args.output, index=False)
                print(json.dumps({"output": str(args.output), "statistics": dataset_summary(data)}, indent=2))
        elif args.command == "workbook":
            print(workbook_from_cleaned(load_cleaned(args.cleaned_csv), args.output))
        elif args.command == "summary":
            print(json.dumps(dataset_summary(load_cleaned(args.cleaned_csv)), indent=2))
        elif args.command == "stimuli":
            data = load_cleaned(args.cleaned_csv)
            counts = data["SourceStimuliName"].dropna().astype(str).value_counts()
            print(json.dumps({"recording": str(args.cleaned_csv), "stimuli": [
                {"name": str(name), "rows": int(count)} for name, count in counts.items()]}, indent=2))
        elif args.command == "heatmap":
            stats = render_heatmap(load_cleaned(args.cleaned_csv), args.image, args.output,
                stimulus=args.stimulus, display_width=args.display_width, display_height=args.display_height,
                display_left=args.display_left, display_top=args.display_top,
                expression=args.expression, tolerance_ms=args.tolerance_ms, bins=args.bins)
            print(json.dumps(stats, indent=2))
        elif args.command == "demo":
            src, image = build_demo(args.output)
            data = read_export(src, participant="synthetic")
            cleaned = args.output / "synthetic_cleaned.csv"
            data.to_csv(cleaned, index=False)
            basic = render_heatmap(data, image, args.output / "demo_gaze.png", stimulus="synthetic_stimulus",
                                   display_width=1280, display_height=720)
            weighted = render_heatmap(data, image, args.output / "demo_joy_weighted.png",
                                      stimulus="synthetic_stimulus", display_width=1280,
                                      display_height=720, expression="Joy", tolerance_ms=100)
            print(json.dumps({"synthetic_data_only": True, "summary": dataset_summary(data),
                              "gaze": basic, "weighted": weighted}, indent=2))
        return 0
    except (DataError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(run())
