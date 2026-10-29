"""List every code site that requests a game mode (strb #imm -> [0x03002BA0 + 0xA]), grouped by mode.

    python -X utf8 tools/debug/modesites.py [--rom ROM]
"""
import argparse
import collections
from pathlib import Path

import capstone

from director import ROM


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', default=str(ROM))
    d = Path(ap.parse_args().rom).read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.skipdata = True
    sites = collections.defaultdict(list)
    recent = []
    for ins in md.disasm(d[:0x2DB00], 0x08000000):
        recent = (recent + [ins])[-4:]
        if ins.mnemonic == 'strb' and ins.op_str.endswith('#0xa]'):
            reg = ins.op_str.split(',')[0]
            for p in reversed(recent[:-1]):
                if p.mnemonic == 'movs' and p.op_str.startswith(reg + ', #'):
                    sites[int(p.op_str.split('#')[1], 0)].append(ins.address)
                    break
    for mode in sorted(sites):
        print(f'{mode:02X}: ' + ' '.join(f'{a:08X}' for a in sites[mode]))


if __name__ == '__main__':
    main()
