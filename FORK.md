# About this fork

This is a working fork of [notofonts/kannada](https://github.com/notofonts/kannada) with Kannada fixes, kept as small source changes so each can go upstream as its own pull request. Drafts of those pull requests are in `drafts/`.

## Changes

| Change | Files | Upstream issue |
|---|---|---|
| ರೃ (U+0CB0 U+0CC3) stays ra + vocalic R sign; it was drawn as ಋ with a reph | Sans `ContextualGSUB12`, `SingleSubstitution13`; Serif `ra_rVocalic_kannada`, `swap_Ra_rVocalic` | notofonts/kannada#61 |
| U+0CDC KANNADA ARCHAIC SHRII, drafted in every master | `archaicshriiknda` (Sans), `archaicShrii_kannada` (Serif) | Unicode 17.0, L2/22-006 |

Not changed: ra + ZWNJ + virama + consonant. An earlier version of this fork made the ZWNJ block the subscript. Kannada Wikipedia uses the sequence 314 times, 304 of them as ra + ZWNJ + virama + ya + vowel sign in loanwords such as ರ‌್ಯಾಂಕ್, the same words also written with the documented ZWJ sequence. Writers mean the subscript, so the fork keeps upstream's behavior, and a test checks that ZWNJ and ZWJ shape alike there. Upstream maintainers said the same on notofonts/kannada PR #65, the earlier attempt, which is closed. See also harfbuzz/harfbuzz#2018.

The U+0CDC outlines are drafts. See "U+0CDC gate results" below for which instances pass the automated gates.

## Names

Fonts built from this fork are distributed as **Neha Sans**, from Noto Sans Kannada, and **Neha Serif**, from Noto Serif Kannada. "Noto" is a trademark of Google, so no distributed file may use it as a name. The SIL Open Font License of this project lists no Reserved Font Name. The sources keep the Noto names so that each change can go upstream as is; `tools/rename.py` renames the built fonts with the names in `rename.toml`:

- family Neha Sans or Neha Serif, PostScript names `NehaSans-Regular` and so on, files `NehaSans[wdth,wght].ttf` and `NehaSerif[wght].ttf`;
- version 1.000, vendor ID `NONE` in place of Google's `GOOG`, and a new unique ID;
- the upstream copyright line kept, with "; Copyright 2026 The Open Kannada Authors" added on the same line; the designer and OFL records kept; the record "Noto is a trademark of Google Inc." removed;
- a description that credits the source ("Based on Noto Sans Kannada by Google") and says the font is named for Neha Prasad, a founding member of Open Kannada.

The tool refuses to write a font that still has "Noto" in any name record other than the copyright and the description. `tests/test_rename.py` checks all of this, and that each renamed font shapes exactly like the build it comes from.

Only renamed fonts leave this repository, through the [releases](https://github.com/openkannada/noto-kannada-fork/releases). The repository commits no binaries, and the upstream release workflow is disabled.

## Build and test

    uv sync --group build
    uv run fontmake -g sources/NotoSansKannada.glyphs -o variable --output-dir build/sans --no-production-names
    uv run fontmake -g sources/NotoSerifKannada.glyphs -o variable --output-dir build/serif --no-production-names
    uv run python tools/rename.py sans build/sans/NotoSansKannada-VF.ttf dist/
    uv run python tools/rename.py serif build/serif/NotoSerifKannada-VF.ttf dist/
    uv run pytest

`dist/` then holds `NehaSans[wdth,wght].ttf` and `NehaSerif[wght].ttf`. The fontmake build has only the glyphs in these sources; the upstream release, built with gftools, also merges in Latin glyphs from Noto Sans.

The upstream workflow `Build, QA, Release` is disabled in this fork; `Fork CI` builds and tests instead.

## Release build

    uv sync --group build --group release
    uv run python tools/release.py sans
    uv run python tools/release.py serif
    uv run python tools/check_release.py sans --fontspector path/to/fontspector

`tools/release.py` copies the source without the Noto Sans Kannada UI instances, builds it with gftools builder (Google Fonts fixes, a variable font, static TTFs autohinted with ttfautohint, static OTFs), renames every font, and writes `dist/NehaSans/` and `dist/NehaSans-1.000.zip` with a `.sha256` file. The folder holds:

- `variable/`, `ttf/`, `otf/`: the fonts;
- `webfonts/`: WOFF2 of the variable font and of each static TTF;
- `web/NehaSans-Kannada[wght].woff2`: the variable font at normal width, cut to Kannada, for websites;
- `specimen.html`: 1 page with the sample text, the new letters and shaping stress tests;
- `OFL.txt`, `FONTLOG.txt`, `SHA256SUMS`.

`tools/check_release.py` runs fontspector with the Google Fonts profile, Shaperglot for `kn_Knda`, and `tests/test_kannada_fixes.py` on the released variable font. `release/known-fails.toml` lists the fontspector checks that fail for reasons outside this release, with the reason; any other failure fails the check. The `Release build` workflow does all of this for both styles and keeps the zip, its checksum and the reports as workflow artifacts.

## U+0CDC gate results

`fontqa gate --chars 0CDC` (kannadi) on every named instance of the variable fonts built from this fork:

| Font | Pass | Fail |
|---|---|---|
| Sans, 36 instances | 16: Thin to Regular at every width | 20: Medium and heavier, where the 3 inside the bowl closes into extra counters; ExtraCondensed Bold and ExtraBold also fail on stroke contrast |
| Serif, 9 instances | 7: Thin to Bold | 2: ExtraBold and Black, extra counters |

The failing weights need a designer, or at least a hand-drawn heavy skeleton.
