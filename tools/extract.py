"""extract.py: dump the string block to script/<window>.json (one file per 0x2000 ROM bytes, one entry per line).

Entry: id (ROM offset, hex), ptrs (pointer word offsets), max (bytes it may take in place; longer text is moved past the
ROM end and repointed), jp (decoded through rom_text.jp_table: {br} = α break, %s/%3d/%6d printf, [XX] other bytes),
en, status (todo | done | data), note. A re-dump never clobbers en/status/note of an existing id.
    python -X utf8 tools/extract.py"""
import json
import re
import sys
from pathlib import Path

import rom_text

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'rom' / 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'
SCRIPT = ROOT / 'script'
WINDOW = 0x2000
STATUS = ('todo', 'done', 'data')
DATA_RANGES = ((0x2F624, 0x30E44, 'ramp table 0x2F624 + 8x8 font tiles 0x2FA64'),)
FORMAT_ONLY = re.compile(r'(%s|%3d|%6d|\[20\])*$')


def classify(r):
    """'' for text, else why the record is data."""
    for a, b, why in DATA_RANGES:
        if a <= r.off < b:
            return why
    if '[' in r.text:
        return 'single-byte bytes, not 12x12 font text: ' + ('ASCII digits' if r.raw.isdigit() else 'half-width/space')
    if FORMAT_ONLY.match(r.text):
        return 'printf format / blank field only'
    return ''


def load():
    """{id: entry} over every script/*.json."""
    out = {}
    for f in sorted(SCRIPT.glob('*.json')):
        for e in json.loads(f.read_text(encoding='utf-8')):
            out[e['id']] = e
    return out


def dump(entries, path):
    path.write_text('[\n' + ',\n'.join(json.dumps(e, ensure_ascii=False) for e in entries) + '\n]\n', encoding='utf-8',
                    newline='\n')


def main():
    old = load() if SCRIPT.is_dir() else {}
    files, changed = {}, []
    for r in rom_text.unpack(ROM.read_bytes()):
        why = classify(r)
        e = {'id': '%06X' % r.off, 'ptrs': ['%X' % p for p in r.ptrs], 'max': r.slot, 'jp': r.text, 'en': '',
             'status': 'data' if why else 'todo', 'note': why}
        if e['id'] in old:
            o = old[e['id']]
            e.update(en=o['en'], status=o['status'], note=o['note'])
            if o['jp'] != e['jp']:
                changed.append(e['id'])
        files.setdefault(r.off & ~(WINDOW - 1), []).append(e)
    SCRIPT.mkdir(exist_ok=True)
    for base, entries in files.items():
        dump(entries, SCRIPT / ('%06X.json' % base))
    n = sum(map(len, files.values()))
    print('%d entries in %d files, %d data' % (n, len(files), sum(e['status'] == 'data' for v in files.values() for e in v)))
    if changed:
        sys.exit('jp changed under existing en (check them): ' + ' '.join(changed))


if __name__ == '__main__':
    main()
