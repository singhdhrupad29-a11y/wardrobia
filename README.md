# Digital Wardrobe

A full-stack personal wardrobe management app built with [Reflex](https://reflex.dev) and **MySQL**. Track your pieces, manage laundry, and generate colour-coordinated outfit combinations from your own wardrobe.

## Tech stack

| Layer | Choice |
| --- | --- |
| Full-stack framework | **Reflex** — UI, state and backend logic all in Python |
| Language | Python 3.10+ |
| Database | **MySQL** (also MariaDB / TiDB) |
| ORM | SQLModel (built on SQLAlchemy) via PyMySQL |

## Features

- **Wardrobe inventory** — add items with category, colour, formality, price, brand, season and an optional photo.
- **Laundry management** — mark items clean or send them to the laundry; each category has a wear limit before a wash is triggered.
- **Outfit generator** — cross-joins clean topwear, bottomwear and footwear, and filters every colour pair through a pre-computed colour-harmony matrix so only harmonious combinations are suggested.
- **Cost-per-wear** — derived on read (`price / wears`), so it never drifts from the counters.
- **Wear history & analytics** — chronological wear log, wardrobe value, season breakdown and neglected-piece alerts.

## Folder structure

```
digital-wardrobe-python/
├── rxconfig.py                     # Reflex app config
├── requirements.txt                # Python dependencies
├── .env.example                    # DATABASE_URL template
└── digital_wardrobe/
    ├── __init__.py                 # package docstring
    ├── digital_wardrobe.py         # main app module: app = rx.App() + page wiring
    ├── models.py                   # SQLModel → MySQL schema
    ├── database.py                 # MySQL engine, init_db(), sessions
    ├── color_matrix.py             # colour-harmony scoring + matrix seeding
    ├── cpw.py                      # cost-per-wear formula
    ├── recommender.py              # SQL outfit engine
    ├── demo.py                     # single-user bootstrap
    ├── seed.py                     # idempotent seed script
    ├── state.py                    # Reflex state (CRUD, laundry, recommend)
    ├── pages/
    │   └── index.py                # main dashboard page
    └── components/                 # header, overview, tabs and shared theme
```

## Setup & run

```bash
cd digital-wardrobe-python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # edit DATABASE_URL for your MySQL
python -m digital_wardrobe.seed # creates the DB + tables + seed data (idempotent)
reflex run                      # or: python -m reflex run
```

### Environment variables

| Variable | Required | Notes |
| --- | --- | --- |
| `DATABASE_URL` | Yes | MySQL URL, e.g. `mysql://root:pass@127.0.0.1:3306/wardrobe_python`. `?ssl=true` is supported for cloud/TLS. |

`.env` is auto-loaded by `digital_wardrobe/database.py`, so the seed script and the app read the same URL. The seed script auto-creates the database (`CREATE DATABASE IF NOT EXISTS`), so you only need a running MySQL server and valid credentials.

## Schema overview

The schema lives in `digital_wardrobe/models.py` and is generated into MySQL by `SQLModel.metadata.create_all()`. Database charset is `utf8mb4`.

| Table | Purpose |
| --- | --- |
| `User` | application users |
| `Category` | Topwear / Bottomwear / Footwear / Outerwear / Accessories, each with a wear limit |
| `Brand` / `Season` | item metadata lookups |
| `ClothingItem` | the inventory row: colour, formality, price, status, wear counters, photo |
| `Outfit` / `OutfitItem` | saved outfits and their items (many-to-many) |
| `WearLog` | chronological wear history |
| `ColorCompatibility` | pre-computed colour-pair harmony scores (`color1 ≤ color2`, queried with `LEAST()`/`GREATEST()`) |

## Commands

| Command | Purpose |
| --- | --- |
| `python -m digital_wardrobe.seed` | Create DB + tables + seed data (idempotent) |
| `reflex run` | Start the dev server |
| `reflex init` | Re-initialise the compiled front-end if needed |
