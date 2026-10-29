"""Decode the story director (docs/re/scenes.md): one line per story step with the scene calls its case makes.

The director task at 0x08021548 switches on (u16 0x030042C0 - 1) through the jump table at 0x08021570 (0x10D
cases). Each case calls one of the scene functions below with constant arguments; this follows the case code with
a tiny Thumb register tracker (movs/adds/lsls/ldr literal) and prints the calls.

    python -X utf8 tools/debug/director.py [--rom ROM] [--tsv OUT]
"""
import argparse
import struct
import sys
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / 'rom' / 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'
TABLE, CASES = 0x08021570, 0x10D
CALLS = {0x080213B4: 'EVT', 0x08021408: 'FLD', 0x08021450: 'BTL', 0x0802148C: 'M12', 0x080214A0: 'ACT'}
END = {0x080229A8, 0x0802299C}  # common exits
FUNC = (0x08021510, 0x080229B0)  # the director; a bl into it is a jump (tail-merged case code)


def decode(d, start, limit=0x200):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    regs, stack, out, pc = {}, {}, [], start
    seen = set()
    while pc not in seen and len(seen) < limit:
        seen.add(pc)
        ins = next(md.disasm(d[pc - 0x08000000:pc - 0x08000000 + 4], pc), None)
        if ins is None:
            break
        m, ops = ins.mnemonic, ins.op_str.replace('#', '').split(', ')
        num = lambda s: int(s, 0)
        try:
            if m == 'movs' and ops[1][0].isdigit() or m == 'movs' and ops[1].startswith('0x'):
                regs[ops[0]] = num(ops[1])
            elif m in ('movs', 'adds') and len(ops) == 2 and ops[1] in regs and m == 'movs':
                regs[ops[0]] = regs[ops[1]]
            elif m == 'adds' and len(ops) == 3 and ops[2][0].isdigit():
                regs[ops[0]] = regs.get(ops[1], 0) + num(ops[2]) if ops[1] in regs else None
            elif m == 'adds' and len(ops) == 2 and ops[1][0].isdigit():
                regs[ops[0]] = regs[ops[0]] + num(ops[1]) if regs.get(ops[0]) is not None else None
            elif m == 'subs' and len(ops) == 2 and ops[1][0].isdigit():
                regs[ops[0]] = regs[ops[0]] - num(ops[1]) if regs.get(ops[0]) is not None else None
            elif m == 'rsbs' and ops[2] == '0':
                regs[ops[0]] = -regs[ops[1]] if regs.get(ops[1]) is not None else None
            elif m == 'lsls' and len(ops) == 3 and ops[2][0].isdigit():
                regs[ops[0]] = regs[ops[1]] << num(ops[2]) if regs.get(ops[1]) is not None else None
            elif m == 'ldr' and ops[1] == '[pc':
                lit = ((pc + 4) & ~3) + num(ops[2].rstrip(']'))
                regs[ops[0]] = struct.unpack_from('<I', d, lit - 0x08000000)[0]
            elif m == 'str' and ops[1] == '[sp]':
                stack[0] = regs.get(ops[0])
            elif m == 'str' and ops[1] == '[sp' and ops[2].rstrip(']').isdigit() is False:
                stack[num(ops[2].rstrip(']'))] = regs.get(ops[0])
            elif m == 'bl':
                t = num(ops[0])
                if FUNC[0] <= t < FUNC[1] and t not in END:  # the compiler's far jump inside the director
                    pc = t
                    continue
                if t in CALLS:
                    out.append((CALLS[t], regs.get('r1'), regs.get('r2'), regs.get('r3'), stack.get(0)))
                elif t in END:
                    break
                else:
                    out.append(('call', t))
                for r in ('r0', 'r1', 'r2', 'r3'):
                    regs.pop(r, None)
            elif m == 'b':
                t = num(ops[0])
                if t in END:
                    break
                pc = t
                continue
            elif m.startswith('b') and m not in ('bics', 'bx', 'bl'):
                out.append(('br', m, num(ops[0])))
            elif m in ('pop', 'bx') or m == 'mov' and ops[0] == 'pc':
                break
            elif ops and ops[0] in regs and m not in ('cmp', 'str', 'strh', 'strb', 'tst'):
                regs[ops[0]] = None
        except (ValueError, IndexError, TypeError, KeyError):
            if ops and ops[0] in regs:
                regs[ops[0]] = None
        pc += ins.size
    return out


def fmt(c):
    if c[0] == 'call':
        return f'call {c[1]:08X}'
    if c[0] == 'br':
        return f'{c[1]} {c[2]:08X}'
    h = lambda v: '?' if v is None else f'{v & 0xFFFFFFFF:X}'
    return f'{c[0]}({h(c[1])},{h(c[2])},{h(c[3])},{h(c[4])})'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--rom', default=str(ROM))
    ap.add_argument('--tsv')
    a = ap.parse_args()
    d = Path(a.rom).read_bytes()
    lines = []
    for i in range(CASES):
        t = struct.unpack_from('<I', d, TABLE - 0x08000000 + i * 4)[0] & ~1
        calls = [fmt(c) for c in decode(d, t)]
        lines.append(f'{i + 1}\t{t:08X}\t' + ' '.join(calls))
    text = '\n'.join(lines) + '\n'
    if a.tsv:
        Path(a.tsv).write_text(text, encoding='utf-8')
    sys.stdout.write(text)


if __name__ == '__main__':
    main()
