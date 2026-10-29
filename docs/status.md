# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done; next is phase 5 (engine spike + marker build).
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
- **Next:** phase 5: font/VWF decision (12x12 SJIS font has no Latin half-width glyphs; 8x8 ASCII font exists at
  0x2FA64; box = 20 x 12 px cells x 2 lines), English encoding in the table (en currently must be cp932-encodable),
  marker build (`[id]` per string), find non-text strings, measure every box variant's width. Check how menus /
  battle / name tables draw text (other draw paths than 0x08019EF4?) and the printf callers.
- **Open (not blocking):**
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
