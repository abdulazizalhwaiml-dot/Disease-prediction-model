"""Eight-input bilingual research dashboard; inference stays in session memory."""

import json
import os
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from app.i18n import DISEASE_AR, TEXT
from app.ui import LOGO, disease_grid, help_label, wellness_message
from nhanes_ai.features import derive_features
from nhanes_ai.inference import LIMITS, InputError, ModelRegistry, release_fingerprint
from nhanes_ai.schema import DISEASES, USER_FIELDS

ROOT = Path(__file__).resolve().parents[1]
MODELS = Path(os.environ.get("NHANES_MODELS_DIR", str(ROOT / "models")))
st.set_page_config(page_title="ميزان | MIZAN — Research", page_icon="◈", layout="wide")
language = st.sidebar.selectbox(
    "Language / اللغة",
    ["ar", "en"],
    format_func=lambda value: "العربية" if value == "ar" else "English",
    key="language",
)
t = TEXT[language]
names = DISEASE_AR if language == "ar" else DISEASES
direction = "rtl" if language == "ar" else "ltr"
st.markdown(
    "<style>"
    + (ROOT / "app/style.css").read_text()
    + f'[data-testid="stMainBlockContainer"], [data-testid="stSidebar"] {{direction:{direction};}}'
    + "</style>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f'<div class="sidebar-brand">{LOGO}<div><div class="brand-name">'
    f'{t["brand"]}</div><div class="brand-sub">BODY INSIGHTS LAB</div></div></div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f'<div class="sidebar-fact">{t["scope"]}</div>'
    f'<div class="sidebar-rule"></div><div class="sidebar-caption">{t["privacy"]}</div>',
    unsafe_allow_html=True,
)
st.sidebar.caption("NHANES 1999–2006 + 2011–2018 · v3.0")


@st.cache_resource(show_spinner=False)
def registry(path, fingerprint):
    """Cache immutable models; never cache inputs or predictions globally."""
    return ModelRegistry(Path(path))


try:
    models = registry(str(MODELS), release_fingerprint(MODELS))
except (OSError, ValueError, KeyError, ImportError):
    models = None

st.markdown(
    f'<div class="topbar"><div class="topbar-wordmark">{LOGO}{t["tagline"]}</div>'
    f'<div class="research-badge"><i></i>{t["research"]}</div></div>'
    f'<div class="hero"><div class="eyebrow">{t["eyebrow"]}</div><h1>{t["title"]}</h1>'
    f'<p>{t["subtitle"]}</p><div class="hero-facts"><span>{t["input_count"]}</span>'
    f"<span>{t['derived_count']}</span><span>{t['disease_count']}</span></div></div>"
    f'<div class="research-notice"><span>ⓘ</span><div>{t["notice"]}</div></div>',
    unsafe_allow_html=True,
)
assessment, guide = st.tabs([t["assessment"], t["guide"]])

