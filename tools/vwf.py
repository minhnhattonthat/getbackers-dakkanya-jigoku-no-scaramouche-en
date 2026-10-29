"""vwf.py: English variable-width font for the 12x12 text path (docs/re/text.md §VWF).

Both text loops (state 8 of 0x0801A358 and of the dialogue function at 0x0801A724) call 0x08019EF4, which draws one
12 px Shift-JIS cell. The hooks replace that step with `vwf_step` (Thumb, at CODE): one byte < 0x80 or 0xA0-0xDF is an
English glyph from fonts/font_en.txt ORed into the canvas at any pixel x; a Shift-JIS char still draws as a 12 px glyph;
`α` 0x83BF stays the line break. The col byte ctx+0x6A holds pixels instead of cells.

    python -X utf8 tools/vwf.py      (self-test: assembles, checks every instruction is 16-bit Thumb)"""
import struct
from pathlib import Path

from tbl import Table
import rom_text

ROOT = Path(__file__).resolve().parents[1]
CODE = 0x400000                 # past the original ROM end; relocated text follows
XMAX = 224                      # wrap when a glyph would end past this pixel (canvas x); the ▼ prompt starts at x 227
ROW_OFF = 1                     # font_en rows 0-10 -> glyph rows 1-11
LINE_H = 11                     # line pitch in px: ctx+0x6B counts pixels (the game's own pitch was 16)
Y_LIFT = 1                      # px above the game's first line (clamped at canvas y 0); the dialogue box shows canvas
                                # y 8-41 only (tile row 0 is not on the map): 3 lines x 11 px, ink rows 9-40
EXTRA = {'—': 0xA0, '…': 0xA1}   # bytes 0xA0-0xDF are never a Shift-JIS lead: free for extra glyphs
NCODES = 0xE0
# (site, original bytes, ctx byte-offset source, end-of-text target, drew-a-char target)
SITES = ((0x1A3E6, '206f81460188', 'ldr r1, [r4, #0x74]', 0x1A48C, 0x1A466),
         (0x1A724, '206f81460188', 'movs r1, #0', 0x1A7C8, 0x1A7A4))


def load_font():
    """char -> (top row, art rows of '.'/'#', advance)."""
    font, cur = {}, None
    for line in (ROOT / 'fonts' / 'font_en.txt').read_text(encoding='utf-8').splitlines():
        if line.startswith('== '):
            p = line[3:].split()
            ch = chr(int(p[0][2:], 16)) if p[0].startswith('U+') else p[0]
            adv = int(p[2][4:]) if len(p) > 2 else None
            cur = font[ch] = [int(p[1]), [], adv]
        elif cur is not None and line and set(line) <= set('.#'):
            cur[1].append(line)
    return {c: (top, rows, adv if adv is not None else max(map(len, rows)) + 1) for c, (top, rows, adv) in font.items()}


FONT = load_font()
CODES = {c: EXTRA.get(c, ord(c)) for c in FONT}
ADV = {c: a for c, (_, _, a) in FONT.items()}


def en_table():
    """English bytes first (so '…' and '—' take the 1-byte glyphs), then the whole jp table."""
    lines = ['%02X=%s' % (b, '\\s' if c == ' ' else c) for c, b in sorted(CODES.items(), key=lambda x: x[1])]
    return Table(lines + rom_text.jp_table_lines())


def width(s):
    """Pixel advance of one line of English (Shift-JIS chars count 12)."""
    return sum(ADV.get(c, 12) for c in s)


def font_data():
    """NCODES x 24 bytes (12 rows, u16 big-endian, MSB = left pixel) + NCODES advance bytes."""
    glyphs, adv = bytearray(NCODES * 24), bytearray(NCODES)
    for c, (top, rows, a) in FONT.items():
        b = CODES[c]
        adv[b] = a
        for i, r in enumerate(rows):
            y = top + i + ROW_OFF
            assert y < 12 and len(r) <= 16, c
            struct.pack_into('>H', glyphs, b * 24 + y * 2, int(r.replace('.', '0').replace('#', '1').ljust(16, '0'), 2))
    return bytes(glyphs + adv)


