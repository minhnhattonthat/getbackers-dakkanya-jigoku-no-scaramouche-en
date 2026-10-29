# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 done: v1.0 published 2026-10-30 at the user's request (repo public, GitHub release v1.0 with the zip).
- **Done (phase 1):** `docs/re/` records encoding (Shift-JIS, `α` 0x83BF = line break, printf `%s/%3d/%6d`),
  the dialogue box (12 px cells, 20 chars x 2 lines, auto-wrap), the 12x12 SJIS font (0x26E200) and an 8x8 ASCII
  font (0x2FA64), the string block 0x2DB4C-0x62350 with absolute u32 pointers (tables 0x63000-0x98000), LZ77,
  ROM map and free space (`rom-map.md`), and the graphics-text survey (`graphics.md`).
- **Done (phase 2):** `docs/re/scenes.md`: game modes (table 0x08000244), the story director (u16 step
  0x030042C0, 269 linear steps, `tools/debug/director.py`), warp by step. `tools/debug/warp.lua` + `scenes.txt`
  (73 entries: opening, 7 act cards, first event/field per act, all 36 battles, staff credits, ending, field menu
  pages, save, game over, location card, modes 0x10/0x11); `tools/debug/warp_all.py` warps all of them from a cold
  boot with a proof shot and `work/states/<name>.mss` (last run: all ok, `work/qa/warp_all/sheet*.png`). Title
  CONTINUE: `tools/routes/title_continue.txt` + `--sav work/saves/act1_field.sav` (made by warp_all).
- **Done (phase 3):** `tools/build.py` (rom.sha1 check, `tools/rom_text.py` unpack + repack of the string block,
  romdiff write-log check, `build/writes.txt`) gives a byte-identical ROM with no edits
  (`tests/test_build.py`, also relocation-to-0x400000 + repoint and in-place shorter-text tests). Smoke ok.
- **Done (phase 4):** `tools/extract.py` -> `script/*.json` (28 files, 6139 entries: 5344 text / 95k JP chars, 795
  `data` with a note); build writes `en`. `α` = `{br}` control (also the yes/no separator). Pointer sources limited
  to code + tables (`rom_text.PTR_SRC`, coincidental words in graphics/byte tables excluded); empty-string pointers
  into padding shrink the owner's slot. `tests/test_script.py`: roundtrip, script == ROM, coverage, pointer targets,
  data never silent, en lint (encodable, printf order, leading/trailing blanks), build applies en, re-dump keeps en.
  Details: `docs/re/text.md` §Script.
- **Done (phase 5):** VWF engine `tools/vwf.py` (Thumb at 0x08400000, keystone, MIT `fonts/font_en.txt` from the
  sibling repo): all three 12x12 draw paths hooked (A field box + yes/no, B event dialogue, C help bar). English =
  1 byte per char (`vwf.en_table()`), Shift-JIS still drawn, `{br}` kept. Dialogue and field boxes now hold 3 lines
  x 216 px (11 px pitch); help bar 1 line x 232 px / 47 bytes; yes/no keeps 16 px pitch. Width gate:
  `tools/windows.py` (budgets + entry -> window by pointer location) checked by the en lint. Marker build
  `tools/build.py --marker` (+ `--qa ID=TEXT` overrides): boots, 73/73 warps ok, every box shows `#id`; torture line
  (all glyphs) ok. `jp_left.py --gba-ptrs` on it: nothing missed (only the known 0x6AF14 and a byte-table hit).
  Text tour: `tools/debug/text_tour.py` + `textlog.lua` (which entries each path shows, per event step). Last run
  on the marker build (stopped by the harness for low memory at 136/147 event steps; `--logs-only` aggregates):
  all 136 arrived, no hang, 1600 entries shown (B; one A, 0x37094), 0 mismatches with `windows.window_of`.
  `work/qa/text_tour/seen.tsv`. Rerun with `--jobs 2` when memory allows (steps not yet logged: 11).
  Tests: `tests/test_vwf.py` (unicorn), marker-fills-window, hook branch-target check. Details: `docs/re/text.md`.
