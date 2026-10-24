"""Contract conformance and breaking-change checks (ATLAS-001 FR-06, spec §6.7, DEC-095).

Usage:
    python contract_conformance.py conform --contract C.yaml --implementation A.json [--lint]
    python contract_conformance.py breaking --base BASE.yaml --revision REV.yaml
    python contract_conformance.py normalize FILE

conform  (contract C vs FastAPI-generated A):
  1. validity     optional Redocly lint of both documents (--lint)
  2. inventory    MISSING_OPERATION / UNEXPECTED_OPERATION / OPERATION_ID_MISMATCH,
                  MISSING_COMPONENT / UNEXPECTED_COMPONENT, VERSION_MISMATCH
  3. normalize    strip cosmetic *keywords* only (never property, path, parameter, header
                  or component names); canonicalize nullable form and ordering
  4. exact diff   `oasdiff diff --fail-on-diff` on the normalized pair -> STRUCTURAL_DIFF
breaking (previous release vs current contract):
  `oasdiff breaking --fail-on ERR`; errors fail with BREAKING_CHANGE unless the version
  bump permits them (MAJOR, or MINOR before 1.0.0) -> BREAKING_CHANGE_ACKNOWLEDGED.

oasdiff runs from the digest-pinned image in tools/images.lock (no host install).
Exit status: 0 = conformant / acceptable, 1 = findings, 2 = tool error.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

TOOLS_DIR = Path(__file__).resolve().parent
HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")

# Keywords that never change behaviour. They are removed only where they are keywords.
COSMETIC_KEYWORDS = frozenset(
    {"title", "description", "summary", "example", "examples", "externalDocs", "tags", "$comment"}
)
# Keywords whose value is a map from user-chosen *names* to definitions. Keys under these are
# never stripped, so a property named "title" or "description" stays visible to the diff.
NAME_MAPS = frozenset(
    {"paths", "responses", "content", "properties", "patternProperties", "$defs", "definitions",
     "headers", "schemas", "parameters", "requestBodies", "securitySchemes", "links", "callbacks",
     "encoding", "variables", "webhooks", "pathItems", "dependentSchemas"}
)
UNORDERED_LISTS = frozenset({"required", "enum", "anyOf", "oneOf", "allOf", "type"})


class ToolError(RuntimeError):
    pass


@dataclass(frozen=True)
class Finding:
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def load_document(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict) or "openapi" not in data:
        raise ToolError(f"{path} is not an OpenAPI document")
    return data


def oasdiff_image() -> str:
    images = yaml.safe_load((TOOLS_DIR / "images.lock").read_text(encoding="utf-8"))["images"]
    ref = images["oasdiff"]["ref"]
    if "@sha256:" not in ref:
        raise ToolError("oasdiff image in tools/images.lock must be pinned by digest")
    return str(ref)


# --------------------------------------------------------------------------- inventory
def operations(doc: dict[str, Any]) -> dict[tuple[str, str], str | None]:
    ops: dict[tuple[str, str], str | None] = {}
    for path, item in (doc.get("paths") or {}).items():
        for method in HTTP_METHODS:
            if isinstance(item, dict) and method in item:
                ops[(method.upper(), path)] = item[method].get("operationId")
    return ops


def inventory(contract: dict[str, Any], impl: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    c_ops, a_ops = operations(contract), operations(impl)
    for key in sorted(c_ops.keys() - a_ops.keys()):
        findings.append(Finding("MISSING_OPERATION", f"{c_ops[key]} {key[0]} {key[1]} is in the contract but not implemented"))
    for key in sorted(a_ops.keys() - c_ops.keys()):
        findings.append(Finding("UNEXPECTED_OPERATION", f"{key[0]} {key[1]} ({a_ops[key]}) is implemented but not in the contract"))
    for key in sorted(c_ops.keys() & a_ops.keys()):
        if c_ops[key] != a_ops[key]:
            findings.append(Finding("OPERATION_ID_MISMATCH", f"{key[0]} {key[1]}: contract {c_ops[key]!r}, implementation {a_ops[key]!r}"))
    c_comp, a_comp = contract.get("components") or {}, impl.get("components") or {}
    for section in sorted(set(c_comp) | set(a_comp)):
        c_names, a_names = set(c_comp.get(section) or {}), set(a_comp.get(section) or {})
        for name in sorted(c_names - a_names):
            findings.append(Finding("MISSING_COMPONENT", f"components.{section}.{name} is in the contract but not implemented"))
        for name in sorted(a_names - c_names):
            findings.append(Finding("UNEXPECTED_COMPONENT", f"components.{section}.{name} is implemented but not in the contract"))
    for field, c_val, a_val in (("openapi", contract.get("openapi"), impl.get("openapi")),
                                ("info.version", (contract.get("info") or {}).get("version"), (impl.get("info") or {}).get("version"))):
        if str(c_val) != str(a_val):
            findings.append(Finding("VERSION_MISMATCH", f"{field}: contract {c_val!r}, implementation {a_val!r}"))
    return findings


# --------------------------------------------------------------------------- normalization
def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _canonical_nullable(node: dict[str, Any]) -> dict[str, Any]:
    """`type: [X, 'null']` -> `anyOf: [{type: X, ...constraints}, {type: 'null'}]` (style guide §3)."""
    types = node.get("type")
    if isinstance(types, list) and "null" in types and len(types) == 2:
        other = next(t for t in types if t != "null")
        branch = {k: v for k, v in node.items() if k not in ("type", "default")}
        branch["type"] = other
        rest = {k: v for k, v in node.items() if k == "default"}
        return {**rest, "anyOf": [branch, {"type": "null"}]}
    return node


def _normalize(value: Any, parent_key: str | None) -> Any:
    if isinstance(value, list):
        items = [_normalize(v, None) for v in value]
        if parent_key == "parameters" and all(isinstance(i, dict) for i in items):
            return sorted(items, key=lambda p: (str(p.get("in")), str(p.get("name")), _canonical(p)))
        if parent_key in UNORDERED_LISTS:
            return sorted(items, key=_canonical)
        return items
    if not isinstance(value, dict):
        return value
    if parent_key in NAME_MAPS and parent_key != "parameters":
        # Keys are names: keep every one; values are definitions (keyword context).
        return {name: _normalize(v, None) for name, v in value.items()}
    node = _canonical_nullable(value)
    if "enum" in node and isinstance(node["enum"], list) and len(node["enum"]) == 1 and "const" not in node:
        node = {k: v for k, v in node.items() if k != "enum"} | {"const": node["enum"][0]}
    out: dict[str, Any] = {}
    for key, child in node.items():
        if key in COSMETIC_KEYWORDS:
            continue
        if key == "parameters" and isinstance(child, dict):  # components.parameters is a name map
            out[key] = {name: _normalize(v, None) for name, v in child.items()}
            continue
        out[key] = _normalize(child, key)
    return out


def normalize(doc: dict[str, Any]) -> dict[str, Any]:
    doc = copy.deepcopy(doc)
    top: dict[str, Any] = {"openapi": doc.get("openapi"), "info": {"version": (doc.get("info") or {}).get("version")}}
    for key in ("paths", "components", "webhooks", "jsonSchemaDialect", "security"):
        if key in doc:
            top[key] = doc[key]
    normalized = _normalize({k: v for k, v in top.items() if k != "info"}, None)
    normalized["info"] = top["info"]
    return json.loads(_canonical(normalized))


# --------------------------------------------------------------------------- oasdiff
def _run_oasdiff(args: list[str], files: dict[str, dict[str, Any]]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="atlas-oasdiff-") as tmp:
        for name, content in files.items():
            Path(tmp, name).write_text(json.dumps(content, indent=1, sort_keys=True), encoding="utf-8")
        cmd = ["docker", "run", "--rm", "--network", "none", "-v", f"{tmp}:/w:ro", "-w", "/w", oasdiff_image(), *args]
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=180)
        except FileNotFoundError as exc:
            raise ToolError("docker is required to run the pinned oasdiff image") from exc


def structural_diff(contract: dict[str, Any], impl: dict[str, Any]) -> list[Finding]:
    result = _run_oasdiff(["diff", "contract.json", "implementation.json", "--fail-on-diff", "--format", "text"],
                          {"contract.json": normalize(contract), "implementation.json": normalize(impl)})
    if result.returncode == 0:
        return []
    if result.returncode == 1 and result.stdout.strip():
        return [Finding("STRUCTURAL_DIFF", "normalized documents differ:\n" + result.stdout.strip())]
    raise ToolError(f"oasdiff diff failed (exit {result.returncode}): {result.stderr.strip()}")


def conform(contract: dict[str, Any], impl: dict[str, Any]) -> list[Finding]:
    return inventory(contract, impl) + structural_diff(contract, impl)


# --------------------------------------------------------------------------- breaking
_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def _bump_allows_breaking(base_version: str, revision_version: str) -> bool:
    b, r = _VERSION.match(base_version), _VERSION.match(revision_version)
    if not b or not r:
        return False
    (bmaj, bmin, _), (rmaj, rmin, _) = map(int, b.groups()), map(int, r.groups())
    if bmaj >= 1:
        return rmaj > bmaj
    return rmaj > bmaj or rmin > bmin


def breaking(base: dict[str, Any], revision: dict[str, Any]) -> list[Finding]:
    result = _run_oasdiff(["breaking", "base.json", "revision.json", "--fail-on", "ERR", "--format", "text"],
                          {"base.json": base, "revision.json": revision})
    if result.returncode not in (0, 1):
        raise ToolError(f"oasdiff breaking failed (exit {result.returncode}): {result.stderr.strip()}")
    if result.returncode == 0:
        return []
    base_v, rev_v = str(base["info"]["version"]), str(revision["info"]["version"])
    if _bump_allows_breaking(base_v, rev_v):
        print(f"BREAKING_CHANGE_ACKNOWLEDGED: {base_v} -> {rev_v} permits breaking changes; "
              "owner approval required at release.\n" + result.stdout.strip())
        return []
    return [Finding("BREAKING_CHANGE", f"breaking changes without an allowed version bump ({base_v} -> {rev_v}):\n"
                    + result.stdout.strip())]


# --------------------------------------------------------------------------- lint
def _redocly_image() -> str:
    images = yaml.safe_load((TOOLS_DIR / "images.lock").read_text(encoding="utf-8"))["images"]
    return str(images["redocly"]["ref"])


def lint(doc: dict[str, Any], label: str) -> list[Finding]:
    with tempfile.TemporaryDirectory(prefix="atlas-lint-") as tmp:
        Path(tmp, "openapi.json").write_text(json.dumps(doc), encoding="utf-8")
        cmd = ["docker", "run", "--rm", "--network", "none", "-v", f"{tmp}:/spec:ro", _redocly_image(),
               "lint", "--extends", "minimal", "openapi.json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=180)
    if result.returncode != 0:
        return [Finding("INVALID_OPENAPI", f"{label} failed OpenAPI lint:\n{(result.stdout + result.stderr).strip()}")]
    return []


# --------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_conform = sub.add_parser("conform")
    p_conform.add_argument("--contract", type=Path, required=True)
    p_conform.add_argument("--implementation", type=Path, required=True)
    p_conform.add_argument("--lint", action="store_true", help="also lint both documents with pinned Redocly")
    p_break = sub.add_parser("breaking")
    p_break.add_argument("--base", type=Path, required=True)
    p_break.add_argument("--revision", type=Path, required=True)
    p_norm = sub.add_parser("normalize")
    p_norm.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "normalize":
            print(json.dumps(normalize(load_document(args.file)), indent=2, sort_keys=True))
            return 0
        if args.command == "conform":
            contract, impl = load_document(args.contract), load_document(args.implementation)
            findings: list[Finding] = []
            if args.lint:
                findings += lint(contract, "contract") + lint(impl, "implementation")
            findings += conform(contract, impl)
            ok_msg = f"OK: {args.implementation} conforms to {args.contract}"
        else:
            findings = breaking(load_document(args.base), load_document(args.revision))
            ok_msg = f"OK: no unacknowledged breaking changes from {args.base} to {args.revision}"
    except ToolError as exc:
        print(f"TOOL_ERROR: {exc}", file=sys.stderr)
        return 2
    for finding in findings:
        print(finding, file=sys.stderr)
    if not findings:
        print(ok_msg)
    return 1 if findings else 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    sys.exit(main())
