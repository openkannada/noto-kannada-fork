Title: Add U+0CDC KANNADA ARCHAIC SHRII

Unicode 17.0 adds U+0CDC KANNADA ARCHAIC SHRII (proposal L2/22-006). Noto Sans Kannada and Noto Serif Kannada do not have it, so the character shows as a missing glyph.

This PR adds `archaicshriiknda` (Sans) and `archaicShrii_kannada` (Serif) in every master. The shape follows the representative glyph in L2/22-006: an inner 3-shaped hook, a round left bowl, an arch, and a right loop ending in a flick above the x-height.

Stems, overshoot and side bearings match each master's consonants. The masters are point-compatible. The glyph takes no marks and needs no GSUB or GPOS changes.

Checked: the variable fonts build with fontmake 3.12.2; HarfBuzz shapes U+0CDC alone and before ಗಣೇಶ with no missing glyph and no dotted circle; the other test strings of the kannadi fontqa suite shape as before.

Not done: the heavy masters need a designer's review. The 3 inside the bowl is crowded at Bold.
