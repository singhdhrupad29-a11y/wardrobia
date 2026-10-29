"""Reflex state layer: form handling, inventory CRUD, laundry toggling, image
uploads, the SQL-driven outfit recommender and wear history.

All database work goes through SQLModel against MySQL. State is kept
deliberately JSON-serialisable, so the
generated outfits are stored as plain dicts (not ORM instances) and render
instantly on the client after the "Generate outfits" click.
"""

import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import TypedDict

import reflex as rx
from sqlalchemy import text
from sqlmodel import Session, select

from digital_wardrobe.auth import hash_password, verify_password
from digital_wardrobe.color_matrix import COLOR_HEX
from digital_wardrobe.cpw import cost_per_wear
from digital_wardrobe.database import get_engine
from digital_wardrobe.models import (
    Brand,
    Category,
    ClothingItem,
    Occasion,
    Outfit,
    OutfitItem,
    Season,
    User,
    WearLog,
)
from digital_wardrobe.views import fetch_cost_per_wear

# UI occasion labels -> persisted Occasion enum (Gym / Night Out are studio
# presets that map to the nearest existing band).
OCCASION_ENUM_MAP = {
    "Casual": Occasion.CASUAL,
    "Smart Casual": Occasion.SMART_CASUAL,
    "Work": Occasion.WORK,
    "Formal": Occasion.FORMAL,
    "Gym": Occasion.CASUAL,
    "Night Out": Occasion.SMART_CASUAL,
}
from digital_wardrobe.recommender import (
    OCCASION_OPTIONS,
    SEASON_OPTIONS,
    recommend_outfits,
)

CATEGORY_OPTIONS = ["Topwear", "Bottomwear", "Footwear", "Outerwear", "Accessories"]
COLOR_OPTIONS = list(COLOR_HEX.keys())
FORMALITY_OPTIONS = ["1", "2", "3", "4", "5"]
STATUS_OPTIONS = ["Clean", "In Laundry"]
ITEM_SEASON_OPTIONS = ["Summer", "Winter", "Rainy", "Spring"]

INR = "\u20b9"

# ── form validation ───────────────────────────────────────────────────────────
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
MIN_PASSWORD_LEN = 6
MAX_PASSWORD_LEN = 128
MAX_NAME_LEN = 120


def validate_email(raw: str) -> tuple[str, str]:
    """Return (clean_email, error_message). error_message is '' when valid."""
    email = raw.strip().lower()
    if not email:
        return "", "Enter your email address."
    if email.count("@") != 1 or not EMAIL_RE.match(email):
        return "", "Enter a valid email address (e.g. you@example.com)."
    return email, ""


def validate_password(raw: str) -> tuple[str, str]:
    """Return (password, error_message). error_message is '' when valid."""
    if not raw:
        return "", "Enter your password."
    if len(raw) < MIN_PASSWORD_LEN:
        return "", f"Password must be at least {MIN_PASSWORD_LEN} characters."
    if len(raw) > MAX_PASSWORD_LEN:
        return "", f"Password must be at most {MAX_PASSWORD_LEN} characters."
    if not re.search(r"[A-Za-z]", raw) or not re.search(r"[0-9]", raw):
        return "", "Password needs at least one letter and one number."
    return raw, ""


def validate_name(raw: str) -> str:
    return raw.strip()[:MAX_NAME_LEN]


# Uploaded photos are stored in Reflex's upload dir (project_root/uploaded_files)
# and served by the backend at /_upload/<file>. Only the bare file name is
# persisted in `image_url`; the UI expands it with `image_src()`.
ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
NEGLECT_DAYS = 60


# ── typed state shapes (Reflex needs concrete dict types for rx.foreach) ─────

class StatsDict(TypedDict):
    total: int
    clean: int
    laundry: int
    clean_ratio: int
    clean_ratio_str: str
    avg_cpw: float
    avg_cpw_str: str
    total_wears: int
    wardrobe_value: float
    value_str: str
    worn_30: int
    saved_outfits: int
    brand_count: int


class ItemDict(TypedDict):
    id: int
    name: str
    category: str
    brand: str
    season: str
    brand_season: str
    color: str
    color_hex: str
    formality: int
    price: float
    price_str: str
    wear_count: int
    wear_count_since_wash: int
    wear_limit: int
    wear_pct: int
    cpw: float
    cpw_str: str
    status: str
    image_url: str | None
    created: str


