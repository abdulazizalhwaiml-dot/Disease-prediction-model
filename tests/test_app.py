"""Execute real Streamlit widgets, both languages, invalid inputs and session invalidation."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_bilingual_app_prediction_bmi_and_stale_result_invalidation(model_root):
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / "app/main.py"), default_timeout=60).run()
    assert not app.exception
    # Eight numeric fields and two profile selects = ten inputs, plus separate UI controls.
    assert len(app.number_input) == 8
    app.button(key="predict").click().run(timeout=60)
    assert not app.exception
    assert len(app.session_state["result"]["predictions"]) == 8
    assert app.session_state["result"]["bmi"] > 26
    assert "high_cholesterol" in app.session_state["explanations"]
    assert any("Limited held-out performance" in element.value for element in app.markdown)
    app.selectbox(key="language").set_value("ar").run()
    assert not app.exception
    assert any("ثمانية" in element.value for element in app.subheader)
    assert app.button(key="predict").label == "استكشف ملفي"
    app.number_input(key="height_cm").set_value(180.0).run()
    assert "result" not in app.session_state
    app.number_input(key="body_fat_pct").set_value(55.0).run()
    app.button(key="predict").click().run()
    assert not app.exception
    assert any("لا تتوافق" in element.value for element in app.error)
