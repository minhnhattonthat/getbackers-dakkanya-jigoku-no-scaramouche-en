# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2 (debug tool) done; next is phase 3 (identity build). No build yet.
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
- **Next:** phase 3: identity build (`tools/build.py` unpack + repack with no edits = byte-identical, as a test).
- **Open (not blocking):**
  - Title entries bonus stage / boss retry: conditions unknown (cleared game, lost boss?); modes 0x10/0x11 are
    reached by a mode request, not their real field exit (find a map exit with target 0xEF/0xF0/0xFA-0xFD).
  - Warped party is a new game's (Ginji only, level 1): no GOD/NOENC yet (no HP address); add if a QA route dies.
  - Recon leftovers: 7NEWS headline strip loader; printf callers of the 12 `%s/%d` strings and the `α/β` menu
    labels; one pointer mid-string (0x2DBBC); 0x3E8000-0x3EB7E0 tables; free space 0x3EB7E0+ not trap-tested;
    low-confidence graphics rows (check now with the warp tool in phase 8).
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: the game's own English labels spell Kazuki `KADSUKI`
  (battle stats/names); D2 (official names) suggests `KAZUKI` - default: change it when those labels are redrawn.
  Not checked: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a human at the window).
