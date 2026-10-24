"""Tests for contract_conformance.py (AC-03, spec §6.7).

Every case runs the real pinned oasdiff image. If Docker is unavailable the tests fail
(they are not skipped): conformance evidence must never be silently absent.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from contract_conformance import breaking, conform, load_document, main, normalize

pytestmark = pytest.mark.docker

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts" / "openapi" / "atlas-api.yaml"
FASTAPI_PATH = Path(__file__).resolve().parent / "fixtures" / "fastapi-generated-0.1.0.json"


@pytest.fixture
def contract() -> dict[str, Any]:
    return load_document(CONTRACT_PATH)


@pytest.fixture
def impl() -> dict[str, Any]:
    return load_document(FASTAPI_PATH)


def codes(findings: list[Any]) -> list[str]:
    return [f.code for f in findings]


def messages(findings: list[Any]) -> str:
    return "\n".join(str(f) for f in findings)


# ------------------------------------------------------------------ (a) cosmetic only -> pass
def test_real_fastapi_output_conforms(contract: dict, impl: dict) -> None:
    """Pydantic titles, FastAPI descriptions, key order and servers differ: still conformant."""
    assert conform(contract, impl) == []


def test_synthetic_cosmetic_changes_conform(contract: dict) -> None:
    other = copy.deepcopy(contract)
    other["info"]["title"] = "Renamed"
    other["servers"] = [{"url": "https://example.invalid"}]
    op = other["paths"]["/api/v1/health/ready"]["get"]
    op["summary"], op["tags"], op["description"] = "x", ["other"], "changed"
    op["responses"]["503"]["description"] = "different words"
    build = other["components"]["schemas"]["BuildInfo"]
    build["required"] = list(reversed(build["required"]))
    build["properties"]["environment"]["enum"] = list(reversed(build["properties"]["environment"]["enum"]))
    build["properties"]["db_migration_revision"] = {"type": ["string", "null"], "description": "spelled differently"}
    build["properties"] = dict(reversed(list(build["properties"].items())))
    other["components"]["schemas"]["HealthLive"]["properties"]["status"] = {"type": "string", "enum": ["ok"]}
    assert conform(contract, other) == []


# ------------------------------------------------------------------ (b)(c)(d) inventory
def test_missing_operation_detected(contract: dict, impl: dict) -> None:
    del impl["paths"]["/api/v1/health/live"]
    findings = conform(contract, impl)
    assert "MISSING_OPERATION" in codes(findings)
    assert "getHealthLive GET /api/v1/health/live" in messages(findings)


def test_unexpected_operation_detected(contract: dict, impl: dict) -> None:
    impl["paths"]["/api/v1/diagnostics/extra"] = copy.deepcopy(impl["paths"]["/api/v1/health/live"])
    impl["paths"]["/api/v1/diagnostics/extra"]["get"]["operationId"] = "getDiagnosticsExtra"
    findings = conform(contract, impl)
    assert "UNEXPECTED_OPERATION" in codes(findings)
    assert "GET /api/v1/diagnostics/extra" in messages(findings)


def test_unexpected_method_on_existing_path_detected(contract: dict, impl: dict) -> None:
    impl["paths"]["/api/v1/health/live"]["post"] = copy.deepcopy(impl["paths"]["/api/v1/health/live"]["get"])
    impl["paths"]["/api/v1/health/live"]["post"]["operationId"] = "postHealthLive"
    assert "UNEXPECTED_OPERATION" in codes(conform(contract, impl))


def test_operation_id_mismatch_detected(contract: dict, impl: dict) -> None:
    impl["paths"]["/api/v1/health/live"]["get"]["operationId"] = "live_api_v1_health_live_get"
    assert "OPERATION_ID_MISMATCH" in codes(conform(contract, impl))


# ------------------------------------------------------------------ (e)(f)(g) structural
def test_added_optional_response_property_detected(contract: dict, impl: dict) -> None:
    impl["components"]["schemas"]["BuildInfo"]["properties"]["extra"] = {"type": "string", "title": "Extra"}
    assert codes(conform(contract, impl)) == ["STRUCTURAL_DIFF"]


def test_removed_required_property_detected(contract: dict, impl: dict) -> None:
    schema = impl["components"]["schemas"]["BuildInfo"]
    del schema["properties"]["environment"]
    schema["required"].remove("environment")
    assert codes(conform(contract, impl)) == ["STRUCTURAL_DIFF"]


def test_changed_status_code_detected(contract: dict, impl: dict) -> None:
    responses = impl["paths"]["/api/v1/diagnostics/build"]["get"]["responses"]
    responses["403"] = responses.pop("404")
    assert codes(conform(contract, impl)) == ["STRUCTURAL_DIFF"]


def test_missing_correlation_header_detected(contract: dict, impl: dict) -> None:
    del impl["paths"]["/api/v1/health/ready"]["get"]["responses"]["503"]["headers"]["X-Correlation-ID"]
    assert codes(conform(contract, impl)) == ["STRUCTURAL_DIFF"]


def test_injected_http_validation_error_detected(contract: dict, impl: dict) -> None:
    impl["components"]["schemas"]["HTTPValidationError"] = {"type": "object", "properties": {"detail": {"type": "array"}}}
    impl["paths"]["/api/v1/health/live"]["get"]["responses"]["422"] = {
        "description": "Validation Error",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HTTPValidationError"}}},
    }
    found = codes(conform(contract, impl))
    assert "UNEXPECTED_COMPONENT" in found and "STRUCTURAL_DIFF" in found


def test_changed_pattern_detected(contract: dict, impl: dict) -> None:
    impl["components"]["schemas"]["BuildInfo"]["properties"]["specs_sha"]["pattern"] = "^[0-9a-f]{7,40}$"
    assert codes(conform(contract, impl)) == ["STRUCTURAL_DIFF"]


def test_changed_const_detected(contract: dict, impl: dict) -> None:
    impl["components"]["schemas"]["ReadinessChecks"]["properties"]["redis"]["const"] = "degraded"
    assert codes(conform(contract, impl)) == ["STRUCTURAL_DIFF"]


def test_version_mismatch_detected(contract: dict, impl: dict) -> None:
    impl["info"]["version"] = "0.2.0"
    assert "VERSION_MISMATCH" in codes(conform(contract, impl))


# ------------------------------------------------------------------ normalization never hides meaning
@pytest.mark.parametrize("name", ["title", "description", "summary", "examples", "tags"])
def test_property_named_like_a_cosmetic_keyword_is_not_hidden(contract: dict, name: str) -> None:
    with_prop = copy.deepcopy(contract)
    with_prop["components"]["schemas"]["HealthLive"]["properties"][name] = {"type": "string"}
    assert name in normalize(with_prop)["components"]["schemas"]["HealthLive"]["properties"]
    assert codes(conform(with_prop, contract)) == ["STRUCTURAL_DIFF"]


def test_normalize_keeps_meaningful_keywords(contract: dict) -> None:
    schema = normalize(contract)["components"]["schemas"]["BuildInfo"]
    assert "title" not in schema and "description" not in schema["properties"]["backend_sha"]
    assert schema["properties"]["backend_sha"]["pattern"] == "^([0-9a-f]{40}|unknown)$"
    assert sorted(schema["required"]) == schema["required"]


# ------------------------------------------------------------------ breaking-change control (specs CI)
def test_breaking_change_without_bump_fails(contract: dict) -> None:
    revision = copy.deepcopy(contract)
    schema = revision["components"]["schemas"]["BuildInfo"]
    del schema["properties"]["environment"]
    schema["required"].remove("environment")
    assert codes(breaking(contract, revision)) == ["BREAKING_CHANGE"]


def test_breaking_change_with_minor_bump_before_1_0_is_acknowledged(contract: dict) -> None:
    revision = copy.deepcopy(contract)
    del revision["paths"]["/api/v1/health/live"]
    revision["info"]["version"] = "0.2.0-dev.1"
    assert breaking(contract, revision) == []


def test_additive_change_is_not_breaking(contract: dict) -> None:
    revision = copy.deepcopy(contract)
    revision["components"]["schemas"]["BuildInfo"]["properties"]["region"] = {"type": "string"}
    revision["info"]["version"] = "0.2.0-dev.1"
    assert breaking(contract, revision) == []


# ------------------------------------------------------------------ CLI
def test_cli_conform_exit_codes(tmp_path: Path, impl: dict, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["conform", "--contract", str(CONTRACT_PATH), "--implementation", str(FASTAPI_PATH)]) == 0
    del impl["paths"]["/api/v1/health/live"]
    bad = tmp_path / "impl.json"
    bad.write_text(json.dumps(impl))
    assert main(["conform", "--contract", str(CONTRACT_PATH), "--implementation", str(bad)]) == 1
    assert "MISSING_OPERATION" in capsys.readouterr().err
