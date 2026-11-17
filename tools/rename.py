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

import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from fontTools.ttLib import TTFont

CONFIG = Path(__file__).parent.parent / "rename.toml"

COPYRIGHT, UNIQUE_ID, VERSION, TRADEMARK, MANUFACTURER, DESCRIPTION, VENDOR_URL = (
    0,
    3,
    5,
    7,
    8,
    10,
    11,
)
# Records that may name the upstream font: they credit it.
CREDITS = {COPYRIGHT, DESCRIPTION}
UPSTREAM_MARK = "Noto"


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

    @property
    def upstream_ps(self) -> str:
        return self.upstream.replace(" ", "")

    @property
    def family_ps(self) -> str:
        return self.family.replace(" ", "")


def load(style: str, config: Path = CONFIG) -> Names:
    data = tomllib.loads(config.read_text())
    keys = ("version", "vendor_id", "copyright", "manufacturer", "vendor_url")
    return Names(**data[style], **{k: data[k] for k in keys})


class UpstreamNameLeft(ValueError):
    pass


def rename(font: TTFont, names: Names) -> TTFont:
    """Rename the font in place and return it."""
    table = font["name"]
    for record in list(table.names):
        text = record.toUnicode()
        if record.nameID == TRADEMARK:
            table.removeNames(nameID=TRADEMARK)
            continue
        new = {
            COPYRIGHT: f"{text}; {names.copyright}",
            VERSION: f"Version {names.version}",
            MANUFACTURER: names.manufacturer,
            DESCRIPTION: names.description,
            VENDOR_URL: names.vendor_url,
        }.get(record.nameID)
        if new is None:
            new = text.replace(names.upstream, names.family).replace(
                names.upstream_ps, names.family_ps
            )
        record.string = new
    unique = f"{names.version};{names.vendor_id};{table.getDebugName(6)}"
    for record in table.names:
        if record.nameID == UNIQUE_ID:
            record.string = unique
    font["OS/2"].achVendID = names.vendor_id
    font["head"].fontRevision = float(names.version)
    left = leftovers(font)
    if left:
        raise UpstreamNameLeft(f"upstream name still in name records {left}")
    return font


def leftovers(font: TTFont) -> list[int]:
    """Name IDs outside the credits that still carry the upstream mark."""
    return sorted(
        {
            r.nameID
            for r in font["name"].names
            if r.nameID not in CREDITS and UPSTREAM_MARK.lower() in r.toUnicode().lower()
        }
    )


def file_name(font: TTFont, names: Names) -> str:
    axes = ",".join(sorted(a.axisTag for a in font["fvar"].axes)) if "fvar" in font else ""
    return f"{names.family_ps}[{axes}].ttf" if axes else f"{names.family_ps}.ttf"


def main(argv: list[str]) -> int:
    style, source, out_dir = argv
    names = load(style)
    font = rename(TTFont(source), names)
    out = Path(out_dir) / file_name(font, names)
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
