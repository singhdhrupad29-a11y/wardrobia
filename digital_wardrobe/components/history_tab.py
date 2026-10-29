"""Analytics & History: the metric cards, the chronological wear log with
weather tags, and the neglected-items alert."""

import reflex as rx

from digital_wardrobe import state as st
from digital_wardrobe.components.theme import (
    BORDER,
    FAINT,
    MUTED,
    PRIMARY,
    TEXT,
    stat_card,
)


# ── metrics ───────────────────────────────────────────────────────────────────

def metrics_bar() -> rx.Component:
    return rx.grid(
        stat_card("Total items", st.WardrobeState.stats["total"], "pieces in your wardrobe"),
        stat_card("Clean ratio", st.WardrobeState.stats["clean_ratio_str"], "ready to wear right now"),
        stat_card("In laundry", st.WardrobeState.stats["laundry"], "awaiting a wash"),
        stat_card("Brands", st.WardrobeState.stats["brand_count"], "labels in your wardrobe"),
        stat_card("Avg cost-per-wear", st.WardrobeState.stats["avg_cpw_str"], "across all items"),
        columns="repeat(auto-fit, minmax(150px, 1fr))",
        spacing="3",
        width="100%",
    )


# ── season breakdown ──────────────────────────────────────────────────────────

def _season_row(entry: dict) -> rx.Component:
    return rx.hstack(
        rx.text(
            entry["season"],
            font_size="0.82em",
            font_weight="600",
            color=TEXT,
            width="110px",
            flex_shrink="0",
        ),
        rx.box(
            rx.box(
                background_color=PRIMARY,
                border_radius="999px",
                width=f"{entry['pct']}%",
                height="6px",
            ),
            width="100%",
            height="6px",
            background_color="#EDEAE2",
            border_radius="999px",
        ),
        rx.text(
            f"{entry['count']} · {entry['pct']}%",
            font_size="0.72em",
            color=MUTED,
            width="80px",
            text_align="right",
            flex_shrink="0",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def season_breakdown() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Wardrobe by season", size="4", font_weight="600"),
            rx.text(
                "How your pieces are spread across Summer, Winter, Rainy and Spring.",
                font_size="0.82em",
                color=MUTED,
            ),
            rx.cond(
                st.WardrobeState.season_breakdown,
                rx.vstack(
                    rx.foreach(st.WardrobeState.season_breakdown, _season_row),
                    spacing="2",
                    width="100%",
                ),
                rx.text(
                    "Add items with a season to see the breakdown.",
                    font_size="0.85em",
                    color=MUTED,
                    padding="0.5em 0",
                ),
            ),
            spacing="2",
            align="stretch",
            width="100%",
        ),
        width="100%",
        class_name="dashboard-card",
        border=f"1px solid {BORDER}",
    )


# ── V_ItemCostPerWear (SQL view) ──────────────────────────────────────────────

def _view_header_cell(label: str, width: str) -> rx.Component:
    return rx.text(
        label.upper(),
        font_size="0.64em",
        letter_spacing="0.1em",
        font_weight="700",
        color=FAINT,
        width=width,
        text_align="right",
        flex_shrink="0",
    )


def _view_row(row: dict) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.text(row["name"], font_size="0.85em", font_weight="600", color=TEXT),
            rx.text(row["category"], font_size="0.7em", color=MUTED),
            width="100%",
            flex="1",
            min_width="0",
        ),
        rx.text(
            row["price_str"],
            font_size="0.8em",
            color=MUTED,
            width="90px",
            text_align="right",
            flex_shrink="0",
        ),
        rx.text(
            f"{row['wear_count']}×",
            font_size="0.8em",
            color=MUTED,
            width="55px",
            text_align="right",
            flex_shrink="0",
        ),
        rx.text(
            row["cpw_str"],
            font_size="0.85em",
            font_weight="700",
            color=TEXT,
            width="90px",
            text_align="right",
            flex_shrink="0",
        ),
        spacing="3",
        align="center",
        width="100%",
        padding="0.35em 0",
        border_bottom=f"1px solid {BORDER}",
    )


