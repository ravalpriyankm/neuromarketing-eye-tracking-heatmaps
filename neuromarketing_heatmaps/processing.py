"""Read participant-local iMotions CSV exports and prepare trustworthy sensor data.

The raw iMotions export contains preliminary metadata rows and repeated column
names. Gaze and facial-expression channels are asynchronous; missing signal values
are *not* interpreted as zero or imputed during cleaning.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook

from . import EXPRESSION_COLUMNS, GAZE_COLUMNS

BASE_COLUMNS = ("Timestamp", "Participant", "SourceStimuliName", "SlideEvent")


class DataError(ValueError):
    """Input is unsupported or cannot be interpreted safely."""


def find_header_line(path: str | Path, max_lines: int = 500) -> int:
    """Locate iMotions' actual CSV header after its preamble."""
    with Path(path).open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        for index, line in enumerate(handle):
            if index >= max_lines:
                break
            try:
                cells = next(csv.reader([line]))
            except csv.Error:
                continue
            if len(cells) > 3 and cells[0].strip() == "Row" and "Timestamp" in cells:
                return index
    raise DataError("No iMotions CSV header found within the first 500 lines (Row, Timestamp, ...).")


def read_export(path: str | Path, participant: str | None = None) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file() or path.suffix.lower() != ".csv":
        raise DataError(f"Expected an existing CSV file: {path}")
    try:
        header = find_header_line(path)
        raw = pd.read_csv(path, skiprows=header, low_memory=False, encoding="utf-8-sig")
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise DataError(f"Cannot read {path.name}: {exc}") from exc
    return clean_export(raw, participant or path.stem)


def clean_export(raw: pd.DataFrame, participant: str) -> pd.DataFrame:
    if not isinstance(participant, str) or not participant.strip():
        raise DataError("A non-empty participant label is required")
    required = {"Timestamp", "SlideEvent", "SourceStimuliName"}
    missing = required - set(raw.columns)
    if missing:
        raise DataError("Missing iMotions columns: " + ", ".join(sorted(missing)))
    events = raw["SlideEvent"].replace("", pd.NA).ffill()
    if not events.eq("StartMedia").any():
        raise DataError("No StartMedia events found; expected a sensor export with media boundaries")
    active = events.eq("StartMedia")
    data = raw.loc[active].copy()
    data["SourceStimuliName"] = data["SourceStimuliName"].replace("", pd.NA).ffill()
    data["Participant"] = participant.strip()
    available = [c for c in GAZE_COLUMNS + EXPRESSION_COLUMNS if c in data.columns]
    if not available:
        raise DataError("Export contains neither eye-gaze nor facial-expression columns")
    for col in ("Timestamp", *available):
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=["Timestamp", "SourceStimuliName"])
    for col in GAZE_COLUMNS:
        if col in data:
            data.loc[data[col] < 0, col] = np.nan  # -1 means invalid iMotions gaze
    keep = [*BASE_COLUMNS, *(c for c in GAZE_COLUMNS if c in data),
            *(c for c in EXPRESSION_COLUMNS if c in data)]
    data = data[keep].reset_index(drop=True)
    if data.empty:
        raise DataError("No valid media samples remain after cleaning")
    return data


def load_cleaned(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise DataError(f"CSV not found: {path}")
    try:
        data = pd.read_csv(path, low_memory=False)
    except (OSError, pd.errors.ParserError) as exc:
        raise DataError(f"Could not read cleaned CSV: {exc}") from exc
    required = {"Timestamp", "SourceStimuliName", "Participant"}
    if not required.issubset(data.columns):
        raise DataError("Cleaned CSV needs Timestamp, SourceStimuliName, Participant")
    for col in ("Timestamp", *GAZE_COLUMNS, *EXPRESSION_COLUMNS):
        if col in data:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data


def safe_stem(value: str) -> str:
    """Sanitise labels for filenames without attempting participant de-identification."""
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value).strip()).strip("._-")
    return name[:70] or "sample"


def clean_folder(folder: str | Path, output: str | Path) -> list[tuple[Path, pd.DataFrame]]:
    folder, output = Path(folder), Path(output)
    if not folder.is_dir():
        raise DataError(f"Input folder does not exist: {folder}")
    csvs = sorted(x for x in folder.iterdir() if x.is_file() and not x.is_symlink() and x.suffix.lower() == ".csv")
    if not csvs:
        raise DataError("No CSV files found directly inside the input folder")
    if folder.resolve() == output.resolve():
        raise DataError("Input and output directories must be different")
    output.mkdir(parents=True, exist_ok=True)
    results = []
    used = set()
    for idx, path in enumerate(csvs):
        df = read_export(path)
        stem = safe_stem(path.stem)
        candidate = stem
        if candidate.lower() in used:
            candidate = f"{stem}_{idx+1}"
        used.add(candidate.lower())
        destination = output / f"{candidate}_cleaned.csv"
        df.to_csv(destination, index=False)
        results.append((destination, df))
    return results


