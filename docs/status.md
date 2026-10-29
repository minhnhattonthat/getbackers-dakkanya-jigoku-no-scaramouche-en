# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) done; next is phase 6 (translate).
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
- **Next:** phase 6 (translate): translator brief + glossary, batches by window (`windows.window_of`), budgets
  from `tools/windows.py` (box: 3 x 216 px; help: 1 x 232 px; names/items short). Write `{br}` breaks by
  `vwf.width` (the hook only auto-wraps mid-word as a fallback).
- **Open (not blocking):**
  - Windows still a guess (tools/windows.py): yes/no (0x30F28, 6-tile window), item names in the field found/full
    message, ENEMIES menu names/bios and battle quips (tables 0x65000/0x68000, assumed help bar). Tour them in
    phase 8 (warped party has no items/enemy log).
  - `work/states/*.mss` were last made from the marker build: rerun `warp_all.py` on the English build.
  - Title entries bonus stage / boss retry: conditions unknown (cleared game, lost boss?); modes 0x10/0x11 are
    reached by a mode request, not their real field exit (find a map exit with target 0xEF/0xF0/0xFA-0xFD).
  - Warped party is a new game's (Ginji only, level 1): no GOD/NOENC yet (no HP address); add if a QA route dies.
  - Text that needs no translation but is `todo`: full-width numbers 0x2E604-0x2E858; batches can carry en = jp.
  - 0x6AF14 save-file message (code-referenced, outside the block) stays Japanese; add to `jp_left.py --known`.
  - Recon leftovers: 7NEWS headline strip loader; printf callers of the 12 `%s/%d` strings and the `α/β` menu
    labels; 0x3E8000-0x3EB7E0 tables; free space 0x3EB7E0+ not trap-tested;
    low-confidence graphics rows (check now with the warp tool in phase 8).
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: the game's own English labels spell Kazuki `KADSUKI`
  (battle stats/names); D2 (official names) suggests `KAZUKI` - default: change it when those labels are redrawn.
  Not checked: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a human at the window).
