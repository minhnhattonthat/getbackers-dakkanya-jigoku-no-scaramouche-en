# Game modes, story director, warp

All verified by code read plus emulator runs (`work/qa/scn1`, `work/qa/warp_all`), unless marked.

## Game mode - verified
- `0x03002BA0` system block: +8 u8 current mode, +0xA requested mode (the main loop at 0x0800030C switches when
  +0xA != +8; +0xB = previous mode), +4 u32 frame counter. A+B+Start+Select soft-resets.
- Mode entry functions: table 0x08000244 (21 entries). Keys: held u16 0x03001520, pressed 0x03001F78.

| Mode | Entry | Screen |
|---|---|---|
| 0 | - | boot, requests 3 |
| 3 | 0x080074C8 | logos (Game Boy, Konami) |
| 4 | 0x08007A50 | title + title menu |
| 6 | 0x0801954C | location card (photo + caption, graphics.md); field exit records with target 0xFE |
| 8 | 0x0801910C | ACT card (`ACT.n` + subtitle), card index u16 0x03004194 (= 0x03003E30+0x364); 6 = special |
| 9 | 0x080229C8 | fade/transition: runs the story director task (0x08021510) |
| A | 0x08019C08 | field (isometric map) |
| B | 0x08019CB8 | event (script + dialogue box) |
| C | 0x080051C8 | field menu: SPECIAL / ITEMS / CHANGE / ENEMIES / SAVE / BACK (pages 0x08002FDC..0x080037CC = save) |
| D | 0x08015A58 | battle loader ("DUEL"), then E |
| E | 0x08007C58 | battle |
| F | 0x08018544 | `MISSION FAILED...` game over, then soft reset to the logos (no mode-F write found by modesites.py: requested another way; guess: computed value) |
| 10 | 0x080177C0 | 3x4 grid screen, from field exits (0x0801D948); guess: elevator/floor panel |
| 11 | 0x080181C0 | field screen from exit targets 0xEF/0xF0/0xFA-0xFD (0x0801D932); not identified |
| 12 | 0x08022F70 | credits (text pages; step 269 adds sepia ending scenes) |
| 13 | 0x080187F8 | `スタッフ` staff-roll header |

`tools/debug/modesites.py` lists every `strb #mode -> +0xA` site.

## Story director - verified
- u16 `0x030042C0` = story step (1-269), +2 = previous step. The director task (0x08021548) does
  `switch(step - 1)` through the jump table 0x08021570 (0x10D cases); each case makes one scene call:

| Call | Function | Effect |
|---|---|---|
| EVT(g, i) | 0x080213B4 | event script `table[g][i]` (table 0x08084F24, groups 1-18), mode B. 0x030041A8/AA = g/i, script ptr 0x030041A4 |
| FLD(map, sub, x, y) | 0x08021408 | field map, mode A |
| BTL(id) | 0x08021450 | battle id -> 0x030043AE, mode D |
| ACT(n) | 0x080214A0 | act card n (0-6), mode 8; also bumps the step |
| M12 | 0x0802148C | credits, mode 0x12 (steps 240 and 269) |

- `python -X utf8 tools/debug/director.py` prints all 269 steps. Acts start at steps 3, 55, 98, 123, 184, 209,
  242; 36 battle steps; step 240 = staff credits (no scenes), 269 = ending credits with scenes.
- Case code is tail-merged: a `bl` into the director is a jump, not a call (director.py follows it).
- Event bytecode: u16 opcodes 0x00-0x23, handler table 0x0801F438 (interpreter 0x0801F40C). Not decoded further;
  the event scripts hold no text pointers (text comes from the 0x63000+ tables).

## Warp - verified (`work/qa/warp_all`)
`tools/debug/warp.lua` presses through the title into NEW GAME and, on the director's first read of the step,
writes the target step, so the game runs that step's own scene call. Party, items and flags are those of a new game
(Ginji only, level 1): fine for text QA; a mashed warp to battle step 20 won and played on through steps 21-24 on
its own. Screens with no step (game over, location card, modes 0x10/0x11) are requested with `@X` from the field;
modes 0x10/0x11 so reached are approximate (their real setup comes from a field exit record: find one in phase 8).

Saves: FLASH 64 KB, erased = all 0xFF. The title cursor starts on CONTINUE when a save exists, so warp.lua stops
with an error if the boot loads a save; `warp_all.py` boots every run on an erased save. Entry `save_done` saves
from the field menu (SAVE, Up to `Admit`, A); its file becomes `work/saves/act1_field.sav`, and
`tools/routes/title_continue.txt` with `--sav` that file shows NEW GAME / CONTINUE and loads it (field, mode A).

Not covered yet: title entries bonus stage `ボーナスステージ` and boss retry `負けたボス戦をもう一度だけ戦います`
(conditions unknown: likely a cleared game / a lost boss in the save); GOD/NOENC options (no HP address yet;
not needed so far: warped battles wait for input, and a mashed battle won).

Tools: `scenelog.lua` (log the director's scene calls with a shot), `modelog.lua` (mode changes),
`modepoke.lua` (request a mode on the title), `modesites.py`, `director.py`.
