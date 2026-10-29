import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import vwf  # noqa: E402
import windows  # noqa: E402

BOX = {"id": "044B24", "ptrs": ["7F000"], "jp": "蛮「そーよ、オレが美堂蛮」"}
ROWS = [(["蛮"], "Ban", ["Van"], "Characters"), (["銀次"], "Ginji", [], "Characters")]


def test_wrap_keeps_lines_in_the_box_and_words_whole():
    text = "Ban: \"" + " ".join(["Retrieval"] * 30) + "\""
    lines = batches.wrap(text, 216)
    assert " ".join(lines) == text
    assert all(vwf.width(l) <= 216 for l in lines) and len(lines) > 3


def test_wrapped_box_text_passes_the_window_lint():
    en = "Ban: \"That's right. I'm Ban Mido, the guy with a nearly perfect success rate, and you'd better believe it.\""
    assert not windows.check(BOX, batches.wrapped(BOX, en))
    assert batches.wrapped(BOX, en).count("{br}") == 2


def test_term_hits_whole_runs_only():
    assert batches.term_hits("蛮「よし」", "蛮")
    assert batches.term_hits("蛮ちゃん！", "蛮")             # an honorific after the name still counts
    assert not batches.term_hits("野蛮な奴", "蛮")           # inside a longer kanji run
    assert not batches.term_hits("タイミング", "ミン")


def test_check_entry_catches_speaker_honorific_avoid_and_codes():
    assert not batches.check_entry(BOX, "Ban: \"That's right. I'm Ban Mido.\"", ROWS)
    assert any("speaker" in x for x in batches.check_entry(BOX, "Mido: \"Yo.\"", ROWS))
    assert any("avoid" in x for x in batches.check_entry(BOX, "Ban: \"Van Mido.\"", ROWS))
    e = {"id": "x", "ptrs": ["7F000"], "jp": "銀次「蛮ちゃん、%sだよ」"}
    errs = batches.check_entry(e, "Ginji: \"Ban, it's %s!\"", ROWS)
    assert any("honorific" in x for x in errs)
    assert any("printf" in x for x in batches.check_entry(e, "Ginji: \"Ban-chan!\"", ROWS))
    assert any("font" in x for x in batches.check_entry(BOX, "Ban: “Yo.”", ROWS))