class PieceDict(TypedDict):
    id: int
    name: str
    color: str
    color_hex: str
    image_url: str | None
    position: int


class OutfitDict(TypedDict):
    top: PieceDict
    bottom: PieceDict
    foot: PieceDict
    total_score: int
    harmony_pct: int


class WearLogDict(TypedDict):
    date: str
    date_display: str
    notes: str
    items: list[str]
    items_text: str


class NeglectedDict(TypedDict):
    id: int
    name: str
    category: str
    color: str
    color_hex: str
    wear_count: int
    last_worn: str


class ViewRowDict(TypedDict):
    """One row read back from the V_ItemCostPerWear SQL view."""

    id: int
    name: str
    category: str
    price_str: str
    wear_count: int
    cpw_str: str


def _format_date(d: date) -> str:
    return d.strftime("%d %b %Y").lstrip("0")


def image_src(url: str | None | rx.Var) -> str | rx.Var:
    """Expand a stored image reference into a servable URL.

    New uploads persist only the bare file name inside the backend upload dir;
    ``rx.get_upload_url()`` turns that into ``/_upload/<file>``. Legacy absolute
    paths (old ``/upload/...`` values) pass through untouched. Works with both
    plain strings and state Vars.
    """
    if isinstance(url, rx.Var):
        return rx.cond(
            url.startswith("/") | url.contains("://"),
            url,
            rx.get_upload_url(url),
        )
    if not url:
        return ""
    if url.startswith("/") or "://" in url:
        return url
    return rx.get_upload_url(url)


# ── derived wear metrics (true-3NF schema: counters live only in WearLog) ────
_ZERO_COUNTS = {"total": 0, "since": 0}

_DERIVED_COUNTS_SQL = """
SELECT w.item_id AS item_id,
       COUNT(*) AS total,
       SUM(CASE WHEN w.date_worn >= COALESCE(ci.last_washed_at, '1000-01-01')
                THEN 1 ELSE 0 END) AS since
FROM WearLog w
JOIN ClothingItem ci ON ci.id = w.item_id
WHERE w.item_id IN ({ids})
GROUP BY w.item_id
"""


def _derived_counts(session, item_ids: list[int]) -> dict[int, dict]:
    """wear_count / wears-since-wash per item, computed from WearLog.

    The schema stores no counters (3NF), so every read derives them here:
    `total` = all WearLog rows, `since` = rows dated on/after the last wash.
    """
    ids = [int(i) for i in item_ids if i is not None]
    if not ids:
        return {}
    rows = session.execute(
        text(_DERIVED_COUNTS_SQL.format(ids=", ".join(str(i) for i in ids)))
    ).mappings().all()
    return {
        int(r["item_id"]): {"total": int(r["total"]), "since": int(r["since"] or 0)}
        for r in rows
    }


def _item_to_dict(
    item: ClothingItem,
    category_name: str,
    wear_limit: int,
    brand_name: str = "",
    season_name: str = "",
    counts: dict | None = None,
) -> dict:
    price = float(item.purchase_price)
    total = int(getattr(item, "wear_count", 0))
    since = int(getattr(item, "wear_count_since_wash", 0))
    status = str(getattr(item, "status", "CLEAN")).upper()
    cpw = cost_per_wear(price, total)
    return {
        "id": item.id,
        "name": item.name,
        "category": category_name,
        "brand": brand_name,
        "season": season_name,
        "brand_season": " - ".join(p for p in (brand_name, season_name) if p),
        "color": item.color,
        "color_hex": COLOR_HEX.get(item.color, "#C9C4BA"),
        "formality": item.formality_score,
        "price": round(price, 2),
        "price_str": f"{INR}{round(price, 2):.2f}",
        "wear_count": total,
        "wear_count_since_wash": since,
        "wear_limit": wear_limit,
        "wear_pct": min(100, round(since / wear_limit * 100)) if wear_limit else 0,
        "cpw": cpw,
        "cpw_str": f"{INR}{cpw:.2f}",
        "status": status,
        "image_url": item.image_url,
        "created": _format_date(item.created_at.date()),
    }


