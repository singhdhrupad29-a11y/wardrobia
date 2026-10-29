"""MySQL engine + session management for the Digital Wardrobe (Python).

The app connects straight to MySQL/MariaDB/TiDB through SQLAlchemy + PyMySQL.
The `DATABASE_URL` environment variable is read from `.env` (see `.env.example`).
"""

import os
import ssl
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlmodel import Session, SQLModel

from digital_wardrobe.views import CREATE_COST_PER_WEAR_VIEW, DROP_COST_PER_WEAR_VIEW

# Load .env from the project root (works regardless of the working directory).
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")

MISSING_URL_MESSAGE = (
    "DATABASE_URL is not set. Copy `.env.example` to `.env` inside "
    "digital-wardrobe-python/ and set your MySQL connection string."
)


def _normalize_url(url: str) -> str:
    """Make sure the URL uses the PyMySQL driver."""
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+pymysql://", 1)
    return url


def _ssl_connect_args(url: str) -> dict:
    """Translate `?ssl=true` URL params into PyMySQL `ssl` connect kwargs."""
    params = parse_qs(urlparse(url).query)
    if params.get("ssl", ["false"])[0].lower() == "true":
        return {"ssl": {"check_hostname": False, "verify_mode": ssl.CERT_NONE}}
    return {}


def database_url() -> str:
    """Return the normalized MySQL connection URL."""
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(MISSING_URL_MESSAGE)
    return _normalize_url(url)


def database_name() -> str:
    """Return the database name embedded in the connection URL."""
    name = urlparse(database_url()).path.strip("/")
    return name or "wardrobe_python"


def get_engine():
    """Lazily build and return a shared SQLAlchemy engine."""
    if not hasattr(get_engine, "_engine"):
        url = database_url()
        # Strip the query string: `?ssl=true` / `sslaccept=...` are handled via
        # connect_args below, and Prisma-only params would break PyMySQL.
        get_engine._engine = create_engine(
            _url_without_query(url),
            connect_args=_ssl_connect_args(url),
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    return get_engine._engine


def init_db() -> None:
    """Create the MySQL database (if missing), then create every table."""
    url = database_url()
    server_url = _url_without_query(url).rsplit("/", 1)[0] + "/"
    server_engine = create_engine(server_url, connect_args=_ssl_connect_args(url))
    try:
        with server_engine.connect() as conn:
            conn.execute(
                text(
                    "CREATE DATABASE IF NOT EXISTS `%s` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    % database_name()
                )
            )
            conn.commit()
    finally:
        server_engine.dispose()

    SQLModel.metadata.create_all(get_engine())
    ensure_schema()


def ensure_schema() -> None:
    """Idempotently add columns/indexes that `create_all` skips on existing
    tables (create_all only creates missing tables, never alters existing
    ones). Brand/Season support landed after the first release, so the
    ClothingItem table already exists in most databases.

    Each statement runs on its own connection and its own ALTER, so a single
    unsupported syntax (e.g. combined ADD COLUMN + ADD CONSTRAINT on TiDB)
    never aborts the rest. `ADD COLUMN IF NOT EXISTS` needs MySQL 8.0.29+ /
    MariaDB 10.0+ / TiDB.
    """
    statements = [
        "ALTER TABLE ClothingItem ADD COLUMN IF NOT EXISTS brand VARCHAR(80) NULL",
        "ALTER TABLE ClothingItem ADD COLUMN IF NOT EXISTS season VARCHAR(30) NULL",
        "ALTER TABLE ClothingItem ADD COLUMN IF NOT EXISTS brand_id INT NULL",
        "ALTER TABLE ClothingItem ADD COLUMN IF NOT EXISTS season_id INT NULL",
        "ALTER TABLE ClothingItem ADD COLUMN IF NOT EXISTS wear_count INT NOT NULL DEFAULT 0",
        "ALTER TABLE ClothingItem ADD COLUMN IF NOT EXISTS wear_count_since_wash INT NOT NULL DEFAULT 0",
        "ALTER TABLE ClothingItem ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'CLEAN'",
        # Backfill denormalized brand and season from lookup tables if available
        "UPDATE ClothingItem ci JOIN Brand b ON ci.brand_id = b.id SET ci.brand = b.name WHERE ci.brand IS NULL AND ci.brand_id IS NOT NULL",
        "UPDATE ClothingItem ci JOIN Season s ON ci.season_id = s.id SET ci.season = s.name WHERE ci.season IS NULL AND ci.season_id IS NOT NULL",
        "ALTER TABLE ClothingItem ADD INDEX IF NOT EXISTS ix_clothingitem_user_brand (user_id, brand_id)",
        "ALTER TABLE ClothingItem ADD INDEX IF NOT EXISTS ix_clothingitem_user_season (user_id, season_id)",
        "ALTER TABLE ClothingItem ADD CONSTRAINT fk_clothingitem_brand "
        "FOREIGN KEY (brand_id) REFERENCES Brand (id) ON DELETE SET NULL",
        "ALTER TABLE ClothingItem ADD CONSTRAINT fk_clothingitem_season "
        "FOREIGN KEY (season_id) REFERENCES Season (id) ON DELETE SET NULL",
        # Login: password hashes live on the User table.
        "ALTER TABLE User ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL",
        # The cost-per-wear view, re-created from views.py so the DDL lives in
        # exactly one place.
        DROP_COST_PER_WEAR_VIEW,
        CREATE_COST_PER_WEAR_VIEW,
    ]
    with Session(get_engine()) as session:
        for statement in statements:
            try:
                session.execute(text(statement))
                session.commit()
            except Exception:  # noqa: BLE001 — one failed ALTER should not block the others
                session.rollback()


def _url_without_query(url: str) -> str:
    return url.split("?", 1)[0]


def get_session():
    """Yield a SQLModel session bound to the MySQL engine."""
    with Session(get_engine()) as session:
        yield session
