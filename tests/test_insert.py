"""Phase 7 checks on the English build: writes stay in the allowed ranges, every entry reads back through every
pointer, moved text leaves no reader behind, and no Japanese is left behind a pointer slot."""
import os
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rom_text  # noqa: E402

ROM = ROOT / "rom" / "GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba"
pytestmark = pytest.mark.skipif(not ROM.is_file(), reason="no ROM")
# words outside PTR_SRC that equal GBA | a moved record: graphics data, not readers (rom_text.PTR_SRC)
COINCIDENCES = range(0x350000, 0x3D0000)


@pytest.fixture(scope="module")
def built():
    import build
    import extract
    orig = ROM.read_bytes()
    script = extract.load()
    rom, writes = build.build(orig, script)
    return orig, rom, writes, script, rom_text.unpack(orig)


def test_writes_stay_in_allowed_ranges(built):
    import build
    _, _, writes, _, recs = built
    slots = {p for r in recs for p in r.ptrs}
    assert not build.outside(writes, slots)
    stray = [(0x100, b"\0" * 4, b"\1" * 4, "header"), (min(slots), b"\0" * 8, b"\1" * 8, "past a pointer word")]
    assert len(build.outside(stray, slots)) == 2                      # the gate itself works


def test_every_entry_reads_back_through_every_pointer(built):
    import vwf
    _, rom, _, script, recs = built
    t, bad, n = vwf.en_table(), [], 0
    for r in recs:
        e = script["%06X" % r.off]
        if e["status"] == "data" or not e["en"]:
            continue
        want = t.encode(e["en"]) + b"\0"
        at = [struct.unpack_from("<I", rom, p)[0] - rom_text.GBA for p in r.ptrs] or [r.off]
        bad += ["%s via %X" % (e["id"], o) for o in at if rom[o:o + len(want)] != want]
        n += 1
    assert n == sum(1 for e in script.values() if e["status"] != "data" and e["en"])
    assert not bad, bad[:20]


def test_moved_text_leaves_no_reader_behind(built):
    orig, rom, _, _, recs = built
    moved = {r.off: r for r in recs if r.ptrs and struct.unpack_from("<I", rom, r.ptrs[0])[0] - rom_text.GBA >= rom_text.ROM_END}
    assert moved
    stale = []
    for i, (w,) in enumerate(struct.iter_unpack("<I", orig[:len(orig) & ~3])):
        r = moved.get(w - rom_text.GBA)
        if r and i * 4 not in r.ptrs and i * 4 not in COINCIDENCES:
            stale.append("%X -> %X" % (i * 4, r.off))
    assert not stale, stale[:20]


@pytest.mark.skipif(not os.path.isfile(os.path.expanduser(
    "~/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game/SKILL.md"))
    and not os.environ.get("TRANSLATE_SKILL"), reason="no skill (jp_left.py)")
def test_no_japanese_behind_a_pointer_slot(built, tmp_path):
    from skill import SCRIPTS
    _, rom, _, _, recs = built
    out = tmp_path / "en.gba"
    out.write_bytes(rom)
    slots = tmp_path / "slots.txt"
    slots.write_text("".join("%06X\n" % p for p in sorted({p for r in recs for p in r.ptrs} | {0x22B90})))
    p = subprocess.run([sys.executable, "-X", "utf8", os.path.join(SCRIPTS, "jp_left.py"), str(out), "--sjis",
                        "--slots", str(slots), "--known", str(ROOT / "tools" / "jp_known.txt")],
                       capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stdout[-2000:]
