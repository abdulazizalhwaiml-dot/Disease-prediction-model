"""Mizanak: eight measurements first, followed by a simple interactive research report."""

import json
import logging
import os
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from app.i18n import DISEASE_AR, TEXT
from app.ui import (
    ASSETS,
    disease_grid,
    hero_art_html,
    logo_html,
    scroll_to_results_script,
    wellness_message,
)
from nhanes_ai.features import derive_features
from nhanes_ai.inference import LIMITS, InputError, ModelRegistry, release_fingerprint
from nhanes_ai.schema import DISEASES, USER_FIELDS

ROOT = Path(__file__).resolve().parents[1]
MODELS = Path(os.environ.get("NHANES_MODELS_DIR", str(ROOT / "models")))
st.set_page_config(
    page_title="ميزانك | Mizanak",
    page_icon=str(ASSETS / "logo.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Language belongs in the page header; no sidebar can leave a phantom reserved column.
with st.container(key="topbar", height="content"):
    brand_column, language_column = st.columns([0.72, 0.28], vertical_alignment="top")
with language_column:
    language = st.selectbox(
        "Language / اللغة",
        ["ar", "en"],
        format_func=lambda value: "العربية" if value == "ar" else "English",
        key="language",
        label_visibility="collapsed",
    )
t = TEXT[language]
names = DISEASE_AR if language == "ar" else DISEASES
direction = "rtl" if language == "ar" else "ltr"
st.html(
    "<style>"
    + (ROOT / "app/style.css").read_text(encoding="utf-8")
    + f'[data-testid="stMainBlockContainer"], [data-testid="stPopoverBody"] {{direction:{direction};}}'
    + "</style>"
)
with brand_column:
    # Native HTML measures the logo's actual content height, without Markdown line-box sizing.
    st.html(
        f'<div class="brand" dir="{direction}">{logo_html()}<div><div class="brand-name">{t["brand"]}</div><div class="brand-tagline">{t["tagline"]}</div></div></div>'
    )

st.markdown(
    f'<div class="research-badge"><i></i>{t["research"]}</div>'
    f'<div class="hero"><div class="hero-copy"><span class="eyebrow">{t["eyebrow"]}</span><h1>{t["title"]}</h1>'
    f'<p>{t["subtitle"]}</p><span class="scope-pill">{t["scope"]}</span></div>'
    f'<div class="hero-art" aria-hidden="true">{hero_art_html()}</div></div>',
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def registry(path, fingerprint):
    """Cache immutable trusted models, never globally cache a user's measurements."""
    return ModelRegistry(Path(path))


try:
    models = registry(str(MODELS), release_fingerprint(MODELS))
except (OSError, ValueError, KeyError, ImportError):
    logging.getLogger(__name__).exception("Trusted model loading failed")
    models = None


record = {}


def render_field(field):
    """Accessible native popover keeps a visible help button next to every label."""
    with st.container(key=f"field_{field}"):
        # A non-wrapping Streamlit row becomes an internal scroll container.
        # Let the row grow with its real HTML label and native help button instead.
        with st.container(
            key=f"label_{field}",
            horizontal=True,
            height="content",
            vertical_alignment="center",
            gap="small",
        ):
            st.html(
                f'<span class="field-title">{escape(t[field])}</span>',
                width="content",
            )
            with st.popover(
                f"{t['help_button']}: {t[field]}",
                icon=":material/help:",
                help=t[field],
                key=f"help_{field}",
                width="content",
            ):
                st.markdown(f"**{t[field]}**")
                if field in ["height_cm", "waist_cm"]:
                    st.image(
                        str(ASSETS / ("height.png" if field == "height_cm" else "waist.png")),
                        alt=t["image_alt"][field],
                        width="stretch",
                    )
                st.write(t["help"][field])
                if field in ["height_cm", "waist_cm"]:
                    st.caption(t["image_note"][field])
        if field == "gender":
            record[field] = st.radio(
                t[field],
                [1, 2],
                key=field,
                horizontal=True,
                format_func=lambda value: t["male"] if value == 1 else t["female"],
                label_visibility="collapsed",
            )
        elif field.startswith("family_"):
            record[field] = st.radio(
                t[field],
                [1, 0],
                index=None,
                key=field,
                horizontal=True,
                format_func=lambda value: t["yes"] if value == 1 else t["no"],
                label_visibility="collapsed",
            )
        else:
            low, high = LIMITS[field]
            default = {
                "age": 45,
                "height_cm": 175.0,
                "weight_kg": 80.0,
                "waist_cm": 95.0,
                "body_fat_pct": 30.0,
            }[field]
            record[field] = st.number_input(
                t[field],
                min_value=low if field == "age" else float(low),
                max_value=high if field == "age" else float(high),
                value=default,
                step=1 if field == "age" else 0.5,
                format="%d" if field == "age" else "%.1f",
                key=field,
                label_visibility="collapsed",
            )


with st.container(key="input_panel"):
    st.markdown(
        f'<div class="section-heading"><span class="step-number">01</span><div><h2>{t["form_title"]}</h2><p>{t["form_note"]}</p></div></div>',
        unsafe_allow_html=True,
    )
    for fields in [["age", "gender", "height_cm"], ["weight_kg", "waist_cm", "body_fat_pct"]]:
        for column, field in zip(st.columns(3, gap="medium"), fields):
            with column:
                render_field(field)
    st.markdown(f'<div class="family-heading">{t["family"]}</div>', unsafe_allow_html=True)
    for column, field in zip(
        st.columns(2, gap="medium"), ["family_diabetes", "family_heart_early"]
    ):
        with column:
            render_field(field)
    ready = all(record[field] is not None for field in USER_FIELDS)
    if not ready:
        st.caption(t["family_required"])
    run_id = models.manifest["run_id"] if models else None
    if st.session_state.get("record") != record or st.session_state.get("run_id") != run_id:
        st.session_state.pop("result", None)
    derived = derive_features(pd.DataFrame([record])).iloc[0]
    st.markdown(
        f'<div class="derived-heading">{escape(t["automatic"])}</div><div class="derived-grid">'
        + "".join(
            f'<div class="derived-metric" data-derived="{field}"><span>{escape(t[field])}</span>'
            f'<strong dir="ltr">{derived[field]:.1f}<small>{"kg/m²" if field == "bmi" else escape(t["kg"])}</small></strong></div>'
            for field in ["bmi", "fat_mass_kg", "fat_free_mass_kg"]
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    if st.button(
        t["submit"],
        type="primary",
        width="stretch",
        icon=":material/arrow_downward:",
        key="predict",
        disabled=not ready or models is None,
    ):
        try:
            with st.spinner(t["running"]):
                result = models.predict(record)
            st.session_state.update(
                result=result, record=record.copy(), run_id=run_id, scroll_to_results=True
            )
        except InputError as error:
            field = str(error).split(":")[0]
            st.error(t.get(field + "_error", t["invalid"]))
        except (ValueError, RuntimeError):
            st.error(t["no_models"])
    if models is None:
        st.error(t["no_models"])
        st.code("python -m nhanes_ai.train --jobs 2")

# Results follow the whole input panel in DOM and visual order, on every screen size.
result = st.session_state.get("result")
with st.container(key="report"):
    st.markdown(
        f'<div id="mizanak-results" class="section-heading report-anchor" tabindex="-1"><span class="step-number">02</span><div><h2>{t["results"]}</h2><p>{t["results_subtitle"]}</p></div></div>',
        unsafe_allow_html=True,
    )
    if result:
        st.markdown(wellness_message(result["predictions"], t), unsafe_allow_html=True)
        if result.get("outside_training_range"):
            st.warning(
                t["outside_training"]
                + ", ".join(t.get(field, field) for field in result["outside_training_range"])
            )
        st.markdown(disease_grid(result["predictions"], names, t), unsafe_allow_html=True)
        st.caption(t["legend"])
        if record["age"] >= 60:
            st.caption(t["older_note"])
        st.download_button(
            t["download"],
            json.dumps(result, ensure_ascii=False, indent=2),
            "mizanak-report.json",
            "application/json",
            icon=":material/download:",
            key="download",
        )
    else:
        st.markdown(
            f'<div class="empty-report"><span class="empty-icon" aria-hidden="true">✦</span><strong>{t["empty"]}</strong><p>{t["empty_note"]}</p></div>',
            unsafe_allow_html=True,
        )

if st.session_state.pop("scroll_to_results", False):
    st.html(scroll_to_results_script(result["id"]), unsafe_allow_javascript=True)
st.markdown(
    f'<div class="research-notice">{escape(t["notice"])}</div><footer><span>{escape(t["footer"])}</span><span>{escape(t["privacy"])}</span></footer>',
    unsafe_allow_html=True,
)
