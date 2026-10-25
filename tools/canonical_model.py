"""Reference model for the canonical graph contracts (ATLAS-002 CP2). CI tooling, never deployed.

Implements, in plain Python, exactly what the Accepted ADRs define, so that the golden fixture
can be generated and checked:

* taxonomy loading and type/category matching (ADR-0017, ADR-0019);
* the approved identity normalization rules only (ADR-0003): ``arm-1``, ``guid-1``,
  ``apim-api-1``, ``preserve-1`` (validation only, case preserved), ``k8s-uid-1``,
  ``org-key-1`` and ``source-1``; ``planned`` and ``reserved`` namespaces are rejected;
* as-of reconstruction and the graph hash (ADR-0008 §4, §6);
* the import planner used for the deterministic, idempotent load (ADR-0008 §8);
* validation rules classified HARD / DOMAIN / ADVISORY (contracts/canonical-validation-rules.md).

The backend (CP3/CP4) re-implements these rules; this module is the executable reference
for the contracts, not a library the backend imports.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "contracts" / "taxonomy" / "atlas-taxonomy.v1.json"
SCHEMA_DIR = ROOT / "contracts" / "schemas" / "canonical"

HARD, DOMAIN, ADVISORY = "HARD", "DOMAIN", "ADVISORY"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_of(value: Any) -> str:
    data = value if isinstance(value, bytes) else canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------- taxonomy


class Taxonomy:
    """One taxonomy version, optionally an overlay over a base version."""

    def __init__(self, doc: dict[str, Any]) -> None:
        self.doc = doc
        self.version: str = doc["taxonomy_version"]
        self.enums: dict[str, list[str]] = doc["enumerations"]
        self.types: dict[str, dict[str, Any]] = {t["type_key"]: t for t in doc["entity_types"]}
        self.rels: dict[str, dict[str, Any]] = {r["rel_type"]: r for r in doc["relationship_types"]}
        self.categories = {c["category"] for c in doc["categories"]}
        self.providers = {p["provider"]: p for p in doc["providers"]}
        self.namespaces = {n["namespace"]: n for n in doc["identity_namespaces"]}
        self.actor_namespaces = {a["namespace"]: a for a in doc["actor_namespaces"]}
        self.scope_rules = doc["provider_scope_rules"]
        self.mappings: dict[str, dict[str, str]] = {
            prov: {m["native_type"]: m["category"] for m in items} for prov, items in doc["native_type_mappings"].items()
        }
        common = doc["common_attributes"]
        self.attr_name_re = re.compile(common["attribute_name_pattern"])
        self.forbidden_attr_re = re.compile(common["forbidden_attribute_name_pattern"])
        self.platform_providers = set(common["platform_required_for_providers"])

    @classmethod
    def load(cls, path: Path = TAXONOMY_PATH) -> Taxonomy:
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def with_overlay(self, overlay: dict[str, Any]) -> Taxonomy:
        if overlay.get("extends") != self.version:
            raise ValueError(f"overlay extends {overlay.get('extends')}, base is {self.version}")
        doc = copy.deepcopy(self.doc)
        doc["taxonomy_version"] = overlay["taxonomy_version"]
        doc["status"] = overlay["status"]
        for prov, items in overlay.get("add_native_type_mappings", {}).items():
            doc["native_type_mappings"].setdefault(prov, []).extend(items)
        return Taxonomy(doc)

    # ---- enumerations referenced as "@name"
    def enum_values(self, spec: Any) -> list[str]:
        if isinstance(spec, str) and spec.startswith("@"):
            return self.enums[spec[1:]]
        return list(spec)

    def type_def(self, type_key: str) -> dict[str, Any] | None:
        return self.types.get(type_key)

    def matches(self, type_key: str, refs: list[str]) -> bool:
        """True if ``type_key`` matches any of: type key, ``category:X``, ``category:physical``, ``*``."""
        t = self.types.get(type_key)
        if t is None:
            return False
        for r in refs:
            if r == "*" or r == type_key:
                return True
            if r == "category:physical" and t["kind"] == "physical":
                return True
            if r.startswith("category:") and t["category"] == r.split(":", 1)[1]:
                return True
        return False

    def allowed_parent(self, child_type: str, parent_type: str) -> bool:
        t = self.types.get(child_type)
        return bool(t) and self.matches(parent_type, t["containment_parents"])


# --------------------------------------------------------------------------- identity normalization


class NormalizationError(ValueError):
    pass


GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
K8S_UID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def normalize_arm(original: str) -> tuple[str, dict[str, Any]]:
    """Rule ``arm-1`` (ADR-0003): validate and reject, never repair; trim; one trailing '/'; lowercase."""
    s = original.strip()
    if s.endswith("/"):
        s = s[:-1]
    if len(s) > 2048:
        raise NormalizationError("ARM ID longer than 2048 characters")
    if any(c.isspace() for c in s) or "?" in s or "#" in s:
        raise NormalizationError("ARM ID contains whitespace, a query string or a fragment")
    if not s.startswith("/"):
        raise NormalizationError("ARM ID must start with '/'")
    segments = s[1:].split("/")
    if any(seg == "" for seg in segments):
        raise NormalizationError("ARM ID has an empty segment ('//')")
    if any(seg in (".", "..") for seg in segments):
        raise NormalizationError("ARM ID has a '.' or '..' segment")
    low = [seg.lower() for seg in segments]
    parts: dict[str, Any] = {"subscription_id": None, "resource_group": None, "provider_namespace": None,
                             "type_path": None, "name_path": None}
    i = 0
    if low[0] == "subscriptions":
        if len(low) < 2 or not GUID_RE.match(low[1]):
            raise NormalizationError("ARM ID must start with /subscriptions/{guid}")
        parts["subscription_id"] = low[1]
        i = 2
        if i < len(low) and low[i] == "resourcegroups":
            if i + 1 >= len(low):
                raise NormalizationError("ARM ID names resourceGroups without a name")
            parts["resource_group"] = low[i + 1]
            i += 2
    elif low[0] != "providers":
        raise NormalizationError("ARM ID must start with /subscriptions/ or /providers/")
    if i < len(low):
        if low[i] != "providers" or i + 1 >= len(low):
            raise NormalizationError("ARM ID: expected /providers/{namespace}")
        rest = low[i + 2:]
        if not rest or len(rest) % 2:
            raise NormalizationError("ARM ID: provider part must alternate type and name segments")
        parts["provider_namespace"] = low[i + 1]
        parts["type_path"] = "/".join(rest[0::2])
        parts["name_path"] = "/".join(rest[1::2])
    normalized = "/" + "/".join(low)
    return normalized, parts


def arm_native_type(parts: dict[str, Any]) -> str | None:
    if parts.get("provider_namespace"):
        return f"{parts['provider_namespace']}/{parts['type_path']}"
    if parts.get("resource_group"):
        return "microsoft.resources/resourcegroups"
    if parts.get("subscription_id"):
        return "microsoft.resources/subscriptions"
    return None


def normalize_identity(tax: Taxonomy, namespace: str, original: str) -> tuple[str, dict[str, Any], str]:
    """Return (normalized_key, key_parts, normalization_version) or raise NormalizationError."""
    ns = tax.namespaces.get(namespace)
    if ns is None and namespace.startswith("source."):
        ns = tax.namespaces["source.*"]
        if not re.match(r"^source\.[a-z0-9][a-z0-9_-]*$", namespace):
            raise NormalizationError(f"invalid source namespace {namespace!r}")
    if ns is None:
        raise NormalizationError(f"unknown identity namespace {namespace!r}")
    if ns["status"] in ("planned", "reserved"):
        raise NormalizationError(f"namespace {namespace} is {ns['status']}: no approved normalization rule yet")
    rule = ns["normalization_rule"]
    if rule == "arm-1":
        key, parts = normalize_arm(original)
        return key, parts, rule
    if rule == "guid-1":
        s = original.strip()
        if not GUID_RE.match(s):
            raise NormalizationError("not a canonical GUID")
        return s.lower(), {}, rule
    if rule == "apim-api-1":
        m = re.match(r"^(?P<arm>/[^#]+)#api:(?P<api>[^;#\s]+);rev=(?P<rev>[^;#\s]+)$", original.strip())
        if not m:
            raise NormalizationError("apim.api key must be {arm}#api:{apiId};rev={revision}")
        arm, _ = normalize_arm(m["arm"])
        return f"{arm}#api:{m['api']};rev={m['rev']}", {"apim_service": arm, "api_id": m["api"], "revision": m["rev"]}, rule
    if rule in ("preserve-1", "source-1"):
        s = original.strip()
        if not re.match(ns["pattern"], s):
            raise NormalizationError(f"{namespace} key does not match its approved format {ns['format']}")
        return s, {}, rule
    if rule == "k8s-uid-1":
        cluster, sep, uid = original.strip().rpartition("#")
        cns, sep2, ckey = cluster.partition(":")
        if not sep or not sep2 or not K8S_UID_RE.match(uid):
            raise NormalizationError("k8s.uid key must be {cluster namespace}:{cluster key}#{uid}")
        if cns == "k8s.uid":
            raise NormalizationError("a cluster key cannot itself be a k8s.uid")
        nkey, _, _ = normalize_identity(tax, cns, ckey)
        return f"{cns}:{nkey}#{uid.lower()}", {"cluster_namespace": cns, "cluster_key": nkey}, rule
    if rule == "org-key-1":
        s = original.strip()
        if not s:
            raise NormalizationError("empty organization key")
        return s.lower(), {}, rule
    raise NormalizationError(f"no implementation for rule {rule}")


# --------------------------------------------------------------------------- deterministic UUIDv7

UUID_EPOCH_MS = 1_790_000_000_000  # fixed synthetic timestamp base (2026-09); ordering only


def uuid7(seq: int, name: str) -> str:
    """Deterministic UUIDv7: 48-bit timestamp from a fixed base + sequence, random bits from SHA-256(name)."""
    ts = UUID_EPOCH_MS + seq
    h = int.from_bytes(hashlib.sha256(name.encode("utf-8")).digest()[:10], "big")
    rand_a = (h >> 68) & 0xFFF
    rand_b = h & ((1 << 62) - 1)
    value = (ts << 80) | (0x7 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    hx = f"{value:032x}"
    return f"{hx[0:8]}-{hx[8:12]}-{hx[12:16]}-{hx[16:20]}-{hx[20:32]}"


# --------------------------------------------------------------------------- fixture data access

TABLES = {
    "organizations": "organization",
    "change_sets": "change-set",
    "entities": "entity",
    "entity_versions": "entity-version",
    "relationships": "relationship",
    "relationship_versions": "relationship-version",
    "external_identities": "external-identity",
    "evidence": "evidence",
    "fact_assertions": "fact-assertion",
    "graph_snapshots": "graph-snapshot",
}


def dump_records(records: list[dict[str, Any]]) -> str:
    """One compact, key-sorted record per line: deterministic and diff-friendly."""
    if not records:
        return "[]\n"
    return "[\n" + ",\n".join(canonical_json(r) for r in records) + "\n]\n"


def valid_at(row: dict[str, Any], revision: int) -> bool:
    return row["revision_from"] <= revision and (row["revision_to"] is None or row["revision_to"] > revision)


TRUST_POLICY_FILE = "trust-policy.json"
NO_POLICY: dict[str, Any] = {"freshness": [], "precedence": []}


@dataclass
class Dataset:
    tables: dict[str, list[dict[str, Any]]]
    policy: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(NO_POLICY))   # trust policy (TF-F, TF-2)

    @classmethod
    def load(cls, directory: Path) -> Dataset:
        tables = {t: json.loads((directory / f"{t}.json").read_text(encoding="utf-8")) for t in TABLES}
        policy_path = directory / TRUST_POLICY_FILE
        policy = json.loads(policy_path.read_text(encoding="utf-8")) if policy_path.exists() else copy.deepcopy(NO_POLICY)
        return cls(tables, policy)

    def org_ids(self) -> list[str]:
        return [o["id"] for o in self.tables["organizations"]]

    def head(self, org_id: str) -> int:
        return max((c["revision"] for c in self.tables["change_sets"] if c["org_id"] == org_id), default=0)


@dataclass
class State:
    """Graph state of one organization as of one revision (ADR-0008 §6)."""

    org_id: str
    revision: int
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)        # id -> present version
    relationships: dict[str, dict[str, Any]] = field(default_factory=dict)   # id -> identity + present version
    identities: dict[tuple[str, str], str] = field(default_factory=dict)     # (namespace, normalized) -> entity id
    assertions: list[dict[str, Any]] = field(default_factory=list)
    evidence_hashes: dict[str, str] = field(default_factory=dict)            # artifact_hash -> evidence id


def as_of(ds: Dataset, org_id: str, revision: int) -> State:
    st = State(org_id, revision)
    for v in ds.tables["entity_versions"]:
        if v["org_id"] == org_id and valid_at(v, revision) and v["record_state"] == "present":
            st.entities[v["entity_id"]] = v
    rel_ids = {r["id"]: r for r in ds.tables["relationships"] if r["org_id"] == org_id}
    for v in ds.tables["relationship_versions"]:
        if v["org_id"] == org_id and valid_at(v, revision) and v["record_state"] == "present":
            st.relationships[v["relationship_id"]] = {**rel_ids[v["relationship_id"]], "version": v}
    for i in ds.tables["external_identities"]:
        if i["org_id"] == org_id and valid_at(i, revision):
            st.identities[(i["namespace"], i["normalized_key"])] = i["entity_id"]
    st.assertions = [a for a in ds.tables["fact_assertions"] if a["org_id"] == org_id and valid_at(a, revision)]
    for e in ds.tables["evidence"]:
        if e["org_id"] == org_id and e["change_revision"] <= revision and e["artifact_hash"]:
            st.evidence_hashes[e["artifact_hash"]] = e["id"]
    return st


ENTITY_HASH_FIELDS = ("type_key", "category", "provider", "native_type", "merged_into", "display_name", "lifecycle",
                      "environment_scope", "environment_id", "container_id", "attributes", "trust_state", "verification_state")
REL_HASH_FIELDS = ("lifecycle", "environment_id", "cross_environment", "shared_endpoint", "cross_provider", "attributes",
                   "trust_state", "verification_state")


def graph_hash(st: State) -> str:
    """SHA-256 over present facts and their current assertions; no revision numbers or timestamps (ADR-0008 §4)."""
    ents = [{"id": i, **{k: v[k] for k in ENTITY_HASH_FIELDS}} for i, v in sorted(st.entities.items())]
    rels = [{"id": i, "rel_type": r["rel_type"], "from_id": r["from_id"], "to_id": r["to_id"], "discriminator": r["discriminator"],
             **{k: r["version"][k] for k in REL_HASH_FIELDS}} for i, r in sorted(st.relationships.items())]
    present = set(st.entities) | set(st.relationships)
    asserts = sorted(
        (canonical_json([a["fact_id"], a["field_path"], a["asserted_value"], a["evidence_id"]]) for a in st.assertions if a["fact_id"] in present)
    )
    return sha256_of({"entities": ents, "relationships": rels, "assertions": asserts})


# --------------------------------------------------------------------------- derived values


def default_trust(kinds: set[str]) -> str:
    """Generator's choice from the existence evidence kinds; tools check it against ``trust_v1``."""
    if "provider_configuration" in kinds:
        return "discovered"
    if "human_assertion" in kinds:
        return "curated"
    if kinds and kinds <= {"documentation", "contract"}:
        return "documented"
    if kinds == {"inferred"}:
        return "inferred"
    raise ValueError(f"no trust state for evidence kinds {sorted(kinds)}")


