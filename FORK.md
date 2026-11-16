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

The SIL Open Font License of this project lists no Reserved Font Name, so the license does not require a rename. "Noto" is a trademark of Google LLC, so a build distributed from this fork should use another family name. The sources keep the Noto names so that each change can go upstream as is.

## Build and test

    uv sync --group build
    uv run fontmake -g sources/NotoSansKannada.glyphs -o variable --output-dir build/sans --no-production-names
    uv run fontmake -g sources/NotoSerifKannada.glyphs -o variable --output-dir build/serif --no-production-names
    uv run pytest

The upstream workflow `Build, QA, Release` is disabled in this fork; `Fork CI` builds and tests instead.

## U+0CDC gate results

`fontqa gate --chars 0CDC` (kannadi) on every named instance of the variable fonts built from this fork:

| Font | Pass | Fail |
|---|---|---|
| Sans, 36 instances | 16: Thin to Regular at every width | 20: Medium and heavier, where the 3 inside the bowl closes into extra counters; ExtraCondensed Bold and ExtraBold also fail on stroke contrast |
| Serif, 9 instances | 7: Thin to Bold | 2: ExtraBold and Black, extra counters |

The failing weights need a designer, or at least a hand-drawn heavy skeleton.
