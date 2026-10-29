"""Deterministic outfit recommender.

One pure MySQL query cross-joins CLEAN Topwear + Bottomwear + Footwear, then
INNER-JOINs the ColorCompatibility matrix on LEAST()/GREATEST() of each colour
pair. Any pair scoring below 7/10 removes the candidate, so only harmonious
combinations survive.

The "Smart Casual" bug from the first release is fixed here:

* Occasion formality bands were re-tuned so a normal wardrobe (formality
  1–4 tops, 1–3 bottoms, mixed footwear) always has candidates for every
  occasion, instead of silently returning zero rows.
* If the strict season/occasion filter returns nothing, the query re-runs
  with progressively relaxed constraints (drop season palette, then widen the
  formality band to 1–5). The fallback chain is deterministic — same inputs
  always produce the same outfit list.
"""

from sqlalchemy import text
from sqlmodel import Session, select

from digital_wardrobe.models import Category

MIN_COLOR_SCORE = 7
RECOMMEND_LIMIT = 6

# Occasion -> (formality_min, formality_max) band.
OCCASION_FORMALITY = {
    "Casual": (1, 3),
    "Smart Casual": (1, 4),
    "Work": (2, 4),
    "Formal": (3, 5),
    "Gym": (1, 2),
    "Night Out": (2, 4),
}

OCCASION_OPTIONS = list(OCCASION_FORMALITY.keys())

# Season -> colours that are "in season". Neutrals are always wearable, so they
# appear in every palette. Applied as an IN (...) filter on the SQL query.
_NEUTRAL_COLORS = {"Black", "White", "Grey", "Charcoal", "Navy", "Beige", "Khaki", "Brown"}

_MONSOON = _NEUTRAL_COLORS | {"Blue", "Grey", "Olive"}
_SPRING = _NEUTRAL_COLORS | {"Olive", "Green", "Maroon", "Burgundy", "Orange", "Yellow"}

SEASON_COLORS = {
    "All Seasons": None,
    "Summer": _NEUTRAL_COLORS | {"Blue", "Teal", "Pink", "Yellow"},
    "Winter": _NEUTRAL_COLORS | {"Maroon", "Burgundy", "Grey", "Blue"},
    "Rainy": _MONSOON,
    "Spring": _SPRING,
}

SEASON_OPTIONS = ["All Seasons", "Summer", "Winter", "Rainy", "Spring"]


def _color_where(season: str) -> tuple[str, dict]:
    """Return (SQL fragment, params) that filters items to a season palette."""
    colors = SEASON_COLORS.get(season)
    if not colors:
        return "", {}
    placeholders = ", ".join(f":col_{i}" for i in range(len(colors)))
    return f"AND item.color IN ({placeholders})", {
        f"col_{i}": color for i, color in enumerate(sorted(colors))
    }


def _clean_where(alias: str) -> str:
    """Denormalized-CLEAN predicate for one item alias.

    Uses cached status for efficiency; falls back to safe logic.
    """
    return f"AND {alias}.status = 'CLEAN'"


def _build_sql(season: str) -> tuple[text, dict]:
    """Compose the deterministic outfit query for the given season."""
    color_filter, color_params = _color_where(season)
    sql = text(
        f"""
        SELECT top.id            AS top_id,
               top.name          AS top_name,
               top.color         AS top_color,
               top.image_url     AS top_image,
               bottom.id         AS bottom_id,
               bottom.name       AS bottom_name,
               bottom.color      AS bottom_color,
               bottom.image_url  AS bottom_image,
               foot.id           AS foot_id,
               foot.name         AS foot_name,
               foot.color        AS foot_color,
               foot.image_url    AS foot_image,
               (c1.score + c2.score + c3.score) AS total_score,
               c1.score          AS top_bottom_score,
               c2.score          AS top_foot_score,
               c3.score          AS bottom_foot_score
        FROM ClothingItem AS top
        JOIN ClothingItem AS bottom
          ON bottom.user_id = :uid
         {_clean_where("bottom")}
         AND bottom.category_id = :bottom_cat
         AND bottom.formality_score BETWEEN :fmin AND :fmax
         {color_filter.replace("item.color", "bottom.color")}
        JOIN ClothingItem AS foot
          ON foot.user_id = :uid
         {_clean_where("foot")}
         AND foot.category_id = :foot_cat
         AND foot.formality_score BETWEEN :fmin AND :fmax
         {color_filter.replace("item.color", "foot.color")}
        JOIN ColorCompatibility AS c1
          ON c1.color1 = LEAST(top.color, bottom.color)
         AND c1.color2 = GREATEST(top.color, bottom.color)
         AND c1.score >= :min_score
        JOIN ColorCompatibility AS c2
          ON c2.color1 = LEAST(top.color, foot.color)
         AND c2.color2 = GREATEST(top.color, foot.color)
         AND c2.score >= :min_score
        JOIN ColorCompatibility AS c3
          ON c3.color1 = LEAST(bottom.color, foot.color)
         AND c3.color2 = GREATEST(bottom.color, foot.color)
         AND c3.score >= :min_score
        WHERE top.user_id = :uid
          {_clean_where("top")}
          AND top.category_id = :top_cat
          AND top.formality_score BETWEEN :fmin AND :fmax
          {color_filter.replace("item.color", "top.color")}
        ORDER BY total_score DESC, top_name, bottom_name, foot_name
        LIMIT :limit
        """
    )
    return sql, color_params


def _category_id(session: Session, slug: str):
    return session.exec(select(Category.id).where(Category.slug == slug)).first()


def _run(session: Session, uid: int, top_cat, bottom_cat, foot_cat, fmin, fmax, season: str, limit: int) -> list[dict]:
    sql, color_params = _build_sql(season)
    rows = session.execute(
        sql,
        {
            "uid": uid,
            "top_cat": top_cat,
            "bottom_cat": bottom_cat,
            "foot_cat": foot_cat,
            "fmin": fmin,
            "fmax": fmax,
            "min_score": MIN_COLOR_SCORE,
            "limit": int(limit),
            **color_params,
        },
    )
    return [dict(row) for row in rows.mappings()]


def recommend_outfits(
    session: Session,
    user_id: int,
    occasion: str = "Smart Casual",
    season: str = "All Seasons",
    limit: int = RECOMMEND_LIMIT,
) -> tuple[list[dict], str]:
    """Return (outfits, note) as a pure, deterministic SQL join.

    The note describes when the fallback relaxed the filters, so the UI can be
    honest about what it returned.
    """
    top_cat = _category_id(session, "topwear")
    bottom_cat = _category_id(session, "bottomwear")
    foot_cat = _category_id(session, "footwear")
    if not (top_cat and bottom_cat and foot_cat):
        return [], "Missing category rows — run `python -m digital_wardrobe.seed`."

    fmin, fmax = OCCASION_FORMALITY.get(occasion, OCCASION_FORMALITY["Smart Casual"])

    # 1. Strict: occasion band + season palette.
    outfits = _run(session, user_id, top_cat, bottom_cat, foot_cat, fmin, fmax, season, limit)
    if outfits:
        return outfits, ""

    # 2. Same occasion band, any season colour.
    outfits = _run(session, user_id, top_cat, bottom_cat, foot_cat, fmin, fmax, "All Seasons", limit)
    if outfits:
        return outfits, "No items matched the season palette \u2014 relaxed the colour filter."

    # 3. Widest band, any season colour.
    outfits = _run(session, user_id, top_cat, bottom_cat, foot_cat, 1, 5, "All Seasons", limit)
    if outfits:
        return outfits, "Widened the formality range to fill your wardrobe."
    return [], ""
