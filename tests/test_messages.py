"""Fixed wellness messages follow model thresholds and never certify health."""

from app.i18n import TEXT
from app.ui import wellness_message


def test_general_messages_cover_both_branches_and_languages():
    for text in TEXT.values():
        below = wellness_message([{"above_threshold": False}] * 8, text)
        above = wellness_message([{"above_threshold": False}, {"above_threshold": True}], text)
        assert text["maintain_message"] in below
        assert text["attention_message"] in above
        assert text["attention_message"] not in below
        assert text["maintain_message"] not in above
