"""build.py: original ROM -> build/getbackers_en.gba (+ build/writes.txt, the write log romdiff.py checks).

Checks the dump against rom.sha1, unpacks the string block, repacks it with the `en` of script/*.json, and fails if any
byte changed outside the logged writes.
    python -X utf8 tools/build.py [--marker] [--qa ID=TEXT].. [OUT]
--marker: every string = its id + filler (tools/marker.py); --qa: override one entry's en (stress lines)."""
import sys
from pathlib import Path

import check_rom
import extract
import marker
import rom_text
import romdiff
import vwf

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'rom' / 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'


def build(orig, script=None, engine=True):
    """script: {id: entry} (default: script/*.json); each non-data entry with an en replaces its text.
    engine=False leaves out the VWF code (identity build)."""
    script = extract.load() if script is None else script
    texts = {int(i, 16): e['en'] for i, e in script.items() if e['en'] and e['status'] != 'data'}
    rom, writes = bytearray(orig), []
    if engine:
        vwf.apply(rom, writes)
    writes += rom_text.repack(rom, rom_text.unpack(orig), texts, vwf.en_table())
    errs, _ = romdiff.check(orig, bytes(rom), set(), writes)
    if errs:
        sys.exit('\n'.join(errs))
    return bytes(rom), writes


def main():
    check_rom.check()
    args, qa, mark = [], {}, False
    it = iter(sys.argv[1:])
    for a in it:
        if a == '--marker':
            mark = True
        elif a == '--qa':
            i, _, t = next(it).partition('=')
            qa['%06X' % int(i, 16)] = t
        else:
            args.append(a)
    out = Path(args[0]) if args else ROOT / 'build' / ('getbackers_marker.gba' if mark else 'getbackers_en.gba')
    orig = ROM.read_bytes()
    script = marker.script(extract.load()) if mark else extract.load()
    for i, t in qa.items():
        script[i] = dict(script[i], en=t, status='done')
    rom, writes = build(orig, script)
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(rom)
    (out.parent / 'writes.txt').write_text(''.join('%06X %s %s %s\n' % (o, a.hex(), b.hex(), w) for o, a, b, w in writes),
                                           encoding='utf-8')
    print('%s: %d bytes, %d writes%s' % (out, len(rom), len(writes), ', identical to the original' if rom == orig else ''))


if __name__ == '__main__':
    main()
