"""vwf_step run in unicorn on the built ROM: glyphs land in the canvas where the font says, wrap, line break, pointer."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import vwf  # noqa: E402

ROM = ROOT / "rom" / "GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM")
CTX, TEXT, CANVAS, RET = 0x03000100, 0x03000400, 0x02000000, 0x02F00000


@pytest.fixture(scope="module")
def rom():
    import build
    return build.build(ROM.read_bytes(), {})[0]


def call(rom, entry, fields, ptr_at, text, byteoff=0, pitch=vwf.LINE_H, lift=vwf.Y_LIFT):
    """Runs one call of the VWF entry CODE + entry with r0 = CTX, r1-r3 = byteoff, pitch, lift; fields {ctx offset:
    byte}, the text pointer at ctx + ptr_at. Returns (r0, ctx bytes 0x00-0x7F, text pointer - TEXT, canvas)."""
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_LR, \
        UC_ARM_REG_SP
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    u.mem_map(0x08000000, (len(rom) + 0xFFFF) & ~0xFFFF)
    u.mem_write(0x08000000, rom)
    u.mem_map(0x02000000, 0x40000 * 4)
    u.mem_map(0x03000000, 0x8000)
    u.mem_write(TEXT, text + b"\0\0")
    for o, v in fields.items():
        u.mem_write(CTX + o, bytes((v,)))
    u.mem_write(CTX + ptr_at, struct.pack("<I", TEXT))
    u.mem_write(0x03003D24, struct.pack("<I", CANVAS))
    u.reg_write(UC_ARM_REG_R0, CTX)
    u.reg_write(UC_ARM_REG_R1, byteoff)
    u.reg_write(UC_ARM_REG_R2, pitch)
    u.reg_write(UC_ARM_REG_R3, lift)
    u.reg_write(UC_ARM_REG_SP, 0x03007F00)
    u.reg_write(UC_ARM_REG_LR, RET | 1)
    u.emu_start(0x08000000 + vwf.CODE + entry | 1, RET, count=200000)
    ctx = bytes(u.mem_read(CTX, 0x80))
    ptr = struct.unpack_from("<I", ctx, ptr_at)[0] - TEXT
    return u.reg_read(UC_ARM_REG_R0), ctx, ptr, bytes(u.mem_read(CANVAS, 0x2000))


def run(rom, text, col=0, row=0, base=(0, 0), byteoff=0):
    """One vwf_step (loops A/B); returns (result, ctx bytes 0x68-0x6B, text pointer - TEXT, canvas)."""
    r, ctx, ptr, canvas = call(rom, vwf.STEP_AT, {0x68: base[0], 0x69: base[1], 0x6A: col, 0x6B: row}, 0x70, text,
                               byteoff)
    return r, ctx[0x68:0x6C], ptr, canvas


def pixels(canvas, x0, y0, w, h):
    """Rows of '.'/'#' from the 32x8-tile 4bpp canvas."""
    out = []
    for y in range(y0, y0 + h):
        row = ""
        for x in range(x0, x0 + w):
            b = canvas[((y >> 3) * 32 + (x >> 3)) * 32 + (y & 7) * 4 + (x & 7) // 2]
            row += "#" if (b >> (4 * (x & 1))) & 15 else "."
        out.append(row)
    return out


@needs_rom
def test_letter_lands_at_col_with_font_rows(rom):
    r, ctx, ptr, canvas = run(rom, b"A", col=13, row=2, base=(1, 3))
    top, rows, adv = vwf.FONT["A"]
    y = 3 * 8 + 2 - vwf.Y_LIFT + top + vwf.ROW_OFF      # base y in tiles, row in px
    assert r == 1 and pixels(canvas, 8 + 13, y, 5, len(rows)) == rows
    assert "".join(pixels(canvas, 0, 0, 256, 64)).count("#") == "".join(rows).count("#")
    assert ctx[2] == 13 + adv - 1 and ptr == 1 - 2      # the game then adds 1 and 2


@needs_rom
def test_line_break_then_char_and_wrap(rom):
    r, ctx, ptr, _ = run(rom, "α".encode("cp932") + b"B")
    assert r == 1 and ctx[3] == vwf.LINE_H and ctx[2] == vwf.ADV["B"] - 1 and ptr == 2 + 1 - 2
    r, ctx, _, _ = run(rom, b"W", col=vwf.XMAX - 2)
    assert ctx[3] == vwf.LINE_H and ctx[2] == vwf.ADV["W"] - 1


@needs_rom
def test_sjis_char_and_end(rom):
    r, ctx, ptr, canvas = run(rom, "銀".encode("cp932"))
    assert r == 1 and ctx[2] == 11 and ptr == 0 and "#" in "".join(pixels(canvas, 0, 0, 12, 12))
    assert run(rom, b"")[0] == 0


@needs_rom
def test_help_line_glyph_break_and_end(rom):
    _, ctx, ptr, canvas = call(rom, vwf.C_AT, {0x64: 20, 0x65: 2, 0x35: 5}, 0x6C, b"A")
    top, rows, adv = vwf.FONT["A"]
    assert ctx[0x64] == 20 + adv and ptr == 1 and ctx[0x35] == 5
    assert pixels(canvas, 20, 16 + top + vwf.ROW_OFF, 5, len(rows)) == rows
    _, ctx, ptr, _ = call(rom, vwf.C_AT, {0x64: 20, 0x65: 0}, 0x6C, "α".encode("cp932") + b"A")
    assert ctx[0x64] == 0 and ctx[0x65] == 2 and ptr == 2 and ctx[0x30] == 8
    _, ctx, _, _ = call(rom, vwf.C_AT, {0x35: 5}, 0x6C, b"")
    assert ctx[0x35] == 6
    _, ctx, _, canvas = call(rom, vwf.C_AT, {0x64: vwf.CMAX - 2, 0x35: 5}, 0x6C, b"W")
    assert ctx[0x35] == 6 and not any(canvas)


@needs_rom
def test_nothing_branches_into_a_hook():
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    d = ROM.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    spans = [(s, s + len(new)) for s, _, new in vwf.hooks()]
    bad = []
    for s, e in spans:
        for a in range(max(0, s - 0x1000), s + 0x1000, 2):
            for i in md.disasm(d[a:a + 4], 0x08000000 + a, 1):
                if i.mnemonic.startswith("b") and i.op_str.startswith("#") and s < int(i.op_str[1:], 16) - 0x08000000 < e:
                    bad.append("%X %s %s" % (a, i.mnemonic, i.op_str))
    for o in range(0, 0x2DB00, 4):
        w = (struct.unpack_from("<I", d, o)[0] & ~1) - 0x08000000
        bad += ["word %X -> %X" % (o, w) for s, e in spans if s < w < e]
    assert not bad
