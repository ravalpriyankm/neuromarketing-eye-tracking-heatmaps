"""Offline analysis utilities for a Master's neuromarketing research project.

Not affiliated with or endorsed by iMotions. All data processing is local.
"""

__version__ = "1.1.0"

EXPRESSION_COLUMNS = (
    "Anger", "Contempt", "Disgust", "Fear", "Joy", "Sadness", "Surprise",
    "Engagement", "Valence", "Sentimentality", "Confusion", "Neutral",
)
# Valence may be signed; don't imply a negative number means absent attention.
NONNEGATIVE_EXPRESSIONS = tuple(x for x in EXPRESSION_COLUMNS if x != "Valence")
GAZE_COLUMNS = ("ET_GazeLeftx", "ET_GazeLefty", "ET_GazeRightx", "ET_GazeRighty")
