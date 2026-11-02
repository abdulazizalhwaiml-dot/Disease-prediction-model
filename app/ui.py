"""Small, escaped UI components; predictions always come from the trained pipelines."""

import base64
from functools import lru_cache
from html import escape
from pathlib import Path

from nhanes_ai.schema import DISEASES

ASSETS = Path(__file__).resolve().parent / "assets"
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


@lru_cache(maxsize=1)
def logo_html():
    data = base64.b64encode((ASSETS / "logo.png").read_bytes()).decode("ascii")
    return (
        f'<img class="brand-logo" src="data:image/png;base64,{data}" alt="" width="58" height="58">'
    )


@lru_cache(maxsize=1)
def hero_art_html():
    data = base64.b64encode((ASSETS / "hero-health.svg").read_bytes()).decode("ascii")
    return f'<img class="hero-illustration" src="data:image/svg+xml;base64,{data}" alt="" width="200" height="170">'


def probability_state(probability, threshold):
    """Display bands relative to research thresholds, never clinical risk classes."""
    ratio = probability / max(threshold, 1e-8)
    return "calm" if ratio < 0.65 else "watch" if ratio < 1 else "attention"


def disease_grid(predictions, names, text):
    """Tap a simple card for a fixed condition definition; no feature attribution."""
    cards = []
    for prediction in predictions:
        disease = prediction["disease"]
        if disease not in DISEASES:
            raise ValueError("Unknown condition")
        probability = prediction["probability"]
        tone = probability_state(probability, prediction["threshold"])
        status = (
            text["above"]
            if prediction["above_threshold"]
            else text["near"]
            if tone == "watch"
            else text["below"]
        )
        icon = f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[disease]}</svg>'
        cards.append(
            f'<details class="disease-card {tone}"><summary aria-label="{escape(names[disease], quote=True)}">'
            f'<div class="card-top"><span class="condition-icon">{icon}</span><span class="card-more" aria-hidden="true">⌄</span></div>'
            f'<div class="condition-name">{escape(names[disease])}</div>'
            f'<div class="probability" dir="ltr">{probability * 100:.1f}<small>%</small></div>'
            f'<div class="probability-track"><span style="width:{probability * 100:.4f}%"></span></div>'
            f'<div class="card-status"><i></i>{escape(status)}</div></summary>'
            f'<div class="card-definition"><p>{escape(text["conditions"][disease])}</p>'
            f'<small class="condition-disclaimer">{escape(text["condition_disclaimer"])}</small></div></details>'
        )
    return '<div class="disease-grid">' + "".join(cards) + "</div>"


def wellness_message(predictions, text):
    """Two fixed wellness messages; neither diagnoses disease nor certifies health."""
    attention = any(item["above_threshold"] for item in predictions)
    key = "attention" if attention else "maintain"
    return (
        f'<div class="wellness-message {key}" role="status"><span class="wellness-icon" aria-hidden="true">✦</span><div>'
        f"<strong>{escape(text[key + '_title'])}</strong>"
        f"<p>{escape(text[key + '_message'])}</p></div></div>"
    )


def scroll_to_results_script(token):
    """Run only after submission; target the main page without an iframe or reserved space."""
    return (
        '<script data-report-jump="'
        + escape(token, quote=True)
        + '">'
        + """
    (() => {
      const move = () => {
        const target = document.getElementById('mizanak-results');
        if (!target) return false;
        const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        target.scrollIntoView({behavior: reduced ? 'instant' : 'smooth', block: 'start'});
        target.focus({preventScroll: true});
        return true;
      };
      requestAnimationFrame(() => requestAnimationFrame(() => {
        if (move()) return;
        const observer = new MutationObserver(() => { if (move()) observer.disconnect(); });
        observer.observe(document.body, {childList: true, subtree: true});
        setTimeout(() => observer.disconnect(), 3000);
      }));
    })();
    </script>"""
    )
