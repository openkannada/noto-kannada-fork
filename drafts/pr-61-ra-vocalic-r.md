Title: Keep ರೃ as ra + vocalic R sign (fixes #61)

Noto Sans Kannada and Noto Serif Kannada substitute ರ + ೃ (U+0CB0 U+0CC3) with the vowel letter ಋ plus the reph glyph, so a reader sees ಋ with an arkavattu instead of ರೃ.

- Sans: the rule `sub raknda' lookup SingleSubstitution13 rvocalicvowelsignknda' lookup SingleSubstitution13;` in `ContextualGSUB12`, with its `ignore` line and the 2 entries in `SingleSubstitution13`.
- Serif: the rule in `ra_rVocalic_kannada` and the lookup `swap_Ra_rVocalic`.

This PR removes those rules, so ರೃ shapes as ra + vocalic R sign, as in Tiro Kannada, Anek Kannada and Nanni.

If the ಋ-like form is wanted as a historical option, it could return under a stylistic set; this PR does not add one.

Checked with HarfBuzz 15.0.0 on variable fonts built with fontmake 3.12.2: ರೃ gives `raknda rvocalicvowelsignknda` (Sans) and `ra_kannada rVocalicMatra_kannada` (Serif). The 2,146 strings of the kannadi fontqa suite shape as before apart from this sequence.
