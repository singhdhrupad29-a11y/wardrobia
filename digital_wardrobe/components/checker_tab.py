"""Virtual Closet: the add-item form (rendered inside the modal dialog), the
search + filter controls and the responsive inventory grid."""

import reflex as rx

from digital_wardrobe import state as st
from digital_wardrobe.state import image_src
from digital_wardrobe.components.theme import (
    BORDER,
    FAINT,
    GLASS,
    MUTED,
    TEXT,
    primary_button,
    status_badge,
)


# ── add-item form (dialog body) ───────────────────────────────────────────────

def _field(label: str, control: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.text(label, font_size="0.72em", color=MUTED, font_weight="600"),
        control,
        spacing="1",
        align="stretch",
        width="100%",
    )


def _upload_picker() -> rx.Component:
    return rx.upload(
        rx.vstack(
            rx.icon(tag="image_plus", size=22, color=MUTED),
            rx.text("Click or drop a photo", font_size="0.85em", font_weight="600", color=TEXT),
            rx.text(
                "PNG, JPG, JPEG, WEBP or GIF",
                font_size="0.72em",
                color=MUTED,
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        id="item_photo",
        multiple=False,
        max_files=1,
        accept={"image/*": [".png", ".jpg", ".jpeg", ".webp", ".gif"]},
        on_drop=st.WardrobeState.handle_upload,
        class_name="upload-dropzone",
        padding="1.3em",
        width="100%",
    )


def add_item_form() -> rx.Component:
    return rx.vstack(
        rx.grid(
            rx.vstack(
                _field("Item name", rx.input(
                    placeholder="e.g. Navy Oxford Shirt",
                    value=st.WardrobeState.form_name,
                    on_change=st.WardrobeState.set_form_name,
                )),
                _field("Primary color", rx.select(
                    st.COLOR_OPTIONS,
                    value=st.WardrobeState.form_color,
                    on_change=st.WardrobeState.set_form_color,
                )),
                spacing="3",
                align="stretch",
                width="100%",
            ),
            rx.vstack(
                _field("Category", rx.select(
                    st.CATEGORY_OPTIONS,
                    value=st.WardrobeState.form_category,
                    on_change=st.WardrobeState.set_form_category,
                )),
                _field("Formality (1 = casual, 5 = formal)", rx.select(
                    st.FORMALITY_OPTIONS,
                    value=st.WardrobeState.formality_score,
                    on_change=st.WardrobeState.set_formality_score,
                )),
                spacing="3",
                align="stretch",
                width="100%",
            ),
            rx.vstack(
                _field("Purchase price (₹)", rx.input(
                    type="number",
                    min="0",
                    step="0.01",
                    placeholder="0.00",
                    value=st.WardrobeState.purchase_price,
                    on_change=st.WardrobeState.set_purchase_price,
                )),
                _field("Status", rx.select(
                    st.STATUS_OPTIONS,
                    value=st.WardrobeState.form_status,
                    on_change=st.WardrobeState.set_form_status,
                )),
                spacing="3",
                align="stretch",
                width="100%",
            ),
            rx.vstack(
                _field("Brand (optional)", rx.input(
                    placeholder="e.g. Allen Solly",
                    value=st.WardrobeState.form_brand,
                    on_change=st.WardrobeState.set_form_brand,
                )),
                _field("Season", rx.select(
                    st.ITEM_SEASON_OPTIONS,
                    value=st.WardrobeState.form_season,
                    on_change=st.WardrobeState.set_form_season,
                )),
                spacing="3",
                align="stretch",
                width="100%",
            ),
            columns="repeat(auto-fit, minmax(180px, 1fr))",
            spacing="3",
            width="100%",
        ),
        _field("Photo", _upload_picker()),
        rx.cond(
            st.WardrobeState.form_image_url,
            rx.hstack(
                rx.image(
                    src=image_src(st.WardrobeState.form_image_url),
                    width="56px",
                    height="56px",
                    object_fit="cover",
                    border_radius="10px",
                    border=f"1px solid {BORDER}",
                ),
                rx.vstack(
                    rx.text(st.WardrobeState.uploaded_filename, font_size="0.78em", font_weight="600"),
                    rx.text("Ready to save with this item", font_size="0.72em", color=MUTED),
                    spacing="0",
                    align="start",
                ),
                rx.button(
                    "Remove photo",
                    on_click=st.WardrobeState.clear_form_image,
                    variant="ghost",
                    size="1",
                    color_scheme="gray",
                ),
                spacing="3",
                align="center",
            ),
            rx.text(""),
        ),
        rx.hstack(
            primary_button(
                rx.hstack(
                    rx.icon(tag="plus", size=15),
                    rx.text("Save item", font_weight="600"),
                    spacing="1",
                    align="center",
                ),
                on_click=st.WardrobeState.add_item,
            ),
            spacing="3",
            align="center",
        ),
        spacing="3",
        align="stretch",
        width="100%",
    )


# ── filter bar ────────────────────────────────────────────────────────────────

def _status_segment(value: str, label: str) -> rx.Component:
    return rx.button(
        label,
        on_click=st.WardrobeState.set_laundry_filter(value),
        variant=rx.cond(st.WardrobeState.laundry_filter == value, "solid", "soft"),
        color_scheme="gray",
        size="1",
        border_radius="999px",
    )


def _filter_bar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon(tag="search", size=15, color=FAINT),
                rx.input(
                    placeholder="Search by name or colour…",
                    value=st.WardrobeState.search_query,
                    on_change=st.WardrobeState.set_search_query,
                    variant="soft",
                    color_scheme="gray",
                    width="100%",
                ),
                spacing="2",
                align="center",
                border=f"1px solid {BORDER}",
                background_color=GLASS,
                padding="0 0.7em",
                border_radius="10px",
                width={"base": "100%", "md": "230px"},
            ),
            rx.select(
                ["All", *st.CATEGORY_OPTIONS],
                value=st.WardrobeState.category_filter,
                on_change=st.WardrobeState.set_category_filter,
                width={"base": "100%", "md": "150px"},
                variant="soft",
                color_scheme="gray",
            ),
            rx.select(
                ["All", *st.ITEM_SEASON_OPTIONS],
                value=st.WardrobeState.season_filter,
                on_change=st.WardrobeState.set_season_filter,
                width={"base": "100%", "md": "140px"},
                variant="soft",
                color_scheme="gray",
            ),
            rx.hstack(
                _status_segment("all", "All"),
                _status_segment("clean", "Show Clean"),
                _status_segment("laundry", "Show Laundry Only"),
                spacing="1",
                padding="0.2em",
                border=f"1px solid {BORDER}",
                background_color=GLASS,
                border_radius="999px",
                width={"base": "100%", "md": "auto"},
                justify="center",
                flex_wrap="wrap",
            ),
            rx.text(
                f"{st.WardrobeState.filtered_items.length()} items",
                font_size="0.78em",
                color=FAINT,
                width={"base": "100%", "md": "auto"},
                align="center",
            ),
            spacing="3",
            align_items={"base": "stretch", "md": "center"},
            flex_direction={"base": "column", "md": "row"},
            flex_wrap="wrap",
            width="100%",
        ),
        class_name="glass",
        padding="0.9em 1em",
        width="100%",
    )


