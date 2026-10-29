import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
ROM = ROOT / "rom" / "GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM")
def test_director_decode_matches_play():
    import director
    d = ROM.read_bytes()
    steps = {}
    for i in range(director.CASES):
        t = int.from_bytes(d[director.TABLE - 0x08000000 + i * 4:][:4], "little") & ~1
        steps[i + 1] = [director.fmt(c) for c in director.decode(d, t)]
    # the calls logged by tools/debug/scenelog.lua in a mashed new game
    assert steps[1] == ["EVT(1,2,?,?)"] and steps[2] == ["EVT(1,1,?,?)"] and steps[4] == ["EVT(2,1,?,?)"]
    acts = [n for n, c in steps.items() if any(x.startswith("ACT(") for x in c)]
    assert acts == [3, 55, 98, 123, 184, 209, 242]


def test_scene_list_steps_in_range():
    lines = (ROOT / "tools" / "debug" / "scenes.txt").read_text(encoding="utf-8").splitlines()
    rows = [m.groups() for l in lines if (m := re.match(r"^(\w+)\s+(\d+)\s+([0-9A-Fa-f]+)", l))]
    names = [r[0] for r in rows]
    assert len(names) == len(set(names))
    assert all(1 <= int(r[1]) <= 269 for r in rows)
