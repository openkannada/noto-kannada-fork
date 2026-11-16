"""Shaping tests for the Kannada fixes in this fork, run on both variable fonts."""

import os
from pathlib import Path

import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont

BUILD = Path(os.environ.get("BUILD", Path(__file__).parent.parent / "build"))
FONTS = {"sans": "sans/NotoSansKannada-VF.ttf", "serif": "serif/NotoSerifKannada-VF.ttf"}
VIRAMA, ZWJ, ZWNJ, RA, YA = "\u0ccd", "\u200d", "\u200c", "\u0cb0", "\u0caf"
R_SIGN, ARCHAIC_SHRII = "\u0cc3", "\u0cdc"
CONSONANTS = [chr(cp) for cp in [*range(0x0C95, 0x0CBA), 0x0CDE] if cp not in (0x0CA9, 0x0CB4)]


class Font:
    def __init__(self, path: Path):
        self.hb = hb.Font(hb.Face(path.read_bytes()))
        self.tt = TTFont(path)
        self.names = self.tt.getGlyphOrder()

    def glyphs(self, text: str) -> list[str]:
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        buf.flags = hb.BufferFlags.REMOVE_DEFAULT_IGNORABLES
        hb.shape(self.hb, buf)
        return [self.names[i.codepoint] for i in buf.glyph_infos]


@pytest.fixture(scope="module", params=sorted(FONTS))
def font(request) -> Font:
    return Font(BUILD / FONTS[request.param])


def test_ra_with_vocalic_r_sign_stays_2_glyphs(font):
    # notofonts/kannada#61: the sequence was drawn as the vowel letter with a reph.
    cmap = font.tt.getBestCmap()
    assert font.glyphs(RA + R_SIGN) == [cmap[ord(RA)], cmap[ord(R_SIGN)]]


def test_zwnj_before_the_virama_forms_the_subscript_like_zwj(font):
    # Kannada Wikipedia uses ra + ZWNJ + virama like ZWJ (see the closed notofonts/kannada PR #65).
    assert font.glyphs(RA + ZWNJ + VIRAMA + YA) == font.glyphs(RA + ZWJ + VIRAMA + YA)


def test_zwj_before_the_virama_still_forms_the_subscript(font):
    assert font.glyphs(YA)[0] not in font.glyphs(RA + ZWJ + VIRAMA + YA)


def test_every_consonant_pair_still_forms_a_conjunct(font):
    broken = [
        a + VIRAMA + b
        for a in CONSONANTS
        for b in CONSONANTS
        if font.glyphs(a + VIRAMA + b) == font.glyphs(a + VIRAMA + ZWNJ + b)
    ]
    assert broken == []


def test_archaic_shrii_has_a_glyph_with_ink(font):
    name = font.tt.getBestCmap().get(ord(ARCHAIC_SHRII))
    assert name is not None
    glyph = font.tt["glyf"][name]
    assert glyph.numberOfContours > 0