# --------------------------------------------------------------------------- trust function v1 (contracts/trust-function.md)

TRUST_FUNCTION_VERSION = "trust-1"
EVIDENCE_KINDS = frozenset({"provider_configuration", "contract", "documentation", "human_assertion", "inferred"})
HUMAN_ACTOR_NAMESPACES = frozenset({"oidc"})   # taxonomy actor_namespaces with actor_kind human (a test keeps them equal)
# TF-V: existence evidence that can support a human verification, by claim class
VERIFICATION_SUPPORT = {
    "physical": frozenset({"provider_configuration", "human_assertion"}),
    "logical": frozenset({"human_assertion", "documentation", "contract"}),
}


@dataclass(frozen=True)
class Claim:
    """What a fact claims, as far as trust is concerned.

    ``physical``: a physical entity, or a relationship with at least one physical endpoint.
    ``allowed_kinds``: for a relationship, the taxonomy's allowed evidence kinds for its type.
    """

    fact_kind: str
    physical: bool
    allowed_kinds: frozenset[str] | None = None

    def applicable_kinds(self) -> frozenset[str]:
        """TF-A: evidence kinds that can establish this claim's existence."""
        kinds = frozenset(self.allowed_kinds or ()) if self.fact_kind == "relationship" else EVIDENCE_KINDS
        # provider configuration never establishes a logical or business fact on its own (G2 closure decision 2)
        return kinds if self.physical else kinds - {"provider_configuration"}


