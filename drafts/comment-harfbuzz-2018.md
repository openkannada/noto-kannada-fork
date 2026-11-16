A font-side fix for this, for fonts that want ZWNJ before the virama to block the below-base form: make the `blwf` ligatures contextual and put an `ignore` rule for the joiner first in the same lookup, for example

    ignore sub [consonants] uni200C virama' [consonants]';
    sub virama' ka' by ka.below;

With that change in Noto Sans and Serif Kannada, ರ‌್ಯ shapes with an explicit virama in HarfBuzz 15.0.0, and ರ‍್ಯ still forms the subscript.

A font cannot fix the case with a vowel sign (ರ‌್ಯಾ): HarfBuzz moves the sign in front of the ZWNJ, so blocking the subscript there would put the sign on ra. The rule above leaves that case forming the conjunct, as today.
