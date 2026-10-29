"""rom_text.py: unpack and repack the Shift-JIS string block (docs/re/text.md).

unpack(rom) -> [Rec]: every NUL-terminated record in 0x2DB4C-0x62350 with its slot size (record start to the next
record start, so NUL and zero padding included), its text through the jp table and the u32 pointers that reach it.
repack(rom, recs, texts) writes each text back: in its own slot when it fits, else past the ROM end (0x400000+, room
up to 32 MiB) with every pointer to it rewritten. Returns the write log for romdiff.py --writes.

    python -X utf8 tools/rom_text.py      (unpack + repack with no edits; prints the record and write counts)"""
import struct
from dataclasses import dataclass

from tbl import Table

START, END = 0x2DB4C, 0x62350
ROM_END = 0x400000
GBA = 0x08000000
# where real pointers live: code + data below the block, the script/item/name tables. Other words that happen to equal
# GBA|record (6 in graphics at 0x35xxxx-0x3Cxxxx) are coincidences and must not be repointed.
# Byte tables inside the table area make the same kind of coincidence (0x63EE4 `04 04 05 08` -> mid-string 0x50404).
# shortcut: found by test_pointers_hit_record_starts_or_empty_strings, not by decoding the tables; none of their words
# hits a record start today. Add a range here when that test names a new one.
PTR_SRC = ((0, START), (0x63000, 0x63E00), (0x64300, 0x68D00), (0x69100, 0x6A1C0), (0x6A200, 0x98000))


def jp_table():
    """Every double-byte cp932 code that round-trips, `α` as {br} (line break / choice separator), the printf
    specifiers; other bytes decode as [XX]."""
    return Table(jp_table_lines())


def jp_table_lines():
    lines = ['83BF={br}', '2573=%s', '253364=%3d', '253664=%6d']
    for lead in [*range(0x81, 0xA0), *range(0xE0, 0xFD)]:
        for trail in [*range(0x40, 0x7F), *range(0x80, 0xFD)]:
            b = bytes((lead, trail))
            try:
                c = b.decode('cp932')
            except UnicodeDecodeError:
                continue
            if c.encode('cp932') == b and c != '\\':
                lines.append('%02X%02X=%s' % (lead, trail, c))
    return lines


@dataclass
class Rec:
    off: int        # ROM offset of the first byte
    slot: int       # bytes owned: text + NUL + zero padding up to the next record (just text + NUL for data records)
    ptrs: list      # ROM offsets of u32 words holding GBA | off
    raw: bytes      # original bytes, no NUL
    text: str       # raw through the jp table


def pointers(d):
    refs = {}
    for a, b in PTR_SRC:
        for i, (w,) in enumerate(struct.iter_unpack('<I', d[a:b & ~3])):
            if GBA + START <= w < GBA + END:
                refs.setdefault(w - GBA, []).append(a + i * 4)
    return refs


def unpack(d, table=None):
    table = table or jp_table()
    refs = pointers(d)
    starts, o = [], START
    while o < END:
        starts.append(o)
        o = (d.index(b'\0', o) + 4) & ~3
        while o < END and d[o] == 0:
            o += 4
    recs = []
    for o, nxt in zip(starts, starts[1:] + [END]):
        raw = d[o:d.index(b'\0', o)]
        text, _ = table.decode(raw, 0, len(raw))
        # data records keep bytes after their first NUL (0x2F624 ramp, 0x2FA8C map runs): then the slot ends at the NUL
        slot = nxt - o if not any(d[o + len(raw):nxt]) else len(raw) + 1
        # an "empty string" pointer into the padding (0x68840 name table -> 0x2F618) must keep reading a zero
        slot = min([slot] + [max(t - o, len(raw) + 1) for t in range(o + len(raw), o + slot) if t in refs])
        recs.append(Rec(o, slot, refs.get(o, []), bytes(raw), text))
    return recs


def _write(rom, writes, off, data, who):
    if off + len(data) > len(rom):
        rom.extend(b'\xff' * (off + len(data) - len(rom)))
    old = bytes(rom[off:off + len(data)])
    if old != data:
        rom[off:off + len(data)] = data
        writes.append((off, old, bytes(data), who))


def repack(rom, recs, texts, table=None, relocate=()):
    """texts: {rec.off: text}; records missing from it keep their text. relocate: offsets forced out of their slot
    (for tests). Mutates rom (a bytearray); returns [(off, orig_bytes, new_bytes, writer)]."""
    table = table or jp_table()
    writes, free = [], max(len(rom), ROM_END)
    for r in recs:
        data = (table.encode(texts[r.off]) if r.off in texts else r.raw) + b'\0'
        if len(data) <= r.slot and r.off not in relocate:
            _write(rom, writes, r.off, data + bytes(max(0, len(r.raw) + 1 - len(data))), 'text %X' % r.off)
            continue
        if not r.ptrs:
            raise ValueError('%X: %d bytes > slot %d and no pointer to move it' % (r.off, len(data), r.slot))
        _write(rom, writes, free, data, 'text %X moved' % r.off)
        for p in r.ptrs:
            _write(rom, writes, p, struct.pack('<I', GBA + free), 'ptr %X -> text %X' % (p, r.off))
        free = (free + len(data) + 3) & ~3
    return writes


if __name__ == '__main__':
    from pathlib import Path
    d = (Path(__file__).resolve().parents[1] / 'rom/GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba').read_bytes()
    rom = bytearray(d)
    recs = unpack(d)
    w = repack(rom, recs, {})
    print('records %d, writes %d, identical %s' % (len(recs), len(w), bytes(rom) == d))
