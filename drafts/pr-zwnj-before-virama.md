Title: Do not form a subscript after ZWNJ + virama

HarfBuzz shapes ರ + ZWNJ + virama + ಯ (U+0CB0 U+200C U+0CCD U+0CAF) with a subscript ಯ, the same as the ZWJ sequence that requests that form (harfbuzz/harfbuzz#2018). HarfBuzz applies `rphf` and `blwf` with manual joiners, finds no reph for ra + ZWNJ, and then the font's `blwf` forms the subscript. Uniscribe and Core Text show an explicit virama.

This PR makes `blwf` respect a ZWNJ before the virama:

- each `blwf` ligature becomes a contextual ligature, `sub viramaknda' kaknda' by kasubscriptknda;` (Serif: `halant_kannada`);
- an `ignore sub [consonants nukta] uni200C viramaknda' [consonants]';` rule (Serif: `zerowidthnonjoiner`) comes first in the same lookup. It only applies when the ZWNJ directly follows a consonant: HarfBuzz moves most vowel signs in front of the ZWNJ (ಕ‌್ಕಾ), and blocking the subscript there would put the sign on the first consonant, so those keep the conjunct as before.

Result: ರ‌್ಯ shows ra with an explicit virama, then ya. ರ‍್ಯ (ZWJ) still forms the subscript. Every consonant + virama + consonant still forms its conjunct (1,296 pairs per font). The change applies to new-order (`knd2`) shaping; old-order `knda` lookups are unchanged.

Checked with HarfBuzz 15.0.0 on variable fonts built with fontmake 3.12.2.
