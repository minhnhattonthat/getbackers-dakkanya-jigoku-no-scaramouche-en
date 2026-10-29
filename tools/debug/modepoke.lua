-- Probe: on the title screen (mode 4, frame AT), request game mode POKE (0x03002BAA) and log/shoot what follows.
--   emu.py ROM --out DIR --script tools/debug/modepoke.lua --var POKE=0x10 --frames 1500 --shot-every 60
local M = emu.memType.gbaMemory
local AT = AT or 700
L.on_frame(function(f)
  if f == AT then
    L.log(string.format("f%d mode %X -> request %X", f, emu.read(0x03002BA8, M), POKE))
    emu.write(0x03002BAA, POKE, M)
  end
end)
