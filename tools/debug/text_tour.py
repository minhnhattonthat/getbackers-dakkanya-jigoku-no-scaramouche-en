"""Text tour: warp to scenes, click through their text (emu.py --mash) with tools/debug/textlog.lua, and list which
script entries each 12x12 draw path (A, B, C) showed.

    python -X utf8 tools/debug/text_tour.py [ROM] [--scenes NAME|step:N ...] [--frames 4000] [--jobs 4] [--out DIR]

Default ROM: build/getbackers_marker.gba; default scenes: every story step 1-269 that is an event (`step:N`).
Per scene: <out>/<scene>/ shots every 120 frames + log.txt. <out>/seen.tsv: id, path, first scene, frame (one line per
id and path). Prints how many text entries were seen, per path."""
import argparse
import bisect
import re
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'debug'))
from skill import SKILL  # noqa: E402
import extract  # noqa: E402


def run(rom, out, scene, frames):
    d = out / scene.replace(':', '_')
    cmd = [sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts' / 'emu.py'), str(rom), '--out', str(d),
           '--script', str(ROOT / 'tools' / 'debug' / 'warp.lua'), '--script', str(ROOT / 'tools' / 'debug' / 'textlog.lua'),
           '--var', f"SCENE='{scene}'", '--frames', str(frames), '--mash', '40', '--shot-every', '120', '--sav',
           str(ROOT / 'work' / 'saves' / 'blank.sav')]
    subprocess.run(cmd, capture_output=True)
    log = d / 'log.txt'
    return scene, (log.read_text(encoding='utf-8', errors='replace') if log.is_file() else '')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('rom', nargs='?', default=str(ROOT / 'build' / 'getbackers_marker.gba'))
    ap.add_argument('--scenes', nargs='*')
    ap.add_argument('--frames', type=int, default=4000)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--out', default=str(ROOT / 'work' / 'qa' / 'text_tour'))
    ap.add_argument('--logs-only', action='store_true', help='no emulator: aggregate the logs already in --out')
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    blank = ROOT / 'work' / 'saves' / 'blank.sav'
    if not blank.is_file():
        blank.parent.mkdir(parents=True, exist_ok=True)
        blank.write_bytes(b'\xff' * 0x10000)
    if a.scenes:
        scenes = a.scenes
    else:
        import director
        d = director.ROM.read_bytes()
        scenes = []
        for i in range(director.CASES):
            t = struct.unpack_from('<I', d, director.TABLE - 0x08000000 + i * 4)[0] & ~1
            if any(c[0] == 'EVT' for c in director.decode(d, t)):
                scenes.append('step:%d' % (i + 1))
    script = extract.load()
    rom = Path(a.rom).read_bytes()
    where = []      # (address in this ROM, end, id): moved text is found through its first pointer
    for i, e in script.items():
        o = struct.unpack_from('<I', rom, int(e['ptrs'][0], 16))[0] - 0x08000000 if e['ptrs'] else int(i, 16)
        where.append((o, rom.index(b'\0', o), i))
    where.sort()
    starts = [w[0] for w in where]
    seen = {}
    if a.logs_only:
        logs = [(d.name, (d / 'log.txt').read_text(encoding='utf-8', errors='replace'))
                for d in sorted(out.iterdir()) if (d / 'log.txt').is_file()]
    else:
        logs = ThreadPoolExecutor(a.jobs).map(lambda s: run(a.rom, out, s, a.frames), scenes)
    if True:
        for scene, log in logs:
            for f, path, p in re.findall(r'f(\d+) TXT (\w) ([0-9A-F]+)', log):
                p = int(p, 16)
                k = bisect.bisect_right(starts, p) - 1
                key = (where[k][2] if k >= 0 and p <= where[k][1] else 'RAM/%X' % p, path)
                seen.setdefault(key, (scene, int(f)))
    with open(out / 'seen.tsv', 'w', encoding='utf-8') as fh:
        for (i, path), (scene, f) in sorted(seen.items()):
            fh.write('%s\t%s\t%s\t%d\n' % (i, path, scene, f))
    by = {}
    for (i, path) in seen:
        by.setdefault(path, set()).add(i)
    text = sum(1 for e in script.values() if e['status'] != 'data')
    print('text entries %d; seen: %s' % (text, ', '.join('%s %d' % (p, len(s)) for p, s in sorted(by.items()))))


if __name__ == '__main__':
    main()
