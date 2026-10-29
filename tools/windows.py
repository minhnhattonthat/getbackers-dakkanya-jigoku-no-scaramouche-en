"""windows.py: text budgets per box variant (the width gate, docs/re/text.md §Windows) and which variant shows an entry.

    python -X utf8 tools/windows.py        (counts per window; each window's budget and how it was measured)

Budgets are in pixels of fonts/font_en.txt (vwf.width) per {br}-separated line. Variants:
- box: dialogue box (events, path B) and field box (talk/examine/item found, path A): 3 lines x 216 px.
- help: one-line help/message bar (path C: title, field menu, battle): 1 line x 232 px, and at most 47 bytes after
  printf expansion (0x080022A8 strncpy's 48 bytes into 0x03000030).
- choice: the yes/no window (path A, canvas offset 0x1000): lines of 40 px, one per option.
- item: item names, also inserted into the field box message “X” + found/can't carry (64-byte buffer 0x030000B8).
Assignment is by where the entry's pointers live; menu tables are a guess until each menu is toured (phase 8)."""
import functools

import vwf

# name: (px per line, lines, max bytes or None, how it was measured)
WINDOWS = {
    'box': (vwf.XMAX - 8, 3, None, 'measured: work/qa/torture (B), work/qa/fieldwalk (A top+bottom); x 8-224, ▼ at 227'),
    'help': (vwf.CMAX, 1, 47, 'measured: work/qa/title_c, m_menu_change, m_battle_menu; bytes: strncpy 0x30'),
    'choice': (40, 2, None, 'guess: window 6 tiles at x 23 (0x080201AE), text from x 8; not seen in game yet'),
    'item': (vwf.CMAX, 1, 40, 'guess: help line + field message buffer 64 bytes with the found/full fragments'),
}
HELP_TABLES = ((0x63000, 0x65000), (0x65000, 0x66000), (0x68000, 0x69000))   # menu help, battle quips, names/bios
ITEM_TABLES = ((0x97000, 0x98000),)
CHOICES = {'030F28'}


@functools.lru_cache(None)
def _table():
    return vwf.en_table()


def window_of(e):
    """Window name for a script entry (dict with id, ptrs, jp)."""
    if e['id'] in CHOICES:
        return 'choice'
    p = [int(x, 16) for x in e['ptrs']]
    if not p:
        return 'box'
    if any(a <= q < b for q in p for a, b in ITEM_TABLES):
        return 'item'
    if min(p) < 0x2DB4C or any(a <= q < b for q in p for a, b in HELP_TABLES):
        return 'help'
    return 'box'


def check(e, text=None):
    """Budget errors for one entry's en (or text)."""
    import re
    text = e['en'] if text is None else text
    px, lines, nbytes, _ = WINDOWS[window_of(e)]
    errs = []
    parts = text.split('{br}')
    if len(parts) > lines:
        errs.append('%d lines > %d' % (len(parts), lines))
    for s in parts:
        w = vwf.width(re.sub(r'%(?:s|3d|6d)', 'W' * 8, s))     # %s: a name, counted as 8 wide letters
        if w > px:
            errs.append('%d px > %d: %r' % (w, px, s[:40]))
    if nbytes and len(_table().encode(re.sub(r'%(?:s|3d|6d)', 'x' * 10, text))) > nbytes:
        errs.append('> %d bytes' % nbytes)
    return errs


if __name__ == '__main__':
    import collections
    import extract
    c = collections.Counter(window_of(e) for e in extract.load().values() if e['status'] != 'data')
    for k, (px, lines, nb, how) in WINDOWS.items():
        print('%-7s %4d entries  %d x %d px%s  (%s)' % (k, c[k], lines, px, ', <= %d bytes' % nb if nb else '', how))
