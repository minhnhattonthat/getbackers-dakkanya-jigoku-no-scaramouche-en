"""Recon scan of the Shift-JIS string block (docs/re/text.md): every NUL-terminated record in 0x2DB4C-0x62350 with
the ROM offsets of the u32 pointers (0x08000000|off) that reach it.
    python -X utf8 tools/textscan.py [OUT.tsv]      (columns: offset, pointer count, pointer offsets, text)"""
import struct
import sys

ROM = 'rom/GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'
START, END = 0x2DB4C, 0x62350


def records(d):
    o = START
    while o < END:
        e = d.index(b'\0', o)
        yield o, d[o:e]
        o = (e + 4) & ~3
        while o < END and d[o] == 0:
            o += 4


def pointers(d):
    refs = {}
    for i, (w,) in enumerate(struct.iter_unpack('<I', d)):
        if 0x08000000 + START <= w < 0x08000000 + END:
            refs.setdefault(w - 0x08000000, []).append(i * 4)
    return refs


def main():
    d = open(ROM, 'rb').read()
    refs = pointers(d)
    lines = []
    for o, b in records(d):
        t = b.decode('cp932', 'backslashreplace')
        r = refs.get(o, [])
        lines.append('%06X\t%d\t%s\t%s' % (o, len(r), ','.join('%X' % x for x in r[:8]), t))
    out = open(sys.argv[1], 'w', encoding='utf-8') if len(sys.argv) > 1 else sys.stdout
    out.write('\n'.join(lines) + '\n')
    print('records %d, with pointers %d' % (len(lines), sum(1 for l in lines if l.split('\t')[1] != '0')),
          file=sys.stderr)


if __name__ == '__main__':
    main()
