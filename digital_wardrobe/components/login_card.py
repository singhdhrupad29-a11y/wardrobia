"""Sign-in / sign-up card, rendered full-screen when nobody is logged in.

Shares the warm editorial look of the dashboard: cream paper, Fraunces serif
headings, hairline borders and the ink primary button.
"""

import reflex as rx

from digital_wardrobe import state as st
from digital_wardrobe.components.theme import (
    BORDER,
    DANGER,
    FAINT,
    MUTED,
    PRIMARY,
    SAGE,
    TEXT,
)


def _field(
    label: str,
    placeholder: str,
    value: rx.Var[str],
    on_change,
    input_type: str = "text",
    hint: str = "",
    error: rx.Var[str] | None = None,
) -> rx.Component:
    border_color = f"1px solid {BORDER}"
    note = rx.text(hint, font_size="0.72em", color=MUTED)
    if error is not None:
        border_color = rx.cond(error != "", f"1px solid {DANGER}", border_color)
        note = rx.cond(
            error != "",
            rx.text(error, font_size="0.72em", color=DANGER, font_weight="600"),
            note,
        )
    return rx.vstack(
        rx.text(label, font_size="0.75em", font_weight="600", color=MUTED),
        rx.input(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            type=input_type,
            size="3",
            background_color="#FFFFFF",
            border=border_color,
            border_radius="8px",
        ),
        note,
        spacing="1",
        align="stretch",
        width="100%",
    )


def _demo_hint() -> rx.Component:
    return rx.callout(
        rx.vstack(
            rx.text("Demo accounts", font_size="0.75em", font_weight="700", color=SAGE),
            rx.text(
                "demo@atelier.local · demo1234",
                font_size="0.78em",
                color=MUTED,
                font_family="ui-monospace, monospace",
            ),
            rx.text(
                "sam@atelier.local · sam1234",
                font_size="0.78em",
                color=MUTED,
                font_family="ui-monospace, monospace",
            ),
            spacing="0",
            align="start",
            width="100%",
        ),
        icon="key_round",
        color_scheme="grass",
        variant="soft",
        width="100%",
    )


def login_card() -> rx.Component:
    is_signup = st.WardrobeState.auth_mode == "signup"
    return rx.center(
        rx.card(
            rx.vstack(
                # Brand mark
                rx.vstack(
                    rx.box(
                        rx.text(
                            "W",
                            color="#FFFFFF",
                            font_weight="600",
                            font_size="1.1em",
                        ),
                        width="38px",
                        height="38px",
                        border_radius="10px",
                        background_color=PRIMARY,
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.heading(
                        "Wardrobe",
                        size="6",
                        font_family="'Fraunces', Georgia, serif",
                        font_weight="600",
                        color=TEXT,
                    ),
                    rx.text(
                        rx.cond(
                            is_signup,
                            "Create your account to start your own wardrobe.",
                            "Sign in to open your wardrobe.",
                        ),
                        font_size="0.85em",
                        color=MUTED,
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                    padding_bottom="0.4em",
                ),
                rx.cond(
                    st.WardrobeState.auth_error != "",
                    rx.callout(
                        st.WardrobeState.auth_error,
                        icon="triangle_alert",
                        color_scheme="red",
                        variant="soft",
                        width="100%",
                    ),
                    rx.text(""),
                ),
                rx.vstack(
                    _field(
                        "Email",
                        "you@example.com",
                        st.WardrobeState.auth_email,
                        st.WardrobeState.set_auth_email,
                        hint="Must look like name@example.com",
                        error=st.WardrobeState.auth_email_error,
                    ),
                    _field(
                        "Password",
                        "••••••••",
                        st.WardrobeState.auth_password,
                        st.WardrobeState.set_auth_password,
                        input_type="password",
                        hint="6–128 characters, at least one letter and one number",
                        error=st.WardrobeState.auth_password_error,
                    ),
                    rx.cond(
                        is_signup,
                        _field(
                            "Name (optional)",
                            "How should we call you?",
                            st.WardrobeState.auth_name,
                            st.WardrobeState.set_auth_name,
                            error=st.WardrobeState.auth_name_error,
                        ),
                        rx.text(""),
                    ),
                    spacing="3",
                    align="stretch",
                    width="100%",
                ),
                rx.cond(
                    is_signup,
                    rx.button(
                        "Create account",
                        on_click=st.WardrobeState.register,
                        class_name="btn-primary",
                        size="3",
                        width="100%",
                    ),
                    rx.button(
                        "Sign in",
                        on_click=st.WardrobeState.login,
                        class_name="btn-primary",
                        size="3",
                        width="100%",
                    ),
                ),
                rx.hstack(
                    rx.text(
                        rx.cond(
                            is_signup,
                            "Already have an account?",
                            "New here?",
                        ),
                        font_size="0.8em",
                        color=MUTED,
                    ),
                    rx.cond(
                        is_signup,
                        rx.button(
                            "Sign in",
                            on_click=st.WardrobeState.set_auth_mode("signin"),
                            variant="ghost",
                            size="1",
                            color=SAGE,
                            font_weight="600",
                        ),
                        rx.button(
                            "Create an account",
                            on_click=st.WardrobeState.set_auth_mode("signup"),
                            variant="ghost",
                            size="1",
                            color=SAGE,
                            font_weight="600",
                        ),
                    ),
                    spacing="1",
                    justify="center",
                    align="center",
                    width="100%",
                ),
                rx.cond(is_signup, rx.text(""), _demo_hint()),
                spacing="4",
                align="stretch",
                width="100%",
            ),
            width="100%",
            max_width="390px",
            padding="2em",
            background_color="#FFFFFF",
            border=f"1px solid {BORDER}",
            box_shadow="0 12px 40px rgba(41, 37, 36, 0.07)",
        ),
        width="100%",
        min_height="100vh",
        padding="1.5em",
        background_color="#FAF8F3",
    )