with assessment:
    form_column, result_column = st.columns([0.85, 1.5], gap="large")
    record = {}
    with form_column:
        with st.container(key="input_panel"):
            st.markdown(
                f'<div class="section-title">{t["form_title"]}</div>'
                f'<div class="section-note">{t["form_note"]}</div>'
                f'<div class="form-section">{t["measurements"]}</div>',
                unsafe_allow_html=True,
            )
            for field in USER_FIELDS:
                if field == "family_diabetes":
                    st.markdown(
                        f'<div class="form-section">{t["family"]}</div>', unsafe_allow_html=True
                    )
                st.markdown(help_label(t[field], t["help"][field]), unsafe_allow_html=True)
                if field == "gender":
                    record[field] = st.radio(
                        t[field],
                        [1, 2],
                        key=field,
                        horizontal=True,
                        format_func=lambda v: t["male"] if v == 1 else t["female"],
                        label_visibility="collapsed",
                    )
                elif field.startswith("family_"):
                    record[field] = st.radio(
                        t[field],
                        [1, 0],
                        index=None,
                        key=field,
                        horizontal=True,
                        format_func=lambda v: t["yes"] if v == 1 else t["no"],
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
                        key=field,
                        label_visibility="collapsed",
                    )
            derived = (
                derive_features(pd.DataFrame([record]))[["bmi", "fat_mass_kg", "fat_free_mass_kg"]]
                .iloc[0]
                .to_dict()
            )
            st.markdown(
                f'<div class="automatic-heading">{t["automatic"]}</div><div class="derived-grid">'
                + "".join(
                    f'<div class="derived"><div class="derived-label">{t[k]}</div>'
                    f'<div class="derived-value">{v:.1f}<span class="derived-unit">'
                    f"{'kg/m²' if k == 'bmi' else t['kg']}</span></div></div>"
                    for k, v in derived.items()
                )
                + "</div>",
                unsafe_allow_html=True,
            )
            ready = all(record[field] is not None for field in USER_FIELDS)
            if not ready:
                st.markdown(
                    f'<p class="required-note">{t["family_required"]}</p>', unsafe_allow_html=True
                )
            run_id = models.manifest["run_id"] if models else None
            if st.session_state.get("record") != record or st.session_state.get("run_id") != run_id:
                st.session_state.pop("result", None)
            if st.button(
                t["submit"],
                type="primary",
                width="stretch",
                key="predict",
                disabled=not ready or models is None,
            ):
                try:
                    with st.spinner(t["running"]):
                        result = models.predict(record)
                    st.session_state.update(result=result, record=record.copy(), run_id=run_id)
                except InputError as error:
                    field = str(error).split(":")[0]
                    st.error(t.get(field + "_error", t["invalid"]))
                except (ValueError, RuntimeError):
                    st.error(t["no_models"])
            if models is None:
                st.error(t["no_models"])
                st.code("python -m nhanes_ai.train --jobs 2")
    with result_column:
        st.markdown(
            f'<div class="results-header"><div class="section-title">{t["results"]}</div>'
            '<span class="results-count">NHANES · 8</span></div>'
            f'<div class="section-note">{t["results_subtitle"]}</div>',
            unsafe_allow_html=True,
        )
        result = st.session_state.get("result")
        if result is None:
            st.markdown(
                f'<div class="empty-note"><strong>{t["empty"]}</strong><br>{t["empty_note"]}</div>',
                unsafe_allow_html=True,
            )
        elif result.get("outside_training_range"):
            st.warning(
                t["outside_training"] + ", ".join(t[f] for f in result["outside_training_range"])
            )
        st.markdown(
            disease_grid(
                result["predictions"] if result else None,
                names,
                t,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(f'<p class="legend">{t["legend"]}</p>', unsafe_allow_html=True)
        if result:
            st.markdown(wellness_message(result["predictions"], t), unsafe_allow_html=True)
            if record["age"] >= 60:
                st.caption(t["older_note"])
            st.download_button(
                t["download"],
                json.dumps(result, ensure_ascii=False, indent=2),
                "mizan-assessment.json",
                "application/json",
                key="download",
            )

with guide:
    st.subheader(t["guide_title"])
    st.caption(t["guide_note"])
    for field in USER_FIELDS:
        with st.expander(t[field]):
            st.write(t["help"][field])
    st.subheader(t["formulas"])
    st.code(
        "BMI = weight_kg / (height_cm / 100)²\nFat mass = weight_kg × body_fat_pct / 100\nFat-free mass = weight_kg − fat_mass_kg"
    )
    st.caption(t["formula_note"])
    st.markdown(
        "[NHANES family-history definitions](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/MCQ_G.htm#MCQ300a)"
    )
st.markdown(
    f'<div class="app-footer"><span>{escape(t["footer"])}</span><span>{escape(t["scope"])}</span></div>',
    unsafe_allow_html=True,
)
