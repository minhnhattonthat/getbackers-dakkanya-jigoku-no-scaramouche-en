"""vwf.py: English variable-width font for the 12x12 text path (docs/re/text.md §VWF).

The three callers of 0x08019EF4 (one 12 px Shift-JIS cell) are replaced: the text loops A (0x0801A358) and B
(dialogue, 0x0801A724) call `vwf_step`, the help line C (0x08002188) calls `vwf_c` (Thumb, at CODE). One byte < 0x80 or
0xA0-0xDF is an English glyph from fonts/font_en.txt ORed into the canvas at any pixel x; a Shift-JIS char still draws
as a 12 px glyph; `α` 0x83BF stays the line break. The col bytes (A/B ctx+0x6A, C ctx+0x64) hold pixels.

    python -X utf8 tools/vwf.py      (self-test: assembles, checks every instruction is 16-bit Thumb)"""
import struct
from pathlib import Path

from tbl import Table
import rom_text

ROOT = Path(__file__).resolve().parents[1]
CODE = 0x400000                 # past the original ROM end; relocated text follows
XMAX = 224                      # A/B: wrap when a glyph would end past this canvas x; the ▼ prompt starts at x 227
CMAX = 232                      # C: the help line stops drawing past this canvas x (screen 240)
ROW_OFF = 1                     # font_en rows 0-10 -> glyph rows 1-11
LINE_H = 11                     # A/B line pitch in px: ctx+0x6B counts pixels (the game's own pitch was 16)
Y_LIFT = 2                      # px above the game's first line (clamped at canvas y 0); the dialogue box shows canvas
                                # y 8-39 only (tile row 0 is not on the map, the screen ends below 39): 3 lines x 11
                                # px = font rows 0-10 at y 7-39, so font row 0 (no glyph uses it) is hidden on line 1
EXTRA = {'—': 0xA0, '…': 0xA1}   # bytes 0xA0-0xDF are never a Shift-JIS lead: free for extra glyphs
NCODES = 0xE0
STEP_AT, C_AT = 0, 4            # entry points (CODE + n): branches to vwf_step / vwf_c
# loops A and B: (site, original bytes, ctx byte-offset source, end-of-text target, drew-a-char target, pitch, lift)
# A draws the field box (canvas offset 0: 3 lines like B) and the yes/no window (offset 0x1000: keeps the JP 16 px
# pitch, the choice cursor steps 16 px); pitch/lift here are for offset 0
SITES = ((0x1A3E6, '206f81460188', 'ldr r1, [r4, #0x74]', 0x1A48C, 0x1A466, LINE_H, Y_LIFT),
         (0x1A724, '206f81460188', 'movs r1, #0', 0x1A7C8, 0x1A7A4, LINE_H, Y_LIFT))
CHOICE_PITCH = 16
C_SITE, C_OLD, C_RET = 0x2208, '1648261c6436337818180078271c6537', 0x229C


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
  b vwf_step
  movs r0, r0
  b vwf_c
  movs r0, r0

@ vwf_step(r0 = text ctx, r1 = canvas byte offset, r2 = line pitch px, r3 = lift px) -> r0 = 0 (end of text) /
@ 1 (drew one glyph). Loops A and B.
vwf_step:
  push {r4-r7, lr}
  mov r4, r8
  mov r5, r9
  push {r4, r5}
  mov r4, r0
  mov r7, r1
  mov r8, r2
  mov r9, r3