def _ts(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def freshness_of(assertion: dict[str, Any], policy: dict[str, Any], at: str) -> str:
    """TF-F: ``fresh``, ``expired`` or ``unassessed`` (no freshness policy defined for the source)."""
    rule = next((p for p in policy.get("freshness", []) if p["method"] == assertion["method"]), None)
    if rule is None:
        return "unassessed"
    age_days = (_ts(at) - _ts(assertion["observed_at"])) / 86400
    return "expired" if age_days > rule["stale_after_days"] else "fresh"


def trust_v1(claim: Claim, assertions: list[dict[str, Any]], verification: dict[str, Any] | None, policy: dict[str, Any],
             at: str, prior_values: dict[str, Any] | None = None, origin: str = "published") -> dict[str, Any]:
    """Pure, deterministic trust function v1 (owner decision U-3, 25 Oct 2026).

    ``assertions`` are the fact's current assertions at the evaluated revision, each with ``evidence_kind``,
    ``field_path``, ``asserted_value``, ``method``, ``observed_at`` and ``valid_to`` (from its evidence).
    ``at`` is the evaluation time (the publishing change set's time), never the wall clock.
    Returns the trust state, the verification state it supports, the deciding rule and the selected values
    of every asserted field.
    """
    if policy.get("precedence"):
        raise ValueError("trust-1 accepts no precedence rules: DEC-034 values are not approved")
    out: dict[str, Any] = {"function": TRUST_FUNCTION_VERSION, "selected": {}}
    if origin == "draft":
        return {**out, "trust_state": "proposed", "verification_state": "unverified", "rule": "TF-0"}
    current = [a for a in assertions if not a.get("valid_to") or _ts(a["valid_to"]) > _ts(at)]
    existence = [a for a in current if a["field_path"] is None and a["evidence_kind"] in claim.applicable_kinds()]
    # TF-2: materially incompatible values for one field, unresolved (no approved precedence in v1)
    values: dict[str, set[str]] = {}
    for a in current:
        if a["field_path"] is not None:
            values.setdefault(a["field_path"], set()).add(canonical_json(a["asserted_value"]))
    conflicts = sorted(p for p, vs in values.items() if len(vs) > 1)
    for p, vs in values.items():
        out["selected"][p] = (prior_values or {}).get(p) if p in conflicts else json.loads(next(iter(vs)))
    out["conflicts"] = conflicts
    if not existence:
        return {**out, "trust_state": None, "verification_state": "unverified", "rule": "TF-1"}
    usable = [a for a in existence if freshness_of(a, policy, at) != "expired"]
    kinds = {a["evidence_kind"] for a in usable}
    v = verification or {}
    recorded = v.get("verification_state") == "verified"
    expired = recorded and v.get("expires_at") is not None and _ts(v["expires_at"]) <= _ts(at)
    if conflicts:
        state, rule = "conflicted", "TF-2"
    elif expired:
        state, rule = "stale", "TF-3a"
    elif not usable:
        state, rule = "stale", "TF-3b"
    elif "provider_configuration" in kinds:
        state, rule = "discovered", "TF-4"
    elif "human_assertion" in kinds:
        state, rule = "curated", "TF-5"
    elif kinds & {"documentation", "contract"}:
        state, rule = "documented", "TF-6"
    else:
        state, rule = "inferred", "TF-7"
    out.update(trust_state=state, rule=rule)
    # TF-V: a recorded human verification counts only when the claim's evidence can support it
    reasons = []
    if recorded:
        if (v.get("verified_by") or {}).get("namespace") not in HUMAN_ACTOR_NAMESPACES:
            reasons.append("verified_by is not a human actor")
        if not v.get("verified_at") or _ts(v["verified_at"]) > _ts(at):
            reasons.append("verified_at missing or after the evaluation time")
        if state not in ("discovered", "curated", "documented"):
            reasons.append(f"trust state {state}")
        support = VERIFICATION_SUPPORT["physical" if claim.physical else "logical"]
        if not kinds & support:
            reasons.append(f"no current evidence of {sorted(support)}")
    out["verification_state"] = "verified" if recorded and not reasons else "unverified"
    out["verification_reasons"] = reasons
    return out


def relationship_flags(frm: dict[str, Any], to: dict[str, Any]) -> dict[str, Any]:
    """Environment and provider flags derived from endpoint versions (ADR-0017 §4.4, ADR-0019 §6)."""
    single = [v for v in (frm, to) if v["environment_scope"] == "single"]
    envs = {v["environment_id"] for v in single}
    cross_env = len(single) == 2 and len(envs) == 2
    shared = any(v["environment_scope"] == "shared" for v in (frm, to))
    if cross_env or not single:
        env_id = None
    else:
        env_id = next(iter(envs))
    cross_provider = bool(frm["provider"] and to["provider"] and frm["provider"] != to["provider"])
    return {"environment_id": env_id, "cross_environment": cross_env, "shared_endpoint": shared, "cross_provider": cross_provider}


# --------------------------------------------------------------------------- relationship compatibility


def check_pair(tax: Taxonomy, rel_type: str, frm: dict[str, Any], to: dict[str, Any], attributes: dict[str, Any]) -> list[str]:
    """Return reasons why (rel_type, from version, to version, attributes) is not allowed (D-04). Empty = allowed."""
    rel = tax.rels.get(rel_type)
    if rel is None:
        return [f"unknown relationship type {rel_type}"]
    if rel["status"] != "active":
        return [f"{rel_type} is reserved in taxonomy {tax.version}; writes are rejected"]
    ft, tt = frm["type_key"], to["type_key"]
    if rel_type == "CONTAINS":
        reasons = []
        if not tax.allowed_parent(tt, ft):
            reasons.append(f"{ft} is not an allowed CONTAINS parent of {tt}")
        if tax.types[ft]["kind"] != tax.types[tt]["kind"]:
            reasons.append("containment never crosses logical and physical families")
        elif tax.types[ft]["kind"] == "physical" and frm["provider"] != to["provider"]:
            reasons.append("physical containment stays within one provider")
        return reasons
    reasons = []
    ok_pair = None
    for pair in rel["pairs"]:
        if not (tax.matches(ft, pair["from"]) and (tax.matches(tt, pair["to"]) and tt not in pair.get("to_exclude", []))):
            continue
        cond = pair.get("when_from")
        if cond and any(frm.get(k) != v for k, v in cond.items()):
            continue
        kinds = pair.get("connectivity_kinds")
        if kinds and attributes.get("connectivity_kind") not in kinds:
            continue
        ok_pair = pair
        break
    if ok_pair is None:
        reasons.append(f"{rel_type} is not allowed from {ft} to {tt}" +
                       (f" with connectivity_kind {attributes.get('connectivity_kind')}" if rel_type == "CONNECTS_TO" else ""))
    for a in rel["required_attributes"]:
        if attributes.get(a) in (None, ""):
            reasons.append(f"{rel_type} requires attribute {a}")
    allowed_attrs = set(rel["required_attributes"]) | set(rel["optional_attributes"])
    for a in attributes:
        if a not in allowed_attrs:
            reasons.append(f"{rel_type} has no attribute {a}")
    for a, spec in rel["attribute_enums"].items():
        if a in attributes and attributes[a] not in tax.enum_values(spec):
            reasons.append(f"{rel_type}.{a} = {attributes[a]!r} is not in the vocabulary")
    if rel["logical_only"] and (tax.types[ft]["kind"] != "logical" or tax.types[tt]["kind"] != "logical"):
        reasons.append(f"{rel_type} is between logical types only")
    return reasons


def discriminator_of(tax: Taxonomy, rel_type: str, attributes: dict[str, Any]) -> str:
    d = tax.rels[rel_type]["discriminator"] if rel_type in tax.rels else None
    return str(attributes.get(d, "")) if d else ""


# --------------------------------------------------------------------------- findings


@dataclass(frozen=True)
class Finding:
    rule: str
    cls: str
    message: str

    def __str__(self) -> str:
        return f"[{self.cls}] {self.rule}: {self.message}"


# --------------------------------------------------------------------------- import planner (ADR-0008 §8)

ENTITY_COMPARE = ("type_key", "display_name", "lifecycle", "provider", "native_type", "environment_scope",
                  "environment_id", "container_id", "attributes")


@dataclass
class Plan:
    """Differences between an import batch and the current state. Empty plan = no change set."""

    new_entities: list[dict[str, Any]] = field(default_factory=list)
    changed_entities: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    new_relationships: list[dict[str, Any]] = field(default_factory=list)
    new_containments: list[tuple[str, str]] = field(default_factory=list)   # (parent id, child id) implied by "parent"
    changed_relationships: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)

    @property
    def empty(self) -> bool:
        return not (self.new_entities or self.changed_entities or self.new_relationships or self.changed_relationships)


