"""Shared UI palette + tiny building blocks for the dashboard.

Warm, editorial look: cream paper, stone ink, a muted sage accent and soft
hairline borders. No neon, no glow, no dark mode.
"""

import reflex as rx

PAPER = "#FAF8F3"      # page background (cream)
CARD = "#FFFFFF"       # card surface
INK = "#292524"        # primary text (stone-800)
MUTED = "#78716C"      # secondary text (stone-500)
FAINT = "#A8A197"      # tertiary text (warm stone)
BORDER = "#E8E3D6"     # warm hairline border
SAGE = "#5F6F52"       # muted sage green accent
SAGE_SOFT = "#EEF1E9"  # very light sage wash
CREAM = "#EFEAE0"      # warm sand panel
PRIMARY = "#191610"    # ink — buttons, active nav, progress bars (reference --primary)
PRIMARY_FG = "#F8F8F8"  # text on ink
PRIMARY_HOVER = "#2A2620"

# Compatibility aliases used across the components (warm mapping of the
# generic names introduced during the dashboard refresh).
TEXT = INK
GLASS = CARD
GLASS_STRONG = "#F6F3EA"
INDIGO = SAGE
VIOLET = "#7D8B6F"
GREEN = SAGE
AMBER = "#B45309"
DANGER = "#B91C1C"


def status_badge(status) -> rx.Component:
    """Pill chip for the current wash status of an item."""
    return rx.cond(
        status == "CLEAN",
        rx.badge(
            rx.hstack(rx.icon(tag="check", size=11), rx.text("Clean"), spacing="1", align="center"),
            color_scheme="grass",
            variant="soft",
            class_name="pill",
        ),
        rx.badge(
            rx.hstack(rx.icon(tag="layers", size=11), rx.text("In Laundry"), spacing="1", align="center"),
            color_scheme="amber",
            variant="soft",
            class_name="pill",
        ),
    )


def section_heading(eyebrow: str, title: str, subtitle: str) -> rx.Component:
    """Small editorial heading reused at the top of each tab."""
    return rx.vstack(
        rx.text(eyebrow.upper(), font_size="0.7em", letter_spacing="0.14em", color=SAGE, font_weight="600"),
        rx.heading(title, size="5"),
        rx.text(subtitle, font_size="0.85em", color=MUTED),
        spacing="1",
        align="start",
        width="100%",
    )


def stat_card(label: str, value, hint: str = "") -> rx.Component:
    """Metric card with a label and a big serif number."""
    return rx.card(
        rx.vstack(
            rx.text(label, font_size="0.75em", color=MUTED, font_weight="600"),
            rx.text(
                value,
                font_size="1.9em",
                font_family="'Fraunces', Georgia, serif",
                font_weight="500",
                line_height="1.1",
                font_variant_numeric="tabular-nums",
            ),
            rx.cond(
                hint != "",
                rx.text(hint, font_size="0.72em", color=MUTED),
                rx.text(""),
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        width="100%",
        height="100%",
        border=f"1px solid {BORDER}",
        class_name="dashboard-card",
    )


def primary_button(children, on_click=None, width=None, size="2") -> rx.Component:
    """Muted sage gradient primary action button."""
    return rx.button(
        children,
        on_click=on_click,
        class_name="btn-primary",
        width=width,
        size=size,
    )


def pill_badge(text: str, accent: str = SAGE, bg: str = "rgba(95,111,82,0.14)") -> rx.Component:
    """Generic pill chip with a custom accent tint."""
    return rx.badge(
        text,
        background_color=bg,
        color=accent,
        class_name="pill",
        border_radius="999px",
    )
