"""letter.py: draw English onto colour-index pixel arrays with the VWF font (fonts/font_en.txt, MIT) for graphics text.
draw(px, text, cx, y, ink, sx, sy, bold, track): centred on cx, cell top y; each font pixel becomes sx*sy (+bold px
right), track = extra px between letters."""
import vwf


def width(text, sx=1, bold=0, track=0):
    return sum(vwf.ADV[c] * sx + track for c in text) + bold - sx - track


def draw(px, text, cx, y, ink, sx=1, sy=1, bold=0, track=0, lo=4, hi=236, outline=None):
    """Draw text centred on cx (x0 = cx - width/2), track = extra px after each letter; fails if it leaves [lo, hi).
    outline: colour of a 1 px ring around the letters (8 neighbours)."""
    bad = sorted({c for c in text if c not in vwf.FONT})
    assert not bad, 'not in the font: %r' % ''.join(bad)
    w = width(text, sx, bold, track)
    x = cx - w // 2
    assert lo <= x and x + w <= hi, '%r is %d px, too wide for %d-%d' % (text, w, lo, hi)
    dots = set()
    for c in text:
        top, rows, adv = vwf.FONT[c]
        for r, row in enumerate(rows):
            for k, ch in enumerate(row):
                if ch == '#':
                    dots |= {(xx, yy) for yy in range(y + (top + r) * sy, y + (top + r + 1) * sy)
                             for xx in range(x + k * sx, x + (k + 1) * sx + bold)}
        x += adv * sx + track
    if outline is not None:
        for xx, yy in {(a + i, b + j) for a, b in dots for i in (-1, 0, 1) for j in (-1, 0, 1)} - dots:
            px[yy][xx] = outline
    for xx, yy in dots:
        px[yy][xx] = ink
    return w
