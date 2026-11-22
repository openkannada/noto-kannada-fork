# Neha Sans and Neha Serif

Neha Sans and Neha Serif are free Kannada fonts built from Google's Noto Sans Kannada and Noto Serif Kannada, with fixes to Kannada shaping and the Unicode 17.0 letter U+0CDC ARCHAIC SHRII. Both shape all 2,146 Kannada test strings in [font-health-action](https://github.com/openkannada/font-health-action), and Shaperglot finds full Kannada support (`kn_Knda`, 100%).

This repository is a fork of [notofonts/kannada](https://github.com/notofonts/kannada). The sources keep the Noto names so each fix can go upstream as its own pull request; the fonts that leave this repository carry the Neha names, because Noto is a trademark of Google.

## Quick start

Download [NehaSans-1.000.zip](https://github.com/openkannada/noto-kannada-fork/releases/download/v1.000/NehaSans-1.000.zip) or [NehaSerif-1.000.zip](https://github.com/openkannada/noto-kannada-fork/releases/download/v1.000/NehaSerif-1.000.zip). On a website, use the Kannada-only variable font from the zip:

```css
@font-face { font-family: "Neha Sans"; src: url("web/NehaSans-Kannada[wght].woff2") format("woff2"); font-weight: 100 900; }
:lang(kn) { font-family: "Neha Sans", sans-serif; }
```

See both fonts beside Gari at [openkannada.org/fonts](https://openkannada.org/fonts/).

## What's in each release

| File | Contents |
|---|---|
| `NehaSans-1.000.zip` | 1 variable font (weight 100 to 900, width 62.5 to 100), 36 static TTF and 36 static OTF, WOFF2 of each, a Kannada-only web font, a specimen |
| `NehaSerif-1.000.zip` | 1 variable font (weight 100 to 900), 9 static TTF and 9 static OTF, WOFF2 of each, a Kannada-only web font, a specimen |

Each zip has `OFL.txt`, `FONTLOG.txt` and `SHA256SUMS` inside, and a `.sha256` file next to it.

## Changes from Noto

| Change | Upstream |
|---|---|
| ra followed by the vocalic R sign (ರೃ) stays ra with the sign, as typed. Noto draws it as the vowel letter ಋ with a reph | [notofonts/kannada#61](https://github.com/notofonts/kannada/issues/61) |
| U+0CDC KANNADA ARCHAIC SHRII, added in every weight | Unicode 17.0, L2/22-006 |
| Own font names, version 1.000 and vendor ID | Required by the Noto trademark |

[FORK.md](FORK.md) has the details.

## Results

Measured in CI: font-health-action on every commit, and Shaperglot and fontspector on the 1.000 release fonts.

| Check | Neha Sans | Neha Serif |
|---|---|---|
| font-health-action, 2,146 Kannada shaping strings | all pass | all pass |
| Shaperglot 1.2.2, `kn_Knda` | 100% | 100% |
| fontspector 1.9.1, Google Fonts profile | no failures beyond [release/known-fails.toml](release/known-fails.toml) | same |
| U+0CDC passes kannadi's fontqa gate | 16 of 36 instances: Thin to Regular at every width | 7 of 9 instances: Thin to Bold |

Known gaps:

- No Latin letters. Set Latin text in a companion font.
- U+0CDC is a draft at heavy weights: from Medium in Neha Sans and from ExtraBold in Neha Serif, the small 3 inside the letter closes up.

## Build and test

[FORK.md](FORK.md#build-and-test) has the commands that build both fonts from the Glyphs sources, rename them and run the tests, and the release build that makes the zips.

## Related

- [Gari](https://github.com/openkannada/gari-font): a handwriting-style Kannada font built on Navilu.
- [font-health-action](https://github.com/openkannada/font-health-action): the Kannada shaping tests both fonts run on every commit.
- [kannadi](https://github.com/openkannada/kannadi): converts old Nudi and Baraha documents to Unicode, and holds the fontqa tools.
- [notofonts/kannada](https://github.com/notofonts/kannada): the upstream sources.

## License

The fonts are under the [SIL Open Font License 1.1](OFL.txt), with no Reserved Font Name. Copyright 2022 The Noto Project Authors; copyright 2026 The Open Kannada Authors for the changes. The tests and tools written for this fork are under MIT OR Apache-2.0. [NOTICE.md](NOTICE.md) lists which files are under which license, and [CONTRIBUTING.md](CONTRIBUTING.md) explains the sign-off.

Part of [Open Kannada](https://github.com/openkannada), free and open-source tools that make Kannada work properly on computers.
