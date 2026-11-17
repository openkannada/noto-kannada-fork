# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""The renamed builds carry the Open Kannada names, keep the upstream notices, and shape
exactly like the builds they come from."""

import sys
from pathlib import Path

import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from test_kannada_fixes import BUILD, CONSONANTS, FONTS, VIRAMA

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import rename  # noqa: E402

SIGNS = [chr(cp) for cp in [*range(0x0CBE, 0x0CC5), *range(0x0CC6, 0x0CC9), 0x0CCA, 0x0CCB, 0x0CCC]]
TEXTS = [c + s for c in CONSONANTS for s in ["", *SIGNS]] + [
    a + VIRAMA + b for a in CONSONANTS for b in CONSONANTS
]
NAME_IDS = (1, 2, 3, 4, 6, 16, 17, 21, 22, 25)


@pytest.fixture(scope="module", params=sorted(FONTS))
def pair(request, tmp_path_factory):
    """(style, names, source font, renamed font, renamed file)."""
    style = request.param
    names = rename.load(style)
    source = BUILD / FONTS[style]
    out = tmp_path_factory.mktemp(style)
    font = rename.rename(TTFont(source), names)
    path = out / rename.file_name(font, names)
    font.save(path)
    return style, names, TTFont(source), TTFont(path), path


def records(font, name_id):
    return [r.toUnicode() for r in font["name"].names if r.nameID == name_id]


def test_no_upstream_name_outside_the_credits(pair):
    _, _, _, font, _ = pair
    assert rename.leftovers(font) == []
    for name_id in NAME_IDS:
        assert all("noto" not in s.lower() for s in records(font, name_id))


def test_upstream_mark_only_in_the_name_table(pair):
    _, _, _, _, path = pair
    raw = path.read_bytes()
    ttf = TTFont(path)
    name_bytes = ttf.getTableData("name")
    rest = raw.replace(name_bytes, b"")
    for mark in ("Noto", "noto"):
        assert mark.encode("ascii") not in rest
        assert mark.encode("utf-16-be") not in rest


def test_family_and_postscript_names(pair):
    _, names, _, font, path = pair
    assert set(records(font, 1)) == {names.family}
    assert all(s.startswith(names.family_ps + "-") for s in records(font, 6))
    assert all(s.startswith(names.family) for s in records(font, 4))
    assert path.name.startswith(names.family_ps + "[")


def test_upstream_copyright_and_license_are_kept(pair):
    _, names, source, font, _ = pair
    for old, new in zip(records(source, 0), records(font, 0), strict=True):
        assert new == f"{old}; {names.copyright}"
    assert records(font, 13) == records(source, 13)
    assert records(font, 14) == records(source, 14)
    assert records(font, 9) == records(source, 9)


def test_description_credits_the_upstream_font(pair):
    _, names, _, font, _ = pair
    assert all(f"Based on {names.upstream} by Google" in s for s in records(font, 10))


def test_name_records_fit_google_fonts_limits(pair):
    # FontBakery googlefonts/name/line_breaks and googlefonts/name/description_max_length.
    _, _, _, font, _ = pair
    assert all("\n" not in r.toUnicode() for r in font["name"].names if r.nameID != 13)
    assert all(len(s) <= 200 for s in records(font, 10))


def test_trademark_record_is_dropped(pair):
    _, _, _, font, _ = pair
    assert records(font, 7) == []


def test_fresh_version_vendor_and_unique_id(pair):
    _, names, source, font, _ = pair
    assert font["head"].fontRevision == float(names.version)
    assert records(font, 5) == [f"Version {names.version}"]
    assert font["OS/2"].achVendID == names.vendor_id != source["OS/2"].achVendID
    assert records(font, 3) != records(source, 3)
    assert all(
        s.startswith(f"{names.version};{names.vendor_id};{names.family_ps}-")
        for s in records(font, 3)
    )


def test_renamed_font_shapes_exactly_like_its_source(pair):
    style, _, _, _, path = pair
    before = hb.Font(hb.Face((BUILD / FONTS[style]).read_bytes()))
    after = hb.Font(hb.Face(path.read_bytes()))

    def shape(font, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf)
        return [
            (i.codepoint, p.x_advance, p.x_offset, p.y_offset)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions, strict=True)
        ]

    assert [t for t in TEXTS if shape(before, t) != shape(after, t)] == []


def test_refuses_a_font_that_keeps_the_upstream_name(tmp_path):
    names = rename.load("sans")
    wrong = rename.Names(**{**names.__dict__, "upstream": "Some Other Family"})
    with pytest.raises(rename.UpstreamNameLeft):
        rename.rename(TTFont(BUILD / FONTS["sans"]), wrong)
