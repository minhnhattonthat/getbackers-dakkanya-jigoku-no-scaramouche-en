"""Warp to every entry of tools/debug/scenes.txt from a cold boot: proof shot, savestate, arrival-mode check.

    python -X utf8 tools/debug/warp_all.py [ROM] [--only NAME ...] [--jobs 3] [--out work/qa/warp_all]

Per entry: <out>/<name>/final.png (the proof), work/states/<name>.mss, and a line in <out>/report.tsv. Then one
contact sheet of every final shot (<out>/sheet*.png). Exit 1 if any entry fails to arrive in its expected mode.
Every run boots on an erased battery save; the in-game save of entry save_done becomes work/saves/act1_field.sav,
the fixture for the title's CONTINUE (tools/routes/title_continue.txt with emu.py --sav).
Regenerate the states after any code, font or graphics change (savestates keep the old VRAM and code).
"""
import argparse
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL  # noqa: E402

DEFAULT_ROM = ROOT / 'rom' / 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba'
BOOT = 700   # cold boot to the warp (the director first runs ~f560)
TAIL = 360   # frames after arrival before the proof shot, for entries with no route (a route sets its own length)


def scenes():
    out = []
    for line in (ROOT / 'tools' / 'debug' / 'scenes.txt').read_text(encoding='utf-8').splitlines():
        m = re.match(r'^(\w+)\s+(\d+)\s+([0-9A-Fa-f]+)\s*([^#]*)', line)
        if m:
            route = m.group(4).strip()
            frames = sum(int(n) for n in re.findall(r'(\d+)\s+\S+', route)) + 2 * route.count('@')
            out.append((m.group(1), int(m.group(2)), int(m.group(3), 16), frames))
    return out


def run(rom, outdir, name, mode, rframes):
    d = outdir / name
    state = ROOT / 'work' / 'states' / f'{name}.mss'
    blank = outdir / 'blank.sav'  # erased FLASH: the title offers NEW GAME only, and in-game saves stay in d
    if not blank.exists():
        blank.write_bytes(b'\xff' * 0x10000)
    cmd = [sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts' / 'emu.py'), str(rom), '--out', str(d),
           '--script', str(ROOT / 'tools' / 'debug' / 'warp.lua'), '--var', f"SCENE='{name}'",
           '--frames', str(BOOT + (rframes or TAIL)), '--state-out', str(state), '--sav', str(blank), '--timeout', '300']
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log = (d / 'log.txt').read_text(encoding='utf-8', errors='replace') if (d / 'log.txt').exists() else ''
    m = re.search(r'f(\d+) arrived: mode ([0-9A-F]+)', log)
    got = int(m.group(2), 16) if m else None
    modes = ' '.join(re.findall(r'f\d+ mode ([0-9A-F]+)', log))
    ok = r.returncode == 0 and got == mode and (d / 'final.png').exists()
    return name, ok, f'{got:X}' if got is not None else '-', modes, r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('rom', nargs='?', default=str(DEFAULT_ROM))
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--out', default=str(ROOT / 'work' / 'qa' / 'warp_all'))
    a = ap.parse_args()
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    todo = [s for s in scenes() if not a.only or s[0] in a.only]
    # Mesen keeps one battery file for all runs (tools/mesen/Saves): entries that save in game (save_*) run alone,
    # after the rest, or a parallel boot would see their save and the title would default to CONTINUE.
    todo.sort(key=lambda s: s[0].startswith('save'))
    par = [s for s in todo if not s[0].startswith('save')]
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda s: run(a.rom, outdir, s[0], s[2], s[3]), par))
    res += [run(a.rom, outdir, s[0], s[2], s[3]) for s in todo[len(par):]]
    made = outdir / 'save_done' / (Path(a.rom).stem + '.sav')
    if made.exists():  # the CONTINUE fixture for tools/routes/title_continue.txt
        (ROOT / 'work' / 'saves').mkdir(parents=True, exist_ok=True)
        shutil.copy(made, ROOT / 'work' / 'saves' / 'act1_field.sav')
    lines = ['name\tok\tarrived\texpected\tmodes\texit']
    for (name, ok, got, modes, rc), s in zip(res, todo):
        lines.append(f'{name}\t{"ok" if ok else "FAIL"}\t{got}\t{s[2]:X}\t{modes}\t{rc}')
        print(lines[-1])
    (outdir / 'report.tsv').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    shots = [str(outdir / s[0] / 'final.png') for s in todo if (outdir / s[0] / 'final.png').exists()]
    if shots:
        subprocess.run([sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts' / 'sheet.py'), *shots,
                        '--out', str(outdir / 'sheet.png')], check=False)
    bad = [r[0] for r in res if not r[1]]
    print(f'{len(res) - len(bad)}/{len(res)} ok' + (f'; FAIL: {" ".join(bad)}' if bad else ''))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
