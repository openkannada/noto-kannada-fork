# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""The renamed builds carry the Open Kannada names, keep the upstream notices, and draw and
shape exactly like the builds they come from."""

import sys
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance

from test_kannada_fixes import BUILD, FONTS

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import rename  # noqa: E402

NAME_IDS = (1, 2, 3, 4, 6, 16, 17, 21, 22, 25)
# Tables the rename may change; every other table must be byte-identical.
RENAMED_TABLES = {"name", "OS/2", "head"}


@pytest.fixture(scope="module", params=sorted(FONTS))
def pair(request, tmp_path_factory):
    """(names, source font, renamed font, renamed file)."""
    names = rename.load(request.param)
    source = BUILD / FONTS[request.param]
    font = rename.rename(TTFont(source), names)
    path = tmp_path_factory.mktemp(request.param) / rename.file_name(font, names)
    font.save(path)
    return names, TTFont(source), TTFont(path), path


def records(font, name_id):
    return [r.toUnicode() for r in font["name"].names if r.nameID == name_id]


def test_no_upstream_name_outside_the_credits(pair):
    _, _, font, _ = pair
    assert rename.leftovers(font) == []
    for name_id in NAME_IDS:
        assert all("noto" not in s.lower() for s in records(font, name_id))


def test_family_and_postscript_names(pair):
    names, _, font, path = pair
    assert set(records(font, 1)) == {names.family}
    assert all(s.startswith(names.family_ps + "-") for s in records(font, 6))
    assert all(s.startswith(names.family) for s in records(font, 4))
    assert path.name.startswith(names.family_ps + "[")


def test_upstream_copyright_and_license_are_kept(pair):
    names, source, font, _ = pair
    for old, new in zip(records(source, 0), records(font, 0), strict=True):
        assert new == f"{old}; {names.copyright}"
    for name_id in (9, 12, 13, 14):
        assert records(font, name_id) == records(source, name_id)


def test_description_credits_the_upstream_font(pair):
    names, _, font, _ = pair
    assert all(f"Based on {names.upstream} by Google" in s for s in records(font, 10))
    assert all(
        "Named for Neha Prasad, a founding member of Open Kannada." in s for s in records(font, 10)
    )


def test_name_records_fit_google_fonts_limits(pair):
    # FontBakery googlefonts/name/line_breaks and googlefonts/name/description_max_length.
    _, _, font, _ = pair
    assert all("\n" not in r.toUnicode() for r in font["name"].names if r.nameID != 13)
    assert all(len(s) <= 200 for s in records(font, 10))


def test_trademark_record_is_dropped(pair):
    _, _, font, _ = pair
    assert records(font, 7) == []


def test_fresh_version_vendor_and_unique_id(pair):
    names, source, font, _ = pair
    assert round(font["head"].fontRevision, 3) == float(names.version)
    assert records(font, 5) == [f"Version {names.version}"]
    assert font["OS/2"].achVendID == names.vendor_id != source["OS/2"].achVendID
    unique = f"{names.version};{names.vendor_id};{names.family_ps}-"
    assert records(font, 3) != records(source, 3)
    assert all(s.startswith(unique) for s in records(font, 3))


def test_only_names_vendor_and_version_change(pair):
    # Every glyph, metric and layout table is untouched, so the font draws and shapes as before.
    _, source, font, _ = pair
    assert set(font.keys()) == set(source.keys())
    for tag in set(source.keys()) - RENAMED_TABLES - {"GlyphOrder"}:
        assert font.getTableData(tag) == source.getTableData(tag), tag
    source["OS/2"].achVendID = font["OS/2"].achVendID
    assert source["OS/2"].compile(source) == font["OS/2"].compile(font)
    for field in ("fontRevision", "checkSumAdjustment", "modified"):
        setattr(source["head"], field, getattr(font["head"], field))
    assert source["head"].compile(source) == font["head"].compile(font)


def test_records_a_release_build_adds_are_renamed_too():
    # gftools release builds add typographic names, Macintosh records and instance names.
    names = rename.load("sans")
    font = TTFont(BUILD / FONTS["sans"])
    table = font["name"]
    for name_id, text in (
        (16, "Noto Sans Kannada"),
        (17, "Regular"),
        (21, "Noto Sans Kannada"),
        (22, "Regular"),
        (25, "NotoSansKannada"),
    ):
        table.setName(text, name_id, 3, 1, 0x409)
    table.setName("Noto Sans Kannada", 1, 1, 0, 0)
    table.setName("Noto is a trademark of Google Inc.", 7, 1, 0, 0)
    instance_ps = table.addName("NotoSansKannada-Thin")
    instance = NamedInstance()
    instance.subfamilyNameID = font["fvar"].instances[0].subfamilyNameID
    instance.postscriptNameID = instance_ps
    instance.coordinates = dict(font["fvar"].instances[0].coordinates)
    font["fvar"].instances.append(instance)

    rename.rename(font, names)
    assert records(font, 16) == records(font, 21) == ["Neha Sans"]
    assert records(font, 25) == ["NehaSans"]
    assert table.getName(1, 1, 0, 0).toUnicode() == "Neha Sans"
    assert records(font, 7) == []
    assert table.getDebugName(instance_ps) == "NehaSans-Thin"


def test_refuses_a_font_that_is_not_the_upstream_family():
    names = rename.load("sans")
    with pytest.raises(rename.RenameError):
        rename.rename(TTFont(BUILD / FONTS["serif"]), names)
    renamed = rename.rename(TTFont(BUILD / FONTS["sans"]), names)
    with pytest.raises(rename.RenameError):
        rename.rename(renamed, names)


def test_refuses_a_font_that_keeps_the_upstream_name():
    names = rename.load("sans")
    font = TTFont(BUILD / FONTS["sans"])
    # Upper case escapes the replacement but not the case-blind check.
    font["name"].setName("NOTO SANS KANNADA", 18, 3, 1, 0x409)
    with pytest.raises(rename.RenameError):
        rename.rename(font, names)


def test_vendor_id_must_be_4_characters():
    names = rename.load("sans")
    with pytest.raises(ValueError):
        rename.Names(**{**vars(names), "vendor_id": "OPENK"})
