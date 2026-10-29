# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done; next is phase 1 (research and recon). No build yet.
- **Done:** template files filled in (AGENTS.md, README, rom.sha1, decisions D1-D7, glossary rulings). MesenCE 2.2.1 +
  GBA BIOS in `tools/mesen/` (settings copy in `tools/emu-config/`). Original ROM boots under `emu.py --smoke` with
  `tools/routes/boot.txt` (Nintendo/Konami logos -> title -> NEW GAME -> "7NEWS" intro scene, route input works).
  Plugin guard hook blocks `sed -i`/heredocs (verified). Pre-commit runs `tools/check.py` and rejected a failing test
  (verified). `tools/` has copies of `tbl.py`, `bps.py`, `romdiff.py`, `skill.py`.
- **Next:** phase 1: earlier patches/docs, text encoding (likely Shift-JIS, check with relsearch), pointer tables,
  compression (LZ77 0x10?), control codes, free space, graphics-text survey (title logo, menus, 7NEWS banner).
- **Open bugs:** none.
- **Waiting on the user:** nothing. Not checked: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a human at the
  window; emu.py writes default key mappings). Release year in README (2003) unverified.
