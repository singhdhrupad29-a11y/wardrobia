"""Sticky top navigation bar: brand mark, the Overview / Wardrobe / Outfits /
Analytics view links and the "Add item" modal dialog.

The active link renders as a dark ink pill, matching the reference dashboard.
"""

import reflex as rx

from digital_wardrobe import state as st
from digital_wardrobe.components.checker_tab import add_item_form
from digital_wardrobe.components.theme import BORDER, CREAM, MUTED, PRIMARY, TEXT

NAV_ITEMS = [
    ("Overview", "overview", "layout-dashboard"),
    ("Wardrobe", "wardrobe", "shirt"),
    ("Outfits", "outfits", "sparkles"),
    ("Analytics", "analytics", "chart-column-big"),
]


def _nav_link(label: str, value: str, icon: str) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(tag=icon, size=15),
            rx.text(label, class_name="nav-label"),
            spacing="2",
            align="center",
        ),
        on_click=st.WardrobeState.set_active_view(value),
        variant="ghost",
        class_name=rx.cond(
            st.WardrobeState.active_view == value,
            "nav-link nav-link-active",
            "nav-link",
        ),
        size="2",
    )


def _dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.hstack(
                    rx.icon(tag="plus", size=15),
                    rx.text("Add item", font_weight="600"),
                    spacing="1",
                    align="center",
                ),
                on_click=st.WardrobeState.open_form,
                class_name="btn-primary",
                size="2",
                padding="0 0.9em",
                height="32px",
                border_radius="8px",
            )
        ),
        rx.dialog.content(
            rx.dialog.title(
                rx.text("Add a new item", font_family="'Fraunces', Georgia, serif", font_weight="600"),
            ),
            rx.dialog.description(
                rx.text(
                    "Enter the details for your new item. Adding a photo is optional.",
                    font_size="0.85em",
                    color=MUTED,
                ),
            ),
            add_item_form(),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        rx.hstack(rx.icon(tag="x", size=14), rx.text("Close"), spacing="1", align="center"),
                        variant="soft",
                        on_click=st.WardrobeState.close_form,
                    )
                ),
                justify="end",
                width="100%",
            ),
            size="3",
            background_color="#FFFFFF",
            border=f"1px solid {BORDER}",
        ),
        open=st.WardrobeState.show_form,
        on_open_change=st.WardrobeState.set_show_form,
    )


def header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.hstack(
                    rx.text("W", color="#FFFFFF", font_weight="600", font_size="0.95em"),
                    width="30px",
                    height="30px",
                    border_radius="8px",
                    background_color=PRIMARY,
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.hstack(
                    rx.heading("Wardrobe", size="4", font_family="'Fraunces', Georgia, serif", font_weight="600"),
                    spacing="2",
                    align="baseline",
                ),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.foreach(
                    NAV_ITEMS,
                    lambda item: _nav_link(item[0], item[1], item[2]),
                ),
                spacing="3",
                align="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon(tag="user", size=14, color=PRIMARY),
                        width="28px",
                        height="28px",
                        border_radius="999px",
                        background_color=CREAM,
                        border=f"1px solid {BORDER}",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        flex_shrink="0",
                    ),
                    rx.vstack(
                        rx.text(
                            "Signed in as",
                            font_size="0.62em",
                            color=MUTED,
                            line_height="1",
                        ),
                        rx.text(
                            st.WardrobeState.display_name,
                            font_size="0.82em",
                            font_weight="600",
                            color=TEXT,
                            line_height="1.3",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.icon_button(
                    rx.icon(tag="log-out", size=15),
                    on_click=st.WardrobeState.logout,
                    variant="ghost",
                    size="2",
                    aria_label="Sign out",
                ),
                spacing="2",
                align="center",
            ),
            _dialog(),
            justify="between",
            align="center",
            width="100%",
            max_width="1152px",
            margin="0 auto",
            padding="1.15em 1.5em",
        ),
        class_name="site-nav",
        position="sticky",
        top="0",
        z_index="40",
        width="100%",
    )
