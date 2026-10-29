import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM")
def test_rom_matches_sha1():
    import check_rom
    check_rom.check()


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM")
def test_rom_header():
    head = ROM.read_bytes()[:0xC0]
    assert head[0xA0:0xB2] == b"GETBACKERS\0\0AGBJA4"