def gaze_points(data: pd.DataFrame) -> pd.DataFrame:
    if any(k not in data for k in GAZE_COLUMNS):
        raise DataError("This dataset has no complete eye-gaze column schema")
    l = data[list(GAZE_COLUMNS[:2])].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    r = data[list(GAZE_COLUMNS[2:])].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    good_l = np.isfinite(l).all(axis=1) & (l >= 0).all(axis=1)
    good_r = np.isfinite(r).all(axis=1) & (r >= 0).all(axis=1)
    valid = good_l | good_r
    result = data.loc[valid, ["Timestamp", "Participant", "SourceStimuliName"]].copy()
    mid = np.full_like(l, np.nan)
    both = good_l & good_r
    mid[both] = (l[both] + r[both]) / 2
    mid[good_l & ~good_r] = l[good_l & ~good_r]
    mid[good_r & ~good_l] = r[good_r & ~good_l]
    result["gaze_x"] = mid[valid, 0]
    result["gaze_y"] = mid[valid, 1]
    return result.reset_index(drop=True)


def match_gaze_expression(data: pd.DataFrame, expression: str, tolerance_ms: float) -> pd.DataFrame:
    """Nearest-sample time matching within the same participant and stimulus.

    Timestamp is assumed to represent milliseconds; verify export settings.
    Association is temporal only and cannot prove an experienced emotion.
    """
    if expression not in EXPRESSION_COLUMNS:
        raise DataError(f"Unsupported expression score: {expression}")
    if not np.isfinite(tolerance_ms) or tolerance_ms <= 0:
        raise DataError("Time-matching tolerance must be a finite positive number in milliseconds")
    if expression not in data:
        raise DataError(f"Missing expression column: {expression}")
    gaze = gaze_points(data)
    expr = data.loc[data[expression].notna(), ["Timestamp", "Participant", "SourceStimuliName", expression]].copy()
    if gaze.empty or expr.empty:
        raise DataError("No usable gaze or expression samples available for time matching")
    for f in (gaze, expr):
        f["Timestamp"] = pd.to_numeric(f["Timestamp"], errors="coerce").astype("float64")
        f.dropna(subset=["Timestamp", "Participant", "SourceStimuliName"], inplace=True)
        f["Participant"] = f["Participant"].astype(str)
        f["SourceStimuliName"] = f["SourceStimuliName"].astype(str)
    gaze.sort_values("Timestamp", inplace=True)
    expr.sort_values("Timestamp", inplace=True)
    expr["expression_timestamp"] = expr["Timestamp"]
    merged = pd.merge_asof(gaze, expr, on="Timestamp", by=["Participant", "SourceStimuliName"],
                           tolerance=float(tolerance_ms), direction="nearest")
    merged["delta_ms"] = (merged["Timestamp"] - merged["expression_timestamp"]).abs()
    return merged


def workbook_from_cleaned(data: pd.DataFrame, destination: str | Path) -> Path:
    if "SourceStimuliName" not in data or data.empty:
        raise DataError("No stimuli available for workbook export")
    wb = Workbook()
    wb.remove(wb.active)
    taken: set[str] = set()
    for stimulus, subset in data.groupby("SourceStimuliName", sort=True, dropna=True):
        stem = re.sub(r"[\\/*?:\[\]]", "_", str(stimulus)).strip("'").strip()[:31] or "Stimulus"
        title = stem
        index = 1
        while title.lower() in taken:
            index += 1
            title = f"{stem[:27]}_{index}"[:31]
        taken.add(title.lower())
        ws = wb.create_sheet(title=title)
        ws.append(list(subset.columns))
        for tup in subset.itertuples(index=False, name=None):
            row = []
            for val in tup:
                if pd.isna(val):
                    row.append(None)
                elif isinstance(val, str) and val.startswith(("=", "+", "-", "@")):
                    row.append("'" + val)  # avoid spreadsheet formula injection
                elif hasattr(val, "item"):
                    row.append(val.item())
                else:
                    row.append(val)
            ws.append(row)
    if not wb.worksheets:
        raise DataError("No non-empty stimulus identifiers found")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destination)
    return destination


def dataset_summary(data: pd.DataFrame) -> dict:
    stats = {
        "total_rows": int(len(data)),
        "participants": int(data.Participant.nunique()) if "Participant" in data else 0,
        "stimuli": int(data.SourceStimuliName.nunique()) if "SourceStimuliName" in data else 0,
        "gaze_samples": 0,
        "facial_expression_samples": 0,
    }
    if set(GAZE_COLUMNS).issubset(data.columns):
        stats["gaze_samples"] = int(len(gaze_points(data)))
    available = [x for x in EXPRESSION_COLUMNS if x in data]
    if available:
        stats["facial_expression_samples"] = int(data[available].notna().any(axis=1).sum())
    return stats
