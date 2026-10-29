# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon) done; next is phase 2 (debug tool). No build yet.
- **Done (phase 1):** `docs/re/` records encoding (Shift-JIS, `α` 0x83BF = line break, printf `%s/%3d/%6d`),
  the dialogue box (12 px cells, 20 chars x 2 lines, auto-wrap), the 12x12 SJIS font (0x26E200) and an 8x8 ASCII
  font (0x2FA64), the string block 0x2DB4C-0x62350 with absolute u32 pointers (every Japanese record has one;
  tables 0x63000-0x98000), LZ77 (BIOS swi 0x11; `tools/lzscan.py` + `tools/lzcomp.py`, roundtrip test), ROM map
  and free space (`rom-map.md`), and the graphics-text survey (`graphics.md`: static sweep of every raw/LZ region
  by 9 reviewer agents). Not the Jagan Fuuin engine (no PAC3). No earlier fan patch exists for this game.
  Tools: `tools/textscan.py` (string list + pointer refs), `tools/gfxsweep.py` (sweep sheets).
- **Next:** phase 2: debug tool in `tools/debug/` (warp to any scene/chapter/ending from a cold boot). Find the
  scene/chapter state in RAM (script context: text ptr at ctx+0x70, script ptr at ctx+0x64, loop 0x0801A6C0) and
  the chapter-card / credits triggers. Then use it to confirm the open graphics rows below in-game.
- **Open (recon leftovers, not blocking):**
  - 7NEWS headline strip tiles (`裏都庁強制捜査開始か？` etc.) not found in ROM or any LZ block: find the loader.
  - printf callers of the 12 `%s/%d` strings; how menu labels `α（アルファ）`/`β（ベータ）` are drawn.
  - One pointer aims mid-string (0x2DBBC); 0x3E8000-0x3EB7E0 tables not decoded; free space 0x3EB7E0+ not
    trap-tested (prefer growing the ROM).
  - Low-confidence graphics rows (Z1ABD44 kana, Z314590 sign, Z186D8C facade, Z2C441C brush fragment): check
    in-game. Blocks of `sweepm4` were only read at 4bpp.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: the game's own English labels spell Kazuki `KADSUKI`
  (battle stats/names); D2 (official names) suggests `KAZUKI` - default: change it when those labels are redrawn.
  Not checked: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a human at the window).
