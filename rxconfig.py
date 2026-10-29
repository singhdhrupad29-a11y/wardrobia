"""Reflex configuration for the Digital Wardrobe.

The Reflex runtime only uses `db_url` for its own internal bookkeeping; the
application database is MySQL and is managed through SQLModel/SQLAlchemy in
`digital_wardrobe/database.py`, driven by the `DATABASE_URL` environment
variable (see `.env.example`).

The Radix themes plugin carries the light, warm, editorial theme (soft "grass"
sage accent on a "sand" neutral scale). The paper background and typography
live in `assets/custom.css`.
"""

import reflex as rx

config = rx.Config(
    app_name="digital_wardrobe",
    db_url="sqlite:///reflex.db",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                accent_color="grass",
                gray_color="sand",
                radius="medium",
                # The paper background is painted by assets/custom.css, so the
                # theme root itself must stay transparent.
                has_background=False,
            )
        ),
    ],
)
