import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM")


@needs_rom
def test_identity_build_is_byte_identical():
    import build
    orig = ROM.read_bytes()
    rom, writes = build.build(orig)
    assert writes == [] and rom == orig


@needs_rom
def test_relocated_strings_read_back_through_their_pointers():
    import rom_text
    orig = ROM.read_bytes()
    recs = rom_text.unpack(orig)
    moved = [r for r in recs if r.ptrs][::50]
    rom = bytearray(orig)
    rom_text.repack(rom, recs, {}, relocate={r.off for r in moved})
    assert len(rom) > rom_text.ROM_END
    for r in moved:
        for p in r.ptrs:
            (w,) = struct.unpack_from("<I", rom, p)
            assert w - rom_text.GBA >= rom_text.ROM_END
            o = w - rom_text.GBA
            assert bytes(rom[o:rom.index(b"\0", o)]) == r.raw, hex(r.off)


@needs_rom
def test_longer_text_moves_and_shorter_stays():
    import rom_text
    orig = ROM.read_bytes()
    recs = rom_text.unpack(orig)
    a, b = [r for r in recs if r.ptrs and len(r.raw) >= 8 and not set("[%{") & set(r.text)][:2]
    rom = bytearray(orig)
    rom_text.repack(rom, recs, {a.off: a.text * 3, b.off: b.text[:2]})
    assert struct.unpack_from("<I", rom, a.ptrs[0])[0] == rom_text.GBA + rom_text.ROM_END
    assert rom[b.off:b.off + len(b.raw) + 1] == b.raw[:4] + bytes(len(b.raw) - 3)


def test_jp_table_roundtrips_text_and_unknown_bytes():
    import rom_text
    t = rom_text.jp_table()
    raw = "蛮「%sおい、銀次！」α".encode("cp932") + b"\x02\x20"
    text, n = t.decode(raw, 0, len(raw))
    assert n == len(raw) and text == "蛮「%sおい、銀次！」{br}[02][20]" and t.encode(text) == raw
