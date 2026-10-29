-- Probe: log the scene-change calls (docs/re/scenes.md) with their arguments and a shot:
--   EVT  0x080213B4(task, group, idx)  start event script table[group][idx] (mode B)
--   FLD  0x08021408(task, map, ...)    enter the field (mode A)
--   BTL  0x08021450(task, id)          mode D
--   ACT  0x080214A0(task, arg)         act card (mode 8), act counter u16 0x030042C0 += 1
-- Usage: --script tools/debug/scenelog.lua
local function reg(s, n) return s["cpu.r" .. n] or s["cpu.r[" .. n .. "]"] or -1 end
local names = { [0x080213B4] = "EVT", [0x08021408] = "FLD", [0x08021450] = "BTL", [0x080214A0] = "ACT" }
for addr, tag in pairs(names) do
  L.on_exec(addr, addr, function()
    local s = emu.getState()
    local act = emu.read16(0x030042C0, emu.memType.gbaMemory)
    L.log(string.format("f%06d %s r1=%X r2=%X r3=%X act=%d", L.frame, tag, reg(s, 1), reg(s, 2), reg(s, 3), act))
    L.shot(string.format("s%06d_%s.png", L.frame, tag))
  end)
end
if DUMP_KEYS then
  L.on_frame(function(f)
    if f == 10 then
      local ks = {}
      for k in pairs(emu.getState()) do if k:sub(1, 4) == "cpu." then ks[#ks + 1] = k end end
      table.sort(ks); L.log(table.concat(ks, " "))
    end
  end)
end
