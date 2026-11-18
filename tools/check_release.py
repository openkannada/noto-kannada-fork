# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Check the release files of 1 style: fontspector, shaperglot and this fork's shaping tests.

    uv run python tools/check_release.py sans --fontspector path/to/fontspector

fontspector runs the Google Fonts profile on the variable and static TTFs. A FAIL, ERROR or
FATAL fails this script unless release/known-fails.toml lists the check with a reason; a
listed check that now passes is reported, so the list can shrink. Reports go to
dist/checks/.
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import rename  # noqa: E402

ROOT = Path(__file__).parent.parent
KNOWN = ROOT / "release" / "known-fails.toml"
BAD = {"FAIL", "ERROR", "FATAL"}
SHAPERGLOT = "uvx --from shaperglot==1.2.2 shaperglot"
# Where tests/test_kannada_fixes.py looks for each style's variable font, under BUILD.
TEST_FONTS = {"sans": "sans/NotoSansKannada-VF.ttf", "serif": "serif/NotoSerifKannada-VF.ttf"}


def failing_checks(report: dict) -> dict[str, list[str]]:
    """check id -> the files (or "family") it failed on."""
    out: dict[str, list[str]] = {}
    for path, sections in report["results"].items():
        for checks in sections.values():
            for check in checks:
                if check["worst_status"] in BAD:
                    out.setdefault(check["check_id"], []).append(Path(path).name or "family")
    return out


def fontspector(binary: Path, fonts: list[Path], out: Path) -> dict[str, list[str]]:
    report = out / "fontspector.json"
    command = [str(binary), "--profile", "googlefonts", "--skip-network", "--json", str(report)]
    command += ["--ghmarkdown", str(out / "fontspector.md"), *map(str, fonts)]
    subprocess.run(command, check=False)
    return failing_checks(json.loads(report.read_text()))


def shaperglot(command: str, font: Path, out: Path) -> bool:
    result = subprocess.run(
        [*shlex.split(command), "check", str(font), "kn_Knda"],
        capture_output=True,
        text=True,
        check=False,
    )
    (out / "shaperglot.txt").write_text(result.stdout + result.stderr)
    return result.returncode == 0 and "100.0%" in result.stdout


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
    parser.add_argument("--shaperglot", default=SHAPERGLOT, help="command that runs shaperglot")
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    args = parser.parse_args(argv)

    names = rename.load(args.style)
    folder = args.dist / names.family_ps
    variable = next((folder / "variable").glob("*.ttf"))
    statics = sorted((folder / "ttf").glob("*.ttf"))
    out = args.dist / "checks" / names.family_ps
    out.mkdir(parents=True, exist_ok=True)

    known = tomllib.loads(KNOWN.read_text()).get(args.style, {})
    failed = fontspector(args.fontspector, [variable, *statics], out)
    new = sorted(set(failed) - set(known))
    fixed = sorted(set(known) - set(failed))
    for check in sorted(failed):
        print(f"fontspector {check}: {'known' if check in known else 'NEW'}")
    for check in fixed:
        print(f"fontspector {check}: listed in known-fails.toml but passes now")
    glot = shaperglot(args.shaperglot, variable, out)
    print(f"shaperglot kn_Knda: {'pass' if glot else 'FAIL'}")
    tests = shaping_tests(args.style, variable)
    print(f"tests/test_kannada_fixes.py on {variable.name}: {'pass' if tests else 'FAIL'}")
    return 0 if not new and glot and tests else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