- **Done (phase 6):** all 5344 text entries `done` in `script/` (36 batches b001-b036, 9 translator agents, 9
  reviewer passes: 0 Critical; every Important and most Minors fixed by the original translator; project sweeps for
  UK spelling, "sir" to Scaramouche, "Tocho"/abbreviations clean). `tools/batches.py` split/check/merge/fit/pairs/
  story (`tests/test_batches.py`): translators write prose, the merge word-wraps box pages with `{br}` at 216 px and
  keeps the JP's leading/trailing blank; the check enforces ids, printf, `{br}` count, font chars, width, speaker
  labels and honorifics from `glossary.md` (generic "Label" rows: speaker only). Docs: `docs/translator-brief.md`,
  `docs/reviewer-brief.md`, `docs/style-reference.md`, `docs/synopsis.md`, `glossary.md` (302 terms + batch
  decisions). Batch files live in `work/tl/` (gitignored; `script/` is the source of truth). Build + smoke ok
  (sha1 7fe398ca...). Opening dialogue checked in-game (step 4): wraps cleanly in 3 lines.
- **Done (phase 7):** build gate: romdiff write log + allowed ranges (string block, VWF hooks, 0x400000+, single
  pointer words) + 32 MiB cap; `tests/test_insert.py` (builds its own ROM: every entry reads back through every
  pointer, no stale reader of moved text, `jp_left.py --slots build/slots.txt --known tools/jp_known.txt` clean);
  stored-script lint = `batches.check_entry(stored=True)` (glossary, speakers, honorifics, `{br}`/printf, font,
  stub last lines, no empty en). Balanced box wrap (`batches.wrap` DP; `batches.py rewrap` re-wrapped 1363
  entries, 125 stubs gone). Details: `docs/re/text.md` §Insert checks. Check 32 passed; smoke ok
  (sha1 aaf24002...); step 4 warp draws the opening line.
- **Phase 6 review fixes (2026-10-30):** the batch check / stored lint now require every glossary term's EN form
  (`batches.has_term`, neighbour pages via `near_text`, `Label`/`Loose` glossary notes, one-offs in `GLOSS_OK`);
  Ban's オッチャン = "old man" (5 lines), Paro in caps (7 lines), ハンバーガー = hamburger (2 lines).
- **Phase 8 in progress:** graphics redrawn with the VWF font (`tools/letter.py`) in `tools/cards.py` (build applies
  it, repoints): 26 picture cards (17 credits, 2 end cards, 7 act cards: tables 0x6A888/0x6A970), 7 location card
  captions (palette -0x200 + tiles + map moved as one; all 7 seen in-game with `warp.lua` `CARD=1-9`), title
  subtitle "Scaramouche of Hell" + copyright (inpainted, checked in-game). Staff name readings not confirmed:
  田辺裕詞 Hiroshi, 鈴木謙子 Kenko, 中原郁奈子 Ikunako, 北上一三 Kazumi, 杉本憲英 Norihide (cards.EN 10-14).
  Item cards (24) and skill labels (44): sheets rewritten in place (`cards.SHEETS`), names from the script; with
  `warp.lua` `ALL=1` all 24 item cards and 21 skill labels seen in the menus (Ban's sheet and later skills: unlock
  bits not found, static only). Non-blocking: the 雷帝降臨 label reads "Lightning Emperor" (body 22 px: 2 lines;
  `cards.SHORT`, D4 last resort); Thunder-bolt/Thunder-clap hyphenated. 7NEWS headline + caption in English
  (seen, step 1). Z29D860 (0x704C) = KCE Japan logo, English. `warp_all.py` on the English build: 73/73 ok
  (`work/states/` now English).
  Last graphics rows closed: field signposts Z11C08C -> PET/ZOO, BIRD/PARK and Ginji's sheet Z1ABD44 はい/いいえ ->
  Yes/No (static: no screen found by `tools/debug/gfxscan.py` over 54 field maps + 36 battles), Z314590 texture,
  Z2C441C unused. Text tour on the English build (`work/qa/tour_en`): 147 event steps (B 1832 entries seen) +
  battle steps 20-149; the run for battles 152-267 was stopped by the harness for low memory (rerun:
  `text_tour.py build/getbackers_en.gba --jobs 2 --out work/qa/tour_en --scenes step:152 step:159 ...`, then
  `--logs-only`). Sheets: `sheet.py DIR --changed 0.02 --div 1 --max 16 --cols 4` per scene + `zz_gfx/` proofs;
  `work/qa/manifest.tsv` 324 sheets, 11 chunks (`work/qa/chunks`), verdicts in `work/qa/verdicts`. No `tour_jp`.
  Visual QA (3 rounds, 17 reviewer agents) found and fixed: third-line descenders cut by the screen bottom (VWF:
  `Y_LIFT` 2 and `plot` now skips rows above canvas y 0 instead of clamping, so pitch stays 11 px; test
  `test_first_line_lifted_above_canvas_keeps_pitch`), bold lettering filling 1 px gaps (m, w) on act cards and
  credits (`letter.draw`), Japanese ruby + 奪還屋 badge on the title logo (D5: removed), countdown/sign indents
  (JP centring kept), narrower `j`, Ban's split page; stale shots (taken before a graphics build) re-shot.
  Tour sheets other than the re-shot ones predate the 1 px text lift (checked on B 3-line pages, the field box A
  and the yes/no window: fine).
  Round 3-4: all re-shot sheets ok; the title's old badge area under the "s" was a smear of row 57 (now body red,
  `cards.title_english`). Battle tour re-run (`--jobs 2`) stopped again by the harness for low memory: battles
  159-225 done (12, sheets in the manifest, round 5 = `work/qa/chunks5`), 229-267 not run (9 battles; partial
  dirs step_229/232 have no sheet). `--logs-only` over every step dir: B 1410 seen (the re-shot scenes replaced
  their longer logs). Phase 9 ready: `tools/release.py` (build, check, smoke, jp_left, qa_gate, BPS + re-apply,
  zip) + `docs/README_release.txt`.