STEP = """
@ vwf_step(r0 = text ctx, r1 = canvas byte offset) -> r0 = 0 (end of text) / 1 (drew one glyph)
vwf_step:
  push {r4-r7, lr}
  mov r4, r8
  mov r5, r9
  mov r6, r10
  mov r7, r11
  push {r4-r7}
  mov r4, r0
  mov r8, r1
next:
  ldr r5, [r4, #0x70]
  ldrb r0, [r5]
  cmp r0, #0
  beq ret_end
  cmp r0, #0x83
  bne not_br
  ldrb r1, [r5, #1]
  cmp r1, #0xBF
  bne sjis
  bl newline
  adds r5, #2
  str r5, [r4, #0x70]
  b next
not_br:
  cmp r0, #0x80
  blo en
  cmp r0, #0xA0
  blo sjis
  cmp r0, #0xE0
  bhs sjis
en:
  ldr r1, lit_adv
  ldrb r6, [r1, r0]
  movs r1, #24
  muls r0, r1
  ldr r1, lit_font
  adds r0, r0, r1
  movs r3, #1
  mov r9, r3
  b draw
sjis:
  mov r0, r5
  ldr r3, lit_lookup
  bl call_r3
  cmp r0, #0
  beq ret_end
  movs r6, #12
  movs r3, #2
  mov r9, r3
draw:
  mov r10, r0
  mov r3, r4
  adds r3, #0x68
  ldrb r0, [r3, #0]
  lsls r0, r0, #3
  ldrb r1, [r3, #2]
  adds r0, r0, r1
  adds r1, r0, r6
  cmp r1, #XMAX
  ble nowrap
  bl newline
  ldrb r0, [r3, #0]
  lsls r0, r0, #3
nowrap:
  mov r11, r0
  ldrb r1, [r3, #1]
  lsls r1, r1, #3
  ldrb r2, [r3, #3]
  adds r1, r1, r2
  subs r1, #Y_LIFT
  bpl lifted
  movs r1, #0
lifted:
  @ the game adds 1 to the col and 2 to the text pointer after the char's wait
  ldrb r2, [r3, #2]
  adds r2, r2, r6
  subs r2, #1
  strb r2, [r3, #2]
  add r5, r9
  subs r5, #2
  str r5, [r4, #0x70]
  ldr r2, lit_canvas
  ldr r2, [r2]
  add r2, r8
  mov r12, r2
  movs r5, r1
  adds r1, #12
  mov r9, r1
rowloop:
  mov r0, r10
  ldrb r6, [r0]
  ldrb r1, [r0, #1]
  adds r0, #2
  mov r10, r0
  lsls r6, r6, #24
  lsls r1, r1, #16
  orrs r6, r1
  beq rownext
  lsrs r1, r5, #3
  lsls r1, r1, #10
  mov r3, r12
  adds r3, r3, r1
  movs r1, #7
  ands r1, r5
  lsls r1, r1, #2
  adds r3, r3, r1
  mov r0, r11
pixloop:
  lsls r6, r6, #1
  bcc nopix
  lsrs r1, r0, #3
  lsls r1, r1, #5
  adds r1, r1, r3
  movs r7, #7
  ands r7, r0
  lsrs r7, r7, #1
  adds r1, r1, r7
  ldrb r7, [r1]
  movs r2, #1
  ands r2, r0
  lsls r2, r2, #4
  bne hinib
  movs r2, #1
hinib:
  orrs r7, r2
  strb r7, [r1]
nopix:
  adds r0, #1
  cmp r6, #0
  bne pixloop
rownext:
  adds r5, #1
  cmp r5, r9
  blo rowloop
  movs r0, #1
  b ret
ret_end:
  movs r0, #0
ret:
  pop {r4-r7}
  mov r8, r4
  mov r9, r5
  mov r10, r6
  mov r11, r7
  pop {r4-r7}
  pop {r1}
  bx r1
newline:
  mov r3, r4
  adds r3, #0x68
  movs r0, #0
  strb r0, [r3, #2]
  ldrb r0, [r3, #3]
  adds r0, #LINE_H
  strb r0, [r3, #3]
  bx lr
call_r3:
  bx r3
.align 2
lit_adv: .word ADV
lit_font: .word FONT
lit_lookup: .word 0x0801A1AD
lit_canvas: .word 0x03003D24
"""

HOOK = """
  adds r0, r4, #0
  {arg}
  ldr r2, lit
  bl stub
  cmp r0, #0
  beq {end:#x}
  b {drew:#x}
stub:
  bx r2
.align 2
lit: .word {fn:#x}
"""


def asm(src, addr):
    """Thumb source -> bytes; the trailing `.word` lines are data and skip the encoding check."""
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    code = bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, addr)[0])
    end = len(code) - 4 * src.count('.word')
    # keystone picks Thumb-2 encodings the GBA (ARMv4T) can't run: only BL may be 4 bytes
    n = 0
    for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(code[:end], addr):
        assert i.size == 2 or i.mnemonic == 'bl', '%X: %s %s' % (i.address, i.mnemonic, i.op_str)
        n += i.size
    assert n == end, 'undecodable bytes at %X' % (addr + n)
    return code


def build_code():
    """(bytes at CODE, address of vwf_step)."""
    data = font_data()
    fnt = 0x08000000 + CODE + 0x400
    src = STEP.replace('XMAX', str(XMAX)).replace('LINE_H', str(LINE_H)).replace('Y_LIFT', str(Y_LIFT)).replace('lit_adv: .word ADV', 'lit_adv: .word %#x' % (fnt + NCODES * 24))
    code = asm(src.replace('lit_font: .word FONT', 'lit_font: .word %#x' % fnt), 0x08000000 + CODE)
    assert len(code) <= 0x400 and code.endswith(struct.pack('<II', 0x0801A1AD, 0x03003D24))
    return code.ljust(0x400, b'\0') + data


def apply(rom, writes):
    """Writes the VWF code + font at CODE and the two hooks into rom (a bytearray of the original), logging to writes."""
    assert len(rom) == CODE, 'VWF goes first, before any relocated text'
    rom_text._write(rom, writes, CODE, build_code(), 'vwf code+font')
    for site, old, arg, end, drew in SITES:
        assert rom[site:site + 6].hex() == old, '%X: unexpected bytes' % site
        hook = asm(HOOK.format(arg=arg, end=0x08000000 + end, drew=0x08000000 + drew, fn=0x08000000 + CODE + 1),
                   0x08000000 + site)
        rom_text._write(rom, writes, site, hook, 'vwf hook %X' % site)


if __name__ == '__main__':
    c = build_code()
    print('vwf: %d bytes code+font, %d glyphs' % (len(c), len(FONT)))
    for site, _, arg, end, drew in SITES:
        print('%X hook %s' % (site, asm(HOOK.format(arg=arg, end=0x08000000 + end, drew=0x08000000 + drew,
                                                  fn=0x08000000 + CODE + 1), 0x08000000 + site).hex()))
