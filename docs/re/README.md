# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [text.md](text.md) | Shift-JIS encoding, line break, dialogue box, 12x12 font, 8x8 font, string block, pointers | verified; printf callers and the `α` menu labels open |
| [rom-map.md](rom-map.md) | ROM layout, LZ77, free space | mostly verified; 0x3E8000-0x3EB7E0 and free space untested |
| [scenes.md](scenes.md) | game modes, story director (269 steps), warp tool | verified; save-dependent title entries open |
| [graphics.md](graphics.md) | graphics-text survey (static sweep + tour) | static sweep done; tour limited to boot/intro until the debug tool |
