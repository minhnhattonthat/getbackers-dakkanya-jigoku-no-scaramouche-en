import json
import re
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import rom_text  # noqa: E402

ROM = ROOT / "rom" / "GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM")
PRINTF = re.compile(r"%(?:s|3d|6d)")
BLANK = " 　"


@pytest.fixture(scope="module")
def orig():
    return ROM.read_bytes()


@pytest.fixture(scope="module")
def recs(orig):
    return rom_text.unpack(orig)


@pytest.fixture(scope="module")
def script():
    return extract.load()


@needs_rom
def test_every_string_roundtrips(recs):
    t = rom_text.jp_table()
    bad = ["%X" % r.off for r in recs if t.encode(r.text) != r.raw]
    assert not bad


@needs_rom
def test_script_matches_rom(recs, script):
    assert list(script) == ["%06X" % r.off for r in recs]
    for r in recs:
        e = script["%06X" % r.off]
        assert (e["jp"], e["max"], e["ptrs"]) == (r.text, r.slot, ["%X" % p for p in r.ptrs]), e["id"]


@needs_rom
def test_block_is_covered(orig, recs, script):
    """Every non-zero byte of the block is a text record's text or inside a data record's span."""
    ends = [r.off for r in recs[1:]] + [rom_text.END]
    for r, nxt in zip(recs, ends):
        if script["%06X" % r.off]["status"] == "data":
            continue
        tail = orig[r.off + len(r.raw):nxt]
        assert not any(tail), "%X: non-zero bytes after a text record" % r.off


@needs_rom
def test_pointers_hit_record_starts_or_empty_strings(orig, recs):
    starts = {r.off for r in recs}
    refs = rom_text.pointers(orig)
    for t, srcs in refs.items():
        assert t in starts or orig[t] == 0, "%X <- %s: pointer into the middle of a string" % (t, srcs)
    for r in recs:  # an empty string in the padding stays outside what a longer text may fill
        assert not any(t in refs for t in range(r.off + len(r.raw) + 1, r.off + r.slot)), "%X" % r.off


@needs_rom
def test_text_is_never_marked_data_silently(recs, script):
    for r in recs:
        e = script["%06X" % r.off]
        assert e["status"] in extract.STATUS, e["id"]
        if e["status"] == "data":
            assert e["note"] and not e["en"], e["id"]
        elif extract.classify(r):
            pytest.fail("%s looks like data (%s) but is %s" % (e["id"], extract.classify(r), e["status"]))


def test_en_lint(script):
    t = rom_text.jp_table()
    errs = []
    for e in script.values():
        en, jp = e["en"], e["jp"]
        if not en or e["status"] == "data":
            continue
        try:
            t.encode(en)
        except ValueError as x:
            errs.append("%s: %s" % (e["id"], x))
        if PRINTF.findall(en) != PRINTF.findall(jp):
            errs.append("%s: printf specifiers differ" % e["id"])
        for strip in (str.lstrip, str.rstrip):
            if len(jp) - len(strip(jp, BLANK)) and len(en) == len(strip(en, BLANK)):
                errs.append("%s: en drops the jp's leading/trailing blank" % e["id"])
    assert not errs, "\n".join(errs[:50])


@needs_rom
def test_build_applies_en_through_the_pointers(orig, recs):
    import build
    r = next(r for r in recs if len(r.ptrs) and len(r.raw) >= 8 and "[" not in r.text)
    script = {"%06X" % r.off: {"en": "テスト", "status": "done"}}
    rom, writes = build.build(orig, script)
    (w,) = struct.unpack_from("<I", rom, r.ptrs[0])
    o = w - rom_text.GBA
    assert rom[o:rom.index(b"\0", o)] == "テスト".encode("cp932") and writes


@needs_rom
def test_redump_keeps_en(tmp_path, monkeypatch):
    monkeypatch.setattr(extract, "SCRIPT", tmp_path)
    extract.main()
    f = tmp_path / "02C000.json"
    entries = json.loads(f.read_text(encoding="utf-8"))
    entries[1].update(en="X", status="done", note="kept")
    extract.dump(entries, f)
    extract.main()
    assert json.loads(f.read_text(encoding="utf-8"))[1] == entries[1]
