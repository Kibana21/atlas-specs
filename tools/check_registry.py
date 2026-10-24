"""Validate requirement, backlog, decision and deviation identifiers across atlas-specs (FR-09).

Usage:
    python check_registry.py [REPO_ROOT]

Checks:
  * requirement IDs in phase0/requirements-registry.csv are unique and non-empty
  * every requirement maps to at least one backlog item, and every BL- reference
    (registry, backlog, features/) exists in phase0/prioritized-backlog.md
  * DEC- IDs are unique in decisions/decision-register.md; every DEC- reference in
    the repository's non-baseline documents and the registry resolves
  * every decision the registry lists as open is still Open in the register
  * every TD-DEV- reference resolves to decisions/baseline-deviations.md
Baseline documents (brd/, ux/, technical/) are read-only inputs and are not scanned.
Exit status 0 when valid; 1 with one line per finding ("CODE: message") otherwise.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

BL_ROW = re.compile(r"^\| *\d+ *\| (BL-\d{3}) ", re.M)
DEC_ROW = re.compile(r"^\| (DEC-\d{3}) \|", re.M)
TD_ROW = re.compile(r"^\| (TD-DEV-\d{3}) \|", re.M)
DEC_REF = re.compile(r"\bDEC-\d{3}\b")
BL_REF = re.compile(r"\bBL-\d{3}\b")
TD_REF = re.compile(r"\bTD-DEV-\d{3}\b")
SECTION = re.compile(r"^## ([A-Z]\d?)\. ", re.M)
SECTION_STATUS = {"A": "Confirmed", "A2": "Confirmed", "B": "Proposed", "C": "Open", "F": "Provisional"}
SCANNED_DIRS = ("phase0", "features", "decisions", "contracts", "design", "tools")
SCANNED_FILES = ("README.md", "CLAUDE.md")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def _decision_status(register: str) -> dict[str, str]:
    status: dict[str, str] = {}
    marks = [(m.start(), m.group(1)) for m in SECTION.finditer(register)] + [(len(register), "")]
    for (start, section), (end, _) in zip(marks, marks[1:]):
        for dec in DEC_ROW.findall(register[start:end]):
            status[dec] = SECTION_STATUS.get(section, "Unknown")
    return status


def _scanned_text(root: Path) -> dict[Path, str]:
    files: list[Path] = [root / f for f in SCANNED_FILES if (root / f).exists()]
    for directory in SCANNED_DIRS:
        files += [p for p in (root / directory).rglob("*") if p.suffix in (".md", ".csv", ".json", ".yaml", ".sql", ".conf")
                  and "tests" not in p.parts and ".venv" not in p.parts]
    return {p: p.read_text(encoding="utf-8") for p in sorted(files)}


def check_registry(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    register = (root / "decisions" / "decision-register.md").read_text(encoding="utf-8")
    backlog = (root / "phase0" / "prioritized-backlog.md").read_text(encoding="utf-8")
    deviations_path = root / "decisions" / "baseline-deviations.md"
    deviations = deviations_path.read_text(encoding="utf-8") if deviations_path.exists() else ""

    dec_ids = DEC_ROW.findall(register)
    for dec, n in Counter(dec_ids).items():
        if n > 1:
            findings.append(Finding("DUPLICATE_DECISION", f"{dec} appears {n} times in the decision register"))
    bl_ids = BL_ROW.findall(backlog)
    for bl, n in Counter(bl_ids).items():
        if n > 1:
            findings.append(Finding("DUPLICATE_BACKLOG", f"{bl} appears {n} times in the backlog"))
    td_ids = TD_ROW.findall(deviations)
    for td, n in Counter(td_ids).items():
        if n > 1:
            findings.append(Finding("DUPLICATE_DEVIATION", f"{td} appears {n} times in the deviation record"))
    status = _decision_status(register)

    with (root / "phase0" / "requirements-registry.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    ids = [r["req_id"].strip() for r in rows]
    if not rows:
        findings.append(Finding("EMPTY_REGISTRY", "requirements-registry.csv has no rows"))
    for rid, n in Counter(ids).items():
        if not rid:
            findings.append(Finding("EMPTY_REQUIREMENT_ID", f"{n} row(s) without req_id"))
        elif n > 1:
            findings.append(Finding("DUPLICATE_REQUIREMENT", f"{rid} appears {n} times"))
    for row in rows:
        if not BL_REF.findall(row["backlog"]):
            findings.append(Finding("UNMAPPED_REQUIREMENT", f"{row['req_id']} maps to no backlog item"))
        for dec in row["open_decisions"].split():
            if status.get(dec) not in (None, "Open"):
                findings.append(Finding("STALE_OPEN_DECISION",
                                        f"{row['req_id']} lists {dec} as open but the register says {status[dec]}"))

    known_bl, known_dec, known_td = set(bl_ids), set(dec_ids), set(td_ids)
    for path, text in _scanned_text(root).items():
        rel = path.relative_to(root)
        for bl in sorted(set(BL_REF.findall(text)) - known_bl):
            findings.append(Finding("UNKNOWN_BACKLOG_REF", f"{rel} references {bl}"))
        for dec in sorted(set(DEC_REF.findall(text)) - known_dec):
            findings.append(Finding("UNKNOWN_DECISION_REF", f"{rel} references {dec}"))
        for td in sorted(set(TD_REF.findall(text)) - known_td):
            findings.append(Finding("UNKNOWN_DEVIATION_REF", f"{rel} references {td}"))
    return findings


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else Path(__file__).resolve().parents[1]
    try:
        findings = check_registry(root)
    except (OSError, KeyError, csv.Error) as exc:
        print(f"REGISTRY_UNREADABLE: {exc}", file=sys.stderr)
        return 1
    for finding in findings:
        print(finding, file=sys.stderr)
    if not findings:
        with (root / "phase0" / "requirements-registry.csv").open(encoding="utf-8") as fh:
            n = sum(1 for _ in csv.DictReader(fh))
        print(f"OK: {n} requirements unique and mapped; all BL-/DEC-/TD-DEV- references resolve")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
