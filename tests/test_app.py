"""Exercise the real eight-input UI, both languages and stale-result handling."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.i18n import TEXT
from nhanes_ai.schema import USER_FIELDS


@pytest.mark.parametrize("entrypoint", ["app/main.py", "streamlit_app.py"])
def test_bilingual_eight_input_app_and_clickable_help(model_root, entrypoint):
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / entrypoint), default_timeout=60).run()
    assert not app.exception
    assert len(app.number_input) == 5
    assert app.button(key="predict").disabled
    assert len(app.radio) == 3
    assert app.radio(key="family_diabetes").value is None
    assert app.radio(key="family_heart_early").value is None
    markup = "\n".join(element.value for element in app.markdown)
    for field in USER_FIELDS:
        assert TEXT["ar"]["help"][field] in markup
    assert markup.count('<details class="field-help">') == 8
    app.radio(key="family_diabetes").set_value(1)
    app.radio(key="family_heart_early").set_value(0).run()
    assert not app.button(key="predict").disabled
    app.button(key="predict").click().run(timeout=60)
    assert not app.exception
    assert len(app.session_state["record"]) == 8
    result = app.session_state["result"]
    assert len(result["predictions"]) == 8
    assert result["fat_mass_kg"] == 24
    assert result["fat_free_mass_kg"] == 56
    markup = "\n".join(element.value for element in app.markdown)
    assert 'class="wellness-message ' in markup
    assert "وراء الأرقام" not in markup
    assert "explanations" not in app.session_state
    assert len(app.selectbox) == 1  # Language only; no disease/explanation selector.
    app.number_input(key="age").set_value(79).run()
    assert "result" not in app.session_state
    app.button(key="predict").click().run(timeout=60)
    assert not app.exception
    assert len(app.session_state["result"]["predictions"]) == 8
    app.selectbox(key="language").set_value("en").run()
    assert not app.exception
    assert app.button(key="predict").label == "Explore my estimates"
    assert len(app.session_state["result"]["predictions"]) == 8
    app.number_input(key="height_cm").set_value(180.0).run()
    assert "result" not in app.session_state


def test_language_help_has_no_missing_input_definitions():
    for language in ["ar", "en"]:
        assert set(TEXT[language]["help"]) == set(USER_FIELDS)
        assert "50" in TEXT[language]["help"]["family_heart_early"]


def test_lower_estimates_show_maintenance_without_health_certificate(model_root):
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / "streamlit_app.py"), default_timeout=60).run()
    app.number_input(key="age").set_value(20)
    app.radio(key="gender").set_value(2)
    app.number_input(key="height_cm").set_value(165.0)
    app.number_input(key="weight_kg").set_value(50.0)
    app.number_input(key="waist_cm").set_value(65.0)
    app.number_input(key="body_fat_pct").set_value(20.0)
    app.radio(key="family_diabetes").set_value(0)
    app.radio(key="family_heart_early").set_value(0).run()
    app.button(key="predict").click().run()
    assert not app.exception
    assert not any(p["above_threshold"] for p in app.session_state["result"]["predictions"])
    markup = "\n".join(element.value for element in app.markdown)
    assert TEXT["ar"]["maintain_message"] in markup
    assert TEXT["ar"]["attention_message"] not in markup
