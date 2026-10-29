"""SQLModel schema for the Digital Wardrobe MySQL database.

Nine tables: User, Category, Brand, Season, ClothingItem, Outfit, OutfitItem,
WearLog, ColorCompatibility. Column names are snake_case; table names match
the model names. See README.md for the full MySQL DDL walk-through.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    DECIMAL,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlmodel import Field, SQLModel


# ── Application enums (persisted as real MySQL ENUM columns) ──────────────────

class Occasion(str, Enum):
    CASUAL = "CASUAL"
    SMART_CASUAL = "SMART_CASUAL"
    WORK = "WORK"
    FORMAL = "FORMAL"


CATEGORY_NAMES = ["Topwear", "Bottomwear", "Footwear", "Outerwear", "Accessories"]


def _now() -> datetime:
    return datetime.utcnow()


# ── User ───────────────────────────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "User"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    name: Optional[str] = Field(default=None, sa_column=Column(String(120)))
    # PBKDF2-HMAC-SHA256 digest as `pbkdf2_sha256$<iterations>$<salt>$<hexdigest>`.
    # NULL only for rows created before login existed; seed() backfills them.
    password_hash: Optional[str] = Field(
        default=None, sa_column=Column(String(255))
    )
    created_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )


# ── Category ───────────────────────────────────────────────────────────────────

class Category(SQLModel, table=True):
    __tablename__ = "Category"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    slug: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    # Wears tolerated before the laundry trigger flips an item to LAUNDRY.
    wear_limit: int = Field(default=3, sa_column=Column(Integer, nullable=False))
    sort_order: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    created_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )


# ── Brand (who makes the item) ────────────────────────────────────────────────

class Brand(SQLModel, table=True):
    __tablename__ = "Brand"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(80), nullable=False, unique=True))
    created_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )


# ── Season (when the item is wearable) ────────────────────────────────────────

class Season(SQLModel, table=True):
    __tablename__ = "Season"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(30), nullable=False, unique=True))
    slug: str = Field(sa_column=Column(String(30), nullable=False, unique=True))
    sort_order: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    created_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )


# ── ClothingItem (the core inventory row) ──────────────────────────────────────

class ClothingItem(SQLModel, table=True):
    """One piece of clothing.

    3NF note: this table stores only *atomic facts* about the item. The wear
    counters and the CLEAN/LAUNDRY status used to live here as well — that
    was a transitive dependency (status depends on the wear count, which
    depends on WearLog) — so they are now derived at read time:

      wear_count          = COUNT(WearLog rows for the item)
      wear_count_since_wash = rows dated on/after `last_washed_at`
      status              = LAUNDRY if `sent_to_laundry_at` is set by hand,
                            or if wears-since-wash >= Category.wear_limit
    """

    __tablename__ = "ClothingItem"
    __table_args__ = (
        Index("ix_clothingitem_user_category", "user_id", "category_id"),
        Index("ix_clothingitem_user_brand", "user_id", "brand_id"),
        Index("ix_clothingitem_user_season", "user_id", "season_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False
        )
    )
    category_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("Category.id", ondelete="RESTRICT"), nullable=False
        )
    )
    brand: Optional[str] = Field(
        default=None, sa_column=Column(String(80))
    )
    season: Optional[str] = Field(
        default=None, sa_column=Column(String(30))
    )
    brand_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("Brand.id", ondelete="SET NULL")),
    )
    season_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("Season.id", ondelete="SET NULL")),
    )
    name: str = Field(sa_column=Column(String(120), nullable=False))
    # Primary colour name, used by the colour-harmony matrix.
    color: str = Field(sa_column=Column(String(30), nullable=False))
    # 1 = laid back, 5 = formal.
    formality_score: int = Field(default=3, sa_column=Column(Integer, nullable=False))
    purchase_price: Decimal = Field(
        default=Decimal("0.00"), sa_column=Column(DECIMAL(10, 2), nullable=False)
    )
    # Atomic wash facts (what the derived status is computed from).
    last_washed_at: Optional[date] = Field(
        default=None, sa_column=Column(Date)
    )
    sent_to_laundry_at: Optional[date] = Field(
        default=None, sa_column=Column(Date)
    )
    # Denormalized for performance (maintained by app logic)
    wear_count: int = Field(default=0, sa_column=Column(Integer, nullable=False, default=0))
    wear_count_since_wash: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, default=0)
    )
    status: str = Field(default="CLEAN", sa_column=Column(String(20), nullable=False, default="CLEAN"))
    image_url: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    created_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )


# ── Outfit ─────────────────────────────────────────────────────────────────────

class Outfit(SQLModel, table=True):
    __tablename__ = "Outfit"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False
        )
    )
    name: str = Field(sa_column=Column(String(120), nullable=False))
    occasion: Occasion = Field(
        default=Occasion.SMART_CASUAL,
        sa_column=Column(SAEnum(Occasion), nullable=False),
    )
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )


class OutfitItem(SQLModel, table=True):
    __tablename__ = "OutfitItem"
    __table_args__ = (UniqueConstraint("outfit_id", "item_id", name="uq_outfit_item"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    outfit_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("Outfit.id", ondelete="CASCADE"), nullable=False
        )
    )
    item_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("ClothingItem.id", ondelete="CASCADE"), nullable=False
        )
    )
    # 1 = base, 2 = layering, 3 = footwear.
    position: int = Field(default=1, sa_column=Column(Integer, nullable=False))


# ── Wear analytics ─────────────────────────────────────────────────────────────

class WearLog(SQLModel, table=True):
    __tablename__ = "WearLog"
    __table_args__ = (
        Index("ix_wearlog_item_date", "item_id", "date_worn"),
        Index("ix_wearlog_user_date", "user_id", "date_worn"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False
        )
    )
    item_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("ClothingItem.id", ondelete="CASCADE"), nullable=False
        )
    )
    outfit_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("Outfit.id", ondelete="SET NULL")),
    )
    date_worn: date = Field(sa_column=Column(Date, nullable=False))
    weather_temp: Optional[int] = Field(default=None, sa_column=Column(Integer))
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(
        default_factory=_now, sa_column=Column(DateTime, nullable=False)
    )


# ── Colour-wheel compatibility matrix ──────────────────────────────────────────

class ColorCompatibility(SQLModel, table=True):
    __tablename__ = "ColorCompatibility"
    __table_args__ = (
        UniqueConstraint("color1", "color2", name="uq_color_pair"),
        Index("ix_colorcompat_color2", "color2"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    color1: str = Field(sa_column=Column(String(30), nullable=False))
    color2: str = Field(sa_column=Column(String(30), nullable=False))
    # Normalised colour pairs (color1 <= color2) with a 0-10 harmony score.
    score: int = Field(default=5, sa_column=Column(Integer, nullable=False))
