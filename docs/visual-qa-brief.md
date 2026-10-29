# Visual-QA reviewer brief - GetBackers Dakkanya: Jigoku no Scaramouche (GBA)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 "$(python tools/skill.py)/scripts/sheet.py" SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png`
  (scratch = `work/qa/zoom/<chunk>_*.png`) and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- English the original already had: HP/AT/DE/SP/LV labels, character name plates (`GINJI`, `BAN`, `KADSUKI` -
  the game's own spelling, a known open item), `HONKY TONK` card, KCE Japan logo, `MISSION FAILED`, `DUEL`, `ACT.n`.
- Dialogue boxes hold 3 lines in a proportional font; the original held 2. Speaker names sit inside the text
  (`Ginji: ...`), not in a separate plate.
- Hyphenated item/skill card labels (`Thunder-`/`bolt`, `Thunder-`/`clap`) and the short label `Lightning Emperor`
  are deliberate (fixed-size cards).
- Tour shots are taken every 120 frames while the tour mashes A, so most boxes are caught mid-typing or between
  pages; judge only what is fully drawn.
- Parrot Paro speaks in capitals.
- The isometric field after a warp may show the party standing in an odd spot or a black fade: the warp, not a bug.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
