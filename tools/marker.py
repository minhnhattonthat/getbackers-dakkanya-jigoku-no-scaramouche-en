"""marker.py: the marker script (phase 5): every text entry becomes `#<id>` + filler, so each box shows which entry it is.

Each marker fills its window (tools/windows.py) to the budget exactly: box = 3 lines to 216 px, help/item = 1 line to
232 px within the byte limit, choice = `#id` + one short option per {br} part. Text of SHORT jp chars or fewer
(names, labels) gets `#id` + a word. printf specifiers stay, in order.
    python -X utf8 tools/build.py --marker      -> build/getbackers_marker.gba"""
import re

import vwf
import windows

SHORT = 8
FILLER = 'The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. ' * 3
PRINTF = re.compile(r'%(?:s|3d|6d)')


def fill(head, px, nbytes=None):
    out = head
    for w in FILLER.split():
        if vwf.width(out + ' ' + w) > px or (nbytes and len(out) + 1 + len(w) > nbytes):
            break
        out += ' ' + w
    return out


def marker(e):
    jp, mid = e['jp'], '#' + e['id'].lstrip('0')
    head = mid + ''.join(' ' + p for p in PRINTF.findall(jp))
    win = windows.window_of(e)
    px, lines, nbytes, _ = windows.WINDOWS[win]
    if win == 'choice':
        return '{br}'.join([mid] + ['Ab'] * jp.count('{br}'))
    if len(jp) <= SHORT and '{br}' not in jp:
        return head + ' Abc'
    if PRINTF.search(jp):       # %s expands to a name: keep room for it
        px, nbytes = px - 60, (nbytes or 999) - 12
    return '{br}'.join([fill(head, px, nbytes)] + [fill('', px)[1:]] * (lines - 1))


def script(base):
    """base: {id: entry} -> the same entries with en = marker for every text entry."""
    return {i: dict(e, en=marker(e), status='done') for i, e in base.items() if e['status'] != 'data'}
