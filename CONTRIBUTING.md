# Contributing

This fork carries Kannada fixes to Noto Sans Kannada and Noto Serif Kannada as small source changes, so each one can go upstream to [notofonts/kannada](https://github.com/notofonts/kannada) as its own pull request. [FORK.md](FORK.md) lists the changes.

The most useful report is a word that renders wrongly. Open an issue with the text, the app and its version, and a screenshot.

For changes, open a pull request from a branch. Every shaping change comes with a test in `tests/`; build both fonts and run `uv run pytest` as described in FORK.md before asking for review.

## Sign-off

This repository uses the [Developer Certificate of Origin](https://developercertificate.org). Sign off every commit to certify that you wrote the change or have the right to submit it:

    git commit -s

This adds a line such as `Signed-off-by: Your Name <you@example.com>`. A contribution is licensed under the license of the files it changes, as listed in [NOTICE.md](NOTICE.md).
