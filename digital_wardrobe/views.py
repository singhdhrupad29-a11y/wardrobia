"""The `V_ItemCostPerWear` SQL VIEW — one definition, used by both the schema
migrator and the Analytics tab.

A view is a stored SELECT: it owns no rows, so every read re-joins the live
tables. Keeping the join + arithmetic here means the cost-per-wear formula has
a single source of truth in the database instead of being re-implemented in
Python, and any SQL client can run `SELECT * FROM V_ItemCostPerWear` to get
exactly what the UI shows.

The view holds every user's rows; the app filters with `WHERE user_id = :uid`.
"""

from sqlalchemy import text

# Same formula as digital_wardrobe.cpw.cost_per_wear: price / MAX(wears, 1).
# The wear metrics and status use denormalized columns for efficiency.
CREATE_COST_PER_WEAR_VIEW = """
CREATE VIEW V_ItemCostPerWear AS
SELECT
    ci.id                    AS id,
    ci.user_id               AS user_id,
    ci.name                  AS name,
    cat.name                 AS category,
    ci.purchase_price        AS purchase_price,
    ci.wear_count            AS wear_count,
    ci.status                AS status,
    ci.purchase_price /
        GREATEST(ci.wear_count, 1)
                           AS cost_per_wear
FROM ClothingItem ci
JOIN Category cat ON cat.id = ci.category_id
"""

DROP_COST_PER_WEAR_VIEW = "DROP VIEW IF EXISTS V_ItemCostPerWear"

COST_PER_WEAR_ROWS = """
SELECT id, name, category, purchase_price, wear_count, cost_per_wear
FROM V_ItemCostPerWear
WHERE user_id = :uid
ORDER BY cost_per_wear ASC, name ASC
"""


def fetch_cost_per_wear(session, user_id: int) -> list[dict]:
    """Run the view for one user and return plain dicts (no ORM mapping)."""
    result = session.execute(text(COST_PER_WEAR_ROWS), {"uid": user_id})
    rows = []
    for row in result.mappings():
        rows.append(
            {
                "id": int(row["id"]),
                "name": row["name"],
                "category": row["category"],
                "purchase_price": float(row["purchase_price"]),
                "wear_count": int(row["wear_count"]),
                "cost_per_wear": float(row["cost_per_wear"]),
            }
        )
    return rows
