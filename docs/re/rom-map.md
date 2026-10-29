# ROM map, compression, free space

Header: `GETBACKERS` / `AGBJ` / maker `A4` (Konami). 4 MiB (0x400000). Save: FLASH (`FLASH_V120` at 0x62350).

| Range | Contents | State |
|---|---|---|
| 0x000000-0x02DB00 | Thumb code + literal pools (BIOS LZ77 wrapper: `swi 0x11` at 0x080267C4; CpuSet/CpuFastSet 0x080267B0) | verified (disasm) |
| 0x02DB4C-0x062350 | Shift-JIS string block (docs/re/text.md) | verified |
| 0x062350-0x063000 | Nintendo FLASH save library | verified (signature) |
| 0x063000-0x098000 | data tables: script/event records with string pointers, item and name tables | verified (pointer scan) |
| 0x098000-0x0A4C00 | 16-byte record table | seen in the sweep |
| 0x0A4C00-0x26E200 | mostly LZ77 blocks reached through tables, not direct pointers (~1566 blocks unpacking to >= 256 bytes: ~510 tile sets incl. portraits and the 7NEWS headline banners 0x1A6xxx, ~1056 tilemaps), with raw gaps | verified (7NEWS screen tiles traced to 0x1A6128.., 0x21B464, 0x21BC78 with vramfind) |
| 0x26E200-0x29CAA8 | dialogue font, 12x12 1bpp, SJIS-keyed | verified |
| 0x29CBE4-0x3482xx | 352 LZ77 (type 0x10) blocks reached by pointers (title screen 0x29E49C, title menu labels 0x2A4F7C, sprites), with palettes and maps between them | verified (decode + render) |
| 0x348xxx-0x3E8000 | raw data/maps; 16-bit tables 0x369Axx-0x36AAxx, music data from 0x36B267 | partly checked by the sweep |
| 0x3E8000-0x3EB7E0 | data with 301 pointers in (tables) | not looked at |
| 0x3EB7E0-0x400000 | zero fill (~83 KB) | free-space candidate: not trap-tested |

- LZ77: `tools/lzscan.py` (decompress, scan) and `tools/lzcomp.py` (VRAM-safe compressor), copied from the Jagan
  Fuuin repo. `tests/test_lz.py` round-trips every 17th pointer-reached block (compress -> decompress == original
  data). The compressor is not byte-identical to Konami's; repack only blocks we edit.
- Free space: the cleanest room is past the original end: the ROM can grow to 32 MiB (no EEPROM, so no 16 MiB
  limit; release as BPS). Treat 0x3EB7E0-0x400000 as a candidate only until it is trap-filled and toured.
- Pointers everywhere are absolute u32 `0x08000000|off`; repoint only inside decoded tables (docs/re/text.md).
- Sweep tool: `tools/gfxsweep.py OUTDIR [4|8]` renders every raw region and pointer-reached LZ block;
  `--new-lz` renders the LZ blocks no pointer reaches (tilemaps skipped, listed in OUTDIR/skipped_maps.txt).
  Pointer-only LZ discovery missed the whole 0x0A4C00-0x26E200 range at first: scan for headers, not pointers.
