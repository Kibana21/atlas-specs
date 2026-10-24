"""JSON Schemas in contracts/schemas must equal the OpenAPI components they describe.

Prevents the two contract artefacts (S-03 schemas, S-04 OpenAPI) from drifting apart. The
comparison uses the same cosmetic normalization as conformance.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from contract_conformance import load_document, normalize

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "contracts" / "schemas"
# schema file -> (root component, {$defs name: component name})
MAPPING = {
    "error.v1.json": ("ErrorEnvelope", {"ErrorBody": "ErrorBody"}),
    "health-live.v1.json": ("HealthLive", {}),
    "health-ready.v1.json": ("HealthReady", {"ReadinessChecks": "ReadinessChecks"}),
    "build-info.v1.json": ("BuildInfo", {}),
}
SCHEMA_ONLY_KEYS = ("$schema", "$id", "$defs")


def _as_component(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: (v.replace("#/$defs/", "#/components/schemas/") if k == "$ref" else _as_component(v))
                for k, v in node.items() if k not in SCHEMA_ONLY_KEYS}
    if isinstance(node, list):
        return [_as_component(v) for v in node]
    return node


def _normalized_schema(schema: Any) -> Any:
    wrapper = {"openapi": "3.1.0", "info": {"version": "x"}, "components": {"schemas": {"X": schema}}}
    return normalize(wrapper)["components"]["schemas"]["X"]


@pytest.fixture(scope="module")
def components() -> dict[str, Any]:
    return load_document(ROOT / "contracts" / "openapi" / "atlas-api.yaml")["components"]["schemas"]


def test_every_schema_file_is_mapped() -> None:
    assert sorted(p.name for p in SCHEMAS.glob("*.json")) == sorted(MAPPING)


@pytest.mark.parametrize("filename", sorted(MAPPING))
def test_schema_matches_component(filename: str, components: dict[str, Any]) -> None:
    schema = json.loads((SCHEMAS / filename).read_text())
    root, defs = MAPPING[filename]
    assert _normalized_schema(_as_component(schema)) == _normalized_schema(components[root])
    for def_name, component in defs.items():
        assert _normalized_schema(_as_component(schema["$defs"][def_name])) == _normalized_schema(components[component])
