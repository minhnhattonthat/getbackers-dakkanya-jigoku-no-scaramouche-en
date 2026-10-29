"""build.py: original ROM -> build/getbackers_en.gba (+ build/writes.txt, the write log romdiff.py checks).

Checks the dump against rom.sha1, unpacks the string block, repacks it with the `en` of script/*.json, and fails if any
byte changed outside the logged writes.
    python -X utf8 tools/build.py [--marker] [--qa ID=TEXT].. [OUT]
--marker: every string = its id + filler (tools/marker.py); --qa: override one entry's en (stress lines)."""
import sys
from pathlib import Path

import cards
import check_rom
import extract
import marker
import rom_text
import romdiff
import vwf

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'rom' / 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'
MAX_ROM = 0x2000000     # GBA cartridge address space: 32 MiB


def allowed():
    """[(start, end)] the build may write: the string block, the VWF hook sites, and everything past the original ROM
    end (VWF code + font, relocated text). Pointer words are allowed one by one (outside)."""
    return [(rom_text.START, rom_text.END), (rom_text.ROM_END, MAX_ROM), *((s, s + max(len(old), len(new))) for s, old, new in vwf.hooks())]


def outside(writes, slots=frozenset()):
    """Writes not inside one allowed range nor exactly one pointer word of slots (the strings' pointer offsets) or of
    the graphics tables (cards.pointer_words)."""
    ok, slots = allowed(), set(slots) | cards.pointer_words()
    return [w for w in writes if not (w[0] in slots and len(w[2]) == 4)
            and not any(a <= w[0] and w[0] + len(w[2]) <= b for a, b in ok)]


def build(orig, script=None, engine=True):
    """script: {id: entry} (default: script/*.json); each non-data entry with an en replaces its text.
    engine=False leaves out the VWF code (identity build)."""
    script = extract.load() if script is None else script
    texts = {int(i, 16): e['en'] for i, e in script.items() if e['en'] and e['status'] != 'data'}
    rom, writes, recs = bytearray(orig), [], rom_text.unpack(orig)
    if engine:
        vwf.apply(rom, writes)
    writes += rom_text.repack(rom, recs, texts, vwf.en_table())
    if engine:
        cards.apply(rom, writes)
    errs, _ = romdiff.check(orig, bytes(rom), set(), writes)
    slots = {p for r in recs for p in r.ptrs}
    errs += ['0x%06X: %s writes outside the allowed ranges' % (o, who) for o, _, _, who in outside(writes, slots)]
    if len(rom) > MAX_ROM:
        errs.append('ROM is %d bytes, past the 32 MiB address space' % len(rom))
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
    # every pointer slot the game reads text through, for jp_left.py --slots (+ the code-referenced save message)
    slots = sorted({p for r in rom_text.unpack(orig) for p in r.ptrs} | {0x22B90})
    (out.parent / 'slots.txt').write_text(''.join('%06X\n' % p for p in slots), encoding='utf-8')
    print('%s: %d bytes, %d writes%s' % (out, len(rom), len(writes), ', identical to the original' if rom == orig else ''))


if __name__ == '__main__':
    main()
