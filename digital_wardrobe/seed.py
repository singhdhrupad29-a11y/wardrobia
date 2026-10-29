"""Seed the MySQL database with demo categories, a user, items, an outfit,
wear logs and the full colour-harmony matrix.

Run from the project root:

    python -m digital_wardrobe.seed

The seed is idempotent: running it twice never duplicates rows.
"""

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

from sqlmodel import Session, select

from digital_wardrobe.color_matrix import seed_matrix
from digital_wardrobe.database import database_url, get_engine, init_db
from digital_wardrobe.demo import get_or_create_demo_user, get_or_create_second_user
from digital_wardrobe.models import (
    Brand,
    Category,
    ClothingItem,
    Occasion,
    Outfit,
    OutfitItem,
    Season,
    WearLog,
)

CATEGORIES = [
    # name, slug, wear_limit, sort_order
    ("Topwear", "topwear", 3, 1),
    ("Bottomwear", "bottomwear", 3, 2),
    ("Footwear", "footwear", 5, 3),
    ("Outerwear", "outerwear", 5, 4),
    ("Accessories", "accessories", 5, 5),
]

SEASONS = [
    # name, slug, sort_order
    ("Summer", "summer", 1),
    ("Winter", "winter", 2),
    ("Rainy", "rainy", 3),
    ("Spring", "spring", 4),
]

BRANDS = ["Allen Solly", "H&M", "Levi's", "Nike", "Adidas", "Uniqlo", "Woodland"]

# The 3NF schema stores no wear counters and no status column: every item's
# CLEAN/LAUNDRY state is derived from WearLog + the wash dates, so the seed
# now writes real wear rows and picks wash dates that reproduce the intended
# status below (see _wash_plan).
CLEAN = "CLEAN"
DIRTY = "LAUNDRY"

DEMO_ITEMS = [
    # name, category, color, formality, price, wear_count, status, brand, season
    ("Navy Oxford Shirt", "Topwear", "Navy", 4, 2400, 6, CLEAN, "Allen Solly", "Spring"),
    ("White Crew Tee", "Topwear", "White", 1, 800, 12, DIRTY, "H&M", "Summer"),
    ("Charcoal Sweater", "Topwear", "Charcoal", 3, 1600, 4, CLEAN, "Uniqlo", "Winter"),
    ("Light Blue Polo", "Topwear", "Blue", 2, 1200, 8, CLEAN, "Nike", "Summer"),
    ("Black Chinos", "Bottomwear", "Black", 3, 1800, 10, CLEAN, "Allen Solly", "Spring"),
    ("Beige Chinos", "Bottomwear", "Beige", 3, 1800, 5, CLEAN, "H&M", "Spring"),
    ("Blue Jeans", "Bottomwear", "Blue", 1, 1500, 15, DIRTY, "Levi's", "Summer"),
    ("White Sneakers", "Footwear", "White", 1, 3200, 20, CLEAN, "Nike", "Summer"),
    ("Brown Leather Shoes", "Footwear", "Brown", 5, 4200, 3, CLEAN, "Woodland", "Winter"),
    ("Black Boots", "Footwear", "Black", 3, 3600, 2, DIRTY, "Adidas", "Winter"),
]

SAMPLE_OUTFIT = ("Smart Casual Blue", "SMART_CASUAL", [
    "Navy Oxford Shirt", "Beige Chinos", "White Sneakers",
])

# A second account so two logins visibly open two different wardrobes.
SECOND_ITEMS = [
    # name, category, color, formality, price, wear_count, status, brand, season
    ("Maroon Oversized Tee", "Topwear", "Maroon", 1, 900, 3, CLEAN, "H&M", "Summer"),
    ("Olive Cargo Pants", "Bottomwear", "Olive", 2, 2100, 6, CLEAN, "Woodland", "Rainy"),
    ("Grey Running Shoes", "Footwear", "Grey", 1, 2800, 9, DIRTY, "Adidas", "Spring"),
    ("Khaki Bomber Jacket", "Outerwear", "Khaki", 3, 3400, 2, CLEAN, "Uniqlo", "Winter"),
]


