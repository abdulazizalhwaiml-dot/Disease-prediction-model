"""Responsive English/Arabic research interface. Inputs never leave the local model runtime."""

import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.i18n import DISEASE_AR, ETHNICITY_AR, TEXT
from nhanes_ai.inference import LIMITS, InputError, ModelRegistry, release_fingerprint
from nhanes_ai.schema import DISEASES, ETHNICITY

ROOT = Path(__file__).resolve().parents[1]
MODELS = Path(os.environ.get("NHANES_MODELS_DIR", str(ROOT / "models")))
st.set_page_config(page_title="Body & Health AI | ذكاء الجسم والصحة", page_icon="◈", layout="wide")
language = st.sidebar.selectbox(
    "Language / اللغة",
    ["en", "ar"],
    format_func=lambda value: "English" if value == "en" else "العربية",
    key="language",
)
t = TEXT[language]
names = DISEASES if language == "en" else DISEASE_AR
direction = "rtl" if language == "ar" else "ltr"
st.markdown(
    f"""
<style>
 .stApp {{ background: #f4f7fb; color: #122c3b; font-family: Inter, Tahoma, sans-serif; }}
 [data-testid="stMainBlockContainer"] {{ max-width: 1240px; padding-top: 2rem; direction: {direction}; }}
 [data-testid="stSidebar"] {{ background: #e9f0f5; direction: {direction}; }}
 h1,h2,h3 {{ color:#102c3b; letter-spacing:-.035em; }}
 .hero {{ background:linear-gradient(125deg,#102c3b,#164d59); border-radius:24px;
          padding:40px; margin-bottom:24px; color:white; }}
 .hero h1 {{ color:white; font-size:clamp(1.8rem,3.2vw,3rem); line-height:1.2; max-width:850px; }}
 .hero p {{ color:#d0e1e6; max-width:800px; font-size:1.08rem; line-height:1.7; }}
 .eyebrow {{ color:#b6e5a2; font-size:.75rem; font-weight:700; letter-spacing:.13em; margin-bottom:14px; }}
 .estimate-card {{ background:white; border:1px solid #e0e7ee; border-radius:18px;
                   padding:20px; margin-bottom:16px; min-height:190px; }}
 .estimate-name {{ font-size:.88rem; color:#4f6470; min-height:42px; }}
 .estimate-number {{ font-size:2.3rem; color:#123949; font-weight:750; letter-spacing:-.04em; }}
 .estimate-meta {{ font-size:.74rem; color:#667d88; margin-top:8px; line-height:1.5; }}
 .track {{ height:5px; background:#edf2f5; border-radius:5px; margin-top:12px; overflow:hidden; }}
 .fill {{ height:100%; background:#238b85; border-radius:5px; }}
 [data-testid="stMetric"] {{ background:#fff; border-radius:14px; padding:14px; border:1px solid #e0e7ee; }}
 .stButton>button[kind="primary"] {{ background:#166f73; border:0; border-radius:12px; min-height:48px; }}
 .stNumberInput input {{ direction:ltr; }}
 @media(max-width:650px) {{ .hero {{ padding:24px; }} .estimate-card {{ min-height:160px; }} }}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def registry(path, fingerprint):
    """Cache immutable models, never patient measurements or predictions."""
    return ModelRegistry(Path(path))


st.sidebar.title(t["brand"])
st.sidebar.info(t["scope"])
st.sidebar.caption(t["country"])
st.sidebar.caption(t["privacy"])
st.markdown(
    f'<div class="hero"><div class="eyebrow">{t["edition"]}</div>'
    f"<h1>{t['title']}</h1><p>{t['subtitle']}</p></div>",
    unsafe_allow_html=True,
)
st.warning(t["notice"])
try:
    models = registry(str(MODELS), release_fingerprint(MODELS))
except (OSError, ValueError, KeyError, ImportError):
    st.error(t["no_models"])
    st.code("python -m nhanes_ai.train --data DATA_SET --output models --reports reports")
    st.stop()
st.sidebar.caption(f"{t['release']}: {models.manifest['run_id']}")
assessment, evidence, method = st.tabs([t["assessment"], t["evidence"], t["method"]])

with assessment:
    st.subheader(t["inputs"])
    st.caption(t["input_note"])
    record = {}
    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.markdown(f"#### {t['profile']}")
            record["age"] = st.number_input(t["age"], 20, 59, 45, key="age")
            record["gender"] = st.selectbox(
                t["gender"],
                [1, 2],
                format_func=lambda value: t["male"] if value == 1 else t["female"],
                key="gender",
            )
            record["ethnicity"] = st.selectbox(
                t["ethnicity"],
                [None, *ETHNICITY],
                key="ethnicity",
                format_func=lambda value: (
                    t["unknown"]
                    if value is None
                    else (ETHNICITY[value] if language == "en" else ETHNICITY_AR[value])
                ),
            )
            st.caption(t["ethnicity_note"])
            record["height_cm"] = st.number_input(
                t["height_cm"], 120.0, 220.0, 175.0, 0.5, key="height_cm"
            )
            record["weight_kg"] = st.number_input(
                t["weight_kg"], 25.0, 205.0, 80.0, 0.5, key="weight_kg"
            )
    with right:
        with st.container(border=True):
            st.markdown(f"#### {t['composition']}")
            for field, default, step in [
                ("waist_cm", 95.0, 0.5),
                ("bone_mass_kg", 3.0, 0.1),
                ("body_fat_pct", 30.0, 0.5),
                ("fat_mass_kg", 24.0, 0.5),
                ("lean_mass_kg", 53.0, 0.5),
            ]:
                low, high = LIMITS[field]
                record[field] = st.number_input(
                    t[field], float(low), float(high), default, step, key=field
                )
            st.caption(t["dxa_note"])
    c1, c2 = st.columns([1, 2])
    c1.metric(
        t["bmi"],
        f"{record['weight_kg'] / (record['height_cm'] / 100) ** 2:.1f}",
        "kg/m²",
        delta_color="off",
    )
    if record["ethnicity"] is None:
        c2.info(t["unknown_note"])
    # Clear stale results whenever measurements or the active model release change.
    if (
        st.session_state.get("record") != record
        or st.session_state.get("run_id") != models.manifest["run_id"]
    ):
        for key in ["result", "explanations"]:
            st.session_state.pop(key, None)
    if st.button(t["submit"], type="primary", width="stretch", key="predict"):
        try:
            with st.spinner(t["running"]):
                result = models.predict(record)
            st.session_state.update(
                result=result,
                record=record.copy(),
                explanations={},
                run_id=models.manifest["run_id"],
            )
        except InputError as error:
            prefix = str(error).split(":")[0]
            st.error(t.get(prefix, t["invalid"]))
        except (ValueError, RuntimeError):
            st.error(t["no_models"])
    if "result" not in st.session_state:
        st.info(t["empty"])
    else:
        st.divider()
        st.subheader(t["results"])
        st.caption(t["result_note"])
        result = st.session_state.result
        if result.get("outside_training_range"):
            st.warning(
                t["outside_training"]
                + " "
                + ", ".join(t[field] for field in result["outside_training_range"])
            )
        columns = st.columns(4)
        for index, prediction in enumerate(result["predictions"]):
            probability = prediction["probability"] * 100
            status = t["above"] if prediction["above_threshold"] else t["below"]
            quality_note = (
                t["limited_evidence"]
                if models.manifest["models"][prediction["disease"]].get("quality_flags")
                else ""
            )
            columns[index % 4].markdown(
                f'<div class="estimate-card"><div class="estimate-name">{names[prediction["disease"]]}</div>'
                f'<div class="estimate-number">{probability:.1f}%</div>'
                f'<div class="track"><div class="fill" style="width:{probability}%"></div></div>'
                f'<div class="estimate-meta">{status}<br>{t["threshold"]}: '
                f"{prediction['threshold'] * 100:.1f}%<br>{quality_note}</div></div>",
                unsafe_allow_html=True,
            )
        chart = go.Figure(
            go.Bar(
                x=[p["probability"] * 100 for p in result["predictions"]],
                y=[names[p["disease"]] for p in result["predictions"]],
                orientation="h",
                marker_color="#238b85",
                name=t["probability"],
            )
        )
        chart.add_trace(
            go.Scatter(
                x=[p["threshold"] * 100 for p in result["predictions"]],
                y=[names[p["disease"]] for p in result["predictions"]],
                mode="markers",
                marker={"symbol": "diamond", "color": "#c07b37", "size": 9},
                name=t["threshold"],
            )
        )
        chart.update_layout(
            height=380,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis_title=t["probability"],
            xaxis_range=[0, 100],
            yaxis_autorange="reversed",
            legend_orientation="h",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(chart, width="stretch")
        st.subheader(t["explain"])
        disease = st.selectbox(
            t["select"], list(DISEASES), format_func=lambda key: names[key], key="explain_disease"
        )
        try:
            if disease not in st.session_state.explanations:
                with st.spinner(t["explaining"]):
                    st.session_state.explanations[disease] = models.explain(
                        st.session_state.record, disease
                    )
            explanation = st.session_state.explanations[disease]
            base, value, net = st.columns(3)
            base.metric(t["baseline"], f"{explanation['baseline'] * 100:.1f}%")
            value.metric(t["estimate"], f"{explanation['probability'] * 100:.1f}%")
            net.metric(
                t["net"], f"{(explanation['probability'] - explanation['baseline']) * 100:+.1f} pp"
            )
            contributions = sorted(
                explanation["contributions"].items(), key=lambda pair: abs(pair[1])
            )
            labels = [t.get(name, name) for name, _ in contributions]
            impacts = [value * 100 for _, value in contributions]
            waterfall = go.Figure(
                go.Bar(
                    x=impacts,
                    y=labels,
                    orientation="h",
                    marker_color=["#c07b37" if value > 0 else "#238b85" for value in impacts],
                )
            )
            waterfall.update_layout(
                height=420,
                xaxis_title=t["impact"],
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            waterfall.add_vline(x=0, line_color="#adbcc6", line_width=1)
            st.plotly_chart(waterfall, width="stretch")
            st.caption(t["explain_note"])
        except Exception:
            # A failure to explain must never be hidden or replaced by made-up contributions.
            st.error(t["explain_error"])
            if st.button(t["retry"]):
                st.session_state.explanations.pop(disease, None)
                st.rerun()

with evidence:
    st.subheader(t["evidence"])
    st.info(t["evidence_note"])
    rows = []
    for key, entry in models.manifest["models"].items():
        score = entry["test"]
        rows.append(
            {
                t["disease"]: names[key],
                t["algorithm"]: entry["algorithm"],
                **{
                    t[metric]: round(score[metric], 3)
                    for metric in ["recall", "precision", "f1", "roc_auc", "pr_auc", "brier"]
                },
                t["positive"]: score["positive"],
                t["n"]: score["n"],
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    selected = st.selectbox(
        t["select"], list(DISEASES), format_func=lambda key: names[key], key="evidence_disease"
    )
    score = models.manifest["models"][selected]["test"]
    st.caption(t["interval"])
    st.dataframe(
        pd.DataFrame(
            [
                {t["disease"]: t[key], "95% CI": f"{value[0]:.3f} – {value[1]:.3f}"}
                for key, value in score["bootstrap_95_ci"].items()
            ]
        ),
        hide_index=True,
        width="stretch",
    )

with method:
    st.subheader(t["audit"])
    st.metric(t["remaining"], f"{models.manifest['cohort']['remaining_records']:,}")
    st.write(t["method_text"])
    st.write(t["labels_text"].format(**models.manifest["label_config"]))
    st.write(t["training_text"])
    st.caption(t["scope"])
st.divider()
st.caption(t["footer"])
