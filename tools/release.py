# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Build the release files for 1 style of this fork.

    uv run --group build --group release python tools/release.py sans

writes dist/NehaSans/ (variable, static TTF and OTF, WOFF2, a Kannada subset for the web, a
specimen, OFL.txt, FONTLOG.txt and SHA256SUMS) and dist/NehaSans-<version>.zip.

gftools builder compiles the fonts with the Google Fonts fixes and autohints the static TTFs.
The source is first copied without the instances of other families (the Sans source also
defines Noto Sans Kannada UI). Every built font is then renamed by tools/rename.py.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
from io import BytesIO
from pathlib import Path

import glyphsLib
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, str(Path(__file__).parent))
import rename  # noqa: E402
import specimen  # noqa: E402

ROOT = Path(__file__).parent.parent
SOURCES = {"sans": "NotoSansKannada.glyphs", "serif": "NotoSerifKannada.glyphs"}
# Kannada, the joiners, the dotted circle and the dandas; the site sets Latin in another font.
WEB_UNICODES = [*range(0x0C80, 0x0D00), 0x200C, 0x200D, 0x25CC, 0x0964, 0x0965, 0x0020, 0x00A0]
DOCS = ("OFL.txt", "FONTLOG.txt")


def prepare(style: str, names: rename.Names, work: Path) -> Path:
    """Copy the source keeping only this family's instances, and write the builder config."""
    font = glyphsLib.GSFont(str(ROOT / "sources" / SOURCES[style]))
    font.instances = [i for i in font.instances if i.familyName == names.upstream]
    src = work / "src"
    src.mkdir(parents=True, exist_ok=True)
    font.save(str(src / SOURCES[style]))
    config = src / "config.yaml"
    config.write_text(
        "\n".join(
            [
                "sources:",
                f"  - {SOURCES[style]}",
                f"familyName: {names.upstream}",
                "buildVariable: true",
                "buildStatic: true",
                "buildTTF: true",
                "buildOTF: true",
                "buildWebfont: false",
                "autohintTTF: true",
                "ttfaUseScript: true",
                "googleFonts: true",
                f"outputDir: {work / 'fonts'}",
                "",
            ]
        )
    )
    return config


def build(config: Path) -> None:
    gftools = Path(sys.executable).parent / "gftools"
    subprocess.run([str(gftools), "builder", str(config)], check=True, cwd=config.parent)


def renamed(built: Path, names: rename.Names, out: Path, kind: str) -> list[Path]:
    """Rename every font in built/kind into out/kind; return the written paths."""
    written = []
    for path in sorted(built.glob("*.[ot]tf")):
        font = rename.rename(TTFont(path), names)
        target = out / kind / rename.file_name(font, names, path.suffix)
        target.parent.mkdir(parents=True, exist_ok=True)
        font.save(target)
        unrenamed(target)
        written.append(target)
    if not written:
        raise SystemExit(f"no fonts in {built}")
    return written


def unrenamed(path: Path) -> None:
    """Fail if the upstream mark is left in the name or CFF fields, or in any other table."""
    font = TTFont(path)
    left = rename.leftovers(font)
    for tag in sorted(set(font.keys()) - {"GlyphOrder", "name", "CFF "}):
        data = font.getTableData(tag)
        if any(m in data for m in (b"Noto", "Noto".encode("utf-16-be"))):
            left.append(tag)
    if left:
        raise SystemExit(f"{path.name}: upstream name left in {left}")


def woff2(font_path: Path, out_dir: Path) -> Path:
    font = TTFont(font_path)
    font.flavor = "woff2"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{font_path.stem}.woff2"
    font.save(target)
    return target


def web_subset(variable: Path, out_dir: Path, names: rename.Names) -> Path:
    """The variable font at normal width, cut to Kannada, as WOFF2 for the site."""
    font = TTFont(variable)
    if any(a.axisTag == "wdth" for a in font["fvar"].axes):
        pinned = BytesIO()
        instantiateVariableFont(font, {"wdth": 100}, updateFontNames=False).save(pinned)
        font = TTFont(BytesIO(pinned.getvalue()))  # the subsetter needs freshly loaded tables
    options = subset.Options()
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.notdef_outline = True
    options.flavor = "woff2"
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=WEB_UNICODES)
    subsetter.subset(font)
    axes = ",".join(sorted(a.axisTag for a in font["fvar"].axes))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{names.family_ps}-Kannada[{axes}].woff2"
    font.flavor = "woff2"
    font.save(target)
    return target


def checksums(folder: Path) -> Path:
    lines = [
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(folder).as_posix()}"
        for p in sorted(folder.rglob("*"))
        if p.is_file() and p.name != "SHA256SUMS"
    ]
    target = folder / "SHA256SUMS"
    target.write_text("\n".join(lines) + "\n")
    return target


def archive(folder: Path, version: str) -> Path:
    target = folder.parent / f"{folder.name}-{version}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(folder.parent).as_posix())
    return target


def release(style: str, work: Path, dist: Path, skip_build: bool = False) -> Path:
    names = rename.load(style)
    out = dist / names.family_ps
    if out.exists():
        shutil.rmtree(out)
    if not skip_build:
        build(prepare(style, names, work))
    fonts = work / "fonts"
    variable = renamed(fonts / "variable", names, out, "variable")
    statics = renamed(fonts / "ttf", names, out, "ttf")
    renamed(fonts / "otf", names, out, "otf")
    for path in [*variable, *statics]:
        woff2(path, out / "webfonts")
    web_subset(variable[0], out / "web", names)
    for doc in DOCS:
        shutil.copy(ROOT / doc, out / doc)
    credit = f"Based on {names.upstream} by Google."
    specimen.write(out, names.family, names.version, credit, variable[0])
    checksums(out)
    zipped = archive(out, names.version)
    digest = hashlib.sha256(zipped.read_bytes()).hexdigest()
    zipped.with_name(zipped.name + ".sha256").write_text(f"{digest}  {zipped.name}\n")
    return zipped


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("style", choices=sorted(SOURCES))
    parser.add_argument("--work", type=Path, default=ROOT / "build" / "release")
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    parser.add_argument("--skip-build", action="store_true", help="reuse fonts in --work")
    args = parser.parse_args(argv)
    print(release(args.style, args.work / args.style, args.dist, args.skip_build))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
