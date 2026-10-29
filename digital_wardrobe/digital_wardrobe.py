"""Main Reflex app module.

Reflex looks for this module at `{app_name}/{app_name}.py` (see rxconfig.py)
and reads the module-level `app` object from it. This module imports every
state, page and model used by the app so Reflex includes them in the build.

The light, warm editorial theme is configured in rxconfig.py via the Radix
themes plugin; `assets/custom.css` handles fonts and the paper background.
All layout lives in `digital_wardrobe/components/`.
"""

import reflex as rx

from digital_wardrobe import state as st
from digital_wardrobe.pages.index import index

app = rx.App(
    stylesheets=["/custom.css"],
)

app.add_page(
    index,
    route="/",
    title="Wardrobe \u00b7 Digital Wardrobe",
    on_load=st.WardrobeState.load_all,
)
