# Notices

This repository is a fork of [notofonts/kannada](https://github.com/notofonts/kannada). These authors made the work it is built on:

| Work | Authors | License | Used here |
|---|---|---|---|
| Noto Sans Kannada | The Noto Project Authors; designed by Jelle Bosma and the Monotype design team | OFL-1.1, no Reserved Font Name | `sources/NotoSansKannada.glyphs` and its config |
| Noto Serif Kannada | The Noto Project Authors; designed by Universal Thirst, Indian Type Foundry and the Monotype design team | OFL-1.1, no Reserved Font Name | `sources/NotoSerifKannada.glyphs` and its config |
| The Noto build scripts, workflow and documentation | The Noto Project Authors | OFL-1.1 (upstream ships no separate license for them) | `scripts/`, `Makefile`, `.github/workflows/build.yaml`, `documentation/`, `README.md` apart from the fork's paragraphs at its top and bottom |

"Noto" is a trademark of Google, and the upstream fonts' trademark field says so. Fonts built from this fork are distributed as Neha Sans and Neha Serif. See [FORK.md](FORK.md).

## What is licensed how

| Files | License |
|---|---|
| The font sources and upstream's files | OFL-1.1, see [OFL.txt](OFL.txt) |
| Tests, tools and configuration written for this fork: `tests/`, `tools/`, `release/`, `specimen/template.html`, `rename.toml`, `pyproject.toml`, `uv.lock`, `.github/workflows/fork-ci.yml`, `.github/workflows/release.yml` | MIT OR Apache-2.0, copyright The Open Kannada Authors, see [LICENSES](LICENSES) |
| Documents written for this fork: `FORK.md`, `FONTLOG.txt`, `NOTICE.md`, `CONTRIBUTING.md`, `drafts/` | CC BY 4.0, copyright The Open Kannada Authors, see [LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt) |
| `specimen/sample-kn.json`: Kannada sample text from [googlefonts/lang](https://github.com/googlefonts/lang) (`kn_Knda.textproto`, from the Kannada translation of the Universal Declaration of Human Rights), with 4 typos fixed | Apache-2.0, as googlefonts/lang |
