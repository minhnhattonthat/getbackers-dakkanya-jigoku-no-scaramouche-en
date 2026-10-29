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


def test_wrap_balances_lines_and_leaves_no_stub():
    lines = batches.wrap("Ginji: \"The storeroom's open! Let's go check it out!\"", 216)
    assert lines == ["Ginji: \"The storeroom's open!", "Let's go check it out!\""]
    e = dict(BOX, jp="蛮「よし」")
    assert any("stub" in x for x in batches.check_entry(e, "Ban: \"Let's go check it out right now{br}ok.\"", ROWS, stored=True))


def test_wrapped_box_text_passes_the_window_lint():
    en = "Ban: \"That's right. I'm Ban Mido, the guy with a nearly perfect success rate, and you'd better believe it.\""
    assert not windows.check(BOX, batches.wrapped(BOX, en))
    assert batches.wrapped(BOX, en).count("{br}") == 2
    blank = dict(BOX, jp="　【　ポチの部屋　】　")
    assert batches.wrapped(blank, "[ Pochi's Room ]") == " [ Pochi's Room ] "


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
    br = {"id": "y", "ptrs": ["7F000"], "jp": "はい{br}いいえ"}
    assert not batches.check_entry(br, "Yes{br}No", ROWS)
    客 = [(["客"], "Customer", [], "Labels")]
    assert not batches.check_entry({"id": "z", "ptrs": ["7F000"], "jp": "お客さん、どうぞ"}, "Go ahead, sir.", 客)


def test_check_entry_catches_wrong_glossary_terms():
    rows = [(["美堂蛮"], "Ban Mido", [], "Characters"), (["蛮"], "Ban", [], "Characters"),
            (["ハンバーガー"], "Hamburger", [], "Items"), (["自分"], "Self", [], "Loose")]
    item = {"id": "q1", "ptrs": ["7F000"], "jp": "ハンバーガー"}
    assert any("Hamburger" in x for x in batches.check_entry(item, "Banana", rows))
    assert not batches.check_entry(item, "HAMBURGERS", rows)
    assert any("Ban Mido" in x for x in batches.check_entry(BOX, "Ban: \"I am John Smith.\"", rows))
    assert not batches.check_entry(BOX, "Ban: \"Yeah, I'm Ban Mido.\"", rows)
    page = {"id": "q2", "ptrs": ["7F000"], "jp": "蛮「オレが美堂蛮と"}
    assert not batches.check_entry(page, "Ban: \"Call me", rows, near="Ban Mido, got it?\"")
    assert not batches.check_entry({"id": "q3", "ptrs": ["7F000"], "jp": "自分の家"}, "My own house", rows)
