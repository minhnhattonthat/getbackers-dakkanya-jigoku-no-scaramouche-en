# Text

Not the engine of the sibling game Jagan Fuuin (`../getbackers-dakkanya-jagan-fuuin`, PAC3 scripts, custom glyph
codes): no `PAC3` anywhere in this ROM, text is plain Shift-JIS.

## Encoding: Shift-JIS (cp932) - verified
- Decoding the ROM as cp932 gives the strings seen on screen (7NEWS intro: 0x445E8 `犯罪組織も巻き込んだ事態に
  発展するとの見込みです。` = frame 1950 of `work/qa/recon1`, boot route + mash A).
- Every character is 2 bytes: the dialogue loop reads the text with `ldrh` (0x0801A728) and steps by 2. Single-byte
  ASCII in a displayed string would misalign it (and `ldrh` needs 2-byte alignment).
- Strings are NUL-terminated and start 4-byte aligned, padded with zeros to the next 4-byte boundary.

## Control codes - partly verified
- `α` (0x83BF) = line break: the loop compares the char with 0xBF83 (byte-swapped) at 0x0801A756, resets the column
  and moves down 2 tiles. 17 strings use it (e.g. 0x310D0). Two item names use `α`/`β` literally
  (0x2F0C0 `β（ベータ）`, 0x2F0E0 `α（アルファ）`) - those are menu labels, check how the menu path draws them.
- `%s`, `%3d`, `%6d`: printf-style, in 12 system/battle strings (0x2DB70 `%sの各キャラとの相性です`,
  0x2DE24 `%sがレベルアップ！`). Guess: a sprintf at the caller; find it before translating those 12.
- Speaker names are plain text: `蛮「...」` (2718 strings) or `銀次：...` (79, near 0x2DD28).
- No other control bytes in the 0x2DB4C-0x62350 string block (strings with bytes < 0x20 there are data tables, e.g.
  0x2F624, 0x2FA84-0x2FB48 map-like `"`/0x02 runs - not text).

## Dialogue box - verified (code read)
- Typewriter draw, one char per step: 0x0801A724 reads the char, 0x08019EF4(x_tile, y_tile, ptr, subcol) draws it.
- Fixed 12 px cells: tile x = col*3/2 (col counter at script-context +0x6A). Auto-wrap when tile x > 0x1B (27):
  20 chars per line on a 240 px screen; line pitch 2 tiles (16 px). Box = 2 lines (40 chars), `▼` prompt.
  Longest string 39 chars (0x4B184).
- Script context: r4+0x64 = script pointer (u32 stream), r4+0x70 = current text pointer.

## Font - verified (draw path + render)
- 0x26E200-0x29CAA8: 7332 records of 26 bytes: u16 Shift-JIS code stored as raw bytes (lead, trail) + 12 rows x
  u16 big-endian bitmap (12x12 1bpp, MSB = left pixel). Covers 0x8140-0xEAFC (full JIS level 1+2).
- Lookup 0x0801A1AC (r0 = pointer to the char): fast index for leads 0x81-0x84 and 0x89-0x9F/0xE0-0xEA
  (`idx = (lead-0x81)*0xBC - 0x40 + trail - (trail>0x7F)`, record = 0x0826E200 + idx*26 [+0x5F7A for kanji]),
  else a linear search over all 0x1CA3+1 records. 1bpp -> 4bpp unpack at 0x0801A0C0-0x0801A1A6.
- No half-width / ASCII glyphs in this font: English needs either full-width letters (12 px each, 20 per line) or
  new glyphs plus a VWF (phase 5 decision).

## 8x8 system font - verified (VRAM dump + vramfind)
- Raw 4bpp tiles at 0x2FA64-0x30E43 (inside the string block's data area): ASCII 0x21-0x7E (`¥` for `\`) and
  half-width katakana, loaded to BG char base 0xC000 on the 7NEWS screen (`work/qa/news/ppu_000450`). Who draws
  with it (numbers, menus?) is not known yet; a ready-made 8 px Latin font if the dialogue path can use it.

## Strings and pointers - verified (scan)
- String block 0x2DB4C-0x62350 (just before the FLASH_V120 library at 0x62350): 6139 NUL-terminated records, of
  which ~5320 are Japanese text; the rest are small data tables.
- Pointers are absolute u32 `0x08000000 | offset`. 5163 of 5166 string starts in 0x20000-0x80000 have at least one
  pointer. Pointer tables sit in 0x63000-0x98000 (script/event data, item tables, name tables), plus ~70 code
  literal pools below 0x2DB00. Examples:
  - 0x6399C: menu help + item names, u32 list (`最初からゲームをプレイします`, `リカバージュース（Ｓ）`...).
  - 0x68840: party/character names, 8-byte entries (name ptr, ptr to an empty string).
  - 0x70520: field "examine" texts, 8-byte entries (two pointer slots, 0 = none).
- Strings are stored in reverse order of use inside a scene (0x50000: the last line of a talk comes first).
- One pointer aims mid-string (0x2DBBC `た`, tail of 0x2DBA8) - check before relying on it; may be a coincidental
  value.
- The full scan script: `python -X utf8 tools/textscan.py` (string list with reference counts).

## Repack (identity build) - verified (tests/test_build.py)
- `tools/rom_text.py`: `unpack` -> 6139 records (slot = record start to next record start; data records with
  bytes after their first NUL, e.g. 0x2F624, 0x2FA8C-0x2FB48, own only text + NUL), text through an in-code cp932
  table (unknown bytes `[XX]`); `repack` writes in place when it fits, else at 0x400000+ with every pointer
  rewritten. `tools/build.py` with no edits = byte-identical ROM (0 writes).
- Repoint uses every 4-aligned u32 in the ROM equal to `0x08000000|record`: a coincidental data word would be
  rewritten too. Phase 4: restrict to the decoded pointer tables + code literal pools if a moved string breaks
  something.
