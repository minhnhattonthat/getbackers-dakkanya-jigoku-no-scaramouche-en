-- Probe: log each change of the game mode (0x03002BA8) and of the u8/u16/u32 cells in WATCH (comma list of
-- "addr:size"), with a shot at every change. Usage: --script tools/debug/modelog.lua [--var "WATCH='0x0300xxxx:2'"]
local M = emu.memType.gbaMemory
local cells = { { 0x03002BA8, 1 } }
for spec in string.gmatch(WATCH or "", "[^,]+") do
  local a, n = spec:match("(0x%x+):(%d)")
  cells[#cells + 1] = { tonumber(a), tonumber(n) }
end
local function rd(a, n)
  if n == 1 then return emu.read(a, M) elseif n == 2 then return emu.read16(a, M) end
  return emu.read32(a, M)
end
local last = {}
L.on_frame(function(f)
  for i, c in ipairs(cells) do
    local v = rd(c[1], c[2])
    if v ~= last[i] then
      L.log(string.format("f%06d %08X = %X", f, c[1], v))
      if last[i] ~= nil then L.shot(string.format("m%06d_%X.png", f, i)) end
      last[i] = v
    end
  end
end)