# ── inventory grid ────────────────────────────────────────────────────────────

def _meta_stat(label: str, value) -> rx.Component:
    return rx.vstack(
        rx.text(label, font_size="0.64em", color=FAINT, font_weight="600"),
        rx.text(value, font_weight="700", font_size="0.9em"),
        spacing="0",
        align="start",
    )


def _delete_trigger(item: dict) -> rx.Component:
    """Trash button wrapped in a confirm dialog for one wardrobe item."""
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.icon_button(
                rx.icon(tag="trash-2", size=14),
                variant="ghost",
                color_scheme="gray",
                size="1",
                aria_label="Delete item",
                cursor="pointer",
            ),
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title(
                rx.text(
                    "Delete this item?",
                    font_family="'Fraunces', Georgia, serif",
                    font_weight="600",
                ),
            ),
            rx.alert_dialog.description(
                rx.text(
                    f"“{item['name']}” will be removed from your wardrobe, its outfits and wear history. This can’t be undone.",
                    font_size="0.85em",
                    color=MUTED,
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        rx.hstack(
                            rx.icon(tag="trash-2", size=14),
                            rx.text("Delete", font_weight="600"),
                            spacing="1",
                            align="center",
                        ),
                        color_scheme="red",
                        variant="solid",
                        size="2",
                        on_click=st.WardrobeState.delete_item(item["id"]),
                    ),
                ),
                spacing="3",
                justify="end",
                width="100%",
            ),
            size="3",
            background_color="#FFFFFF",
            border=f"1px solid {BORDER}",
        ),
    )


def item_card(item: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(item["category"], variant="soft", color_scheme="grass", size="1", class_name="pill"),
                rx.spacer(),
                rx.hstack(
                    status_badge(item["status"]),
                    _delete_trigger(item),
                    spacing="1",
                    align="center",
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                item["image_url"],
                rx.image(
                    src=image_src(item["image_url"]),
                    width="100%",
                    aspect_ratio="4/5",
                    object_fit="cover",
                    border_radius="10px",
                    border=f"1px solid {BORDER}",
                    on_click=st.WardrobeState.open_detail(item["id"]),
                    cursor="pointer",
                ),
                rx.box(
                    rx.text(item["color"], font_size="0.72em", color="#FFFFFF", font_weight="600"),
                    width="100%",
                    aspect_ratio="4/5",
                    border_radius="10px",
                    background_color=item["color_hex"],
                    border=f"1px solid {BORDER}",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    on_click=st.WardrobeState.open_detail(item["id"]),
                    cursor="pointer",
                ),
            ),
            rx.text(
                item["name"],
                font_weight="600",
                font_size="0.95em",
                color=TEXT,
                on_click=st.WardrobeState.open_detail(item["id"]),
                cursor="pointer",
            ),
            rx.text(
                f"{item['color']} · Formality {item['formality']}/5 · {item['price_str']}",
                font_size="0.74em",
                color=MUTED,
            ),
            rx.cond(
                item["brand_season"] != "",
                rx.text(item["brand_season"], font_size="0.72em", color=FAINT),
                rx.text(""),
            ),
            rx.divider(),
            rx.hstack(
                _meta_stat("CPW", item["cpw_str"]),
                _meta_stat("Worn", item["wear_count"]),
                _meta_stat("Price", item["price_str"]),
                rx.spacer(),
                width="100%",
            ),
            rx.button(
                rx.cond(item["status"] == "CLEAN", "Send to Laundry", "Mark as Clean"),
                on_click=st.WardrobeState.toggle_status(item["id"]),
                size="2",
                width="100%",
                color_scheme=rx.cond(item["status"] == "CLEAN", "amber", "grass"),
                variant="soft",
            ),
            align="start",
            spacing="2",
        ),
        width="100%",
        height="100%",
        class_name="item-card",
    )


