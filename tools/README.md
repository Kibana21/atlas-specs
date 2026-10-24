# atlas-specs tooling

CI validation scripts for this repository. **Not product code; never deployed.**
Python 3.12 in a project-local uv environment (`uv run --project tools ...`); no global installs.
Container tools (markdownlint, Redocly, oasdiff) are pinned by digest in `images.lock`.

| Script | Purpose | Spec |
|---|---|---|
| `check_specs_lock.py` | Validate a consumer `specs.lock` (full SHA on `main`, files present, version match, `--release` tag) | FR-05 |
| `contract_conformance.py` | Operation inventory + normalized exact diff + breaking check | FR-06, §6.7 |
| `check_tokens.py` | WCAG contrast and completeness of `design/tokens.json` | FR-08 |
| `check_registry.py` | Unique requirement IDs; `BL-`/`DEC-`/`TD-DEV-` references resolve | FR-09 |

Run everything with `make check` from the repository root.
