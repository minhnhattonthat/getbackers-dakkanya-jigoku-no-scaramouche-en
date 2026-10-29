"""batches.py: translation batches (docs/translator-brief.md, skill references/translation.md).

    python -X utf8 tools/batches.py split [--chars 3500] [--max 150]   work/tl/bNNN.tsv + build/terms_bNNN.txt (todo only)
    python -X utf8 tools/batches.py check BATCH..                      validate work/tl/BATCH.out.tsv; prints OK
    python -X utf8 tools/batches.py merge BATCH..                      check, then write en (wrapped) + done to script/
    python -X utf8 tools/batches.py fit "text" [--window box]          wrapped lines with their px widths
    python -X utf8 tools/batches.py pairs OUT BATCH..                  reviewer pairs file (>> id | JP / EN, story order)
    python -X utf8 tools/batches.py story                              work/tl/story.txt: all text by first event step

Input TSV: id, speaker, form, limit, jp. Output TSV: id, English (prose; the merge word-wraps box lines with {br}
at windows.WINDOWS px, so translators write {br} only where the JP has one). Order = pointer order (script order)."""
import argparse
import re
import sys
from pathlib import Path

import extract
import vwf
import windows

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / 'work' / 'tl'
TERMS = ROOT / 'build'
SEEN = ROOT / 'work' / 'qa' / 'text_tour' / 'seen.tsv'
PRINTF = re.compile(r'%(?:s|3d|6d)')
BLANK = ' 　'
SPEAKER = re.compile(r'^([^「」：…。、！？\s]{1,12})[「：]')
HONORIFIC = {'さん': '-san', 'くん': '-kun', '君': '-kun', 'ちゃん': '-chan', '様': '-sama', 'サン': '-san'}
LITERAL_ALPHA = {'02F0E0'}     # α（アルファ） menu label: the α decodes as {br} but is a letter here (docs/re/text.md)
SCRIPTS = (r'[一-鿿々]', r'[゠-ヿー]', r'[぀-ゟ]', r'[Ａ-Ｚａ-ｚ０-９]')


def order_key(e):
    return (min(int(p, 16) for p in e['ptrs']) if e['ptrs'] else int(e['id'], 16), int(e['id'], 16))


def entries():
    """Text entries (not data, jp not empty) in script order."""
    return sorted((e for e in extract.load().values() if e['status'] != 'data' and e['jp']), key=order_key)


def form_of(e):
    w = windows.window_of(e)
    if w != 'box':
        return {'help': 'menu', 'item': 'name', 'choice': 'choice'}[w]
    return 'dlg' if SPEAKER.match(e['jp']) or '」' in e['jp'] else 'narration'


def limit_of(e):
    px, lines, nb, _ = windows.WINDOWS[windows.window_of(e)]
    return '%dx%dpx' % (lines, px) + ('/%dB' % nb if nb else '')


