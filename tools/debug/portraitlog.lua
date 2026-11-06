-- Probe: which portrait each dialogue line asks for (docs/re/text.md §Portraits). One line per plain script line:
--   PORTRAIT <text ROM offset> <id, FF = none, the portraits on screen stay>
-- Hooks the return of the speaker lookup in the dialogue task (0x0801A706: r0 = id, ctx r4+0x70 = text).
-- Usage: --script tools/debug/portraitlog.lua --script tools/debug/warp.lua --var "SCENE='step:13'" --mash 40
local M = emu.memType.gbaMemory
L.on_exec(0x0801A706, 0x0801A706, function()
  local s = emu.getState()
  local r0 = s["cpu.r0"] or s["cpu.r[0]"]
  local r4 = s["cpu.r4"] or s["cpu.r[4]"]
  L.log(string.format("f%06d PORTRAIT %06X %02X", L.frame, emu.read32(r4 + 0x70, M) - 0x08000000, r0 & 0xFF))
end)
