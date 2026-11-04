"""Render descriptive gaze density and time-matched expression-weighted maps."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

from . import NONNEGATIVE_EXPRESSIONS
from .processing import DataError, gaze_points, match_gaze_expression


def _blur(histogram: np.ndarray, sigma: float) -> np.ndarray:
    """Small dependency-free Gaussian smoothing on a fixed-size histogram."""
    radius = max(1, int(round(3 * sigma)))
    x = np.arange(-radius, radius + 1, dtype=float)
    kernel = np.exp(-x * x / (2 * sigma * sigma))
    kernel /= kernel.sum()
    a = np.apply_along_axis(lambda row: np.convolve(row, kernel, mode="same"), 1, histogram)
    return np.apply_along_axis(lambda col: np.convolve(col, kernel, mode="same"), 0, a)


def density_map(x: np.ndarray, y: np.ndarray, weights: np.ndarray | None = None,
                bins: int = 200, sigma: float = 3.5) -> np.ndarray:
    if bins < 32 or bins > 1024:
        raise DataError("Heatmap bins must be between 32 and 1024")
    if not np.isfinite(sigma) or sigma <= 0:
        raise DataError("Gaussian smoothing sigma must be positive")
    counts, _, _ = np.histogram2d(y, x, bins=(bins, bins), range=((0, 1), (0, 1)), weights=weights)
    smoothed = _blur(counts, sigma)
    peak = float(np.max(smoothed))
    return smoothed / peak if peak > 0 else smoothed


def render_heatmap(
    cleaned: pd.DataFrame,
    image_path: str | Path,
    output_path: str | Path,
    *,
    stimulus: str,
    display_width: int,
    display_height: int,
    display_left: float = 0,
    display_top: float = 0,
    expression: str | None = None,
    tolerance_ms: float = 100,
    bins: int = 200,
) -> dict:
    """Overlay samples on the provided stimulus image.

    display_* describe the *observed media bounding rectangle on the recording
    display*, in source gaze pixels. Correct stimulus registration is the user's
    responsibility: without recorded viewport dimensions, maps are exploratory.
    """
    if not stimulus or not isinstance(stimulus, str):
        raise DataError("Specify the exact SourceStimuliName")
    if display_width <= 0 or display_height <= 0:
        raise DataError("Media display dimensions must be greater than zero")
    if not np.isfinite(display_left) or not np.isfinite(display_top):
        raise DataError("Media display position must be finite")
    data = cleaned.loc[cleaned["SourceStimuliName"].astype(str).eq(stimulus)].copy()
    if data.empty:
        raise DataError(f"No samples for stimulus: {stimulus!r}")
    if expression:
        if expression not in NONNEGATIVE_EXPRESSIONS:
            raise DataError("Expression weighting requires a non-negative expression score (not signed Valence)")
        samples = match_gaze_expression(data, expression, tolerance_ms)
        sample_count_before_match = len(samples)
        samples = samples.loc[np.isfinite(samples[expression]) & (samples[expression] >= 0)].copy()
        weights = samples[expression].to_numpy(dtype=float)
        mode = f"{expression} score-weighted gaze"
    else:
        samples = gaze_points(data)
        sample_count_before_match = len(samples)
        weights = None
        mode = "raw gaze sample density"
    if samples.empty:
        raise DataError("No valid paired gaze/expression samples; try gaze-only mode or review timestamp settings")
    x = (samples["gaze_x"].to_numpy(dtype=float) - display_left) / display_width
    y = (samples["gaze_y"].to_numpy(dtype=float) - display_top) / display_height
    valid = np.isfinite(x) & np.isfinite(y) & (x >= 0) & (x <= 1) & (y >= 0) & (y <= 1)
    x, y = x[valid], y[valid]
    if weights is not None:
        weights = weights[valid]
    if not len(x):
        raise DataError("No gaze points inside media bounds. Check display width, height and offset")
    if weights is not None and not np.any(weights > 0):
        raise DataError("Matched expression scores are all zero; cannot create weighted heatmap")
    density = density_map(x, y, weights=weights, bins=bins)
    # Agg is a headless, deterministic backend. Tk GUI may import this safely.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    image_path = Path(image_path)
    if not image_path.is_file():
        raise DataError(f"Stimulus image not found: {image_path}")
    try:
        with Image.open(image_path) as img:
            image = img.convert("RGB")
    except (OSError, ValueError) as exc:
        raise DataError(f"Cannot open stimulus image: {exc}") from exc
    w, h = image.size
    # Convert the small density grid to exactly the stimulus image dimensions.
    density_img = Image.fromarray(np.asarray(density * 255, dtype=np.uint8)).resize((w, h), Image.Resampling.BILINEAR)
    overlay = np.asarray(density_img, dtype=float) / 255
    alpha = np.clip(overlay * 0.83, 0, 0.83)
    fig, ax = plt.subplots(figsize=(max(6, w / 180), max(3.8, h / 180)), dpi=120)
    ax.imshow(image, origin="upper", extent=(0, w, h, 0))
    # Apply per-pixel alpha: low sample density leaves the original image visible.
    ax.imshow(overlay, cmap="inferno", origin="upper", extent=(0, w, h, 0),
              alpha=alpha, vmin=0, vmax=1, interpolation="bilinear")
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{stimulus} | {mode} | n={len(x)}", fontsize=10, pad=12)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fig.savefig(output_path, dpi=120, bbox_inches="tight", pad_inches=0.13)
    finally:
        plt.close(fig)
    return {
        "mode": mode,
        "stimulus": stimulus,
        "source_gaze_samples": int(sample_count_before_match),
        "temporally_matched_and_in_bounds_samples": int(len(x)),
        "time_tolerance_ms": tolerance_ms if expression else None,
        "display_bounds_pixels": {"left": display_left, "top": display_top,
                                  "width": display_width, "height": display_height},
        "image_size_pixels": {"width": w, "height": h},
        "output": str(output_path),
        "warning": "Descriptive raw-sample visualisation, not fixation duration or a direct measurement of emotion.",
    }
