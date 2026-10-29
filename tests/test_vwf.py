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


def run(rom, text, col=0, row=0, base=(0, 0), byteoff=0):
    """Runs one vwf_step; returns (result, ctx bytes 0x68-0x6B, text pointer - TEXT, canvas)."""
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_LR, UC_ARM_REG_SP
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    u.mem_map(0x08000000, (len(rom) + 0xFFFF) & ~0xFFFF)
    u.mem_write(0x08000000, rom)
    u.mem_map(0x02000000, 0x40000 * 4)
    u.mem_map(0x03000000, 0x8000)
    u.mem_write(TEXT, text + b"\0\0")
    u.mem_write(CTX + 0x68, bytes((base[0], base[1], col, row)))
    u.mem_write(CTX + 0x70, struct.pack("<I", TEXT))
    u.mem_write(0x03003D24, struct.pack("<I", CANVAS))
    u.reg_write(UC_ARM_REG_R0, CTX)
    u.reg_write(UC_ARM_REG_R1, byteoff)
    u.reg_write(UC_ARM_REG_SP, 0x03007F00)
    u.reg_write(UC_ARM_REG_LR, RET | 1)
    u.emu_start(0x08000000 + vwf.CODE | 1, RET, count=200000)
    ctx = bytes(u.mem_read(CTX + 0x68, 4))
    ptr = struct.unpack("<I", u.mem_read(CTX + 0x70, 4))[0] - TEXT
    return u.reg_read(UC_ARM_REG_R0), ctx, ptr, bytes(u.mem_read(CANVAS, 0x2000))


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