def plan_batch(tax: Taxonomy, batch: dict[str, Any], st: State) -> Plan:
    """Match by exact identity only (ADR-0003 step 1/3); never by name. Rejected items are reported, never dropped."""
    plan = Plan()
    ev_kinds = {e["ref"]: e["kind"] for e in batch["evidence"]}
    by_ref: dict[str, dict[str, Any]] = {}   # ref -> desired version (with id)

    def resolve(ref: dict[str, Any] | None) -> str | None:
        if ref is None:
            return None
        if "ref" in ref:
            return by_ref[ref["ref"]]["entity_id"] if ref["ref"] in by_ref else None
        if "org_key" in ref:
            return st.identities.get(("org.key", ref["org_key"].strip().lower()))
        ns, orig = ref["identity"]["namespace"], ref["identity"]["original_key"]
        try:
            key, _, _ = normalize_identity(tax, ns, orig)
        except NormalizationError:
            return None
        return st.identities.get((ns, key))

    def reject(item: dict[str, Any], rule: str, reasons: list[str]) -> None:
        plan.rejected.append({"item": item, "rule": rule, "reasons": reasons})

    for item in batch["entities"]:
        t = tax.type_def(item["type_key"])
        if t is None:
            reject(item, "D-01", [f"unknown type {item['type_key']}"])
            continue
        idents, bad = [], []
        for ident in item["identities"]:
            try:
                key, parts, rule = normalize_identity(tax, ident["namespace"], ident["original_key"])
                idents.append({"namespace": ident["namespace"], "original_key": ident["original_key"], "normalized_key": key,
                               "key_parts": parts, "normalization_version": rule})
            except NormalizationError as exc:
                bad.append(str(exc))
        if bad:
            reject(item, "H-08", bad)
            continue
        bound = {st.identities.get((i["namespace"], i["normalized_key"])) for i in idents} - {None}
        if len(bound) > 1:
            reject(item, "D-17", ["identities resolve to different entities: ambiguous, no link (ADR-0003)"])
            continue
        missing = [a for a in t["required_attributes"] if a not in (item.get("attributes") or {})]
        if missing:
            reject(item, "D-01", [f"missing required attributes {missing}"])
            continue
        eid = next(iter(bound)) if bound else item.get("id")
        if eid is None:
            reject(item, "D-18", ["no identity match and no explicit fixture ID; the loader assigns IDs only outside fixtures"])
            continue
        desired = {
            "entity_id": eid, "type_key": item["type_key"], "category": t["category"], "display_name": item["display_name"],
            "lifecycle": item.get("lifecycle", "active"), "provider": item.get("provider"), "native_type": item.get("native_type"),
            "environment_scope": item.get("environment_scope"), "environment_id": resolve(item.get("environment")),
            "container_id": resolve(item.get("parent")), "attributes": item.get("attributes") or {},
            "identities": idents, "evidence_kinds": sorted({ev_kinds[r] for r in item["evidence_refs"]}),
            "evidence_refs": item["evidence_refs"], "ref": item["ref"],
        }
        by_ref[item["ref"]] = desired
        current = st.entities.get(eid)
        if current is None:
            plan.new_entities.append(desired)
            if desired["container_id"]:
                plan.new_containments.append((desired["container_id"], eid))
        else:
            changes = {k: desired[k] for k in ENTITY_COMPARE if current[k] != desired[k]}
            new_ids = [i for i in idents if (i["namespace"], i["normalized_key"]) not in st.identities]
            if changes or new_ids:
                plan.changed_entities.append((eid, {"fields": changes, "identities": new_ids, "evidence_refs": item["evidence_refs"]}))

    def version_of(eid: str | None) -> dict[str, Any] | None:
        if eid is None:
            return None
        for d in by_ref.values():
            if d["entity_id"] == eid:
                return d
        return st.entities.get(eid)

    existing = {(r["rel_type"], r["from_id"], r["to_id"], r["discriminator"]): (rid, r) for rid, r in st.relationships.items()}
    for item in batch["relationships"]:
        fid, tid = resolve(item["from"]), resolve(item["to"])
        fv, tv = version_of(fid), version_of(tid)
        attrs = item.get("attributes") or {}
        if fv is None or tv is None:
            reject(item, "H-04", ["an endpoint does not resolve (rejected entity, or no identity match)"])
            continue
        reasons = check_pair(tax, item["rel_type"], fv, tv, attrs)
        kinds = {ev_kinds[r] for r in item["evidence_refs"]}
        rel = tax.rels.get(item["rel_type"])
        if rel and not kinds <= set(rel["allowed_evidence_kinds"]):
            reasons.append(f"evidence kinds {sorted(kinds - set(rel['allowed_evidence_kinds']))} not allowed for {item['rel_type']}")
        if reasons:
            reject(item, "D-04", reasons)
            continue
        disc = discriminator_of(tax, item["rel_type"], attrs)
        key = (item["rel_type"], fid, tid, disc)
        if key in existing:
            rid, r = existing[key]
            if r["version"]["attributes"] != attrs:
                plan.changed_relationships.append((rid, {"attributes": attrs, "evidence_refs": item["evidence_refs"]}))
            continue
        if item.get("id") is None:
            reject(item, "D-18", ["new relationship without an explicit fixture ID"])
            continue
        plan.new_relationships.append({"id": item["id"], "rel_type": item["rel_type"], "from_id": fid, "to_id": tid,
                                       "discriminator": disc, "attributes": attrs, "evidence_refs": item["evidence_refs"],
                                       "evidence_kinds": sorted(kinds)})
    return plan
