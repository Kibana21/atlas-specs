"""Tests for check_tokens.py (AC-14, FR-08)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from check_tokens import check_tokens, contrast_ratio, main

TOKENS_PATH = Path(__file__).resolve().parents[2] / "design" / "tokens.json"


@pytest.fixture
def tokens() -> dict[str, Any]:
    return json.loads(TOKENS_PATH.read_text())


def codes(findings: list[Any]) -> list[str]:
    return sorted({f.code for f in findings})


def test_contrast_formula_matches_wcag_reference_values() -> None:
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert contrast_ratio("#FFFFFF", "#FFFFFF") == pytest.approx(1.0)
    assert contrast_ratio("#767676", "#FFFFFF") == pytest.approx(4.54, abs=0.01)  # classic AA boundary grey


def test_repository_tokens_are_valid(tokens: dict) -> None:
    findings, checked = check_tokens(tokens)
    assert findings == []
    assert checked == len(tokens["contrast_pairs"]) >= 100


def test_failing_text_pair_detected(tokens: dict) -> None:
    tokens["color"]["entity"]["api"]["text"]["value"] = "#1674E8"  # the accent: 4.08:1 on subtle, below 4.5
    findings, _ = check_tokens(tokens)
    assert codes(findings) == ["CONTRAST"]
    assert any("color.entity.api.text" in str(f) for f in findings)


def test_failing_non_text_pair_detected(tokens: dict) -> None:
    tokens["color"]["line"]["strong"]["value"] = "#C9D4E3"  # decorative grey: ~1.4:1
    assert codes(check_tokens(tokens)[0]) == ["CONTRAST"]


def test_missing_entity_kind_detected(tokens: dict) -> None:
    del tokens["color"]["entity"]["messaging"]
    assert "MISSING_TOKEN" in codes(check_tokens(tokens)[0])


def test_missing_group_detected(tokens: dict) -> None:
    del tokens["motion"]
    assert codes(check_tokens(tokens)[0]) == ["MISSING_GROUP"]


def test_dark_scheme_rejected(tokens: dict) -> None:
    tokens["meta"]["color_scheme"] = "dark"
    assert codes(check_tokens(tokens)[0]) == ["COLOR_SCHEME"]


def test_bad_colour_format_detected(tokens: dict) -> None:
    tokens["color"]["surface"]["raised"]["value"] = "white"
    assert "COLOR_FORMAT" in codes(check_tokens(tokens)[0])


def test_unapproved_status_detected(tokens: dict) -> None:
    tokens["color"]["ink"]["primary"]["status"] = "final"
    assert codes(check_tokens(tokens)[0]) == ["TOKEN_STATUS"]


def test_slow_motion_and_missing_reduced_motion_detected(tokens: dict) -> None:
    broken = copy.deepcopy(tokens)
    broken["motion"]["duration"]["slow"]["value"] = "400ms"
    del broken["motion"]["reduced"]["duration"]
    assert codes(check_tokens(broken)[0]) == ["MOTION"]


def test_minimums_enforced(tokens: dict) -> None:
    tokens["typography"]["size"]["xs"]["value"] = "10px"
    tokens["size"]["control-sm"]["value"] = "20px"
    tokens["focus"]["ring-width"]["value"] = "1px"
    assert codes(check_tokens(tokens)[0]) == ["FOCUS", "TARGET_SIZE", "TYPOGRAPHY"]


def test_unknown_reference_detected(tokens: dict) -> None:
    tokens["contrast_pairs"].append({"fg": "color.ink.missing", "bg": "color.surface.app", "min": "text", "purpose": "x"})
    assert codes(check_tokens(tokens)[0]) == ["UNKNOWN_REFERENCE"]


def test_cli(tmp_path: Path, tokens: dict, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(TOKENS_PATH)]) == 0
    assert "contrast pairs meet" in capsys.readouterr().out
    tokens["color"]["ink"]["muted"]["value"] = "#9AA7B8"
    bad = tmp_path / "tokens.json"
    bad.write_text(json.dumps(tokens))
    assert main([str(bad)]) == 1
