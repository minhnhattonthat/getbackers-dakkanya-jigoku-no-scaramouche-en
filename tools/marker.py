"""marker.py: the marker script (phase 5): every text entry becomes `#<id>` + filler, so each box shows which entry it is.

Each {br}-separated part of the jp gets its own line; one-part text longer than SHORT jp chars fills two lines (the
dialogue box) to LINE px each on LINES lines, shorter text (names, labels) gets `#id` + a word. printf specifiers stay, in order.
    python -X utf8 tools/build.py --marker      -> build/getbackers_marker.gba"""
import re

import vwf

LINE = vwf.XMAX - 8     # px per dialogue line (text starts at x 8): a marker line that wraps shows a narrower box
LINES = 3
SHORT = 8
FILLER = 'The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. ' * 3
PRINTF = re.compile(r'%(?:s|3d|6d)')


def fill(head, px=LINE):
    out = head
    for w in FILLER.split():
        if vwf.width(out + ' ' + w) > px:
            break
        out += ' ' + w
    return out


def marker(e):
    jp, mid = e['jp'], '#' + e['id'].lstrip('0')
    parts = jp.split('{br}')
    spec = ''.join(' ' + p for p in PRINTF.findall(jp))
    if len(parts) == 1 and len(jp) <= SHORT:
        return mid + spec + ' Abc'
    if len(parts) == 1:
        return '{br}'.join([fill(mid + spec)] + [fill('')[1:]] * (LINES - 1))
    return '{br}'.join(fill((mid + spec) if i == 0 else '', LINE)[0 if i == 0 else 1:] for i in range(len(parts)))


def script(base):
    """base: {id: entry} -> the same entries with en = marker for every text entry."""
    return {i: dict(e, en=marker(e), status='done') for i, e in base.items() if e['status'] != 'data'}