def _inventory_grid() -> rx.Component:
    return rx.cond(
        st.WardrobeState.filtered_items,
        rx.grid(
            rx.foreach(st.WardrobeState.filtered_items, item_card),
            columns="repeat(auto-fill, minmax(200px, 1fr))",
            spacing="4",
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.icon(tag="search", size=26, color=FAINT),
                rx.text("Nothing matches these filters.", font_size="0.9em", font_weight="600"),
                rx.text(
                    "Try a different search, category or laundry view, or add a new item.",
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
    )


# ── item detail modal ─────────────────────────────────────────────────────────

def _detail_fact(label: str, value) -> rx.Component:
    return rx.vstack(
        rx.text(
            label,
            font_size="0.62em",
            color=FAINT,
            font_weight="600",
            text_transform="uppercase",
            letter_spacing="0.05em",
        ),
        rx.text(value, font_size="0.9em", font_weight="600", color=TEXT),
        spacing="0",
        align="start",
    )


def _detail_photo(item: dict) -> rx.Component:
    return rx.cond(
        item["image_url"],
        rx.image(
            src=image_src(item["image_url"]),
            width="100%",
            aspect_ratio="4/5",
            object_fit="cover",
            border_radius="12px",
            border=f"1px solid {BORDER}",
        ),
        rx.box(
            rx.text(item["color"], font_size="0.9em", color="#FFFFFF", font_weight="600"),
            width="100%",
            aspect_ratio="4/5",
            border_radius="12px",
            background_color=item["color_hex"],
            border=f"1px solid {BORDER}",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
    )


def item_detail_dialog() -> rx.Component:
    """Larger profile view of one item, with a delete action."""
    item = st.WardrobeState.detail_item
    return rx.dialog.root(
        rx.dialog.content(
            rx.cond(
                st.WardrobeState.detail_item,
                rx.vstack(
                    rx.hstack(
                        rx.dialog.title(
                            rx.text(
                                item["name"],
                                font_family="'Fraunces', Georgia, serif",
                                font_weight="600",
                            ),
                        ),
                        rx.spacer(),
                        status_badge(item["status"]),
                        width="100%",
                        align="center",
                    ),
                    _detail_photo(item),
                    rx.grid(
                        _detail_fact("Category", item["category"]),
                        _detail_fact("Brand", rx.cond(item["brand"], item["brand"], "—")),
                        _detail_fact("Season", rx.cond(item["season"], item["season"], "—")),
                        _detail_fact("Colour", item["color"]),
                        _detail_fact("Formality", f"{item['formality']}/5"),
                        _detail_fact("Price", item["price_str"]),
                        _detail_fact("Cost per wear", item["cpw_str"]),
                        _detail_fact("Worn", item["wear_count"]),
                        _detail_fact("Since wash", f"{item['wear_count_since_wash']}/{item['wear_limit']}"),
                        _detail_fact("Added", item["created"]),
                        columns="repeat(auto-fit, minmax(130px, 1fr))",
                        spacing="3",
                        width="100%",
                    ),
                    rx.hstack(
                        _delete_trigger(item),
                        rx.spacer(),
                        rx.dialog.close(
                            rx.button(
                                rx.hstack(
                                    rx.icon(tag="x", size=14),
                                    rx.text("Close"),
                                    spacing="1",
                                    align="center",
                                ),
                                variant="soft",
                                on_click=st.WardrobeState.close_detail,
                            ),
                        ),
                        width="100%",
                    ),
                    spacing="4",
                    align="stretch",
                    width="100%",
                ),
                rx.text(""),
            ),
            size="4",
            background_color="#FFFFFF",
            border=f"1px solid {BORDER}",
        ),
        open=rx.cond(st.WardrobeState.detail_item, True, False),
        on_open_change=st.WardrobeState.set_detail_open,
    )


# ── view root ─────────────────────────────────────────────────────────────────

def checker_tab() -> rx.Component:
    return rx.vstack(
        _filter_bar(),
        _inventory_grid(),
        item_detail_dialog(),
        spacing="4",
        align="stretch",
        width="100%",
    )
