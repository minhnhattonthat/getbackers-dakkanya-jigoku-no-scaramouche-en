"""cards.py: the full-screen picture cards (docs/re/graphics.md): staff credits, end cards, act cards.

Card tables of (tiles LZ77 4bpp, map LZ77 32x20 u16, palette 16 x BGR555 raw) ROM pointers: 0x6A888 x 19
(0-16 staff credits, 17-18 end cards; then a 0 word), 0x6A970 x 7 (cards 19-25: ACT.1-6 + the final act).
    python -X utf8 tools/cards.py render OUTDIR [en]      every card as OUTDIR/card_NN.png (+ sheet.png); en: redrawn"""
import struct
import sys
from pathlib import Path

from PIL import Image

import extract
import letter
import lzcomp
import lzscan
import rom_text

ROM = Path(__file__).resolve().parents[1] / 'rom' / 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'
COUNT = 26
W, H = 32, 20                   # map tiles
STYLE = {'role': (1, 1, 0, 0), 'name': (1, 1, 1, 0), 'head': (1, 2, 1, 1), 'title': (2, 2, 1, 1)}  # sx, sy, bold, track
# card: [(cell top y, style, text)]. Names: D2 (official romanisation); staff readings not confirmed are in
# docs/re/graphics.md. The act cards keep their ACT label (rows above KEEP).
EN = {
    0: [(70, 'head', 'STAFF')],
    1: [(30, 'role', 'Original Story'), (42, 'name', 'Yuya Aoki'), (64, 'role', 'Manga'), (76, 'name', 'Rando Ayamine'),
        (102, 'role', 'Based on "GetBackers", serialized in'), (114, 'role', "Kodansha's Weekly Shonen Magazine")],
    2: [(40, 'role', 'Supervision'), (52, 'name', 'Yuya Aoki'), (76, 'role', 'Cooperation'),
        (88, 'name', 'Weekly Shonen Magazine'), (100, 'name', 'Editorial Department')],
    3: [(34, 'role', 'Executive Producers'), (64, 'name', 'Motoyuki Yoshioka'), (96, 'name', 'Satoshi Shimomura')],
    4: [(16, 'role', 'Producer'), (30, 'name', 'Takashi Shimomichi'), (96, 'role', 'Assistant Producer'),
        (110, 'name', 'Hirotaka Reizei')],
    5: [(34, 'role', 'Director'), (48, 'name', 'Kazuo Taniguchi'), (90, 'role', 'Scenario'), (104, 'name', 'Cool Izumi')],
    6: [(39, 'role', 'Mission Mode Program'), (53, 'name', 'Kazuo Taniguchi'), (94, 'role', 'Mission Mode Design'),
        (108, 'name', 'Kazunobu Uchida')],
    7: [(38, 'role', 'Battle Mode Program'), (52, 'name', 'Norihide Sugimoto'), (93, 'role', 'Battle Mode Design'),
        (107, 'name', 'Taketoshi Inagaki')],
    8: [(48, 'role', 'Field Design'), (63, 'name', 'Mikiko Sugiura'), (78, 'name', 'Takashi Nishimura')],
    9: [(6, 'role', 'Map Mode Design'), (21, 'name', 'Eisuke Matsuda'), (62, 'role', 'Character Design Assistance'),
        (77, 'name', 'Yasunori Kobayashi'), (118, 'role', 'Program Assistance'), (133, 'name', 'Tsutomu Watanabe')],
    10: [(24, 'role', 'Music'), (39, 'name', 'Naoko Ishii'), (54, 'name', 'Hiroshi "Nabeyan" Tanabe'),
         (96, 'role', 'Sound Effects'), (113, 'name', 'ARY')],
    11: [(32, 'role', 'Product Design'), (47, 'name', 'Kenko Suzuki'), (84, 'role', 'Package Art'),
         (99, 'name', 'Rando Ayamine')],
    12: [(33, 'role', 'Debugging'), (48, 'name', 'Roppongi Monitoring Center'), (89, 'role', 'Promotion'),
         (104, 'name', 'Ikunako Nakahara')],
    13: [(23, 'role', 'Special Thanks'), (43, 'role', 'Konami'), (61, 'name', 'Kazumi Kitakami'),
         (92, 'name', 'Masato Sakai'), (108, 'name', 'Hideki Hayakawa')],
    14: [(20, 'role', 'Special Thanks'), (55, 'role', 'Konami Marketing'), (73, 'name', 'Noboru Sakagami'),
         (92, 'name', 'Ikunako Nakahara')],
    15: [(24, 'role', 'Development'), (44, 'name', 'Konami Computer Entertainment'), (57, 'name', 'Japan East'),
         (94, 'role', 'Produced by'), (111, 'name', 'Konami Co., Ltd.')],
    16: [(63, 'name', '(C) 2001 Yuya Aoki / Rando Ayamine / Kodansha'), (82, 'name', '(C) 2001 KONAMI')],
    17: [(112, 'title', 'The End')],
    18: [(68, 'head', 'Enjoy your dream?')],
    19: [(84, 'title', 'Enter the GetBackers!')],
    20: [(72, 'head', 'Paranormal Hospital'), (96, 'title', 'Den of Demons!!')],
    21: [(72, 'head', 'Omen of a Great Evil'), (96, 'head', "Take Back a Girl's Hope!")],
    22: [(70, 'title', 'Ferocious!'), (98, 'head', 'Smash-and-Chase in the Tech Tower!')],
    23: [(72, 'head', 'Ura-Shinjuku Station Dash!'), (100, 'head', 'Be Still, My Friend....')],
    24: [(72, 'head', 'Into the Terrifying Ura-Tocho!'), (100, 'head', "Expose Scaramouche's Ambition!")],
    25: [(72, 'head', 'Ura-Tocho: The Last Battle'), (96, 'title', 'Into the Unknown!')],
}
KEEP = 60                       # act cards: rows above stay (the ACT.N label is English already)


