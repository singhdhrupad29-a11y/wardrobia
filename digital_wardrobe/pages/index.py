"""Main dashboard page.

Nobody is signed in → the login card. Signed in → sticky top navbar plus the
active view (Overview / Wardrobe / Outfits / Analytics) driven by
`state.WardrobeState.active_view`.

Every value rendered here comes from `state.WardrobeState`.
"""

import reflex as rx

from digital_wardrobe import state as st
from digital_wardrobe.components.checker_tab import checker_tab
from digital_wardrobe.components.generator_tab import generator_tab
from digital_wardrobe.components.header import header
from digital_wardrobe.components.history_tab import history_tab
from digital_wardrobe.components.login_card import login_card
from digital_wardrobe.components.overview import overview


def _view() -> rx.Component:
    return rx.match(
        st.WardrobeState.active_view,
        ("overview", overview()),
        ("wardrobe", checker_tab()),
        ("outfits", generator_tab()),
        ("analytics", history_tab()),
        overview(),
    )


def _dismissible_callout(text, icon: str, color_scheme: str) -> rx.Component:
    return rx.callout(
        rx.hstack(
            rx.text(text, flex="1"),
            rx.icon_button(
                rx.icon(tag="x", size=12),
                variant="ghost",
                size="1",
                aria_label="Dismiss",
                on_click=st.WardrobeState.clear_feedback,
                cursor="pointer",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        icon=icon,
        color_scheme=color_scheme,
        width="100%",
    )


def _dashboard() -> rx.Component:
    return rx.vstack(
        header(),
        rx.box(
            rx.vstack(
                rx.cond(
                    st.WardrobeState.error,
                    _dismissible_callout(
                        st.WardrobeState.error,
                        "triangle_alert",
                        "red",
                    ),
                    rx.text(""),
                ),
                rx.cond(
                    st.WardrobeState.message,
                    _dismissible_callout(
                        st.WardrobeState.message,
                        "check",
                        "grass",
                    ),
                    rx.text(""),
                ),
                _view(),
                spacing="6",
                align="stretch",
                width="100%",
            ),
            width="100%",
            max_width="1152px",
            margin_x="auto",
            padding="2.2em 1.4em",
        ),
        align="stretch",
        width="100%",
        spacing="0",
    )


def index() -> rx.Component:
    return rx.cond(
        st.WardrobeState.is_logged_in,
        _dashboard(),
        login_card(),
    )
