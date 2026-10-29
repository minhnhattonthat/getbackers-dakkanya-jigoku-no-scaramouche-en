"""Static graphics-text sweep (docs/re/graphics.md): render every raw and LZ77-packed graphics region as numbered
4bpp tile sheets with an offset index, for reviewer agents to list Japanese cells.
    python -X utf8 tools/gfxsweep.py OUTDIR [4|8]      (bits per pixel, default 4)
Writes OUTDIR/sNNN.png (2048 tiles each, 32 tiles per row, zoom 2, left margin = ROM offset of the row)
and OUTDIR/index.txt (sheet -> source ranges). Prints every ROM range it skips and why."""
import os
import struct
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lzscan  # noqa: E402

ROM = 'rom/GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'
COLS, ROWS, ZOOM, MARGIN = 32, 64, 2, 70
# docs/re/README.md map: below 0x98000 is code, text and pointer tables; the font is 1bpp, not tiles
SKIP = [(0x000000, 0x098000, 'code, SJIS text 0x2DB4C-0x62350, script/pointer tables'),
        (0x26E200, 0x29CAA8, 'dialogue font (12x12 1bpp, docs/re/text.md)'),
        (0x3EB7E0, 0x400000, 'zero fill (free)')]


def lz_blocks(d, only_new=False):
    """Every 4-aligned LZ77 block: pointer-reached ones of any size, others (reached through tables, e.g. 0x21B464
    on the 7NEWS screen) when they unpack to >= 256 bytes. only_new: just the ones no pointer reaches."""
    refs = {w - 0x08000000 for (w,) in struct.iter_unpack('<I', d) if 0x08098000 <= w < 0x083EB7E0}
    out = []
    for o in range(0x98000, 0x3EB7E0, 4):
        if d[o] != 0x10 or (out and o < out[-1][0] + out[-1][2]):
            continue
        r = lzscan.lz77(d, o)
        if r and (o in refs or len(r[0]) >= 256):
            out.append((o, r[0], r[1]))
    return [b for b in out if b[0] not in refs] if only_new else out


def sheet(path, pieces):
    """pieces: [(kind, rom_offset, bytes)] laid out row by row; each piece starts on a new row. Raw rows are
    labelled with their ROM offset; LZ blocks with Z<block ROM offset>, then +<offset in the unpacked data>."""
    rows = []
    for kind, off, data in pieces:
        for r in range(0, len(data), COLS * 8 * BPP):
            label = '%06X' % (off + r) if kind == 'raw' else ('Z%06X' % off if r == 0 else '+%X' % r)
            rows.append((label, data[r:r + COLS * 8 * BPP]))
    img = Image.new('L', (MARGIN + COLS * 8 * ZOOM, len(rows) * 8 * ZOOM), 40)
    px = img.load()
    dr = ImageDraw.Draw(img)
    for y, (label, data) in enumerate(rows):
        dr.text((2, y * 8 * ZOOM + 2), label, fill=255)
        tb = 8 * BPP
        for t in range(len(data) // tb):
            for i in range(64):
                b = data[t * tb + i * BPP // 8]
                v = b if BPP == 8 else ((b >> 4) if i & 1 else (b & 15)) * 17
                x0 = MARGIN + (t * 8 + i % 8) * ZOOM
                y0 = (y * 8 + i // 8) * ZOOM
                for dy in range(ZOOM):
                    for dx in range(ZOOM):
                        px[x0 + dx, y0 + dy] = v
    img.save(path)


def main():
    global BPP
    out = sys.argv[1]
    BPP = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    row = COLS * 8 * BPP
    page = ROWS * row
    os.makedirs(out, exist_ok=True)
    d = open(ROM, 'rb').read()
    for a, b, why in SKIP:
        print('skip %06X-%06X %s' % (a, b, why))
    lz = lz_blocks(d)
    if '--new-lz' in sys.argv:      # second pass: only the blocks no pointer reaches, no raw ranges
        new = lz_blocks(d, True)
        # text-BG tilemaps (u16 entries, few distinct high bytes = palette/flip/tile-bank) are not glyph art
        # (low-colour lettering also has few distinct bytes, but in both halves; a map's low bytes = tile numbers vary)
        def is_map(x):
            return len(set(x[1::2])) <= 24 and len(set(x[0::2])) >= 48
        maps = [b for b in new if is_map(b[1])]
        new = [b for b in new if not is_map(b[1])]
        if '--was-map' in sys.argv:  # only the blocks the older, looser map rule skipped
            new = [b for b in new if len(set(b[1][1::2])) <= 24]
        print('new lz blocks', len(new), '; skipped as tilemaps:', len(maps))
        open(os.path.join(out, 'skipped_maps.txt'), 'w').write(''.join('%06X+%X\n' % (o, len(x)) for o, x, _ in maps))
        lz, SKIP[:] = new, SKIP + [(0, len(d), 'raw ranges: covered by the first pass')]
    # raw ranges = ROM minus SKIP minus LZ extents
    cut = sorted([(a, b) for a, b, _ in SKIP] + [(o, o + n) for o, _, n in lz])
    raw, pos = [], 0
    for a, b in cut:
        if a > pos:
            raw.append((pos, a))
        pos = max(pos, b)
    if pos < len(d):
        raw.append((pos, len(d)))
    pieces = []
    for a, b in raw:
        for o in range(a, b, page):
            pieces.append(('raw', o, d[o:min(b, o + page)]))
    for o, data, _ in lz:
        pieces.append(('lz', o, data))
    index, cur, n, size = [], [], 0, 0
    for kind, o, data in pieces + [(None, 0, None)]:
        if data is None or (cur and size + len(data) > page):
            name = 's%03d.png' % n
            sheet(os.path.join(out, name), cur)
            index.append('%s %s' % (name, ' '.join('%s:%06X+%X' % (p[0], p[1], len(p[2])) for p in cur)))
            n, cur, size = n + 1, [], 0
            if data is None:
                break
        cur.append((kind, o, data))
        size += len(data) + (-len(data)) % row
    open(os.path.join(out, 'index.txt'), 'w').write('\n'.join(index) + '\n')
    print('sheets', n, 'raw ranges', len(raw), 'lz blocks', len(lz))


if __name__ == '__main__':
    main()