def slot(i):
    """ROM offset of card i's 3 pointers."""
    return 0x6A888 + 12 * i if i < 19 else 0x6A970 + 12 * (i - 19)


def entry(rom, i):
    """(tiles ROM offset, map ROM offset, palette ROM offset)."""
    return tuple(p - 0x08000000 for p in struct.unpack_from('<3I', rom, slot(i)))


def palette(rom, off, n=16):
    return [((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31)
            for c in struct.unpack_from('<%dH' % n, rom, off)]


def load(rom, i):
    t, m, p = entry(rom, i)
    tiles = lzscan.lz77(rom, t)[0]
    mp = list(struct.unpack('<%dH' % (W * H), lzscan.lz77(rom, m)[0]))
    return tiles, mp, palette(rom, p)


def tile_px(tiles, n, bpp=4):
    """8x8 colour indices of tile n."""
    if bpp == 8:
        return [list(tiles[64 * n + 8 * y:64 * n + 8 * y + 8]) for y in range(8)]
    b = tiles[32 * n:32 * n + 32]
    return [[(b[y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]


def to_pixels(tiles, mp, bpp=4):
    """256x160 rows of colour indices (map flips applied; palette bank must be 0)."""
    px = [[0] * (W * 8) for _ in range(H * 8)]
    for k, e in enumerate(mp):
        assert e >> 12 == 0, 'palette bank %d' % (e >> 12)
        t = tile_px(tiles, e & 0x3FF, bpp)
        for y in range(8):
            for x in range(8):
                px[k // W * 8 + y][k % W * 8 + x] = t[7 - y if e & 0x800 else y][7 - x if e & 0x400 else x]
    return px


def from_pixels(px, bpp=4, first=None):
    """(tiles, map) for 256x160 indices: tile 0 = first (default blank), duplicates (also flipped ones) shared."""
    first = first or bytes(64)
    seen, tiles, mp = {first: 0}, bytearray(first if bpp == 8 else
                                            bytes(first[i] | first[i + 1] << 4 for i in range(0, 64, 2))), []
    for k in range(W * H):
        rows = [px[k // W * 8 + y][k % W * 8:k % W * 8 + 8] for y in range(8)]
        e = None
        for flip, rr in ((0, rows), (0x400, [r[::-1] for r in rows]), (0x800, rows[::-1]),
                         (0xC00, [r[::-1] for r in rows[::-1]])):
            key = bytes(v for r in rr for v in r)
            if key in seen:
                e = seen[key] | flip
                break
        if e is None:
            n = len(tiles) // (8 * bpp)
            assert n < 1024, 'too many tiles'
            seen[bytes(v for r in rows for v in r)] = n
            tiles += bytes(v for r in rows for v in r) if bpp == 8 else \
                bytes(r[x] | r[x + 1] << 4 for r in rows for x in range(0, 8, 2))
            e = n
        mp.append(e)
    return bytes(tiles), mp


def image(px, pal, zoom=1):
    im = Image.new('RGB', (len(px[0]), len(px)))
    im.putdata([pal[v] for r in px for v in r])
    return im.resize((im.width * zoom, im.height * zoom), Image.NEAREST) if zoom > 1 else im


def pack(tiles, mp):
    """LZ77 blocks for the ROM: (tiles, map)."""
    return lzcomp.compress(tiles), lzcomp.compress(struct.pack('<%dH' % len(mp), *mp))


def english(rom, i):
    """Card i as 256x160 colour indices with its English lines (on-screen width 240)."""
    tiles, mp, pal = load(rom, i)
    px = to_pixels(tiles, mp)
    bg = max(range(16), key=lambda c: sum(r[:240].count(c) for r in px))
    ink = min(range(16), key=lambda c: abs(sum(pal[c]) - (765 if sum(pal[bg]) < 383 else 0)))
    for y in range(KEEP if i >= 19 else 0, H * 8):
        px[y][:240] = [bg] * 240
    for y, style, text in EN[i]:
        letter.draw(px, text, 120, y, ink, *STYLE[style])
    return px


def apply(rom, writes):
    """Redraw every card in EN: new tiles + map past the ROM end, the card table repointed. rom: bytearray."""
    for i in sorted(EN):
        for k, data in enumerate(pack(*from_pixels(english(rom, i)))):
            off = (len(rom) + 3) & ~3
            rom_text._write(rom, writes, off, data, 'card %d %s' % (i, ('tiles', 'map')[k]))
            rom_text._write(rom, writes, slot(i) + 4 * k, struct.pack('<I', 0x08000000 + off), 'card %d ptr' % i)
    loc_apply(rom, writes)
    sheet_apply(rom, writes)
    news_apply(rom, writes)
    kana_apply(rom, writes)
    props_apply(rom, writes)


def pointer_words():
    """ROM offsets of the pointer words apply() may rewrite (build.py allows these single words)."""
    return {slot(i) + 4 * k for i in EN for k in (0, 1)} | set(LOC) | set(LOC_PICS)


# --- location cards ---------------------------------------------------------------------------------------------
# [256 colours BGR555][8bpp tiles LZ77, pixels 0-127][its 32x20 map LZ77 at align4(end of tiles)]: the code (0x196C0)
# loads the tiles pointer from a literal (the key), copies the palette from 0x200 before it (the park card's pixels
# land on the upper 128 colours, the others' on the lower), and finds the map at a fixed distance after the tiles (a
# literal or an immediate), so a moved card keeps that whole layout. The caption is map rows 16-17, columns 0-9
# (80x16 px); the English one also takes row 18 (blank before, on screen): two 8 px lines, all caps.
# HONKY TONK (0x19678) is English already.
LOC = {0x196A8: ['SAZANAMI', 'CORPORATION'], 0x19698: ['URA-TOCHO'], 0x19658: ['URA-SHINJUKU', 'CENTRAL PARK'],
       0x1966C: ['HARAGURO', "BOSS'S MANSION"], 0x19688: ['URA-SHINJUKU', 'WEST HOSPITAL'],
       0x196B4: ["KIMOJI'S", 'PET SHOP'], 0x19718: ['URA-SHINJUKU', 'STATION']}
CAP = (128, 144, 0, 80)         # JP caption y0, y1, x0, x1; the English one ends at y1 + 8


def loc_load(rom, p):
    """(tiles offset, map offset, tiles, map) of the location card whose tiles pointer is at p."""
    t = struct.unpack_from('<I', rom, p)[0] - 0x08000000
    tiles, n = lzscan.lz77(rom, t)
    m = (t + n + 3) & ~3
    return t, m, tiles, list(struct.unpack('<%dH' % (W * H), lzscan.lz77(rom, m)[0]))


def loc_palette(rom, p):
    """The 128 colours the card's pixels use: the upper half of its palette, or the lower when the upper is flat."""
    t = struct.unpack_from('<I', rom, p)[0] - 0x08000000
    up = palette(rom, t - 0x100, 128)
    return up if len(set(up)) > 1 else palette(rom, t - 0x200, 128)


def loc_english(rom, p):
    _, _, tiles, mp = loc_load(rom, p)
    px, pal = to_pixels(tiles, mp, 8), loc_palette(rom, p)
    y0, y1, x0, x1 = CAP
    cap = [v for r in px[y0:y1] for v in r[x0:x1]]
    bg = max(set(cap), key=cap.count)
    ink = max(set(cap) - {0}, key=lambda c: sum(pal[c]))   # the caption's brightest colour (0 is transparent)
    assert all(e == 0 for e in mp[18 * W:18 * W + 10]), 'map row 18 is not blank'
    for y in range(y0, y1 + 8):
        px[y][x0:x1] = [bg] * (x1 - x0)
    lines = LOC[p]
    for k, text in enumerate(lines):
        letter.draw(px, text, (x0 + x1) // 2, y0 + (11 * k if len(lines) == 2 else 6), ink, lo=x0, hi=x1)
    return px


def inpaint(px, mask, top=0):
    """Fill each masked pixel from the nearest unmasked one in its column (above, but not above row top, or below)."""
    for x, y in sorted(mask):
        up = next((y - k for k in range(1, 40) if (x, y - k) not in mask and y - k >= top), None)
        dn = next((y + k for k in range(1, 40) if (x, y + k) not in mask), None)
        src = up if dn is None or (up is not None and y - up <= dn - y) else dn
        px[y][x] = px[src][x]


# --- title screen: same layout as a location card (tiles pointer 0x70D0, palette at -0x200, map at +0x6574) ------
TITLE = 0x70D0
SUB = (30, 214, 68, 86)         # x0, x1, y0, y1 of the 地獄のスカラムーシュ lettering (white 83 outline, dark fill)
CPR = ((33, 210, 133, 146), (33, 126, 146, 159))      # x0, x1, y0, y1 of the two copyright lines
WHITE, DARK, LIGHT = 83, 253, 31
RUBY = (160, 228, 20, 29)       # x0, x1, y0, y1 searched for the ruby's white plate (filled between its light ends)
BADGE = (182, 210, 58, 67)      # the blue 奪還屋 box


def title_english(rom):
    _, _, tiles, mp = loc_load(rom, TITLE)
    px = to_pixels(tiles, mp, 8)
    x0, x1, y0, y1 = SUB
    white = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[y][x] == WHITE}
    mask = {(x + i, y + j) for x, y in white for i in range(-3, 4) for j in range(-3, 4)
            if y0 - 1 <= y + j < y1 + 2}
    inpaint(px, mask, y0)           # nothing from the logo above
    bx0, bx1, by0, by1 = BADGE      # D5: the 奪還屋 badge under "rs": the letters run on to y 62, the logo's bottom
    for y in range(by0, by1):       # outline rows (63-66) continue from the column on its left
        px[y][bx0:bx1] = px[by0 - 1][bx0:bx1] if y < 63 else [px[y][bx0 - 1]] * (bx1 - bx0)
    letter.draw(px, 'Scaramouche of Hell', 120, 67, DARK, 2, 2, 1, outline=WHITE)
    # the two (anti-aliased) copyright lines over the art: filled from the art above and below, redrawn
    inpaint(px, {(x, y) for x0, x1, y0, y1 in CPR for y in range(y0, y1) for x in range(x0, x1)})
    letter.draw(px, '(C) 2001 Yuya Aoki/Rando Ayamine/Kodansha', 120, 132, LIGHT, outline=DARK)
    letter.draw(px, '(C) 2001 KONAMI', 38 + letter.width('(C) 2001 KONAMI') // 2, 146, LIGHT, outline=DARK)
    # D5: the logo keeps its English "GetBackers"; the ゲットバッカーズ ruby plate is blanked white
    pal = palette(rom, struct.unpack_from('<I', rom, TITLE)[0] - 0x08000000 - 0x200, 256)
    for y in range(RUBY[2], RUBY[3]):
        light = [x for x in range(RUBY[0], RUBY[1]) if sum(pal[px[y][x]]) > 600]
        for x in range(light[0], light[-1] + 1):
            px[y][x] = WHITE
    return px


LOC_PICS = {TITLE: title_english}       # other pictures in the location card layout, redrawn by their function


# --- item cards and skill-name labels: 4bpp sprite sheets (32 tiles wide, 16 rows), 64x32 cards in slot order ---
# Each sheet keeps blank cards of its card shapes after its names; a card is cleared by copying the blank of the
# same shape and its name redrawn in the blank's inner area. Item sheets are reached by pointers, the skill sheets
# by a table the build doesn't know, so a sheet is rewritten in place (it must not grow past its old size).
ITEMS = [['Recovery Juice (S)', 'Recovery Juice (M)', 'Recovery Juice (L)', "Gen's Special Drink", 'Ginseng Extract',
          'Peony Extract', 'Hamburger', 'Big Burger'],
         ['Poison Cure', 'Paralysis Cure', 'Stabilizer', 'All Cure', 'Neutralizer', 'Spider Lily Powder',
          'Tiger Lily Bulb', 'Horai Jewel'],
         ['Fury Pill', 'Hardening Powder', 'Gale Pill', 'Sharp Tonic', 'Decline Pill', 'Slack Powder', 'Slow Pill',
          'Dull Tonic']]
SKILL_JP = ['蛇咬', 'プラズマ', '解毒香', '猫擬', '絃結界', '赤い雨']    # first label of each skill sheet
SHEETS = [0x2CF684, 0x2D0718, 0x2D1878, 0x2D2A24, 0x2D3928, 0x2D49F0, 0x2D5BCC, 0x2D6D74, 0x2D8074]


def sheet_names(script, k):
    """English names on sheet k: items from ITEMS, skills = the script's names from the first one, address down."""
    if k < 3:
        return ITEMS[k]
    es = sorted((e for e in script.values() if e['jp']), key=lambda e: -int(e['id'], 16))
    i = next(i for i, e in enumerate(es) if e['jp'] == SKILL_JP[k - 3])
    names = []
    for e in es[i:]:
        if '：' in e['jp'] or len(names) == 8 or (names and e['jp'] in SKILL_JP):
            break
        names.append(SHORT.get(e['en'], e['en']))
    return names


def card_px(px, n):
    return [r[n % 4 * 64:n % 4 * 64 + 64] for r in px[n // 4 * 32:n // 4 * 32 + 32]]


def sheet_english(rom, off, names):
    tiles = lzscan.lz77(rom, off)[0]
    px = [[0] * 256 for _ in range(128)]
    for k in range(512):
        for y, row in enumerate(tile_px(tiles, k)):
            px[k // 32 * 8 + y][k % 32 * 8:k % 32 * 8 + 8] = row
    # blanks: slots after the names holding a card (centre not transparent) of 5-8 colours (text makes 13-14)
    blanks = [n for n in range(len(names), 16)
              if 5 <= len({v for r in card_px(px, n) for v in r}) <= 8 and card_px(px, n)[16][32] != 0]
    assert blanks, 'sheet %X: no blank card' % off
    for n, name in enumerate(names):
        card = card_px(px, n)
        b = min(blanks, key=lambda m: sum(a != c for ra, rc in zip(card, card_px(px, m)) for a, c in zip(ra, rc)))
        blank = card_px(px, b)
        fill = max({v for r in blank for v in r}, key=lambda c: sum(r.count(c) for r in blank))
        ink = max((v for ra, rb in zip(card, blank) for v, w in zip(ra, rb) if v != w and v != fill),
                  key=lambda c: sum(r.count(c) for r in card))
        rows = [y for y in range(32) if blank[y].count(fill) >= 20]
        cols = [x for x in range(64) if blank[rows[len(rows) // 2]][x] == fill]
        y0, y1 = rows[0], rows[-1] + 1
        lines = fit(name, cols[-1] - cols[0] - 1, (y1 - y0 + 1) // PITCH)
        for y in range(32):
            px[n // 4 * 32 + y][n % 4 * 64:n % 4 * 64 + 64] = blank[y]
        def spans(top):
            # per line: the columns that are fill on every row its cell covers (a notch narrows them)
            out = []
            for i, line in enumerate(lines):
                band = range(max(y0, top + PITCH * i), min(y1, top + PITCH * i + 11))
                s = [x for x in range(64) if all(blank[y][x] == fill for y in band)]
                out.append(s if s and s[-1] - s[0] + 1 >= letter.width(line) else None)
            return out
        mid = y0 + (y1 - y0 - PITCH * len(lines) + 1) // 2 - 1
        top = min((t for t in range(y0 - 1, y1 - PITCH * len(lines) + 1) if all(spans(t))), key=lambda t: abs(t - mid))
        for i, (line, s) in enumerate(zip(lines, spans(top))):
            letter.draw(px, line, n % 4 * 64 + (s[0] + s[-1] + 1) // 2, n // 4 * 32 + top + PITCH * i, ink,
                        lo=n % 4 * 64 + s[0], hi=n % 4 * 64 + s[-1] + 1)
    return px


PITCH = 9                       # label line pitch: 8 px capitals + 1
HYPHEN = {'Thunderbolt': 'Thunder- bolt', 'Thunderclap': 'Thunder- clap'}     # words wider than a label
# D4 last resort, flagged in docs/status.md: the label body is 22 px tall, 2 lines; the menus keep the full name
SHORT = {'Lightning Emperor Descends': 'Lightning Emperor'}


def fit(text, width, nmax):
    """Greedy word wrap to lines of at most width px; fails past nmax lines."""
    lines = []
    for w in ' '.join(HYPHEN.get(w, w) for w in text.split(' ')).split(' '):
        if lines and not lines[-1].endswith('-') and letter.width(lines[-1] + ' ' + w) <= width:
            lines[-1] += ' ' + w
        else:
            lines.append(w)
    assert len(lines) <= nmax and all(letter.width(l) <= width for l in lines), '%r does not fit %d px x %d' % (
        text, width, nmax)
    return lines


def sheet_tiles(px):
    return bytes(px[k // 32 * 8 + y][k % 32 * 8 + x] | px[k // 32 * 8 + y][k % 32 * 8 + x + 1] << 4
                 for k in range(512) for y in range(8) for x in range(0, 8, 2))


def sheet_apply(rom, writes):
    script = extract.load()             # the stored names, also in a marker build
    for k, off in enumerate(SHEETS):
        data = lzcomp.compress(sheet_tiles(sheet_english(rom, off, sheet_names(script, k))))
        old = (lzscan.lz77(rom, off)[1] + 3) & ~3
        assert len(data) <= old, 'sheet %X: %d bytes > %d' % (off, len(data), old)
        rom_text._write(rom, writes, off, data + bytes(old - len(data)), 'sheet %X' % off)


def sheet_ranges():
    """[(start, end)] of the LZ77 blocks rewritten in place, in the original ROM (build.allowed)."""
    rom = ROM.read_bytes()
    return [(off, off + ((lzscan.lz77(rom, off)[1] + 3) & ~3)) for off in SHEETS + [NEWS, KANA, PROPS]]


# --- 7NEWS intro screen: one 4bpp sheet, 16 tiles wide, reached by a table: rewritten in place -------------------
# Headline strip (BG1 rows 13-14): sheet columns 9-15 of rows 0, 2, 4, 6 side by side, rows 1, 3, 5, 7 below
# (224x16 px; white 0xF, text x 5-146, the 7N mark after it). Photo (BG2): rows 1-8, columns 0-8 (72x64 px), its
# caption box fill 6 at y 51-61.
NEWS = 0x1A6480
STRIP = [[r * 16 + 9 + c for r in rows for c in range(7)] for rows in ((0, 2, 4, 6), (1, 3, 5, 7))]
PHOTO = [[(r + 1) * 16 + c for c in range(9)] for r in range(8)]


def grid(tiles, layout):
    """Pixels of tiles laid out as rows of tile indices (4bpp)."""
    px = [[0] * (8 * len(layout[0])) for _ in range(8 * len(layout))]
    for r, row in enumerate(layout):
        for c, n in enumerate(row):
            for y, line in enumerate(tile_px(tiles, n)):
                px[r * 8 + y][c * 8:c * 8 + 8] = line
    return px


def ungrid(tiles, layout, px):
    for r, row in enumerate(layout):
        for c, n in enumerate(row):
            tiles[32 * n:32 * n + 32] = bytes(px[r * 8 + y][c * 8 + x] | px[r * 8 + y][c * 8 + x + 1] << 4
                                              for y in range(8) for x in range(0, 8, 2))


def relabel(px, box, fill, text, style=(1, 1, 0, 0)):
    """Clear box (x0, x1, y0, y1) to fill, then draw text centred in it in the box's commonest other colour."""
    x0, x1, y0, y1 = box
    inks = [v for r in px[y0:y1] for v in r[x0:x1] if v != fill]
    ink = max(set(inks), key=inks.count)
    for y in range(y0, y1):
        px[y][x0:x1] = [fill] * (x1 - x0)
    letter.draw(px, text, (x0 + x1) // 2, (y0 + y1) // 2 - 5 * style[1], ink, *style, lo=x0, hi=x1)


def news_apply(rom, writes):
    tiles = bytearray(lzscan.lz77(rom, NEWS)[0])
    px = grid(tiles, STRIP)
    relabel(px, (5, 147, 3, 14), 0xF, 'Ura-Tocho Raid Underway?', (1, 1, 1, 0))
    ungrid(tiles, STRIP, px)
    px = grid(tiles, PHOTO)
    relabel(px, (14, 66, 51, 61), 6, 'URA-TOCHO')    # x < 14 is behind the newscaster's hair
    ungrid(tiles, PHOTO, px)
    rewrite(rom, writes, NEWS, tiles, '7NEWS sheet')


def rewrite(rom, writes, off, tiles, what):
    """Recompress tiles into the LZ77 block at off, in place."""
    data = lzcomp.compress(bytes(tiles))
    old = (lzscan.lz77(rom, off)[1] + 3) & ~3
    assert len(data) <= old, '%s: %d bytes > %d' % (what, len(data), old)
    rom_text._write(rom, writes, off, data + bytes(old - len(data)), what)


# --- Ginji's field sprite sheet: 16 tiles wide; small はい / いいえ at tile rows 12-15, columns 2-7, beside the
# "!" / "?" emotes (what shows them is not found: redrawn so they can't surface in Japanese) ----------------------
KANA = 0x1ABD44
YESNO = [[(12 + r) * 16 + 2 + c for c in range(6)] for r in range(4)]


def kana_apply(rom, writes):
    tiles = bytearray(lzscan.lz77(rom, KANA)[0])
    px = grid(tiles, YESNO)
    relabel(px, (0, 48, 0, 16), 0, 'Yes')
    relabel(px, (0, 48, 16, 32), 0, 'No')
    ungrid(tiles, YESNO, px)
    rewrite(rom, writes, KANA, tiles, 'Ginji sprite sheet')


# --- Field props sheet: two signposts (columns 12-15, tile rows 7-12), each a small plate over a big one, text
# 5 px tall in ink 0xD on fill 2: ふれあい/ひろば and とり/ぱーく. The map that shows them is not found ---------------
PROPS = 0x11C08C
POSTS = [[r * 16 + c for c in range(12, 16)] for r in range(7, 13)]
TINY = {'A': '010 101 111 101 101', 'B': '110 101 110 101 110', 'D': '110 101 101 101 110', 'E': '111 100 110 100 111',
        'G': '011 100 101 101 011', 'I': '1 1 1 1 1', 'K': '101 101 110 101 101', 'N': '101 111 111 101 101',
        'O': '010 101 101 101 010', 'P': '110 101 110 100 100', 'R': '110 101 110 101 101', 'T': '111 010 010 010 010',
        'Z': '111 001 010 100 111'}
SIGNS = [('PET', 'ZOO'), ('BIRD', 'PARK')]      # small plate: rows 2-6, about 22 px wide inside


def tiny(px, text, cx, y, ink):
    """Draw capitals from the 3x5 TINY font centred on cx, top row y, 1 px apart."""
    x = cx - (sum(len(TINY[ch].split()[0]) + 1 for ch in text) - 1) // 2
    for ch in text:
        rows = TINY[ch].split()
        for dy, r in enumerate(rows):
            for dx, b in enumerate(r):
                if b == '1':
                    px[y + dy][x + dx] = ink
        x += len(rows[0]) + 1


def props_apply(rom, writes):
    tiles = bytearray(lzscan.lz77(rom, PROPS)[0])
    px = grid(tiles, POSTS)
    for k, (top, big) in enumerate(SIGNS):
        for y0, y1, x0, x1 in ((2, 8, 5, 29), (11, 18, 5, 29)):
            for y in range(y0 + 24 * k, y1 + 24 * k):
                px[y][x0:x1] = [2 if v in (1, 9, 0xB, 0xD) else v for v in px[y][x0:x1]]
        tiny(px, top, 16, 2 + 24 * k, 0xD)
        tiny(px, big, 16, 12 + 24 * k, 0xD)
    ungrid(tiles, POSTS, px)
    rewrite(rom, writes, PROPS, tiles, 'field props sheet')


def loc_apply(rom, writes):
    for p in sorted(LOC) + sorted(LOC_PICS):
        t, m, tiles, _ = loc_load(rom, p)
        nt, nm = pack(*from_pixels(LOC_PICS[p](rom) if p in LOC_PICS else loc_english(rom, p), 8, tiles[:64]))
        assert len(nt) <= m - t, 'location card %X: tiles grew past the map distance' % p
        off = ((len(rom) + 3) & ~3) + 0x200
        rom_text._write(rom, writes, off - 0x200, rom[t - 0x200:t] + nt + bytes(m - t - len(nt)) + nm,
                        'location card %X' % p)
        rom_text._write(rom, writes, p, struct.pack('<I', 0x08000000 + off), 'location card ptr %X' % p)


def main():
    if len(sys.argv) not in (3, 4) or sys.argv[1] != 'render':
        sys.exit(__doc__)
    rom = (Path(__file__).resolve().parents[1] / 'rom' / 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba').read_bytes()
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (256 * 4, 160 * 7))
    for i in range(COUNT):
        tiles, mp, pal = load(rom, i)
        px = english(rom, i) if sys.argv[3:] == ['en'] else to_pixels(tiles, mp)
        assert to_pixels(*from_pixels(px)) == px
        im = image(px, pal)
        im.save(out / ('card_%02d.png' % i))
        sheet.paste(im, (i % 4 * 256, i // 4 * 160))
    sheet.save(out / 'sheet.png')
    print('%d cards -> %s' % (COUNT, out))


if __name__ == '__main__':
    main()
