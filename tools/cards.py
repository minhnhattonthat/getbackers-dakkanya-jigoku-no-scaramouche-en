"""cards.py: the full-screen picture cards (docs/re/graphics.md): staff credits, end cards, act cards.

Card tables of (tiles LZ77 4bpp, map LZ77 32x20 u16, palette 16 x BGR555 raw) ROM pointers: 0x6A888 x 19
(0-16 staff credits, 17-18 end cards; then a 0 word), 0x6A970 x 7 (cards 19-25: ACT.1-6 + the final act).
    python -X utf8 tools/cards.py render OUTDIR [en]      every card as OUTDIR/card_NN.png (+ sheet.png); en: redrawn"""
import struct
import sys
from pathlib import Path

from PIL import Image

import letter
import lzcomp
import lzscan
import rom_text

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


def palette(rom, off):
    return [((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31)
            for c in struct.unpack_from('<16H', rom, off)]


def load(rom, i):
    t, m, p = entry(rom, i)
    tiles = lzscan.lz77(rom, t)[0]
    mp = list(struct.unpack('<%dH' % (W * H), lzscan.lz77(rom, m)[0]))
    return tiles, mp, palette(rom, p)


def tile_px(tiles, n):
    """8x8 colour indices of 4bpp tile n."""
    b = tiles[32 * n:32 * n + 32]
    return [[(b[y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]


def to_pixels(tiles, mp):
    """256x160 rows of colour indices (map flips applied; palette bank must be 0)."""
    px = [[0] * (W * 8) for _ in range(H * 8)]
    for k, e in enumerate(mp):
        assert e >> 12 == 0, 'palette bank %d' % (e >> 12)
        t = tile_px(tiles, e & 0x3FF)
        for y in range(8):
            for x in range(8):
                px[k // W * 8 + y][k % W * 8 + x] = t[7 - y if e & 0x800 else y][7 - x if e & 0x400 else x]
    return px


def from_pixels(px):
    """(tiles, map) for 256x160 indices: tile 0 blank, duplicates (also flipped ones) shared."""
    seen, tiles, mp = {}, bytearray(32), []
    seen[bytes(64)] = 0
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
            n = len(tiles) // 32
            assert n < 1024, 'too many tiles'
            seen[bytes(v for r in rows for v in r)] = n
            tiles += bytes(r[x] | r[x + 1] << 4 for r in rows for x in range(0, 8, 2))
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


def pointer_words():
    """ROM offsets of the pointer words apply() may rewrite (build.py allows these single words)."""
    return {slot(i) + 4 * k for i in EN for k in (0, 1)}


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
