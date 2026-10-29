"""Deterministic colour-harmony matrix.

Every pair of colours gets a stable 0-10 score computed by pure functions:
identical input ALWAYS produces identical output, so the whole recommender is
reproducible. The matrix is persisted into the ColorCompatibility table and the
outfit engine joins against it directly (it never recomputes scores at query
time).
"""

from sqlmodel import Session, select

from digital_wardrobe.models import ColorCompatibility

# Palette exposed in the add-item form.
COLORS = [
    "Black", "White", "Grey", "Charcoal", "Navy",
    "Beige", "Khaki", "Brown", "Red", "Maroon",
    "Burgundy", "Pink", "Purple", "Orange", "Yellow",
    "Olive", "Green", "Teal", "Blue",
]

# Hex swatches for the UI colour chips.
COLOR_HEX = {
    "Black": "#111111", "White": "#F5F5F0", "Grey": "#9E9E9E", "Charcoal": "#3B3B3B",
    "Navy": "#1F2A44", "Beige": "#D8C9A3", "Khaki": "#B7A67A", "Brown": "#6F4E37",
    "Red": "#C62828", "Maroon": "#7B1F24", "Burgundy": "#6D0E2B", "Pink": "#E8A0B4",
    "Purple": "#6A4C93", "Orange": "#E67E22", "Yellow": "#F4C542", "Olive": "#6B6B3A",
    "Green": "#2E7D32", "Teal": "#0F6B6B", "Blue": "#2C5F8A",
}

# Neutrals pair well with almost anything -> floor of 8/10.
NEUTRALS = {"Black", "White", "Grey", "Charcoal", "Navy", "Beige", "Khaki", "Brown"}

# Approximate hue angle (degrees) used by the deterministic scorer.
_HUE = {
    "Red": 0, "Maroon": 0, "Burgundy": 0, "Pink": 350,
    "Orange": 30, "Yellow": 55, "Olive": 70, "Green": 120,
    "Teal": 180, "Blue": 220, "Navy": 220, "Purple": 270,
    "Black": 0, "White": 0, "Grey": 0, "Charcoal": 0,
    "Beige": 40, "Khaki": 45, "Brown": 25,
}


def color_score(a: str, b: str) -> int:
    """Deterministic 0-10 harmony score for two colour names.

    Unknown colour names are treated as mid-grey (hue 0) so the scorer never
    raises a KeyError on a hand-typed item colour.
    """
    if a == b:
        return 9
    if a in NEUTRALS or b in NEUTRALS:
        return 8
    diff = abs(_HUE.get(a, 0) - _HUE.get(b, 0))
    diff = min(diff, 360 - diff)
    if diff >= 150:  # complementary
        return 9
    if diff <= 30:  # analogous
        return 8
    if diff >= 90:  # strong contrast
        return 7
    return 5  # clashing mid-range


def build_pairs(colors=COLORS):
    """Return sorted (color1, color2, score) tuples for every colour pair."""
    pairs, seen = [], set()
    for a in colors:
        for b in colors:
            key = tuple(sorted((a, b)))
            if key in seen:
                continue
            seen.add(key)
            pairs.append((key[0], key[1], color_score(a, b)))
    return pairs


def seed_matrix(session: Session, colors=COLORS) -> int:
    """Idempotently insert the colour matrix; returns the rows added."""
    added = 0
    for c1, c2, score in build_pairs(colors):
        exists = session.exec(
            select(ColorCompatibility).where(
                ColorCompatibility.color1 == c1,
                ColorCompatibility.color2 == c2,
            )
        ).first()
        if exists is None:
            session.add(ColorCompatibility(color1=c1, color2=c2, score=score))
            added += 1
    session.commit()
    return added
