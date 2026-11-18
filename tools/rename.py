# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Give a variable font built from this fork its Open Kannada name.

    uv run python tools/rename.py sans build/sans/NotoSansKannada-VF.ttf dist/

writes dist/NehaSans[wdth,wght].ttf. Names come from rename.toml. The upstream copyright,
designer and license records are kept; the copyright gains the fork's line after a semicolon,
since name records hold no line breaks; the trademark record is dropped. The tool refuses to
write a font that still carries the upstream name anywhere but the copyright and the
description, which credit it.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from fontTools.ttLib import TTFont

CONFIG = Path(__file__).parent.parent / "rename.toml"
STYLES = ("sans", "serif")

COPYRIGHT = 0
FAMILY = 1
UNIQUE_ID = 3
VERSION = 5
POSTSCRIPT = 6
TRADEMARK = 7
MANUFACTURER = 8
DESCRIPTION = 10
VENDOR_URL = 11
TYPOGRAPHIC_FAMILY = 16
# Records that may name the upstream font: they credit it.
CREDITS = {COPYRIGHT, DESCRIPTION}
UPSTREAM_MARK = "noto"


@dataclass(frozen=True)
class Names:
    upstream: str
    family: str
    description: str
    version: str
    vendor_id: str
    copyright: str
    manufacturer: str
    vendor_url: str

    def __post_init__(self):
        if len(self.vendor_id) != 4 or not self.vendor_id.isascii():
            raise ValueError(f"vendor_id must be 4 ASCII characters: {self.vendor_id!r}")

    @property
    def upstream_ps(self) -> str:
        return self.upstream.replace(" ", "")

    @property
    def family_ps(self) -> str:
        return self.family.replace(" ", "")


def load(style: str, config: Path = CONFIG) -> Names:
    data = tomllib.loads(config.read_text())
    shared = ("version", "vendor_id", "copyright", "manufacturer", "vendor_url")
    return Names(**data[style], **{k: data[k] for k in shared})


class RenameError(ValueError):
    pass


def rename(font: TTFont, names: Names) -> TTFont:
    """Rename the font in place and return it."""
    table = font["name"]
    family = table.getDebugName(TYPOGRAPHIC_FAMILY) or table.getDebugName(FAMILY)
    if family != names.upstream and not family.startswith(f"{names.upstream} "):
        raise RenameError(
            f"family is {family!r}, expected {names.upstream!r}; "
            "already renamed, or the wrong style"
        )
    table.removeNames(nameID=TRADEMARK)
    fixed = {
        VERSION: f"Version {names.version}",
        MANUFACTURER: names.manufacturer,
        DESCRIPTION: names.description,
        VENDOR_URL: names.vendor_url,
    }
    for record in table.names:
        text = record.toUnicode()
        if record.nameID == COPYRIGHT:
            record.string = f"{text}; {names.copyright}"
        elif record.nameID in fixed:
            record.string = fixed[record.nameID]
        elif record.nameID != UNIQUE_ID:
            record.string = text.replace(names.upstream, names.family).replace(
                names.upstream_ps, names.family_ps
            )
    unique = f"{names.version};{names.vendor_id};{table.getDebugName(POSTSCRIPT)}"
    for record in table.names:
        if record.nameID == UNIQUE_ID:
            record.string = unique
    font["OS/2"].achVendID = names.vendor_id
    font["head"].fontRevision = float(names.version)
    left = leftovers(font)
    if left:
        raise RenameError(f"upstream name still in name records {left}")
    return font


def leftovers(font: TTFont) -> list[int]:
    """Name IDs outside the credits that still carry the upstream mark."""
    return sorted(
        {
            r.nameID
            for r in font["name"].names
            if r.nameID not in CREDITS and UPSTREAM_MARK in r.toUnicode().lower()
        }
    )


def file_name(font: TTFont, names: Names, suffix: str = ".ttf") -> str:
    """NehaSans[wdth,wght].ttf for a variable font, the PostScript name for a static one."""
    if "fvar" in font:
        axes = ",".join(sorted(a.axisTag for a in font["fvar"].axes))
        return f"{names.family_ps}[{axes}]{suffix}"
    return f"{font['name'].getDebugName(POSTSCRIPT)}{suffix}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("style", choices=STYLES)
    parser.add_argument("source", type=Path, help="variable font built from this fork")
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args(argv)
    names = load(args.style)
    try:
        font = rename(TTFont(args.source), names)
    except RenameError as error:
        parser.exit(1, f"rename: {error}\n")
    out = args.out_dir / file_name(font, names)
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