def cost_per_wear_view() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Cost per wear", size="4", font_weight="600"),
                rx.badge(
                    "SQL VIEW · V_ItemCostPerWear",
                    variant="soft",
                    color_scheme="grass",
                    class_name="pill",
                ),
                spacing="2",
                align="center",
                justify="between",
                width="100%",
            ),
            rx.text(
                "purchase_price / GREATEST(wear_count, 1) — the join and the "
                "division live in the database, not in Python. Cheapest first.",
                font_size="0.82em",
                color=MUTED,
            ),
            rx.hstack(
                rx.box(
                    rx.text(
                        "ITEM",
                        font_size="0.64em",
                        letter_spacing="0.1em",
                        font_weight="700",
                        color=FAINT,
                    ),
                    width="100%",
                    flex="1",
                    min_width="0",
                ),
                _view_header_cell("Price", "90px"),
                _view_header_cell("Wears", "55px"),
                _view_header_cell("Cost/wear", "90px"),
                spacing="3",
                align="center",
                width="100%",
                padding_bottom="0.3em",
            ),
            rx.cond(
                st.WardrobeState.view_rows,
                rx.foreach(st.WardrobeState.view_rows, _view_row),
                rx.text(
                    "Add items to see them ranked by cost-per-wear.",
                    font_size="0.85em",
                    color=MUTED,
                    padding="0.6em 0",
                ),
            ),
            spacing="2",
            align="stretch",
            width="100%",
        ),
        width="100%",
        class_name="dashboard-card",
        border=f"1px solid {BORDER}",
    )


# ── wear history ──────────────────────────────────────────────────────────────

def _history_row(log: dict) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.box(
                rx.text(log["date_display"], font_family="'Fraunces', Georgia, serif", font_weight="600", font_size="0.95em", color=TEXT),
                rx.text("worn", font_size="0.68em", color=FAINT),
                align="center",
                width="130px",
                flex_shrink="0",
            ),
            rx.box(
                rx.text(log["items_text"], font_size="0.85em", font_weight="600", color=TEXT),
                width="100%",
            ),
            rx.spacer(),
            rx.cond(
                log["notes"] != "",
                rx.badge(
                    rx.hstack(
                        rx.icon(tag="cloud-sun", size=11),
                        rx.text(log["notes"]),
                        spacing="1",
                        align="center",
                    ),
                    variant="soft",
                    color_scheme="sky",
                    class_name="pill",
                ),
                rx.badge("No weather note", variant="soft", color_scheme="gray", size="1", class_name="pill"),
            ),
            spacing="3",
            align="center",
            width="100%",
            flex_wrap="wrap",
            row_gap="2",
        ),
        width="100%",
        class_name="glass",
    )


def wear_history() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.heading("What you've worn", size="4"),
            rx.text(
                "A chronological record of the pieces you've worn, grouped by day.",
                font_size="0.82em",
                color=MUTED,
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.cond(
            st.WardrobeState.wear_logs,
            rx.vstack(
                rx.foreach(st.WardrobeState.wear_logs, _history_row),
                spacing="3",
                width="100%",
            ),
            rx.card(
                rx.text(
                    "No wear history yet — log an outfit from the generator to start the story.",
                    font_size="0.85em",
                    color=MUTED,
                    padding="1.4em",
                ),
                width="100%",
                class_name="glass",
            ),
        ),
        spacing="3",
        align="stretch",
        width="100%",
    )


# ── neglected items ───────────────────────────────────────────────────────────

def _neglected_row(item: dict) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.box(
                width="36px",
                height="36px",
                border_radius="10px",
                background_color=item["color_hex"],
                border=f"1px solid {BORDER}",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(item["name"], font_size="0.85em", font_weight="600", color=TEXT),
                rx.text(
                    f"{item['category']} · {item['color']} · worn {item['wear_count']} times",
                    font_size="0.76em",
                    color=MUTED,
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.badge(
                rx.cond(
                    item["wear_count"] == 0,
                    "Never worn",
                    f"Last worn {item['last_worn']}",
                ),
                variant="soft",
                color_scheme="amber",
                size="1",
                class_name="pill",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        width="100%",
        class_name="glass",
    )


def neglected_items() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.heading("Lonely pieces", size="4"),
            rx.text(
                "Clothes that have never been worn, or haven't been worn in the last 60 days.",
                font_size="0.82em",
                color=MUTED,
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.cond(
            st.WardrobeState.neglected_items,
            rx.vstack(
                rx.foreach(st.WardrobeState.neglected_items, _neglected_row),
                spacing="3",
                width="100%",
            ),
            rx.card(
                rx.text(
                    "Nothing neglected — every piece is earning its keep.",
                    font_size="0.85em",
                    color=MUTED,
                    padding="1.4em",
                ),
                width="100%",
                class_name="glass",
            ),
        ),
        spacing="3",
        align="stretch",
        width="100%",
    )


# ── view root ─────────────────────────────────────────────────────────────────

def history_tab() -> rx.Component:
    return rx.vstack(
        metrics_bar(),
        cost_per_wear_view(),
        season_breakdown(),
        wear_history(),
        neglected_items(),
        spacing="4",
        align="stretch",
        width="100%",
    )
