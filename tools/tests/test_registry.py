"""Tests for check_registry.py (AC-01, FR-09)."""

from __future__ import annotations

from pathlib import Path

import pytest

from check_registry import check_registry, main

HEADER = "req_id,source,section,priority,family,area,requirement,eng_phase,backlog,decisions,open_decisions\n"
REGISTER = """# Register
## A. Confirmed decisions
| ID | Decision |
|---|---|
| DEC-001 | Three repos |
## B. Proposed decisions
| ID | Decision |
|---|---|
| DEC-020 | Stack |
## C. Open decisions
| ID | Decision |
|---|---|
| DEC-050 | Taxonomy |
"""
BACKLOG = """# Backlog
| Rank | ID | Item |
|---:|---|---|
| 1 | BL-001 | Owners |
| 2 | BL-101 | Schema |
"""
DEVIATIONS = "| ID | Baseline |\n|---|---|\n| TD-DEV-001 | layout |\n"


def _repo(tmp_path: Path, rows: list[str], register: str = REGISTER, extra_doc: str = "") -> Path:
    for d in ("phase0", "decisions", "features"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "phase0" / "requirements-registry.csv").write_text(HEADER + "".join(rows))
    (tmp_path / "phase0" / "prioritized-backlog.md").write_text(BACKLOG)
    (tmp_path / "decisions" / "decision-register.md").write_text(register)
    (tmp_path / "decisions" / "baseline-deviations.md").write_text(DEVIATIONS)
    (tmp_path / "features" / "doc.md").write_text(extra_doc or "Uses DEC-001, BL-101 and TD-DEV-001.\n")
    (tmp_path / "brd").mkdir()
    (tmp_path / "brd" / "baseline.md").write_text("Baselines are not scanned: DEC-999 BL-999\n")
    return tmp_path


GOOD = ["INV-01,BRD,5.1,Must,INV,Graph,text,P1,BL-101,DEC-050,DEC-050\n",
        "CAN-01,BRD,5.2,Must,CAN,Canvas,text,P1,BL-101 BL-001,DEC-020,\n"]


def codes(root: Path) -> list[str]:
    return sorted(f.code for f in check_registry(root))


def test_valid_repository_passes(tmp_path: Path) -> None:
    assert codes(_repo(tmp_path, GOOD)) == []


def test_real_repository_passes(repo_root: Path) -> None:
    assert check_registry(repo_root) == []


def test_duplicate_requirement_detected(tmp_path: Path) -> None:
    assert codes(_repo(tmp_path, GOOD + [GOOD[0]])) == ["DUPLICATE_REQUIREMENT"]


def test_empty_requirement_id_detected(tmp_path: Path) -> None:
    assert codes(_repo(tmp_path, GOOD + [",BRD,5.1,Must,INV,G,t,P1,BL-101,,\n"])) == ["EMPTY_REQUIREMENT_ID"]


def test_unmapped_requirement_detected(tmp_path: Path) -> None:
    assert codes(_repo(tmp_path, GOOD + ["INV-02,BRD,5.1,Must,INV,G,t,P1,,,\n"])) == ["UNMAPPED_REQUIREMENT"]


def test_unknown_backlog_reference_detected(tmp_path: Path) -> None:
    assert codes(_repo(tmp_path, GOOD + ["INV-03,BRD,5.1,Must,INV,G,t,P1,BL-404,,\n"])) == ["UNKNOWN_BACKLOG_REF"]


def test_unknown_decision_reference_in_document_detected(tmp_path: Path) -> None:
    assert codes(_repo(tmp_path, GOOD, extra_doc="See DEC-777.\n")) == ["UNKNOWN_DECISION_REF"]


def test_unknown_deviation_reference_detected(tmp_path: Path) -> None:
    assert codes(_repo(tmp_path, GOOD, extra_doc="See TD-DEV-009.\n")) == ["UNKNOWN_DEVIATION_REF"]


def test_duplicate_decision_detected(tmp_path: Path) -> None:
    register = REGISTER + "| DEC-020 | Duplicate |\n"
    assert codes(_repo(tmp_path, GOOD, register=register)) == ["DUPLICATE_DECISION"]


def test_stale_open_decision_detected(tmp_path: Path) -> None:
    stale = ["INV-04,BRD,5.1,Must,INV,G,t,P1,BL-101,DEC-020,DEC-020\n"]  # DEC-020 is Proposed, not Open
    assert codes(_repo(tmp_path, GOOD + stale)) == ["STALE_OPEN_DECISION"]


def test_baselines_are_not_scanned(tmp_path: Path) -> None:
    root = _repo(tmp_path, GOOD)
    assert "DEC-999" in (root / "brd" / "baseline.md").read_text()
    assert codes(root) == []


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(_repo(tmp_path / "ok", GOOD))]) == 0
    assert main([str(_repo(tmp_path / "bad", GOOD + [GOOD[0]]))]) == 1
    assert "DUPLICATE_REQUIREMENT" in capsys.readouterr().err
