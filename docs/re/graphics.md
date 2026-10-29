# Graphics-text survey

Static sweep (2026-10-30): `tools/gfxsweep.py` rendered every raw range and LZ77 block, 4bpp and 8bpp
(`work/sweep4`, `sweep8`: raw + pointer-reached LZ; `sweepz4`, `sweepz8`: LZ blocks no pointer reaches, tilemaps
skipped; `sweepm4`: blocks a looser tilemap rule had skipped). Nine read-only reviewer agents listed every
lettered cell; their lists are in `work/sweep_findings/*.md` (not in git). Tour: cold boot -> title -> NEW GAME ->
7NEWS intro (`work/qa/recon1`). Mid-game screens get confirmed by warping once the debug tool exists (phase 2).

`Z<off>` = LZ77 block at that ROM offset; "map" = the BG tilemap block that lays the tiles out (usually the next
block). Offsets are for the dump in `rom.sha1`. D5: translate all of it; only the logo may stay if no English one.

## Japanese (to translate)

Status column: **EN** = redrawn by `tools/cards.py` (the build applies it) and seen English in a cold-boot shot;
**EN (static)** = redrawn, not yet seen in-game; **open** = still Japanese / not located.

| Element | Data | Notes |
|---|---|---|
| Title logo subtitle 地獄のスカラムーシュ and two copyright lines | Z29E49C tiles (ptr literal 0x70D0), palette tiles-0x200, map tiles+0x6574 (Z2A4A10) | **EN**: "Scaramouche of Hell" (inpainted, outlined), copyright redrawn. Z29D860 (0x704C, same layout) = KCE Japan logo, English |
| Location cards (8bpp, 64 px wide, caption = last 2 rows of 12 tiles): サザナミ・コーポレーション, 裏都庁, 裏新宿中央公園, 腹黒興業組長邸?, 裏新宿西病院, キモジ'sペット店, 裏新宿駅 (HONKY TONK is EN) | Z2AB280, Z2ACEDC, Z2AFEE4, Z2B1C6C, Z2B33DC, Z2B4D14, Z2B66E8 (EN: Z2AE7D0) | **EN** all 7 (`cards.LOC`), each seen in-game: `location_card` + `warp.lua` `CARD=1-9` (1 park, 2 mansion, 3 Honky Tonk, 4 hospital, 5/8 station, 6 Sazanami, 7 pet shop, 9 Ura-Tocho) |
| Possible sign | Z314590 +800 (8bpp) | **open**: low confidence, check in-game |
| 7NEWS headline strip `裏都庁強制捜査開始か？` and photo caption `裏都庁` | Z1A6480 (16-wide sheet: strip = cols 9-15 of rows 0-7, photo = rows 1-8 cols 0-8), rewritten in place | **EN**: "Ura-Tocho Raid Underway?", "URA-TOCHO". Same strip at step 237 (no second headline: the old `…可決？` note was wrong) |
| Staff credits: スタッフ + 16 role/name cards + (C) 2001 card | card table 0x6A888 (tiles, map, palette) x 17 | **EN** (credits_staff warp shows the first card; the rest **EN (static)**). Readings not confirmed: see status.md |
| End cards 終, いい夢、見れたかい？ | card table 0x6A888 entries 17, 18 | **EN (static)**: "The End", "Enjoy your dream?" |
| Chapter cards ACT.1-6 + final `ACT OF...` with Japanese titles | card table 0x6A970 x 7 | **EN**: all 7 seen (work/qa/warp_cards) |
| Item cards (24) | Z2CF684, Z2D0718, Z2D1878: 32-tile-wide sprite sheets, 64x32 cards, blanks after the names | **EN**: `cards.ITEMS` (glossary names); in place. All 24 seen in the ITEMS menu (`warp.lua` `ALL=1`, `menu_items` + R) |
| Skill-name labels (44) | Z2D2A24, Z2D3928, Z2D49F0, Z2D5BCC, Z2D6D74, Z2D8074 (table-reached: rewritten in place) | **EN**: names from the script; 21 seen in the SPECIAL menu with `ALL=1` (Ginji 4, Shido 4, Kazuki 4, Himiko 8, Akabane 1; the sheet is picked by character id, struct byte 0), the other 23 (Ban's sheet, later skills: unlock bits not found) static only; 雷帝降臨 label = "Lightning Emperor" (`cards.SHORT`) |
| Brush-kanji fragment (bottom row only) | Z2C441C +0 | **open**: 18 tiles, no pointer; probably unused (no card uses it) |
| Shop-sign sprites (やきとり lantern, another kana sign) | Z11C08C (+C00..+1400, cols 12-15, 28-31) | **open**: field map props, check in-game |
| Small 8 px kana はい/いいえ and の beside a chibi sprite | Z1ABD44 (+1800..+1C00) | **open**: medium confidence; check in-game |
| Text-block 8x8 font (ASCII + half-width katakana) | raw 0x2FA64-0x30E43 | a font, not a label: see text.md |

## English already (keep; check fit with names in glossary.md)

Title menu NEW GAME/CONTINUE/REVENGE/BONUS (Z2A4F7C); MISSION FAILED (Z2B83AC); `?? KEYLOCK` (Z2B93E8, partial);
7-segment Err/YES (Z2B98B0); save UI NO SAVE DATA./Cancel (Z2CB1C4); GOOD:/BAD: (Z2CB9C4); battle stats + party
names BAN, SHIDO, HIMIKO, MANEKINEKO, GINJI, KADSUKI, AKABANE (Z2CBFFC, Z2D8D8C); pause menu AFFINITY ... BACK
(Z2CC5B0); battle commands ATTACK ... ESCAPE (Z2CDB78); ATK/DEF/SPD/EVD/TEN, COOL!!/JUST!!/GOOD!/BAD..., LVUP,
ALL CLEAR (Z2D91D4); battle intro HEAVEN OR HELL / DUEL (Z2DA7A0 .. Z2EB950); 7NEWS logos (Z1A6480).
`KADSUKI` is the game's own romanization; D2 says official names (Kazuki): decide when the glossary is built.

## Not text
Robot sprite `01` (Z3399F8); building-front pseudo lettering (Z186D8C, low confidence: check in-game); notice-board
dashes (Z0D78D0); key-item icons with illegible micro-print (Z2CCF74).