next:
  ldr r5, [r4, #0x70]
  ldrb r0, [r5]
  cmp r0, #0
  beq s_end
  cmp r0, #0x83
  bne s_char
  ldrb r1, [r5, #1]
  cmp r1, #0xBF
  bne s_char
  bl newline
  adds r5, #2
  str r5, [r4, #0x70]
  b next
s_char:
  movs r0, r5
  bl glyph
  cmp r0, #0
  beq s_end
  movs r6, r1
  @ the game adds 2 to the pointer and 1 to the col after the char's wait
  adds r5, r5, r2
  subs r5, #2
  str r5, [r4, #0x70]
  mov r3, r4
  adds r3, #0x68
  ldrb r1, [r3, #0]
  lsls r1, r1, #3
  ldrb r2, [r3, #2]
  adds r1, r1, r2
  adds r2, r1, r6
  cmp r2, #XMAX
  ble s_nowrap
  push {r0}
  bl newline
  pop {r0}
  ldrb r1, [r3, #0]
  lsls r1, r1, #3
s_nowrap:
  ldrb r2, [r3, #2]
  adds r2, r2, r6
  subs r2, #1
  strb r2, [r3, #2]
  ldrb r2, [r3, #1]
  lsls r2, r2, #3
  ldrb r6, [r3, #3]
  adds r2, r2, r6
  mov r6, r9
  subs r2, r2, r6
  bpl s_lifted
  movs r2, #0
s_lifted:
  movs r3, r7
  bl plot
  movs r0, #1
  b s_ret
s_end:
  movs r0, #0
s_ret:
  pop {r4, r5}
  mov r8, r4
  mov r9, r5
  pop {r4-r7}
  pop {r1}
  bx r1

@ newline (r4 = ctx, r8 = pitch): col 0, row + pitch; leaves r3 = ctx + 0x68
newline:
  mov r3, r4
  adds r3, #0x68
  movs r0, #0
  strb r0, [r3, #2]
  ldrb r0, [r3, #3]
  add r0, r8
  strb r0, [r3, #3]
  bx lr

@ vwf_c(r0 = help task): one glyph per call at col +0x64 (px), y tile +0x65, pointer +0x6C; end -> state +0x35 + 1
vwf_c:
  push {r4-r7, lr}
  mov r4, r0
  ldr r5, [r4, #0x6C]
  ldrb r0, [r5]
  cmp r0, #0
  beq c_end
  cmp r0, #0x83
  bne c_char
  ldrb r1, [r5, #1]
  cmp r1, #0xBF
  bne c_char
  @ line break as the game does it (0x0800224C): y + 2 tiles, col 0, pause 8 frames
  mov r3, r4
  adds r3, #0x64
  movs r0, #0
  strb r0, [r3, #0]
  ldrb r0, [r3, #1]
  adds r0, #2
  strb r0, [r3, #1]
  adds r5, #2
  str r5, [r4, #0x6C]
  movs r0, #8
  str r0, [r4, #0x30]
  b c_ret
c_char:
  movs r0, r5
  bl glyph
  cmp r0, #0
  beq c_end
  adds r5, r5, r2
  str r5, [r4, #0x6C]
  mov r3, r4
  adds r3, #0x64
  ldrb r6, [r3, #0]
  adds r2, r6, r1
  cmp r2, #CMAX
  bhi c_end
  strb r2, [r3, #0]
  movs r1, r6
  ldrb r2, [r3, #1]
  lsls r2, r2, #3
  movs r3, #0
  bl plot
  ldr r0, lit_flags
  ldrb r1, [r0, #0x1A]
  movs r2, #0x80
  orrs r1, r2
  strb r1, [r0, #0x1A]
  b c_ret
c_end:
  mov r0, r4
  adds r0, #0x35
  ldrb r1, [r0]
  adds r1, #1
  strb r1, [r0]
c_ret:
  pop {r4-r7}
  pop {r0}
  bx r0

@ glyph(r0 = char pointer) -> r0 = 12 rows (u16 big-endian) or 0 (no glyph), r1 = advance px, r2 = bytes used
glyph:
  push {lr}
  ldrb r1, [r0]
  cmp r1, #0x80
  blo g_en
  cmp r1, #0xA0
  blo g_sjis
  cmp r1, #0xE0
  bhs g_sjis
g_en:
  ldr r2, lit_adv
  ldrb r2, [r2, r1]
  movs r0, #24
  muls r0, r1
  ldr r3, lit_font
  adds r0, r0, r3
  movs r1, r2
  movs r2, #1
  pop {r3}
  bx r3
g_sjis:
  ldr r3, lit_lookup
  bl call_r3
  movs r1, #12
  movs r2, #2
  pop {r3}
  bx r3

@ plot(r0 = rows, r1 = x px, r2 = y px, r3 = canvas byte offset): ORs colour 1 into the 32x8-tile 4bpp canvas
plot:
  push {r4-r7, lr}
  mov r4, r8
  mov r5, r9
  mov r6, r10
  mov r7, r11
  push {r4-r7}
  mov r10, r0
  mov r11, r1
  ldr r4, lit_canvas
  ldr r4, [r4]
  adds r4, r4, r3
  mov r12, r4
  movs r5, r2
  adds r2, #12
  mov r9, r2
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
  pop {r4-r7}
  mov r8, r4
  mov r9, r5
  mov r10, r6
  mov r11, r7
  pop {r4-r7}
  pop {r0}
  bx r0
call_r3:
  bx r3
.align 2
lit_adv: .word ADV
lit_font: .word FONT
lit_lookup: .word 0x0801A1AD
lit_canvas: .word 0x03003D24
lit_flags: .word 0x03002BA0
"""

HOOK = """
  adds r0, r4, #0
  {arg}
  ldr r3, lit
  mov ip, r3
  movs r2, #{pitch}
  movs r3, #{lift}
  cmp r1, #0
  beq go
  movs r2, #{choice}
  movs r3, #0
go:
  bl stub
  cmp r0, #0
  beq {end:#x}
  b {drew:#x}
stub:
  bx ip
.align 2
lit: .word {fn:#x}
"""

HOOK_C = """
  adds r0, r4, #0
  ldr r2, lit
  bl stub
  b {ret:#x}
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
    """Bytes at CODE: the code (entry points STEP_AT, C_AT), then the font at CODE + 0x400."""
    fnt = 0x08000000 + CODE + 0x400
    src = STEP
    for k, v in (('XMAX', XMAX), ('CMAX', CMAX),
                 ('.word ADV', '.word %#x' % (fnt + NCODES * 24)), ('.word FONT', '.word %#x' % fnt)):
        src = src.replace(k, str(v))
    code = asm(src, 0x08000000 + CODE)
    assert len(code) <= 0x400 and code.endswith(struct.pack('<III', 0x0801A1AD, 0x03003D24, 0x03002BA0))
    return code.ljust(0x400, b'\0') + font_data()


def hooks():
    """[(site, original bytes, hook bytes)] for loops A, B and the help line C."""
    fn = 0x08000000 + CODE + 1
    out = [(site, bytes.fromhex(old), asm(HOOK.format(arg=arg, end=0x08000000 + end, drew=0x08000000 + drew,
                                                       fn=fn + STEP_AT, pitch=pitch, lift=lift, choice=CHOICE_PITCH),
                                          0x08000000 + site))
           for site, old, arg, end, drew, pitch, lift in SITES]
    out.append((C_SITE, bytes.fromhex(C_OLD), asm(HOOK_C.format(ret=0x08000000 + C_RET, fn=fn + C_AT),
                                                    0x08000000 + C_SITE)))
    assert len(out[-1][2]) <= len(C_OLD) // 2, 'help-line hook longer than the checked bytes'
    return out


def apply(rom, writes):
    """Writes the VWF code + font at CODE and the hooks into rom (a bytearray of the original), logging to writes."""
    assert len(rom) == CODE, 'VWF goes first, before any relocated text'
    rom_text._write(rom, writes, CODE, build_code(), 'vwf code+font')
    for site, old, new in hooks():
        assert rom[site:site + len(old)] == old, '%X: unexpected bytes' % site
        rom_text._write(rom, writes, site, new, 'vwf hook %X' % site)


if __name__ == '__main__':
    print('vwf: %d bytes code+font, %d glyphs' % (len(build_code()), len(FONT)))
    for site, _, new in hooks():
        print('%X hook %s' % (site, new.hex()))