- **Done (phase 8):** round 5 (26 sheets) all ok; `;` glyph tail lowered (read as a colon). `qa_gate.py check`:
  353 sheets, exit 0.
- **Done (phase 9):** `tools/release.py` all green (build, 34 tests, smoke, jp_left 0 runs, qa_gate, BPS made +
  re-applied): `release/GetBackers_Dakkanya_Jigoku_no_Scaramouche_EN_v1.0.zip` (BPS 388894 bytes, sha1 5320d237...;
  README.txt). Base CRC32 C0A0A979, patched CRC32 A0726B81 / sha1 7f5a80fe... (= `build/getbackers_en.gba`).
- **Next:** player bug reports (GitHub issues). Battles 229-267 tour when memory
  allows (`text_tour.py build/getbackers_en.gba --jobs 1 --out work/qa/tour_en --scenes step:229 ...`).
- **Phase 8 checks from translation:** 0x2DE14 `の経験値を得た` -> " EXP gained" (how the number joins it);
  item found/full message `"` + name + `" found!` (0x30F4C/50/60); 0x2F0E0 Alpha label; 0x31538 Pochi's Room sign
  alignment; help-bar printf lines with long names (`%s` budget counts 8 W). Paro (parrot) speaks in caps.
- **Open (not blocking):**
  - Windows still a guess (tools/windows.py): yes/no (0x30F28, 6-tile window), item names in the field found/full
    message, ENEMIES menu names/bios and battle quips (tables 0x65000/0x68000, assumed help bar). Tour them in
    phase 8 (warped party has no items/enemy log).
  - Title entries bonus stage / boss retry: conditions unknown (cleared game, lost boss?); modes 0x10/0x11 are
    reached by a mode request, not their real field exit (find a map exit with target 0xEF/0xF0/0xFA-0xFD).
  - Warped party is a new game's (Ginji only, level 1): no GOD/NOENC yet (no HP address); add if a QA route dies.
  - Text that needs no translation but is `todo`: full-width numbers 0x2E604-0x2E858; batches can carry en = jp.
  - 0x6AF14 developer note copied into the save data (never shown) stays Japanese; listed in `tools/jp_known.txt`.
  - Recon leftovers: 7NEWS headline strip loader; printf callers of the 12 `%s/%d` strings and the `α/β` menu
    labels; 0x3E8000-0x3EB7E0 tables; free space 0x3EB7E0+ not trap-tested;
    low-confidence graphics rows (check now with the warp tool in phase 8).
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: the game's own English labels spell Kazuki `KADSUKI`
  (battle stats/names); D2 (official names) suggests `KAZUKI` - default: change it when those labels are redrawn.
  Not checked: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a human at the window).
