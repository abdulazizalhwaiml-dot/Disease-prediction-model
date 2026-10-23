"""Escaped HTML components. Probabilities always come from the trained models."""

from html import escape

from nhanes_ai.schema import DISEASES

LOGO = '<svg viewBox="0 0 48 48" aria-hidden="true"><rect width="48" height="48" rx="15" fill="#29c6b5"/><path d="M9 25h8l4-10 6 19 4-9h8" fill="none" stroke="#102d3a" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICONS = {
    "high_cholesterol": '<path d="M12 3C9 7 5 11 5 15a7 7 0 0014 0c0-4-4-8-7-12Z"/><path d="M9 16a3 3 0 003 3"/>',
    "high_blood_pressure": '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    "diabetes": '<path d="M12 3C9 7 5 11 5 15a7 7 0 0014 0c0-4-4-8-7-12Z"/><path d="M9 14h6m-3-3v6"/>',
    "coronary_artery_disease": '<path d="M20 5c-3-3-7-1-8 1-1-2-5-4-8-1-5 5 3 11 8 15 5-4 13-10 8-15Z"/><path d="M8 12h3l1-3 2 6 1-3h3"/>',
    "heart_attack": '<path d="M20 5c-3-3-7-1-8 1-1-2-5-4-8-1-5 5 3 11 8 15 5-4 13-10 8-15Z"/><path d="m13 8-3 5h4l-3 4"/>',
    "angina": '<path d="M20 5c-3-3-7-1-8 1-1-2-5-4-8-1-5 5 3 11 8 15 5-4 13-10 8-15Z"/><path d="m12 9-2 3 2 3 2-3Z"/>',
    "heart_failure": '<path d="M20 5c-3-3-7-1-8 1-1-2-5-4-8-1-5 5 3 11 8 15 5-4 13-10 8-15Z"/><path d="M8 12h8"/>',
    "stroke": '<path d="M12 4a4 4 0 00-7 3 4 4 0 00-2 7 4 4 0 005 5 4 4 0 004-1V4Zm0 0a4 4 0 017 3 4 4 0 012 7 4 4 0 01-5 5 4 4 0 01-4-1"/><path d="M7 8v4m10-4v4M7 16h2m6 0h2"/>',
}


def help_label(label, text):
    """Native details supports touch, click, keyboard and hover title."""
    return (
        f'<details class="field-help"><summary title="{escape(text, quote=True)}">'
        f'{escape(label)}<span aria-hidden="true">ⓘ</span></summary>'
        f"<p>{escape(text)}</p></details>"
    )


def probability_color(probability, threshold):
    """Colors follow study operating points; they are not clinical risk bands."""
    ratio = probability / max(threshold, 1e-8)
    if ratio < 0.65:
        return "#138b80", "#edf8f5"
    if ratio < 1:
        return "#b47a21", "#fff8e9"
    return "#c96856", "#fff1ed"


def disease_grid(predictions, names, text, model_entries):
    predictions = {p["disease"]: p for p in predictions} if predictions else {}
    cards = []
    for index, disease in enumerate(DISEASES):
        p = predictions.get(disease)
        color, background = (
            probability_color(p["probability"], p["threshold"]) if p else ("#647d87", "#f1f5f7")
        )
        value = f"{p['probability'] * 100:.1f}<small>%</small>" if p else "—<small>%</small>"
        status = (
            text["above"] if p and p["above_threshold"] else text["below"] if p else text["waiting"]
        )
        threshold = f"{text['threshold']} {p['threshold'] * 100:.1f}%" if p else text["probability"]
        limited = bool(p and model_entries[disease].get("quality_flags"))
        quality = (
            f'<div class="quality">{escape(text["limited_evidence"])}</div>' if limited else ""
        )
        width = p["probability"] * 100 if p else 0
        cards.append(
            f'<article class="disease-card" style="--accent:{color};--tint:{background}" '
            f'aria-label="{escape(names[disease], quote=True)}">'
            f'<div class="card-top"><span class="condition-icon"><svg viewBox="0 0 24 24" '
            f'fill="none" stroke="currentColor" stroke-width="1.45" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICONS[disease]}</svg></span>'
            f'<span class="card-index">{index + 1:02}</span></div>'
            f'<div class="condition-name">{escape(names[disease])}</div>'
            f'<div class="probability" dir="ltr">{value}</div>'
            f'<div class="probability-track"><span style="width:{width:.4f}%"></span></div>'
            f'<div class="card-foot"><span class="status-dot"></span>{escape(status)}</div>'
            f'<div class="threshold">{escape(threshold)}</div>{quality}</article>'
        )
    return '<div class="disease-grid">' + "".join(cards) + "</div>"
