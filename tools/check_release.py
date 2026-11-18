# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Check the release files of 1 style: names, fontspector, Shaperglot and the shaping tests.

    uv run python tools/check_release.py sans --fontspector path/to/fontspector

- Every font in the release (TTF, OTF, WOFF2) is scanned for the upstream name.
- fontspector runs the Google Fonts profile on the variable font, the static TTFs and the
  OTFs. A FAIL, ERROR or FATAL fails this script unless release/known-fails.toml lists its
  check and failure code, and its file matches the entry's file patterns, with a reason; a
  listed check that no longer fails is reported, so the list can shrink.
- Shaperglot checks kn_Knda through tools/shaperglot_gate.py.
- tests/test_kannada_fixes.py runs on the released variable font.

Reports go to dist/checks/<family>/.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
from fnmatch import fnmatch
from pathlib import Path

from release import unrenamed
from rename import load

ROOT = Path(__file__).parent.parent
KNOWN = ROOT / "release" / "known-fails.toml"
BAD = {"FAIL", "ERROR", "FATAL"}
SHAPERGLOT_PYTHON = "uvx --from shaperglot==1.2.2 python"
# Where tests/test_kannada_fixes.py looks for each style's variable font, under BUILD.
TEST_FONTS = {"sans": "sans/NotoSansKannada-VF.ttf", "serif": "serif/NotoSerifKannada-VF.ttf"}


Failure = tuple[str, str, str]  # check id, failure code, file name ("" for the family)


def failures(report: dict) -> set[Failure]:
    """Every FAIL, ERROR or FATAL in a fontspector report."""
    return {
        (check["check_id"], sub.get("code") or "", Path(path).name)
        for path, sections in report["results"].items()
        for checks in sections.values()
        for check in checks
        for sub in check["subresults"]
        if sub["severity"] in BAD
    }


def is_known(failure: Failure, known: dict) -> bool:
    """Listed under its check with its code, and its file matches the entry's files, if any."""
    check, code, name = failure
    entry = known.get(check)
    if entry is None or code not in entry["codes"]:
        return False
    return any(fnmatch(name, pattern) for pattern in entry.get("files", ["*"]))


def fontspector(binary: Path, fonts: list[Path], out: Path) -> set[Failure]:
    report = out / "fontspector.json"
    report.unlink(missing_ok=True)
    command = [str(binary), "--profile", "googlefonts", "--skip-network", "--json", str(report)]
    command += ["--ghmarkdown", str(out / "fontspector.md"), *map(str, fonts)]
    subprocess.run(command, check=False)
    if not report.exists():
        raise SystemExit("fontspector wrote no report")
    return failures(json.loads(report.read_text()))


def shaperglot(python: str, font: Path, out: Path, allowed: list[str]) -> bool:
    gate = ROOT / "tools" / "shaperglot_gate.py"
    result = subprocess.run(
        [*shlex.split(python), str(gate), str(font), *allowed],
        capture_output=True,
        text=True,
        check=False,
    )
    (out / "shaperglot.txt").write_text(result.stdout + result.stderr)
    print(result.stdout.strip())
    return result.returncode == 0


def shaping_tests(style: str, variable: Path) -> bool:
    """Run tests/test_kannada_fixes.py on the released variable font."""
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / TEST_FONTS[style]
        target.parent.mkdir(parents=True)
        shutil.copy(variable, target)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-k", style, "tests/test_kannada_fixes.py"],
            cwd=ROOT,
            env={**os.environ, "BUILD": tmp},
            check=False,
        )
    return result.returncode == 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("style", choices=sorted(TEST_FONTS))
    parser.add_argument("--fontspector", type=Path, required=True)
    parser.add_argument(
        "--shaperglot-python", default=SHAPERGLOT_PYTHON, help="a Python that has Shaperglot"
    )
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    args = parser.parse_args(argv)

    names = load(args.style)
    folder = args.dist / names.family_ps
    variable = next((folder / "variable").glob("*.ttf"))
    statics = sorted((folder / "ttf").glob("*.ttf"))
    otfs = sorted((folder / "otf").glob("*.otf"))
    out = args.dist / "checks" / names.family_ps
    out.mkdir(parents=True, exist_ok=True)

    every_font = sorted(p for p in folder.rglob("*") if p.suffix in {".ttf", ".otf", ".woff2"})
    for path in every_font:
        unrenamed(path)
    print(f"names: no upstream name left in {len(every_font)} fonts")

    known = tomllib.loads(KNOWN.read_text()).get(args.style, {})
    found = fontspector(args.fontspector, [variable, *statics, *otfs], out)
    new = sorted(f for f in found if not is_known(f, known))
    for check in sorted({f[0] for f in found}):
        print(f"fontspector {check}: {'NEW' if any(f[0] == check for f in new) else 'known'}")
    for check, code, name in new:
        print(f"  new: {check} ({code}) in {name or 'the family'}")
    for check in sorted(set(known) - {f[0] for f in found}):
        print(f"fontspector {check}: listed in known-fails.toml but passes now")
    glot = shaperglot(args.shaperglot_python, variable, out, [])
    tests = shaping_tests(args.style, variable)
    print(f"tests/test_kannada_fixes.py on {variable.name}: {'pass' if tests else 'FAIL'}")
    return 0 if not new and glot and tests else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
