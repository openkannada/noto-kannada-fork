# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""The release steps after the build: static renames, WOFF2, the web subset, the specimen
and the checksums. The build itself (gftools builder) runs in the release workflow."""

import hashlib
import sys
from pathlib import Path

import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from test_kannada_fixes import BUILD, CONSONANTS, FONTS, VIRAMA

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import release  # noqa: E402
import rename  # noqa: E402
import specimen  # noqa: E402

SAMPLES = ["೜", "ಕ್ಷ್ಮ್ಯ", "ಸ್ತ್ರೀ", "ರ್ಕೈ", "ಕೃಷ್ಣ", *(c + VIRAMA + "ರ" for c in CONSONANTS)]


@pytest.fixture(scope="module")
def sans(tmp_path_factory):
    names = rename.load("sans")
    out = tmp_path_factory.mktemp("sans")
    font = rename.rename(TTFont(BUILD / FONTS["sans"]), names)
    path = out / "variable" / rename.file_name(font, names)
    path.parent.mkdir()
    font.save(path)
    return names, out, path


def shape(data: bytes, text: str, variations: dict | None = None):
    font = hb.Font(hb.Face(data))
    if variations:
        font.set_variations(variations)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return [
        (i.codepoint, p.x_advance, p.x_offset, p.y_offset)
        for i, p in zip(buf.glyph_infos, buf.glyph_positions, strict=True)
    ]


def test_static_fonts_are_renamed_by_postscript_name(tmp_path):
    names = rename.load("sans")
    static = instantiateVariableFont(
        TTFont(BUILD / FONTS["sans"]), {"wght": 700, "wdth": 100}, updateFontNames=False
    )
    static.save(tmp_path / "NotoSansKannada-Bold.ttf")
    written = release.renamed(tmp_path, names, tmp_path / "out", "ttf")
    assert [p.name for p in written] == ["NehaSans-Regular.ttf"]
    assert rename.leftovers(TTFont(written[0])) == []


def test_condensed_static_family_is_accepted():
    names = rename.load("sans")
    font = TTFont(BUILD / FONTS["sans"])
    for record in font["name"].names:
        if record.nameID == 1:
            record.string = "Noto Sans Kannada Condensed"
    rename.rename(font, names)
    assert font["name"].getDebugName(1) == "Neha Sans Condensed"


def test_woff2_keeps_the_font(sans, tmp_path):
    _, _, path = sans
    web = release.woff2(path, tmp_path)
    assert web.suffix == ".woff2" and TTFont(web).flavor == "woff2"
    assert TTFont(web).getGlyphOrder() == TTFont(path).getGlyphOrder()


def test_web_subset_covers_kannada_and_shapes_like_the_full_font(sans, tmp_path):
    names, _, path = sans
    web = release.web_subset(path, tmp_path, names)
    assert web.name == "NehaSans-Kannada[wght].woff2"
    font = TTFont(web)
    assert [a.axisTag for a in font["fvar"].axes] == ["wght"]
    full_cmap = TTFont(path).getBestCmap()
    kannada = {cp for cp in full_cmap if 0x0C80 <= cp <= 0x0CFF}
    assert kannada <= set(font.getBestCmap())
    full, cut = path.read_bytes(), web.read_bytes()
    full_names, cut_names = TTFont(path).getGlyphOrder(), font.getGlyphOrder()
    for weight in (100, 400, 900):
        for text in SAMPLES:
            before = shape(full, text, {"wght": weight, "wdth": 100})
            after = shape(cut, text, {"wght": weight})
            named_before = [(full_names[g[0]], *g[1:]) for g in before]
            named_after = [(cut_names[g[0]], *g[1:]) for g in after]
            assert named_before == named_after, (weight, text)


def test_specimen_fills_every_field_and_shows_the_new_letter(sans):
    names, out, path = sans
    page = specimen.write(out, names.family, names.version, "Based on X.", path).read_text()
    assert "{{" not in page
    assert f'url("webfonts/{path.stem}.woff2")' in page
    cmap = TTFont(path).getBestCmap()
    for cp, _, label in specimen.NEW_LETTERS:
        assert (label in page) == (cp in cmap), label
    for fixed in ("ಹಲ್ಲೆಗಳಿಗೆ", "ತಿಳಿಯಪಡಿಸುವ", "ವ್ಯವಸ್ಥೆ", "ನೈಸರ್ಗಿಕಾಭಿವೃದ್ಧಿಗೂ"):
        assert fixed in page


def test_checksums_list_every_file(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("b")
    lines = release.checksums(tmp_path).read_text().splitlines()
    assert lines == [
        f"{hashlib.sha256(b'a').hexdigest()}  a.txt",
        f"{hashlib.sha256(b'b').hexdigest()}  sub/b.txt",
    ]
