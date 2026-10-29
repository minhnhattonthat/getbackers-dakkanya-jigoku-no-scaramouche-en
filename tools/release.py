"""Release gate + patch: python -X utf8 tools/release.py [--force]
Gate (stops at the first failure): build -> check.py (tests + lint) -> smoke boot -> jp_left on the build's text
pointer slots -> qa_gate check (every tour sheet has a current ok verdict). The debug tool is the external
tools/debug/warp.lua: nothing of it is in the ROM, and the release build is the plain build (no --marker / --qa).
Then BPS (made, re-applied and verified by bps.py, re-applied again here and compared), README with the base ROM
hashes, and release/<name>_v<version>.zip (patch + README only). Refuses to overwrite a version's files without
--force. Never publishes anything."""
import hashlib
import os
import subprocess
import sys
import zipfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
PY = [sys.executable, '-X', 'utf8']
ORIG = os.path.join(ROOT, 'rom', 'GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba')
BUILT = os.path.join(ROOT, 'build', 'getbackers_en.gba')
VERSION = '1.0'
PATCH = 'GetBackers_Dakkanya_Jigoku_no_Scaramouche_EN_v%s.bps' % VERSION
ZIP = os.path.join(ROOT, 'release', 'GetBackers_Dakkanya_Jigoku_no_Scaramouche_EN_v%s.zip' % VERSION)


def run(name, cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    tail = (r.stdout + r.stderr).strip().splitlines()[-4:]
    print('%-10s %s  %s' % (name, 'ok' if r.returncode == 0 else 'FAIL', ' | '.join(tail)[:400]))
    if r.returncode:
        raise SystemExit('release gate failed at %s' % name)
    return r.stdout


def hashes(path):
    d = open(path, 'rb').read()
    return {'size': len(d), 'crc32': '%08X' % (zlib.crc32(d) & 0xFFFFFFFF), 'md5': hashlib.md5(d).hexdigest(),
            'sha1': hashlib.sha1(d).hexdigest()}


def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print(__doc__)
        return 0
    bps = os.path.join(ROOT, 'release', PATCH)
    if '--force' not in sys.argv and (os.path.exists(bps) or os.path.exists(ZIP)):
        raise SystemExit('v%s already released (%s): bump VERSION or pass --force' % (VERSION, ZIP))
    from skill import SCRIPTS
    run('build', PY + ['tools/build.py'])
    run('check', PY + ['tools/check.py'])
    run('smoke', PY + [os.path.join(SCRIPTS, 'emu.py'), BUILT, '--out', 'work/qa/smoke',
                       '--route', 'tools/routes/boot.txt', '--smoke'])
    run('jp_left', PY + [os.path.join(SCRIPTS, 'jp_left.py'), BUILT, '--sjis', '--slots', 'build/slots.txt',
                         '--known', 'tools/jp_known.txt'])
    run('qa_gate', PY + [os.path.join(SCRIPTS, 'qa_gate.py'), 'check', 'work/qa/manifest.tsv', 'work/qa/verdicts'])
    os.makedirs(os.path.join(ROOT, 'release'), exist_ok=True)
    run('bps', PY + [os.path.join(SCRIPTS, 'bps.py'), 'make', ORIG, BUILT, bps])
    chk = os.path.join(ROOT, 'work', 'reapplied.gba')
    run('apply', PY + [os.path.join(SCRIPTS, 'bps.py'), 'apply', ORIG, bps, chk])
    if open(chk, 'rb').read() != open(BUILT, 'rb').read():
        raise SystemExit('re-applied patch differs from the build')
    h0, h1 = hashes(ORIG), hashes(BUILT)
    readme = open(os.path.join(ROOT, 'docs', 'README_release.txt'), encoding='utf-8').read()
    readme = readme.format(version=VERSION, patch=PATCH, size=h0['size'], crc=h0['crc32'], md5=h0['md5'],
                           sha1=h0['sha1'], pcrc=h1['crc32'], psha1=h1['sha1'])
    with open(os.path.join(ROOT, 'release', 'README.txt'), 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(readme)
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(bps, PATCH)
        z.write(os.path.join(ROOT, 'release', 'README.txt'), 'README.txt')
    print('release:', ZIP)
    print('patch sha1', hashlib.sha1(open(bps, 'rb').read()).hexdigest(), 'patched CRC32', h1['crc32'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
