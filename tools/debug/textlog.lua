-- Probe: log which text each 12x12 draw path starts (docs/re/text.md §Draw paths). One line per string start:
--   TXT <path> <ROM offset of the char>   path A = loop 0x0801A358, B = dialogue loop, C = 0x08002188 (x table)
-- Original ROM: the three calls to 0x08019EF4 (r2 = char pointer). VWF build: vwf_step entry (ctx+0x70 = pointer).
-- Usage: --script tools/debug/textlog.lua [--script tools/debug/warp.lua --var SCENE=...]
local function reg(s, n) return s["cpu.r" .. n] or s["cpu.r[" .. n .. "]"] or -1 end
local last = {}
local function seen(path, p)
  -- a new string starts when the pointer is not the previous char + 1 or 2
  local d = p - (last[path] or -100)
  last[path] = p
  if d < 0 or d > 2 then L.log(string.format("f%06d TXT %s %06X", L.frame, path, p - 0x08000000)) end
end
for addr, path in pairs({ [0x0801A45A] = "A", [0x0801A798] = "B", [0x08002224] = "C" }) do
  L.on_exec(addr, addr, function() seen(path, reg(emu.getState(), 2)) end)
end
L.on_exec(0x08400000, 0x08400000, function()
  local s = emu.getState()
  local ctx = reg(s, 0)
  seen(reg(s, 14) < 0x0801A600 and "A" or "B", emu.read32(ctx + 0x70, emu.memType.gbaMemory))   -- lr: hook site
end)
