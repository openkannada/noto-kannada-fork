# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Write a 1-page HTML specimen for a released family, next to its webfonts."""

from __future__ import annotations

import html
import json
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).parent.parent
JOINERS = "\u200c\u200d"
TEMPLATE = ROOT / "specimen" / "template.html"
SAMPLE = ROOT / "specimen" / "sample-kn.json"

# (code point, text that shows it in valid use, label)
NEW_LETTERS = (
    (0x0CDC, "೜ ೜ಗಣೇಶ", "U+0CDC ARCHAIC SHRII (Unicode 17.0)"),
    (0x0CDD, "ೝ ಅವನೝ", "U+0CDD NAKAARA POLLU (Unicode 14.0)"),
    (0x0CF3, "ೳ ಕೳ", "U+0CF3 COMBINING ANUSVARA ABOVE RIGHT (Unicode 15.0)"),
)
STRESS = (
    ("3-consonant clusters", "ಕ್ಷ್ಮ್ಯ ಸ್ತ್ರೀ ಷ್ಟ್ರ ನ್ತ್ರ್ಯ ಕ್ತ್ವ ತ್ಸ್ನ ಜ್ಞಾ ಶ್ರೀ ಕ್ಷ್ಣ ಮ್ಲ್ಯ ಸ್ಪ್ರ ಞ್ಚ್ಯ"),
    ("Arkavattu with vowel signs", "ರ್ಕ ರ್ಕಿ ರ್ಕೀ ರ್ಕೆ ರ್ಕೇ ರ್ಕೈ ರ್ಕೊ ರ್ಕೋ ರ್ಕೌ ರ್ಕಂ ಧರ್ಮ ಸೂರ್ಯ ಕಾರ್ತ್ಯ ವಾರ್ತ್ಯಾ"),
    ("Subscripts with vowel signs", "ಕ್ಕು ಕ್ಕೂ ಕ್ಕೃ ಕ್ಕೄ ಕ್ಯೈ ಕ್ರೌ ಸ್ಥೈ ದ್ಧೊ ಮ್ಮೋ ತ್ತ್ವೋ ಸ್ತ್ರೀಯ ಪ್ರೌಢ"),
    ("Vowel signs on every kind of base", "ಕಿ ಗಿ ಠಿ ಣಿ ಬಿ ಮಿ ಯಿ ೞಿ ಕೈ ಘೈ ಙೈ ಞೈ ಝೌ ಙೌ ಞೌ ಱೌ"),
    ("Vocalic letters and signs", "ಋ ೠ ಌ ೡ ಕೃ ಕೄ ಕೢ ಕೣ ಪಿತೃ ಕೃಷ್ಣ"),
    ("Old letters", "ೞ ಱ ಕ್ೞ ಳ್ೞ ಕ್ಱ ಪೞಿ ಅೞಲ್"),
    ("Joiners", "ರ\u200d್ಯಾಂಕ್ ರ\u200c್ಯಾಂಕ್ ಕ್ಷ ಕ್\u200cಷ"),
    ("Nukta, avagraha, visarga", "ಫ಼ ಜ಼ ಽ ಅಃ ದುಃಖ"),
    ("Digits", "೦೧೨೩೪೫೬೭೮೯ ೨೦೨೬"),
)


def write(out: Path, family: str, version: str, credit: str, font_path: Path) -> Path:
    """out/specimen.html, using out/webfonts/<font>.woff2. The font may be variable or static."""
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    axes = (
        {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes}
        if ("fvar" in font)
        else {}
    )
    weight = font["OS/2"].usWeightClass
    sample = json.loads(SAMPLE.read_text())
    fields = {
        "family": family,
        "version": version,
        "credit": html.escape(credit),
        "font_file": f"webfonts/{font_path.stem}.woff2",
        "font_weight": "{:g} {:g}".format(axes["wght"][0], axes["wght"][2])
        if "wght" in axes
        else str(weight),
        "font_stretch": "{:g}% {:g}%".format(*axes["wdth"][0::2]) if "wdth" in axes else "100%",
        "controls": _controls(axes),
        "body_class": "variable" if axes else "static",
        "headline": html.escape(sample["headline"]),
        "tester": html.escape(sample["tester"]),
        "paragraphs": "\n".join(f"<p>{html.escape(p)}</p>" for p in sample["paragraphs"]),
        "sample_source": html.escape(sample["source"]),
        "new_letters": _new_letters(cmap),
        "stress": "\n".join(_row(label, *_covered(text, cmap)) for label, text in STRESS),
    }
    page = TEMPLATE.read_text()
    for key, value in fields.items():
        page = page.replace("{{" + key + "}}", value)
    if "{{" in page:
        raise ValueError("specimen template has an unfilled field")
    target = out / "specimen.html"
    target.write_text(page)
    return target


def _controls(axes) -> str:
    rows = []
    for tag, label in (("wght", "Weight"), ("wdth", "Width")):
        if tag in axes:
            low, default, high = axes[tag]
            rows.append(
                f'<label>{label} <output id="{tag}-value">{default:g}</output>'
                f'<input type="range" data-axis="{tag}" min="{low:g}" max="{high:g}" '
                f'value="{default:g}" step="1"></label>'
            )
    return "\n".join(rows)


def _new_letters(cmap) -> str:
    rows = [_row(label, text) for cp, text, label in NEW_LETTERS if cp in cmap]
    return "\n".join(rows) or "<p>This family has none of the letters added since Unicode 14.</p>"


def _covered(text: str, cmap) -> tuple[str, str]:
    """The words of text that the font can draw, and the characters it lacks."""

    def drawn(ch):
        return ord(ch) in cmap or ch in JOINERS

    words = text.split()
    missing = sorted({ch for w in words for ch in w if not drawn(ch)})
    kept = " ".join(w for w in words if all(drawn(ch) for ch in w))
    note = (
        "Not in this font: " + " ".join(f"U+{ord(ch):04X} {ch}" for ch in missing)
        if missing
        else ""
    )
    return kept, note


def _row(label: str, text: str, note: str = "") -> str:
    heading, sample = html.escape(label), html.escape(text)
    extra = f'<p class="note">{html.escape(note)}</p>' if note else ""
    return f'<div class="row"><h3>{heading}</h3><p class="big">{sample}</p>{extra}</div>'