def _wear_dates(wears: int) -> list[date]:
    """`wears` distinct consecutive days ending today (oldest first)."""
    start = date.today() - timedelta(days=max(wears - 1, 0))
    return [start + timedelta(days=j) for j in range(wears)]


def _wash_plan(wears: int, wear_limit: int, intended_dirty: bool) -> tuple[date | None, date | None]:
    """Pick (last_washed_at, sent_to_laundry_at) so the derived status equals
    `intended_dirty` once the wear rows exist.

    Derivation rule: LAUNDRY when the item was hand-flagged, or when
    COUNT(WearLog dated >= last_washed_at) >= Category.wear_limit.
    """
    today = date.today()
    if intended_dirty:
        if wears >= wear_limit:
            # Threshold-dirty: exactly `wear_limit` wears land on/after the wash.
            return _wear_dates(wears)[wears - wear_limit], None
        # Not enough wears to cross the limit — flag it by hand instead.
        return None, today
    if wears == 0:
        return None, None
    # Clean: keep wears-since-wash at min(limit - 1, wears).
    target = min(wear_limit - 1, wears)
    if target >= wears:
        return _wear_dates(wears)[0] - timedelta(days=1), None
    return _wear_dates(wears)[wears - target], None


def _seed_items(
    session, user, items, cat_ids, cat_limits, season_ids, brand_ids
) -> None:
    """Insert any missing items for one user, plus their WearLog history.

    Idempotent per user + name: existing items keep their wash dates and
    never gain duplicate wear rows.
    """
    for (
        name,
        cat_name,
        color,
        formality,
        price,
        wears,
        status,
        brand_name,
        season_name,
    ) in items:
        item = session.exec(
            select(ClothingItem).where(
                ClothingItem.user_id == user.id, ClothingItem.name == name
            )
        ).first()
        last_washed, sent = _wash_plan(
            wears, cat_limits[cat_name.lower()], status == DIRTY
        )
        dates = _wear_dates(wears)
        since = (
            wears
            if last_washed is None
            else sum(1 for d in dates if d >= last_washed)
        )
        if item is None:
            item = ClothingItem(
                user_id=user.id,
                category_id=cat_ids[cat_name.lower()],
                name=name,
                color=color,
                formality_score=formality,
                purchase_price=Decimal(price),
                brand=brand_name,
                season=season_name,
                brand_id=brand_ids.get(brand_name),
                season_id=season_ids.get(season_name.lower()),
                wear_count=wears,
                wear_count_since_wash=since,
                status=status,
                last_washed_at=last_washed,
                sent_to_laundry_at=sent,
            )
            session.add(item)
            session.flush()
        else:
            # Backfill brand/season and metrics on existing rows
            item.brand = item.brand or brand_name
            item.season = item.season or season_name
            item.brand_id = brand_ids.get(brand_name) or item.brand_id
            item.season_id = season_ids.get(season_name.lower()) or item.season_id
            item.wear_count = wears
            item.wear_count_since_wash = since
            item.status = status
            session.add(item)

        has_logs = (
            session.exec(select(WearLog.id).where(WearLog.item_id == item.id)).first()
            is not None
        )
        if not has_logs:
            item.last_washed_at = last_washed
            item.sent_to_laundry_at = sent
            session.add(item)
            for worn_on in dates:
                session.add(
                    WearLog(user_id=user.id, item_id=item.id, date_worn=worn_on)
                )
    session.commit()