class AuthState(rx.State):
    """Sign-in / sign-up form state.

    Lives in its own class so the login card only touches these vars;
    `WardrobeState` inherits from it, so the whole app shares one session.
    """

    auth_email: str = ""
    auth_password: str = ""
    auth_name: str = ""
    auth_mode: str = "signin"  # signin | signup
    auth_error: str = ""
    # Per-field errors, refreshed on every keystroke so a wrong format is
    # flagged immediately (not only after pressing the button).
    auth_email_error: str = ""
    auth_password_error: str = ""
    auth_name_error: str = ""

    is_logged_in: bool = False
    user_id: int = 0
    display_name: str = ""

    def set_auth_email(self, value: str):
        self.auth_email = value
        self.auth_error = ""
        self.auth_email_error = validate_email(value)[1] if value.strip() else ""

    def set_auth_password(self, value: str):
        self.auth_password = value
        self.auth_error = ""
        self.auth_password_error = validate_password(value)[1] if value else ""

    def set_auth_name(self, value: str):
        self.auth_name = value
        self.auth_error = ""
        self.auth_name_error = (
            f"Name must be at most {MAX_NAME_LEN} characters."
            if len(value.strip()) > MAX_NAME_LEN
            else ""
        )

    def set_auth_mode(self, value: str):
        self.auth_mode = value
        self.auth_error = ""
        self.auth_email_error = ""
        self.auth_password_error = ""
        self.auth_name_error = ""

    def _start_session(self, user: User) -> None:
        """Mark the given user as signed in (called by WardrobeState.login)."""
        self.user_id = user.id
        self.display_name = (user.name or user.email.split("@")[0]).strip()
        self.is_logged_in = True
        self.auth_password = ""


