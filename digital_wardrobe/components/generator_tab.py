"""Outfit Studio: season/occasion context filters, the "Generate outfits"
action and the instant outfit grid with per-card harmony scores."""

import reflex as rx

from digital_wardrobe import state as st
from digital_wardrobe.state import image_src
from digital_wardrobe.components.theme import (
    BORDER,
    FAINT,
    GLASS,
    INDIGO,
    MUTED,
    TEXT,
    primary_button,
)


def _piece(piece: dict, label: str) -> rx.Component:
    """One layer of an outfit: photo (or swatch), label, name, colour."""
    return rx.vstack(
        rx.cond(
            piece["image_url"],
            rx.image(
                src=image_src(piece["image_url"]),
                width="100%",
                aspect_ratio="4/5",
                object_fit="cover",
                border_radius="10px",
                border=f"1px solid {BORDER}",
            ),
            rx.box(
                width="100%",
                aspect_ratio="4/5",
                border_radius="10px",
                background_color=piece["color_hex"],
                border=f"1px solid {BORDER}",
            ),
        ),
        rx.text(label, font_size="0.66em", color=FAINT, font_weight="600"),
        rx.text(piece["name"], font_size="0.78em", font_weight="600", text_align="center", color=TEXT),
        rx.text(piece["color"], font_size="0.7em", color=MUTED),
        spacing="1",
        align="center",
        width="100%",
    )


def outfit_card(outfit: dict, index: int) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(f"Outfit {index + 1}", variant="soft", color_scheme="gray", size="1", class_name="pill"),
                rx.spacer(),
                rx.badge(
                    f"{outfit['harmony_pct']}% Color Harmony",
                    variant="soft",
                    color_scheme="grass",
                    size="1",
                    class_name="pill",
                ),
                width="100%",
                align="center",
            ),
            rx.hstack(
                _piece(outfit["top"], "Topwear"),
                rx.icon(tag="plus", size=14, color=FAINT),
                _piece(outfit["bottom"], "Bottomwear"),
                rx.icon(tag="plus", size=14, color=FAINT),
                _piece(outfit["foot"], "Footwear"),
                align="center",
                spacing="2",
                width="100%",
            ),
            rx.divider(),
            primary_button(
                rx.hstack(
                    rx.icon(tag="check", size=14),
                    rx.text("Log Outfit Worn Today", font_weight="600"),
                    spacing="1",
                    align="center",
                ),
                on_click=st.WardrobeState.log_wear(index),
                width="100%",
            ),
            spacing="3",
            align="stretch",
            width="100%",
        ),
        width="100%",
        height="100%",
        class_name="outfit-card",
    )


def _context_field(label: str, control: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.text(label, font_size="0.72em", color=MUTED, font_weight="600"),
        control,
        spacing="1",
        align="stretch",
        width="100%",
    )


def _controls() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.grid(
                _context_field(
                    "Season / weather",
                    rx.select(
                        st.SEASON_OPTIONS,
                        value=st.WardrobeState.season,
                        on_change=st.WardrobeState.set_season,
                        width="100%",
                        variant="soft",
                    ),
                ),
                _context_field(
                    "Occasion",
                    rx.select(
                        st.OCCASION_OPTIONS,
                        value=st.WardrobeState.occasion,
                        on_change=st.WardrobeState.set_occasion,
                        width="100%",
                        variant="soft",
                    ),
                ),
                _context_field(
                    "Weather note (optional)",
                    rx.input(
                        placeholder="e.g. Warm and humid, light drizzle",
                        value=st.WardrobeState.weather_notes,
                        on_change=st.WardrobeState.set_weather_notes,
                        width="100%",
                        variant="soft",
                    ),
                ),
                columns="repeat(auto-fit, minmax(200px, 1fr))",
                spacing="3",
                width="100%",
            ),
            rx.hstack(
                primary_button(
                    rx.hstack(
                        rx.icon(tag="sparkles", size=15),
                        rx.text(
                            rx.cond(
                                st.WardrobeState.is_generating,
                                "Generating…",
                                "Generate Outfits",
                            )
                        ),
                        spacing="1",
                        align="center",
                    ),
                    on_click=st.WardrobeState.generate_outfits,
                ),
                rx.cond(
                    st.WardrobeState.generator_note != "",
                    rx.badge(
                        rx.hstack(
                            rx.icon(tag="sliders_horizontal", size=11),
                            rx.text(st.WardrobeState.generator_note),
                            spacing="1",
                            align="center",
                        ),
                        variant="soft",
                        color_scheme="amber",
                        class_name="pill",
                    ),
                    rx.text(""),
                ),
                spacing="3",
                align="center",
            ),
            spacing="3",
            align="stretch",
            width="100%",
        ),
        class_name="glass",
        padding="1em",
        width="100%",
    )


def generator_tab() -> rx.Component:
    return rx.vstack(
        _controls(),
        rx.cond(
            st.WardrobeState.generated_outfits,
            rx.grid(
                rx.foreach(st.WardrobeState.generated_outfits, outfit_card),
                columns="repeat(auto-fill, minmax(280px, 1fr))",
                spacing="4",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.icon(tag="sparkles", size=26, color=INDIGO),
                    rx.text("No outfits generated yet.", font_size="0.9em", font_weight="600"),
                    rx.text(
                        "Pick a season and occasion, then press “Generate Outfits”.",
                        font_size="0.82em",
                        color=MUTED,
                    ),
                    spacing="2",
                    align="center",
                    padding="2em",
                ),
                width="100%",
                class_name="glass",
            ),
        ),
        spacing="4",
        align="stretch",
        width="100%",
    )
