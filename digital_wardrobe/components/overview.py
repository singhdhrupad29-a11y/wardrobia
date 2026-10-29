"""Overview landing view: welcome band, stat cards, laundry queue and the
recent-wears feed — mirroring the reference dashboard's home layout."""

import reflex as rx

from digital_wardrobe import state as st
from digital_wardrobe.components.theme import (
    BORDER,
    MUTED,
    PRIMARY,
    TEXT,
    stat_card,
)


def _section_header(title: str, count) -> rx.Component:
    return rx.hstack(
        rx.heading(title, size="4", font_weight="600"),
        rx.badge(
            rx.text(count),
            variant="soft",
            color_scheme="gray",
            size="1",
            class_name="pill",
        ),
        spacing="2",
        align="center",
        width="100%",
    )


def _welcome_band() -> rx.Component:
    return rx.vstack(
        rx.text(
            f"Digital wardrobe · {st.WardrobeState.stats['total']} pieces tracked",
            class_name="micro-label",
        ),
        rx.heading("Welcome back", size="7", font_weight="500"),
        rx.text(
            "Everything at a glance — what your collection is worth, what you've "
            "worn lately, and what is waiting for a wash.",
            color=MUTED,
            font_size="0.95em",
            max_width="560px",
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def _stat_grid() -> rx.Component:
    return rx.grid(
        stat_card("Wardrobe value", st.WardrobeState.stats["value_str"], "across every item"),
        stat_card("Total wears", st.WardrobeState.stats["total_wears"], "all-time wears logged"),
        stat_card("Worn last 30 days", st.WardrobeState.stats["worn_30"], "days worn this month"),
        stat_card("Saved outfits", st.WardrobeState.stats["saved_outfits"], "outfits logged"),
        columns=rx.breakpoints(
            {"base": "repeat(2, 1fr)", "md": "repeat(4, 1fr)"}
        ),
        spacing="4",
        width="100%",
    )


def _laundry_row(item: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon(tag="shirt", size=15, color=MUTED),
                rx.text(item["name"], font_weight="600", font_size="0.9em", color=TEXT),
                spacing="2",
                align="center",
                min_width="0",
            ),
            rx.spacer(),
            rx.text(
                f"{item['wear_count_since_wash']}/{item['wear_limit']} wears",
                font_size="0.72em",
                color=MUTED,
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        rx.box(
            rx.box(
                width=f"{item['wear_pct']}%",
                height="100%",
                background_color=PRIMARY,
                border_radius="999px",
                transition="width 0.3s ease",
            ),
            width="100%",
            height="6px",
            background_color="#EDEAE2",
            border_radius="999px",
            margin_top="0.5em",
        ),
        class_name="wear-row",
    )


def _laundry_queue() -> rx.Component:
    return rx.cond(
        st.WardrobeState.laundry_items,
        rx.card(
            rx.vstack(
                _section_header("Laundry queue", st.WardrobeState.stats["laundry"]),
                rx.vstack(
                    rx.foreach(st.WardrobeState.laundry_items, _laundry_row),
                    class_name="wear-feed",
                    spacing="0",
                    width="100%",
                ),
                spacing="2",
                align="stretch",
                width="100%",
            ),
            width="100%",
            class_name="dashboard-card",
            border=f"1px solid {BORDER}",
        ),
        rx.card(
            rx.vstack(
                _section_header("Laundry queue", 0),
                rx.text(
                    "Nothing is waiting for a wash — your wardrobe is all clean.",
                    font_size="0.85em",
                    color=MUTED,
                    padding="0.5em 0",
                ),
                spacing="2",
                align="stretch",
                width="100%",
            ),
            width="100%",
            class_name="dashboard-card",
            border=f"1px solid {BORDER}",
        ),
    )


def _wear_row(log: dict) -> rx.Component:
    return rx.hstack(
        rx.icon(tag="shirt", size=15, color=MUTED),
        rx.text(log["items_text"], font_size="0.85em", font_weight="500", color=TEXT, flex="1"),
        rx.text(
            log["date_display"],
            font_size="0.72em",
            color=MUTED,
            class_name="mono-date",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def _recent_wears() -> rx.Component:
    return rx.card(
        rx.vstack(
            _section_header("Recent wears", st.WardrobeState.wear_logs.length()),
            rx.vstack(
                rx.foreach(st.WardrobeState.wear_logs[:6], _wear_row),
                class_name="wear-feed",
                spacing="0",
                width="100%",
            ),
            spacing="2",
            align="stretch",
            width="100%",
        ),
        width="100%",
        class_name="dashboard-card",
        border=f"1px solid {BORDER}",
    )


def overview() -> rx.Component:
    return rx.vstack(
        _welcome_band(),
        _stat_grid(),
        rx.grid(
            _laundry_queue(),
            _recent_wears(),
            columns=rx.breakpoints({"base": "1fr", "lg": "repeat(2, 1fr)"}),
            spacing="4",
            width="100%",
            align_items="start",
        ),
        spacing="6",
        align="stretch",
        width="100%",
    )
