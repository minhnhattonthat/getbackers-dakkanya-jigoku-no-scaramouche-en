import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "GetBackers Dakkanya - Jigoku no Scaramouche (Japan).gba"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM")
def test_lz77_roundtrip_real_blocks():
    import lzcomp
    import lzscan
    d = ROM.read_bytes()
    # blocks a ROM pointer reaches (docs/re/graphics.md): 0x29CBE4-0x34xxxx
    refs = sorted({w - 0x08000000 for (w,) in struct.iter_unpack('<I', d) if 0x0829C000 <= w < 0x08350000})
    blocks = [(o, r) for o in refs if (r := lzscan.lz77(d, o))]
    assert len(blocks) >= 340
    for o, (raw, packed) in blocks[::17]:
        assert lzscan.lz77(lzcomp.compress(raw), 0)[0] == raw, hex(o)
