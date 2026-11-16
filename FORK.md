# About this fork

This is a working fork of [notofonts/kannada](https://github.com/notofonts/kannada) with Kannada fixes, kept as small source changes so each can go upstream as its own pull request. Drafts of those pull requests are in `drafts/`. Nothing here has been submitted.

## Changes

| Change | Files | Upstream issue |
|---|---|---|
| ರೃ (U+0CB0 U+0CC3) stays ra + vocalic R sign; it was drawn as ಋ with a reph | Sans `ContextualGSUB12`, `SingleSubstitution13`; Serif `ra_rVocalic_kannada`, `swap_Ra_rVocalic` | notofonts/kannada#61 |
| A ZWNJ before the virama (ರ‌್ಯ) blocks the subscript; ZWJ still forms it | Sans and Serif `blwf` | harfbuzz/harfbuzz#2018 |
| U+0CDC KANNADA ARCHAIC SHRII, drafted in every master | `archaicshriiknda` (Sans), `archaicShrii_kannada` (Serif) | Unicode 17.0, L2/22-006 |

The U+0CDC outlines are drafts. Light and Regular pass every automated gate; the heavy masters (Sans SemiBold, Bold, Condensed Bold; Serif Bold) need a designer.

## Names

The SIL Open Font License of this project lists no Reserved Font Name, so the license does not require a rename. "Noto" is a trademark of Google LLC, so a build distributed from this fork should use another family name. The sources keep the Noto names so that each change can go upstream as is.

## Build and test

    uv sync --group build
    uv run fontmake -g sources/NotoSansKannada.glyphs -o variable --output-dir build/sans --no-production-names
    uv run fontmake -g sources/NotoSerifKannada.glyphs -o variable --output-dir build/serif --no-production-names
    uv run pytest

The upstream workflow `Build, QA, Release` is disabled in this fork; `Fork CI` builds and tests instead.