# --- glossary ---------------------------------------------------------------------------------------------------
def glossary():
    """[(jp forms, en, avoid list, section)] from the tables in glossary.md."""
    rows, section = [], ''
    for line in (ROOT / 'glossary.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            section = line[3:].strip()
        c = [x.strip() for x in line.strip().strip('|').split('|')] if line.startswith('|') else []
        if len(c) >= 2 and c[0] not in ('JP', '') and not set(c[0]) <= set('-: '):
            avoid = [a.strip() for a in c[4].split(',') if a.strip()] if len(c) > 4 else []
            # generic speaker labels (notes "Label...": 客, お爺さん, 駅員): speaker check, but お客様 is no honorific
            sec = 'Labels' if section == 'Characters' and len(c) > 3 and c[3].startswith('Label') else section
            rows.append(([j.strip() for j in c[0].split(',')], c[1], avoid, sec))
    return rows


def _script_of(ch):
    return next((i for i, p in enumerate(SCRIPTS) if re.match(p, ch)), -1)


def term_hits(jp, term):
    """Whole-run matches of term in jp (the neighbours are not in the same script as the term's ends)."""
    out = []
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if a and _script_of(jp[a - 1]) == _script_of(term[0]) >= 0:
            continue
        if b < len(jp) and _script_of(jp[b]) == _script_of(term[-1]) >= 0 and jp[b] not in HONORIFIC:
            continue
        out.append(m)
    return out


def terms_for(jp, rows):
    return [r for r in rows if any(term_hits(jp, j) for j in r[0])]


# --- wrap / check -----------------------------------------------------------------------------------------------
def wrap(text, px):
    """Greedy word wrap of one {br}-free segment to lines of at most px (vwf.width; %s counted as 8 W)."""
    def w(s):
        return vwf.width(PRINTF.sub('W' * 8, s))
    lines, cur = [], ''
    for word in text.split(' '):
        t = cur + ' ' + word if cur else word
        if cur and w(t) > px:
            lines.append(cur)
            cur = word
        else:
            cur = t
    return lines + [cur]


def wrapped(e, en):
    """en as stored: box text word-wrapped with {br}; other windows unchanged."""
    # the en lint wants the JP's leading/trailing blank kept; editors strip trailing spaces, so the merge adds it
    jp = e['jp']
    if len(jp) > len(jp.lstrip(BLANK)) and en == en.lstrip(BLANK):
        en = ' ' + en
    if len(jp) > len(jp.rstrip(BLANK)) and en == en.rstrip(BLANK):
        en = en + ' '
    if windows.window_of(e) != 'box':
        return en
    px = windows.WINDOWS['box'][0]
    core = en.strip(BLANK)
    lead, trail = en[:len(en) - len(en.lstrip(BLANK))], en[len(en.rstrip(BLANK)):]
    return lead + '{br}'.join(l for seg in core.split('{br}') for l in wrap(seg, px)) + trail


def check_entry(e, en, rows):
    errs, jp = [], e['jp']
    if not en.strip():
        return ['empty']
    if re.search(r'[\t]|\\u[0-9a-fA-F]{4}|\\n', en):
        errs.append('tab, \\n or \\u escape')
    bad = sorted({c for c in en.replace('{br}', '') if c not in vwf.FONT})
    if bad:
        errs.append('characters not in the font: %s' % ''.join(bad))
    if PRINTF.findall(en) != PRINTF.findall(jp):
        errs.append('printf specifiers differ from the JP (%s)' % ' '.join(PRINTF.findall(jp)) or 'none')
    if en.count('{br}') != jp.count('{br}') and e['id'] not in LITERAL_ALPHA:
        errs.append('{br} count %d, JP has %d (write {br} only where the JP has one)' % (en.count('{br}'), jp.count('{br}')))
    if re.sub(r'\{br\}', '', en).count('{') or '}' in re.sub(r'\{br\}', '', en):
        errs.append('braces other than {br}')
    if re.search(r'%(?:s|3d|6d)(st|nd|rd|th)\b', en):
        errs.append('ordinal suffix glued to a variable')
    for x in windows.check(e, wrapped(e, en)):
        errs.append('too long for %s (%s): %s' % (windows.window_of(e), limit_of(e), x))
    m = SPEAKER.match(jp)
    for jps, enr, avoid, section in rows:
        for a in avoid:
            if re.search(r'\b%s\b' % re.escape(a), en):
                errs.append('glossary: avoid %r (use %r)' % (a, enr))
        if section not in ('Characters', 'Labels'):
            continue
        for j in jps:
            if m and m.group(1) == j and not en.startswith(enr + ':'):
                errs.append('speaker %s must be written %r' % (j, enr + ': '))
            for h in term_hits(jp, j) if section == 'Characters' else ():
                hon = next((HONORIFIC[k] for k in HONORIFIC if jp.startswith(k, h.end())), None)
                if hon and enr.split()[0] + hon not in en and enr + hon not in en:
                    errs.append('honorific: %s%s -> %s%s' % (j, jp[h.end():h.end() + 2], enr.split()[0], hon))
    return errs


def read_tsv(path, ncol):
    out = []
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if line.strip():
            c = line.split('\t')
            if len(c) != ncol:
                sys.exit('%s:%d: %d columns, want %d' % (path, n, len(c), ncol))
            out.append(c)
    return out


def check(batch, quiet=False):
    """{id: en} if the batch is clean, else None (errors printed)."""
    src = TL / (batch + '.tsv')
    out = TL / (batch + '.out.tsv')
    if not out.exists():
        print('%s: %s missing' % (batch, out.name))
        return None
    want = [c[0] for c in read_tsv(src, 5)]
    got = read_tsv(out, 2)
    ids = [c[0] for c in got]
    errs = []
    if sorted(ids) != sorted(want) or len(set(ids)) != len(ids):
        miss, extra = set(want) - set(ids), set(ids) - set(want)
        dup = {i for i in ids if ids.count(i) > 1}
        errs.append('ids: missing %s extra %s duplicate %s' % (sorted(miss), sorted(extra), sorted(dup)))
    script, rows = extract.load(), glossary()
    for i, en in got:
        if i in script:
            errs += ['%s: %s' % (i, x) for x in check_entry(script[i], en, rows)]
    for x in errs:
        print('%s %s' % (batch, x))
    if errs:
        print('%s: %d errors' % (batch, len(errs)))
        return None
    if not quiet:
        print('%s: OK (%d entries)' % (batch, len(got)))
    return dict(got)


# --- commands ---------------------------------------------------------------------------------------------------
def cmd_split(a):
    TL.mkdir(parents=True, exist_ok=True)
    TERMS.mkdir(exist_ok=True)
    old = sorted(TL.glob('b[0-9][0-9][0-9].tsv'))
    taken = {c[0] for f in old for c in read_tsv(f, 5)}
    todo = [e for e in entries() if e['status'] == 'todo' and e['id'] not in taken]
    n = int(old[-1].stem[1:]) if old else 0
    rows = glossary()
    batches, cur, size, prev_sp = [], [], 0, ''
    for e in todo:
        if cur and (size + len(e['jp']) > a.chars or len(cur) >= a.max):
            batches.append(cur)
            cur, size = [], 0
        cur.append(e)
        size += len(e['jp'])
    if cur:
        batches.append(cur)
    for b in batches:
        n += 1
        name = 'b%03d' % n
        lines = []
        for e in b:
            m = SPEAKER.match(e['jp'])
            form = form_of(e)
            if m and '「' in e['jp'][:m.end()]:
                prev_sp = m.group(1)
            sp = m.group(1) if m else prev_sp if form in ('dlg', 'narration') else ''
            if sp and form == 'narration':
                form = 'dlg'                # middle page of an open quote
            lines.append('\t'.join((e['id'], sp, form, limit_of(e), e['jp'])))
            if '」' in e['jp'] or form not in ('dlg', 'narration'):
                prev_sp = ''
        p = TL / (name + '.tsv')
        if p.exists():
            sys.exit('%s exists; refusing to overwrite' % p)
        p.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
        t = {}
        for e in b:
            for jps, en, avoid, sec in terms_for(e['jp'], rows):
                t[', '.join(jps)] = '%s -> %s%s' % (', '.join(jps), en, ('  (avoid: %s)' % ', '.join(avoid)) if avoid else '')
        (TERMS / ('terms_%s.txt' % name)).write_text('\n'.join(t.values()) + '\n', encoding='utf-8', newline='\n')
        print('%s: %d entries, %d JP chars, %d terms' % (name, len(b), sum(len(e['jp']) for e in b), len(t)))


def cmd_check(a):
    ok = [check(b) is not None for b in a.batch]
    sys.exit(0 if all(ok) else 1)


def cmd_merge(a):
    got = {}
    for b in a.batch:
        r = check(b, quiet=True)
        if r is None:
            sys.exit('%s: not merged' % b)
        got.update(r)
    files = {}
    for f in sorted(extract.SCRIPT.glob('*.json')):
        import json
        files[f] = json.loads(f.read_text(encoding='utf-8'))
    n = 0
    for f, es in files.items():
        hit = False
        for e in es:
            if e['id'] in got:
                e['en'], e['status'] = wrapped(e, got[e['id']]), 'done'
                hit, n = True, n + 1
        if hit:
            extract.dump(es, f)
    print('merged %d entries from %s' % (n, ' '.join(a.batch)))


def cmd_fit(a):
    e = {'id': 'fit', 'ptrs': [], 'jp': ''}
    px, lines, nb, _ = windows.WINDOWS[a.window]
    ls = [l for seg in a.text.split('{br}') for l in (wrap(seg, px) if a.window == 'box' else [seg])]
    for l in ls:
        print('%4d px  %s' % (vwf.width(PRINTF.sub('W' * 8, l)), l))
    print('%d/%d lines, limit %d px%s' % (len(ls), lines, px, ', %d bytes' % nb if nb else ''))


def cmd_pairs(a):
    script = extract.load()
    out = []
    for b in a.batch:
        src = read_tsv(TL / (b + '.tsv'), 5)
        en = dict(read_tsv(TL / (b + '.out.tsv'), 2))
        out.append('## %s' % b)
        for c in src:
            out.append('>> %s | %s%s | %s / %s' % (c[0], c[2], ' ' + c[1] if c[1] else '', script[c[0]]['jp'], en.get(c[0], '')))
    Path(a.out).write_text('\n'.join(out) + '\n', encoding='utf-8', newline='\n')
    print('%s: %d lines' % (a.out, len(out)))


def cmd_story(a):
    step = {}
    if SEEN.exists():
        for c in read_tsv(SEEN, 4):
            s = int(c[2].split('_')[1]) if c[2].startswith('step_') else 999
            step[c[0]] = min(step.get(c[0], 999), s)
    es = entries()
    es.sort(key=lambda e: (step.get(e['id'], 999), order_key(e)))
    lines, last = [], None
    for e in es:
        s = step.get(e['id'], 999)
        if s != last:
            lines.append('== step %s' % (s if s < 999 else 'unseen (pointer order: field talk, menus, battle)'))
            last = s
        lines.append('%s\t%s' % (e['id'], e['jp']))
    TL.mkdir(parents=True, exist_ok=True)
    (TL / 'story.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print('work/tl/story.txt: %d entries, %d seen in event steps' % (len(es), sum(e['id'] in step for e in es)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='cmd', required=True)
    x = s.add_parser('split')
    x.add_argument('--chars', type=int, default=3500)
    x.add_argument('--max', type=int, default=150)
    for name in ('check', 'merge'):
        s.add_parser(name).add_argument('batch', nargs='+')
    x = s.add_parser('fit')
    x.add_argument('text')
    x.add_argument('--window', default='box', choices=sorted(windows.WINDOWS))
    x = s.add_parser('pairs')
    x.add_argument('out')
    x.add_argument('batch', nargs='+')
    s.add_parser('story')
    a = p.parse_args()
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
