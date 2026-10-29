"""Warp to one step per unique field map (or battle with --battles), dump VRAM, and report which of the BLOCKS'
tiles (graphics with text whose screen is unknown, docs/re/graphics.md) are loaded there.
Run from the repo root: python -X utf8 tools/debug/gfxscan.py [--battles] [--dump-only|--scan-only]
Dumps: work/qa/fieldscan/step_N/ppu_*.vram.bin (kept: rerun with --scan-only after changing BLOCKS)."""
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL  # noqa: E402
import lzscan  # noqa: E402

OUT = ROOT / 'work' / 'qa' / 'fieldscan'
ROM = ROOT / 'build' / 'getbackers_en.gba'
JP = ROOT / 'rom' / 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'
KIND = 'BTL' if '--battles' in sys.argv else 'FLD'
BLOCKS = {'Z314590': (0x314590, 0, None, 32), 'Z11C08C': (0x11C08C, 0xC00, 0x1400, 32),
          'Z1ABD44': (0x1ABD44, 0x1800, 0x1C00, 32), 'Z2C441C': (0x2C441C, 0, None, 32)}


def steps():
    txt = subprocess.run([sys.executable, '-X', 'utf8', 'tools/debug/director.py'], capture_output=True,
                         text=True, encoding='utf-8').stdout
    seen = {}
    for line in txt.splitlines():
        m = re.match(r'(\d+)\t.*FLD\((\w+),(\w+),', line) if KIND == 'FLD' else re.match(r'(\d+)\t.*BTL\((\w+)[,)]', line)
        if m:
            seen.setdefault((m[2], m[3] if KIND == 'FLD' else ''), int(m[1]))
    return seen


def dump(step):
    d = OUT / ('step_%d' % step)
    if list(d.glob('ppu_*.vram.bin')):
        return
    subprocess.run([sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts' / 'emu.py'), str(ROM), '--out', str(d),
                    '--script', 'tools/debug/warp.lua', '--script',
                    str(Path(SKILL) / 'scripts' / 'lua' / 'probes' / 'ppudump.lua'), '--var', "SCENE='step:%d'" % step,
                    '--frames', '1100' if KIND == 'FLD' else '1600', '--sav', 'work/saves/blank.sav'], capture_output=True)


def tiles(b, size):
    return {b[i:i + size] for i in range(0, len(b) - size + 1, size) if len(set(b[i:i + size])) > 1}


def main():
    st = steps()
    print(len(st), 'maps')
    if '--scan-only' not in sys.argv:
        with ThreadPoolExecutor(3) as ex:
            list(ex.map(dump, sorted(st.values())))
    if '--dump-only' in sys.argv:
        return
    rom = JP.read_bytes()
    want = {}
    for k, (o, lo, hi, size) in BLOCKS.items():
        data = lzscan.lz77(rom, o)[0] if isinstance(lzscan.lz77(rom, o), tuple) else lzscan.lz77(rom, o)
        want[k] = (tiles(data[lo:hi], size), size)
    for (m, s), step in sorted(st.items(), key=lambda x: x[1]):
        for v in (OUT / ('step_%d' % step)).glob('ppu_*.vram.bin'):
            vram = v.read_bytes()
            hits = []
            for k, (ts, size) in want.items():
                vt = {vram[i:i + size] for i in range(0, len(vram) - size + 1, 32)}
                n = len(ts & vt)
                if n:
                    hits.append('%s %d/%d' % (k, n, len(ts)))
            print('step %3d map %s,%s: %s' % (step, m, s, ', '.join(hits) or '-'))


if __name__ == '__main__':
    main()
