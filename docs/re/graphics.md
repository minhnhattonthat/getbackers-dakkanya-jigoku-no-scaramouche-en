# Graphics-text survey

Static sweep (2026-10-30): `tools/gfxsweep.py` rendered every raw range and LZ77 block, 4bpp and 8bpp
(`work/sweep4`, `sweep8`: raw + pointer-reached LZ; `sweepz4`, `sweepz8`: LZ blocks no pointer reaches, tilemaps
skipped; `sweepm4`: blocks a looser tilemap rule had skipped). Nine read-only reviewer agents listed every
lettered cell; their lists are in `work/sweep_findings/*.md` (not in git). Tour: cold boot -> title -> NEW GAME ->
7NEWS intro (`work/qa/recon1`). Mid-game screens get confirmed by warping once the debug tool exists (phase 2).

`Z<off>` = LZ77 block at that ROM offset; "map" = the BG tilemap block that lays the tiles out (usually the next
block). Offsets are for the dump in `rom.sha1`. D5: translate all of it; only the logo may stay if no English one.

## Japanese (to translate)

| Element | Data | Notes |
|---|---|---|
| Title logo subtitle 地獄のスカラムーシュ (+4000..+4800) and two copyright lines with kanji (+7800..+8800) | Z29E49C, 8bpp, 30-tile-wide picture starting 18 tiles in | seen in the tour (recon1 f600). Possible kanji in logo pieces Z29D860 (low confidence) |
| Location cards (8bpp, 64 px wide, caption = last 2 rows of 12 tiles): サザナミ・コーポレーション, 裏都庁, 裏新宿中央公園, 腹黒興業組長邸?, 裏新宿西病院, キモジ'sペット店, 裏新宿駅 (HONKY TONK is EN) | Z2AB280, Z2ACEDC, Z2AFEE4, Z2B1C6C, Z2B33DC, Z2B4D14, Z2B66E8 (EN: Z2AE7D0) | names also in the script text: match spellings |
| Possible sign | Z314590 +800 (8bpp) | low confidence, check in-game |
| 7NEWS intro: headline strip (`裏都庁強制捜査開始か？`, another ending `…可決？`), photo caption `裏都庁` | not found: 81 VRAM tiles of `work/qa/news/ppu_000450` match no ROM or LZ block | find the loader (DMA/LZ hook) in phase 2; several headlines exist |
| 7NEWS screen caption boxes and photo captions | Z1A6480 (+0..+C00, cols 9-15, 25-31) | small kanji, illegible in the sweep; read in-game |
| Staff credits: スタッフ + ~20 role/name cards + (C) 2001 line | Z2BCBB0 .. Z2C3CA4, each with its map block (Z2BCCA8 ..) | D3: credits in English |
| End cards 終, いい夢、見れたかい？ | Z2C4674 (map Z2C47BC), Z2C489C (map Z2C4B1C) | |
| Chapter cards ACT.1-6 + final `ACT OF...` with Japanese titles | Z2C5098, Z2C57AC, Z2C60A4, Z2C6B1C, Z2C74F0, Z2C7EC8, Z2C8B90 (maps follow each) | e.g. ACT.1 `GetBackers登場！` |
| Item cards (24): リカバージュースS/M/L, ゲンの特製ドリンク, 高麗エキス, ハンバーガー, ビッグバーガー, キュアー items, 蓬莱の玉, 激烈丹 .. 鈍精湯 | Z2CF684, Z2D0718, Z2D1878 (+0..+1C00, 8 cards each) | same names exist as text at 0x6399C: match spellings |
| Skill-name labels (44): Ban 蛇*, Ginji 雷*, Himiko 香*, Shido 擬*, Kazuki 絃*, Akabane 赤い* | Z2D2A24, Z2D3928, Z2D49F0, Z2D5BCC, Z2D6D74, Z2D8074 (8 per block, 4x2 grid of 8x4-tile labels) | one reading unsure (暗禁閉の戒?) |
| Brush-kanji fragment (bottom row only) | Z2C441C +0 | top half stored elsewhere; probably a title/card piece |
| Shop-sign sprites (やきとり lantern, another kana sign) | Z11C08C (+C00..+1400, cols 12-15, 28-31) | field map props |
| Small 8 px kana はい/いいえ and の beside a chibi sprite | Z1ABD44 (+1800..+1C00) | medium confidence; check in-game |
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
