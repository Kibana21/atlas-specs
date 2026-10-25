"""Validate the canonical graph contracts and the golden fixture (ATLAS-002 CP2). CI tooling, never deployed.

Usage: uv run --project tools python tools/check_canonical.py [--fixture DIR] [--skip-determinism]

Checks, in order:
1. canonical JSON Schemas against the 2020-12 metaschema; every valid example accepted, every invalid example rejected;
2. the taxonomy artifact (schema and self-consistency);
3. the fixture: manifest hashes, every record's schema, HARD and DOMAIN rules at every revision, the import
   no-op and rejection report, snapshot hashes and expected as-of results, and the expected ADVISORY findings;
4. determinism: regenerating the fixture gives byte-identical files.

HARD and DOMAIN findings fail the run. ADVISORY findings are reported and compared with the fixture's
expected-findings.json; they never block publication.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator

from canonical_model import DOMAIN, HARD, ROOT, SCHEMA_DIR, Dataset, Finding, Taxonomy
from canonical_rules import (
    advisory_findings, advisory_summary, fixture_findings, import_findings, manifest_findings, schema_findings,
    snapshot_findings, taxonomy_findings,
)

EXAMPLES = ROOT / "contracts" / "examples" / "canonical"
DEFAULT_FIXTURE = ROOT / "acceptance" / "test-data" / "canonical-golden-v1"


def example_findings() -> tuple[list[Finding], int]:
    f: list[Finding] = []
    n = 0
    for p in sorted(SCHEMA_DIR.glob("*.v1.json")):
        Draft202012Validator.check_schema(json.loads(p.read_text(encoding="utf-8")))
    for d in sorted(p for p in EXAMPLES.iterdir() if p.is_dir()):
        name = d.name
        valid = sorted(d.glob("valid-*.json"))
        invalid = sorted(d.glob("invalid-*.json"))
        if not valid or not invalid:
            f.append(Finding("H-01", HARD, f"examples/{name}: needs at least one valid and one invalid example"))
        for p in valid:
            n += 1
            f += schema_findings(name, json.loads(p.read_text(encoding="utf-8")), f"examples/{name}/{p.name}")
        for p in invalid:
            n += 1
            if not schema_findings(name, json.loads(p.read_text(encoding="utf-8")), p.name):
                f.append(Finding("H-01", HARD, f"examples/{name}/{p.name}: invalid example was accepted"))
    return f, n


def load_taxonomies(fixture: Path) -> tuple[dict[str, Taxonomy], list[Finding]]:
    base = Taxonomy.load()
    found = taxonomy_findings(base)
    taxes = {base.version: base}
    for p in sorted(fixture.glob("taxonomy-overlay.*.json")):
        overlay = json.loads(p.read_text(encoding="utf-8"))
        found += schema_findings("taxonomy-overlay", overlay, p.name)
        tax = base.with_overlay(overlay)
        taxes[tax.version] = tax
    return taxes, found


def determinism_findings(fixture: Path) -> list[Finding]:
    from generate_golden import build

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / fixture.name
        build(out)
        committed = sorted(p.relative_to(fixture) for p in fixture.rglob("*") if p.is_file())
        generated = sorted(p.relative_to(out) for p in out.rglob("*") if p.is_file())
        if committed != generated:
            return [Finding("H-16", HARD, f"regenerated file set differs: {sorted(set(committed) ^ set(generated))}")]
        return [Finding("H-16", HARD, f"{p}: regenerated content differs") for p in committed if (fixture / p).read_bytes() != (out / p).read_bytes()]


def run(fixture: Path, determinism: bool = True) -> tuple[list[Finding], list[Finding], dict[str, int]]:
    blocking: list[Finding] = []
    ex, n = example_findings()
    blocking += ex
    taxes, tf = load_taxonomies(fixture)
    blocking += tf
    blocking += manifest_findings(fixture)
    ds = Dataset.load(fixture)
    blocking += fixture_findings(ds, taxes)
    blocking += import_findings(ds, taxes, fixture)
    blocking += snapshot_findings(ds, fixture)
    advisories = advisory_findings(ds, taxes)
    expected = json.loads((fixture / "expected-findings.json").read_text(encoding="utf-8"))
    summary = advisory_summary(advisories)
    if summary != expected["advisory"]:
        blocking.append(Finding("H-15", HARD, f"advisory findings {summary} differ from expected {expected['advisory']}"))
    if determinism:
        blocking += determinism_findings(fixture)
    return blocking, advisories, {"examples": n}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    ap.add_argument("--skip-determinism", action="store_true")
    ap.add_argument("--show-advisories", action="store_true")
    args = ap.parse_args(argv)
    blocking, advisories, info = run(args.fixture, not args.skip_determinism)
    hard = [x for x in blocking if x.cls == HARD]
    domain = [x for x in blocking if x.cls == DOMAIN]
    for x in hard + domain:
        print(x)
    print(f"canonical: {info['examples']} schema examples checked; HARD {len(hard)}, DOMAIN {len(domain)}, ADVISORY {len(advisories)}")
    print("advisory by rule: " + ", ".join(f"{k}={v}" for k, v in advisory_summary(advisories).items()))
    if args.show_advisories:
        for x in advisories:
            print(f"  {x}")
    if hard or domain:
        print("canonical: FAILED")
        return 1
    print("canonical: contracts and golden fixture valid" + ("" if args.skip_determinism else "; fixture regenerates byte-identically"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
