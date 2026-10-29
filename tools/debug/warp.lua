-- Warp to any story step from a cold boot (docs/re/scenes.md).
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='act2'" --frames 900 --sheet
-- SCENE: a name from tools/debug/scenes.txt, or 'step:N' for story step N (1-269, tools/debug/director.py).
-- How: boot presses Start/A through the title into NEW GAME; when the story director (0x08021548) first reads the
-- step counter (u16 0x030042C0), the step is overwritten, so the game itself runs that step's scene call (event,
-- field, battle, act card, ending) the way it does in play. After arrival (the game mode the step implies) the
-- entry's route, if any, is played: "N buttons" steps as in route files, and "@X" requests game mode X
-- (0x03002BAA) at that point, for screens with no story step of their own (game over, location card).
-- Opt-in: SHOT_AT=N extra shot N frames after arrival. Click through text with emu.py --mash N (it also clicks
-- through the title); save a state with emu.py --state-out. tools/debug/warp_all.py runs the whole list.
local M = emu.memType.gbaMemory
local MODE, STEP, DIRECTOR = 0x03002BA8, 0x030042C0, 0x08021548
local SCENES = SCENES_FILE or "../debug/scenes.txt"  -- Mesen runs in tools/mesen/

local function find_scene(name)
  local n = name:match("^step:(%d+)$")
  if n then return { step = tonumber(n), route = "" } end
  for line in io.lines(SCENES) do
    local nm, st, route = line:match("^([%w_]+)%s+(%d+)%s+%x+%s*([^#]*)")
    if nm == name then return { step = tonumber(st), route = (route:gsub("%s+$", "")) } end
  end
  error("scene not in " .. SCENES .. ": " .. name)
end

local scene = find_scene(assert(SCENE, "set --var \"SCENE='name'\""))
local warped, arrived, pokes = false, nil, {}
L.log(string.format("scene %s step %d route '%s'", SCENE, scene.step, scene.route))

L.on_exec(DIRECTOR, DIRECTOR, function()
  if warped then return end
  warped = true
  emu.write16(STEP, scene.step, M)
  L.log(string.format("f%d warp: step %d", L.frame, scene.step))
end)

local boot_press = 0
local modes_seen = {}
L.on_frame(function(f)
  local mode = emu.read(MODE, M)
  if not warped then
    if mode == 0xA or mode == 0xB then  -- the title cursor sat on CONTINUE: a battery save is present
      error("loaded a save instead of NEW GAME: run with --sav of a blank save (warp_all.py does)")
    end
    -- title (4) or logos (3): Start, then A on NEW GAME (the cursor starts there when no save exists)
    if (mode == 3 or mode == 4) and f - boot_press >= 30 then
      boot_press = f
      L.press((f // 30) % 2 == 0 and "start" or "a", 6)
    end
    return
  end
  if not arrived and mode ~= 9 and mode ~= 4 and mode ~= 3 then
    arrived = f
    L.log(string.format("f%d arrived: mode %X", f, mode))
    L.shot(string.format("arrive_%06d.png", f))
    local t = f
    for step in scene.route:gmatch("[^;]+") do
      local n, keys = step:match("^%s*(%d+)%s+(%S+)")
      local poke = step:match("^%s*@(%x+)")
      if n then L.press(keys, tonumber(n)); t = t + tonumber(n) end
      if poke then pokes[t + 1] = tonumber(poke, 16); L.press("-", 2); t = t + 2 end
    end
  end
  if pokes[f] then
    L.log(string.format("f%d request mode %X", f, pokes[f]))
    emu.write(MODE + 2, pokes[f], M)
  end
  if arrived and SHOT_AT and f == arrived + SHOT_AT then L.shot(string.format("at_%06d.png", f)) end
  if arrived and not modes_seen[mode] then
    modes_seen[mode] = true
    L.log(string.format("f%d mode %X", f, mode))
  end
end)
