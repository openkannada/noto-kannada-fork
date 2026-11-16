A font-side fix for this, for fonts that want ZWNJ before the virama to block the below-base form: make the `blwf` ligatures contextual and put an `ignore` rule for the joiner first in the same lookup, for example

    ignore sub uni200C virama' [consonants]';
    sub virama' ka' by ka.below;

With that change in Noto Sans and Serif Kannada, ರ‌್ಯ shapes with an explicit virama in HarfBuzz 15.0.0, and ರ‍್ಯ still forms the subscript. A draft is ready for notofonts/kannada.