def seed() -> None:
    url = urlparse(database_url())
    print(f"Connecting to MySQL: {url.hostname}:{url.port or 3306} / {url.path.strip('/') or '(no db)'}")
    init_db()

    with Session(get_engine()) as session:
        # ── Categories ─────────────────────────────────────────────────────
        for name, slug, wear_limit, sort_order in CATEGORIES:
            exists = session.exec(select(Category).where(Category.slug == slug)).first()
            if exists is None:
                session.add(
                    Category(name=name, slug=slug, wear_limit=wear_limit, sort_order=sort_order)
                )
        session.commit()

        # ── Seasons ─────────────────────────────────────────────────────────
        for name, slug, sort_order in SEASONS:
            exists = session.exec(select(Season).where(Season.slug == slug)).first()
            if exists is None:
                session.add(Season(name=name, slug=slug, sort_order=sort_order))
        session.commit()

        # ── Brands ──────────────────────────────────────────────────────────
        for name in BRANDS:
            exists = session.exec(select(Brand).where(Brand.name == name)).first()
            if exists is None:
                session.add(Brand(name=name))
        session.commit()

        user = get_or_create_demo_user(session)
        second = get_or_create_second_user(session)
        cat_ids = {c.slug: c.id for c in session.exec(select(Category)).all()}
        cat_limits = {c.slug: c.wear_limit for c in session.exec(select(Category)).all()}
        season_ids = {s.slug: s.id for s in session.exec(select(Season)).all()}
        brand_ids = {b.name: b.id for b in session.exec(select(Brand)).all()}

        # ── Items (one wardrobe per account, with real wear history) ──────
        _seed_items(session, user, DEMO_ITEMS, cat_ids, cat_limits, season_ids, brand_ids)
        _seed_items(session, second, SECOND_ITEMS, cat_ids, cat_limits, season_ids, brand_ids)

        # ── Legacy uploads ─────────────────────────────────────────────────
        # Older rows stored "/upload/<file>" pointing at assets/upload/, which
        # the dev server never served. Move those files into the Reflex upload
        # dir and re-point image_url at the bare file name.
        from reflex.components.core.upload import get_upload_dir

        old_dir = Path(__file__).resolve().parent.parent / "assets" / "upload"
        upload_dir = get_upload_dir()
        moved = 0
        for item in session.exec(select(ClothingItem)).all():
            ref = item.image_url or ""
            if not ref.startswith("/upload/"):
                continue
            filename = ref.rsplit("/", 1)[-1]
            source = old_dir / filename
            if source.exists():
                upload_dir.mkdir(parents=True, exist_ok=True)
                (upload_dir / filename).write_bytes(source.read_bytes())
            item.image_url = filename
            session.add(item)
            moved += 1
        session.commit()
        if moved:
            print(f"Legacy uploads migrated: {moved}")

        # ── Sample outfit ──────────────────────────────────────────────────
        if session.exec(select(Outfit).where(Outfit.user_id == user.id)).first() is None:
            outfit = Outfit(
                user_id=user.id,
                name=SAMPLE_OUTFIT[0],
                occasion=Occasion(SAMPLE_OUTFIT[1]),
                notes="Signature everyday outfit",
            )
            session.add(outfit)
            session.commit()
            session.refresh(outfit)
            for position, item_name in enumerate(SAMPLE_OUTFIT[2], start=1):
                item = session.exec(
                    select(ClothingItem).where(
                        ClothingItem.user_id == user.id, ClothingItem.name == item_name
                    )
                ).first()
                if item is not None:
                    session.add(
                        OutfitItem(outfit_id=outfit.id, item_id=item.id, position=position)
                    )
            session.commit()

        # ── Colour matrix ──────────────────────────────────────────────────
        added = seed_matrix(session)
        print("Categories: seeded")
        print(f"Seasons:    {len(SEASONS)}")
        print(f"Brands:     {len(BRANDS)}")
        print(f"Demo user:  {user.email} / demo1234 ({len(DEMO_ITEMS)} items)")
        print(f"Second user: {second.email} / sam1234 ({len(SECOND_ITEMS)} items)")
        print(f"Colour pairs: {added} inserted")

    print("Done. Start the app with `reflex run`.")


if __name__ == "__main__":
    seed()
