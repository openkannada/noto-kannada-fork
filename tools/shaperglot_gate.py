# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Exit 0 when Shaperglot finds full kn_Knda support, or when its only failure is the
mandatory codepoint check missing characters listed as allowed.

Runs in Shaperglot's own environment, since its wheels are not built for every platform:

    uvx --from shaperglot==1.2.2 python tools/shaperglot_gate.py FONT [U+0CBC ...]

Shaperglot's command line prints "nearly supports" even for a font with nothing left to
fix, so this reads the result through its Python API.
"""

from __future__ import annotations

import sys

from shaperglot import Checker, Languages

LANGUAGE = "kn_Knda"
CODEPOINT_CHECK = "Mandatory orthography codepoints"


def main(argv: list[str]) -> int:
    font, *listed = argv
    allowed = {chr(int(code.removeprefix("U+"), 16)) for code in listed}
    report = Checker(font).check(Languages()[LANGUAGE])
    verdict = "supported" if report.is_success else "not fully supported"
    print(f"Shaperglot {LANGUAGE}: {verdict}, score {report.score:.1f}%")
    failing = [result for result in report if not result.is_success]
    for result in failing:
        print("  " + " | ".join(str(result).splitlines()))
    if report.is_success:
        return 0
    fixes = report.unique_fixes()
    only_codepoints = set(fixes) == {"add_codepoint"} and all(
        str(result).startswith(CODEPOINT_CHECK) for result in failing
    )
    return 0 if only_codepoints and set(fixes["add_codepoint"]) <= allowed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