class WardrobeState(AuthState):
    """Holds the whole dashboard UI state."""

    # ── Layout ─────────────────────────────────────────────────────────────
    active_view: str = "overview"  # overview | wardrobe | outfits | analytics

    # ── Inventory ───────────────────────────────────────────────────────────
    items: list[ItemDict] = []
    stats: StatsDict = {
        "total": 0,
        "clean": 0,
        "laundry": 0,
        "clean_ratio": 0,
        "clean_ratio_str": "0%",
        "avg_cpw": 0.0,
        "avg_cpw_str": f"{INR}0.00",
        "total_wears": 0,
        "wardrobe_value": 0.0,
        "value_str": f"{INR}0.00",
        "worn_30": 0,
        "saved_outfits": 0,
        "brand_count": 0,
    }

    # ── Outfit generator ────────────────────────────────────────────────────
    generated_outfits: list[OutfitDict] = []
    season: str = "All Seasons"
    occasion: str = "Smart Casual"
    weather_notes: str = ""
    generator_note: str = ""
    is_generating: bool = False

    # ── Wardrobe checker filters ────────────────────────────────────────────
    search_query: str = ""
    category_filter: str = "All"
    season_filter: str = "All"
    laundry_filter: str = "all"  # "all" | "clean" | "laundry"

    # ── History ─────────────────────────────────────────────────────────────
    wear_logs: list[WearLogDict] = []
    neglected_items: list[NeglectedDict] = []

    # ── Cost-per-wear, read straight from the V_ItemCostPerWear SQL view ────
    view_rows: list[ViewRowDict] = []

    # ── Add-item form ───────────────────────────────────────────────────────
    show_form: bool = False
    form_name: str = ""
    form_category: str = "Topwear"
    form_brand: str = ""
    form_season: str = "Spring"
    form_color: str = "Navy"
    formality_score: str = "3"
    purchase_price: str = "0"
    form_status: str = "Clean"
    form_image_url: str = ""
    uploaded_filename: str = ""

    # ── Item detail / delete ────────────────────────────────────────────────
    detail_item: ItemDict | None = None
    confirm_delete: bool = False

    # ── Feedback ────────────────────────────────────────────────────────────
    error: str = ""
    message: str = ""

    def clear_feedback(self) -> None:
        """Dismiss the current success/error notification bar."""
        self.message = ""
        self.error = ""

    # ── helpers ─────────────────────────────────────────────────────────────
    def _session(self) -> Session:
        return Session(get_engine())

    def _user_id(self, session: Session) -> int:
        """The signed-in user's id — every query in this state scopes to it."""
        if not self.is_logged_in or not self.user_id:
            raise RuntimeError("Not signed in.")
        return self.user_id

    # ── computed: filtered inventory for the Wardrobe Checker ───────────────
    @rx.var(cache=True)
    def filtered_items(self) -> list[ItemDict]:
        query = self.search_query.strip().lower()
        items: list[ItemDict] = []
        for item in self.items:
            if self.category_filter != "All" and item["category"] != self.category_filter:
                continue
            if self.season_filter != "All" and item["season"] != self.season_filter:
                continue
            if self.laundry_filter == "clean" and item["status"] != "CLEAN":
                continue
            if self.laundry_filter == "laundry" and item["status"] != "LAUNDRY":
                continue
            if query and query not in item["name"].lower() and query not in item["color"].lower():
                continue
            items.append(item)
        return items

    @rx.var(cache=True)
    def laundry_items(self) -> list[ItemDict]:
        return [item for item in self.items if item["status"] == "LAUNDRY"]

    @rx.var(cache=True)
    def season_breakdown(self) -> list[dict]:
        counts: dict[str, int] = {}
        for item in self.items:
            season = item["season"] or "Unspecified"
            counts[season] = counts.get(season, 0) + 1
        total = sum(counts.values()) or 1
        return [
            {"season": season, "count": count, "pct": round(count / total * 100)}
            for season, count in sorted(counts.items(), key=lambda kv: -kv[1])
        ]

    # ── explicit setters (Reflex no longer auto-generates `set_*`) ──────────
    def set_active_view(self, value: str):
        self.active_view = value

    def set_season(self, value: str):
        self.season = value

    def set_occasion(self, value: str):
        self.occasion = value

    def set_weather_notes(self, value: str):
        self.weather_notes = value

    def set_search_query(self, value: str):
        self.search_query = value

    def set_category_filter(self, value: str):
        self.category_filter = value

    def set_season_filter(self, value: str):
        self.season_filter = value

    def set_laundry_filter(self, value: str):
        self.laundry_filter = value

    def set_show_form(self, value: bool):
        self.show_form = value

    def set_form_name(self, value: str):
        self.form_name = value

    def set_form_category(self, value: str):
        self.form_category = value

    def set_form_brand(self, value: str):
        self.form_brand = value

    def set_form_season(self, value: str):
        self.form_season = value

    def set_form_color(self, value: str):
        self.form_color = value

    def set_formality_score(self, value: str):
        self.formality_score = value

    def set_purchase_price(self, value: str):
        self.purchase_price = value

    def set_form_status(self, value: str):
        self.form_status = value

    # ── startup + reload ─────────────────────────────────────────────────────
    def load_all(self):
        if not self.is_logged_in:
            return
        self.load_wardrobe()
        self.load_history()
        self.load_cost_view()

    # ── Auth (login / sign-up / logout) ──────────────────────────────────────
    def login(self):
        """Verify the email + password form against the User table."""
        email, email_err = validate_email(self.auth_email)
        password, password_err = validate_password(self.auth_password)
        self.auth_email_error = email_err
        self.auth_password_error = password_err
        if email_err:
            self.auth_error = email_err
            return
        if password_err:
            self.auth_error = password_err
            return
        try:
            with self._session() as session:
                user = session.exec(select(User).where(User.email == email)).first()
                if user is None or not verify_password(password, user.password_hash):
                    self.auth_error = "Incorrect email or password."
                    return
                self._start_session(user)
        except Exception as exc:  # noqa: BLE001
            self.auth_error = f"Database error: {exc}"
            return
        self.auth_error = ""
        self.auth_email_error = ""
        self.auth_password_error = ""
        self.auth_name_error = ""
        self.error = ""
        self.message = ""
        self.generated_outfits = []
        self.active_view = "overview"
        self.load_all()

    def register(self):
        """Create a new User row from the sign-up form and sign straight in."""
        email, email_err = validate_email(self.auth_email)
        password, password_err = validate_password(self.auth_password)
        self.auth_email_error = email_err
        self.auth_password_error = password_err
        if email_err:
            self.auth_error = email_err
            return
        if password_err:
            self.auth_error = password_err
            return
        try:
            with self._session() as session:
                existing = session.exec(
                    select(User).where(User.email == email)
                ).first()
                if existing is not None:
                    self.auth_error = "An account with that email already exists."
                    return
                name = validate_name(self.auth_name) or email.split("@")[0]
                user = User(
                    email=email,
                    name=name,
                    password_hash=hash_password(password),
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                self._start_session(user)
        except Exception as exc:  # noqa: BLE001
            self.auth_error = f"Database error: {exc}"
            return
        self.auth_error = ""
        self.auth_email_error = ""
        self.auth_password_error = ""
        self.auth_name_error = ""
        self.error = ""
        self.message = f"Welcome, {self.display_name} — your wardrobe is empty. Add your first piece."
        self.active_view = "overview"
        self.load_all()

    def logout(self):
        """End the session and wipe every user-specific value from state."""
        self.is_logged_in = False
        self.user_id = 0
        self.display_name = ""
        self.auth_email = ""
        self.auth_password = ""
        self.auth_name = ""
        self.auth_mode = "signin"
        self.auth_error = ""
        self.auth_email_error = ""
        self.auth_password_error = ""
        self.auth_name_error = ""
        self.active_view = "overview"
        self.items = []
        self.stats = {
            "total": 0,
            "clean": 0,
            "laundry": 0,
            "clean_ratio": 0,
            "clean_ratio_str": "0%",
            "avg_cpw": 0.0,
            "avg_cpw_str": f"{INR}0.00",
            "total_wears": 0,
            "wardrobe_value": 0.0,
            "value_str": f"{INR}0.00",
            "worn_30": 0,
            "saved_outfits": 0,
            "brand_count": 0,
        }
        self.generated_outfits = []
        self.wear_logs = []
        self.neglected_items = []
        self.view_rows = []
        self.detail_item = None
        self.show_form = False
        self.error = ""
        self.message = ""

    # ── Wardrobe CRUD ────────────────────────────────────────────────────────
    def load_wardrobe(self):
        try:
            with self._session() as session:
                uid = self._user_id(session)
                rows = session.exec(
                    select(ClothingItem, Category)
                    .join(Category, Category.id == ClothingItem.category_id)
                    .where(ClothingItem.user_id == uid)
                    .order_by(ClothingItem.created_at.desc())
                ).all()
                items = [
                    _item_to_dict(
                        item,
                        cat.name,
                        cat.wear_limit,
                        item.brand or "",
                        item.season or "",
                    )
                    for item, cat in rows
                ]
                self.items = items
                clean = sum(1 for i in items if i["status"] == "CLEAN")
                cpws = [i["cpw"] for i in items if i["price"] > 0]
                avg_cpw = round(sum(cpws) / len(cpws), 2) if cpws else 0.0
                clean_ratio = round((clean / len(items)) * 100) if items else 0
                total_wears = sum(i["wear_count"] for i in items)
                wardrobe_value = sum(i["price"] for i in items)
                brand_count = len({i["brand"] for i in items if i["brand"]})
                self.stats = {
                    "total": len(items),
                    "clean": clean,
                    "laundry": len(items) - clean,
                    "clean_ratio": clean_ratio,
                    "clean_ratio_str": f"{clean_ratio}%",
                    "avg_cpw": avg_cpw,
                    "avg_cpw_str": f"{INR}{avg_cpw:.2f}",
                    "total_wears": total_wears,
                    "wardrobe_value": wardrobe_value,
                    "value_str": f"{INR}{wardrobe_value:,.2f}",
                    "worn_30": self.stats.get("worn_30", 0),
                    "saved_outfits": self.stats.get("saved_outfits", 0),
                    "brand_count": brand_count,
                }
        except Exception as exc:  # noqa: BLE001 — surface DB problems in the UI
            self.items = []
            self.stats = {
                "total": 0,
                "clean": 0,
                "laundry": 0,
                "clean_ratio": 0,
                "clean_ratio_str": "0%",
                "avg_cpw": 0.0,
                "avg_cpw_str": f"{INR}0.00",
                "total_wears": 0,
                "wardrobe_value": 0.0,
                "value_str": f"{INR}0.00",
                "worn_30": 0,
                "saved_outfits": 0,
                "brand_count": 0,
            }
            self.error = f"Database error: {exc}"

    def open_form(self):
        self.show_form = True
        self.active_view = "wardrobe"
        self.error = ""

    def close_form(self):
        self.show_form = False

    def clear_form_image(self):
        self.form_image_url = ""
        self.uploaded_filename = ""

    def open_detail(self, item_id: int):
        """Show the item profile dialog for one wardrobe item."""
        for item in self.items:
            if item["id"] == item_id:
                self.detail_item = item
                self.confirm_delete = False
                self.error = ""
                self.message = ""
                return
        self.error = "Item not found."

    def close_detail(self):
        self.detail_item = None
        self.confirm_delete = False

    def set_detail_open(self, value: bool):
        if not value:
            self.close_detail()

    def set_confirm_delete(self, value: bool):
        self.confirm_delete = value

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Save dropped photos to Reflex's upload dir and stage the file name.

        Files land in ``rx.get_upload_dir()`` (``uploaded_files/``), which the
        backend serves at ``/_upload/<file>``. Only the bare file name is kept
        in state — the UI builds the servable URL with ``image_src()``.
        """
        if not files:
            return
        for file in files:
            raw_name = file.filename or "photo.png"
            safe_name = Path(raw_name).name
            suffix = Path(safe_name).suffix.lower()
            if suffix not in ALLOWED_IMAGE_EXT:
                self.error = "Please choose a PNG, JPG, JPEG, WEBP or GIF image."
                continue
            stem = re.sub(r"[^A-Za-z0-9_ -]", "_", Path(safe_name).stem).strip().replace(" ", "_")
            stem = stem or "item"
            stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"{stem}_{stamp}{suffix}"
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            data = await file.read()
            (upload_dir / filename).write_bytes(data)
            self.form_image_url = filename
            self.uploaded_filename = raw_name
            self.error = ""

    def add_item(self):
        name = self.form_name.strip()
        if not name:
            self.error = "Please enter an item name."
            return
        try:
            price = max(0.0, float(self.purchase_price or "0"))
        except ValueError:
            self.error = "Purchase price must be a number."
            return
        try:
            formality = int(self.formality_score or "3")
        except ValueError:
            self.error = "Formality score must be a number."
            return
        if not (1 <= formality <= 5):
            self.error = "Formality score must be between 1 and 5."
            return

        try:
            with self._session() as session:
                uid = self._user_id(session)
                category = session.exec(
                    select(Category).where(Category.name == self.form_category)
                ).first()
                if category is None:
                    self.error = f"Unknown category: {self.form_category}"
                    return

                brand_name = self.form_brand.strip() or None
                season_name = self.form_season.strip() or None

                item = ClothingItem(
                    user_id=uid,
                    category_id=category.id,
                    brand=brand_name,
                    season=season_name,
                    name=name,
                    color=self.form_color,
                    formality_score=formality,
                    purchase_price=price,
                    wear_count=0,
                    wear_count_since_wash=0,
                    status="CLEAN" if self.form_status == "Clean" else "LAUNDRY",
                    last_washed_at=(
                        date.today() if self.form_status == "Clean" else None
                    ),
                    sent_to_laundry_at=(
                        None if self.form_status == "Clean" else date.today()
                    ),
                    image_url=self.form_image_url or None,
                )
                session.add(item)
                session.commit()
        except Exception as exc:  # noqa: BLE001
            self.error = f"Database error: {exc}"
            return

        self.message = f"Added “{name}” to your wardrobe."
        self.error = ""
        self.form_name = ""
        self.form_brand = ""
        self.purchase_price = "0"
        self.clear_form_image()
        self.close_form()
        self.load_wardrobe()
        self.load_history()

    def toggle_status(self, item_id: int):
        """Wash a dirty item (resets wears-since-wash to 0 and status to CLEAN)
        or flag a clean one as sent to the laundry (status to LAUNDRY).
        Maintains denormalized status and counter columns directly on ClothingItem."""
        with self._session() as session:
            item = session.get(ClothingItem, item_id)
            if item is None:
                self.error = "Item not found."
                return
            category = session.get(Category, item.category_id)
            limit = category.wear_limit if category else 3
            since = getattr(item, "wear_count_since_wash", 0)
            dirty = (
                item.status == "LAUNDRY"
                or item.sent_to_laundry_at is not None
                or since >= limit
            )
            if dirty:
                item.sent_to_laundry_at = None
                item.last_washed_at = date.today()
                item.wear_count_since_wash = 0
                item.status = "CLEAN"
            else:
                item.sent_to_laundry_at = date.today()
                item.status = "LAUNDRY"
            session.add(item)
            session.commit()
        self.error = ""
        self.message = ""
        self.load_wardrobe()

    def delete_item(self, item_id: int):
        """Permanently remove an item (its OutfitItem/WearLog rows cascade)."""
        try:
            with self._session() as session:
                uid = self._user_id(session)
                item = session.get(ClothingItem, item_id)
                if item is None or item.user_id != uid:
                    self.error = "Item not found."
                    return
                name = item.name
                image_ref = item.image_url
                session.delete(item)
                session.commit()
        except Exception as exc:  # noqa: BLE001
            self.error = f"Database error: {exc}"
            return
        if image_ref and not image_ref.startswith("/") and "/" not in image_ref:
            try:
                (rx.get_upload_dir() / image_ref).unlink(missing_ok=True)
            except Exception:  # noqa: BLE001 — orphaned file is harmless
                pass
        self.message = f"Deleted “{name}” from your wardrobe."
        self.error = ""
        self.close_detail()
        self.load_wardrobe()
        self.load_history()

    # ── Outfit recommender ─────────────────────────────────────────────────
    def generate_outfits(self):
        self.is_generating = True
        self.error = ""
        self.generator_note = ""
        try:
            with self._session() as session:
                uid = self._user_id(session)
                rows, note = recommend_outfits(session, uid, self.occasion, self.season, limit=6)
                self.generated_outfits = [self._outfit_to_dict(r) for r in rows]
                self.generator_note = note
                self.message = "" if self.generated_outfits else (
                    "No matching outfits — add more CLEAN items, or relax the filters."
                )
        except Exception as exc:  # noqa: BLE001
            self.error = f"Database error: {exc}"
            self.generated_outfits = []
        finally:
            self.is_generating = False

    @staticmethod
    def _outfit_to_dict(row: dict) -> dict:
        return {
            "top": {
                "id": row["top_id"],
                "name": row["top_name"],
                "color": row["top_color"],
                "color_hex": COLOR_HEX.get(row["top_color"], "#C9C4BA"),
                "image_url": row["top_image"],
                "position": 1,
            },
            "bottom": {
                "id": row["bottom_id"],
                "name": row["bottom_name"],
                "color": row["bottom_color"],
                "color_hex": COLOR_HEX.get(row["bottom_color"], "#C9C4BA"),
                "image_url": row["bottom_image"],
                "position": 2,
            },
            "foot": {
                "id": row["foot_id"],
                "name": row["foot_name"],
                "color": row["foot_color"],
                "color_hex": COLOR_HEX.get(row["foot_color"], "#C9C4BA"),
                "image_url": row["foot_image"],
                "position": 3,
            },
            "total_score": row["total_score"],
            "harmony_pct": round((row["total_score"] / 30) * 100),
        }

    # ── Log wear today ──────────────────────────────────────────────────────
    def log_wear(self, outfit_index: int):
        """Log a generated outfit for today: +1 wear per piece, WearLog rows,
        and an auto-laundry flip when an item hits its category wear limit."""
        if not (0 <= outfit_index < len(self.generated_outfits)):
            return
        outfit = self.generated_outfits[outfit_index]
        today = date.today()
        sent_to_laundry = []
        try:
            with self._session() as session:
                uid = self._user_id(session)
                db_outfit = Outfit(
                    user_id=uid,
                    name=f"{self.occasion} · {today.strftime('%d %b %Y')}",
                    occasion=OCCASION_ENUM_MAP.get(self.occasion, Occasion.SMART_CASUAL),
                    notes=self.weather_notes or None,
                )
                session.add(db_outfit)
                session.commit()
                session.refresh(db_outfit)

                for piece in (outfit["top"], outfit["bottom"], outfit["foot"]):
                    item = session.get(ClothingItem, piece["id"])
                    if item is None or item.user_id != uid:
                        continue
                    category = session.get(Category, item.category_id)
                    limit = category.wear_limit if category else 3
                    item.wear_count = (item.wear_count or 0) + 1
                    item.wear_count_since_wash = (item.wear_count_since_wash or 0) + 1
                    if item.wear_count_since_wash >= limit:
                        item.status = "LAUNDRY"
                        sent_to_laundry.append(item.name)
                    session.add(item)
                    session.add(
                        OutfitItem(outfit_id=db_outfit.id, item_id=item.id, position=piece["position"])
                    )
                    session.add(
                        WearLog(
                            user_id=uid,
                            item_id=item.id,
                            outfit_id=db_outfit.id,
                            date_worn=today,
                            notes=self.weather_notes or None,
                        )
                    )
                session.commit()
        except Exception as exc:  # noqa: BLE001
            self.error = f"Database error: {exc}"
            return

        self.message = "Logged today's outfit."
        if sent_to_laundry:
            names = ", ".join(sent_to_laundry[:3])
            self.message += f" {names} hit the wear limit and went to the laundry."
        self.weather_notes = ""
        self.load_wardrobe()
        self.load_history()

    # ── History ─────────────────────────────────────────────────────────────
    def load_history(self):
        try:
            with self._session() as session:
                uid = self._user_id(session)

                # Wear logs, grouped by (outfit, date) into readable entries.
                rows = session.exec(
                    select(WearLog, ClothingItem.name, Category.name)
                    .join(ClothingItem, ClothingItem.id == WearLog.item_id)
                    .join(Category, Category.id == ClothingItem.category_id)
                    .where(WearLog.user_id == uid)
                    .order_by(WearLog.date_worn.desc(), WearLog.created_at.desc())
                ).all()
                groups: dict[tuple, dict] = {}
                for log, item_name, cat_name in rows:
                    key = (log.outfit_id, log.date_worn)
                    group = groups.setdefault(
                        key,
                        {
                            "date": log.date_worn.isoformat(),
                            "date_display": _format_date(log.date_worn),
                            "notes": log.notes or "",
                            "items": [],
                        },
                    )
                    group["items"].append(f"{item_name} \u00b7 {cat_name}")
                for group in groups.values():
                    group["items_text"] = ", ".join(group["items"])
                self.wear_logs = sorted(
                    groups.values(), key=lambda g: g["date"], reverse=True
                )[:20]

                # Overview metrics: outfits saved so far + days worn in the
                # last month (from the same WearLog rows above).
                outfit_ids = session.exec(
                    select(Outfit.id).where(Outfit.user_id == uid)
                ).all()
                worn_30 = len(
                    {
                        log.date_worn
                        for log, _item, _cat in rows
                        if log.date_worn >= date.today() - timedelta(days=30)
                    }
                )
                if "worn_30" in self.stats or "saved_outfits" in self.stats:
                    self.stats["worn_30"] = worn_30
                    self.stats["saved_outfits"] = len(outfit_ids)

                # Neglected items: never worn, or not worn in the last N days.
                cutoff = date.today() - timedelta(days=NEGLECT_DAYS)
                all_items = session.exec(
                    select(ClothingItem, Category)
                    .join(Category, Category.id == ClothingItem.category_id)
                    .where(ClothingItem.user_id == uid)
                ).all()
                last_worn: dict[int, date] = {}
                for log in session.exec(select(WearLog).where(WearLog.user_id == uid)).all():
                    last_worn[log.item_id] = max(last_worn.get(log.item_id, date.min), log.date_worn)
                neglected = []
                for item, cat in all_items:
                    last = last_worn.get(item.id)
                    total = item.wear_count or 0
                    if total > 0 and last is not None and last >= cutoff:
                        continue
                    neglected.append(
                        {
                            "id": item.id,
                            "name": item.name,
                            "category": cat.name,
                            "color": item.color,
                            "color_hex": COLOR_HEX.get(item.color, "#C9C4BA"),
                            "wear_count": total,
                            "last_worn": "Never" if last is None else _format_date(last),
                        }
                    )
                neglected.sort(key=lambda n: (n["wear_count"], n["name"]))
                self.neglected_items = neglected
        except Exception as exc:  # noqa: BLE001
            self.wear_logs = []
            self.neglected_items = []
            self.error = f"Database error: {exc}"

    # ── V_ItemCostPerWear (SQL view) ────────────────────────────────────────
    def load_cost_view(self):
        """Read the cost-per-wear rows for the signed-in user from the view."""
        try:
            with self._session() as session:
                uid = self._user_id(session)
                rows = fetch_cost_per_wear(session, uid)
            self.view_rows = [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "category": row["category"],
                    "price_str": f"{INR}{row['purchase_price']:.2f}",
                    "wear_count": row["wear_count"],
                    "cpw_str": f"{INR}{row['cost_per_wear']:.2f}",
                }
                for row in rows
            ]
        except Exception as exc:  # noqa: BLE001
            self.view_rows = []
            self.error = f"Database error: {exc}"
