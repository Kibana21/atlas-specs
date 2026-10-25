"""Deterministic generator of the canonical golden fixture (ATLAS-002 CP2). CI tooling, never deployed.

Usage: uv run --project tools python tools/generate_golden.py [OUTPUT_DIR]
Default output: acceptance/test-data/canonical-golden-v1. Same inputs give byte-identical output.

All names, keys, accounts and GUIDs are synthetic. Every relationship is allowed by the taxonomy
version its row names and carries evidence; nothing is added to reach a count.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from canonical_model import (
    ROOT, TABLES, Taxonomy, as_of, canonical_json, check_pair, default_trust, discriminator_of, dump_records, graph_hash,
    normalize_identity, plan_batch, relationship_flags, sha256_of, uuid7, Dataset, TRUST_FUNCTION_VERSION, TRUST_POLICY_FILE,
)

FIXTURE = "canonical-golden-v1"
FIXTURE_VERSION = "1.1.0"
TAXONOMY_VERSION = "1.1.0"   # must equal the artifact (checked in build)
DEFAULT_OUT = ROOT / "acceptance" / "test-data" / FIXTURE
OVERLAY_NAME = "taxonomy-overlay.1.2.0-test.1.json"
OVERLAY = {
    "overlay_format": "atlas.taxonomy-overlay.v1",
    "taxonomy_version": "1.2.0-test.1",
    "extends": TAXONOMY_VERSION,
    "status": "synthetic_test_only",
    "note": "SYNTHETIC, TEST ONLY. Not an approved taxonomy version. Exists so the fixture can show taxonomy-version-aware "
            "history: a native type unmapped in 1.1.0 becomes mapped, and the entity is re-typed with its ID kept (ADR-0017 §2.4).",
    "add_native_type_mappings": {"gcp": [{"native_type": "bigquery.googleapis.com/Dataset", "category": "data_store"}]},
}

# Fixture trust policy (ADR-0018: freshness values "are fixed for fixtures"). Synthetic: real per-source values are DEC-072
# (Open) and per-field precedence is DEC-034 (Proposed), so no precedence rule is defined.
TRUST_POLICY = {
    "policy_format": "atlas.trust-policy.v1",
    "function": TRUST_FUNCTION_VERSION,
    "status": "synthetic_test_only",
    "note": "SYNTHETIC, TEST ONLY. Not an approved freshness or precedence policy. Sources without an entry are unassessed: "
            "they never make a fact stale.",
    "freshness": [{"method": "import:document:v1", "stale_after_days": 365}],
    "precedence": [],
}

STEWARD = {"kind": "human", "namespace": "oidc", "key": "https://login.example.invalid/synthetic|steward-0001", "label": "EA Steward (synthetic)"}
STEWARD_REF = {"namespace": "oidc", "key": STEWARD["key"]}
LOADER = {"kind": "service", "namespace": "atlas.service", "key": "fixture-loader", "label": "Fixture loader"}
IMPORTER = {"kind": "service", "namespace": "atlas.service", "key": "import-worker", "label": "Import worker"}
MIGRATOR = {"kind": "system", "namespace": "atlas.system", "key": "taxonomy-migration", "label": "Taxonomy migration"}

SUB_NP = "00000000-0000-4000-8000-00000000a001"
SUB_PR = "00000000-0000-4000-8000-00000000a002"
SUB_B = "00000000-0000-4000-8000-00000000b001"
TENANT = "00000000-0000-4000-8000-00000000c001"


def arm(sub: str, rg: str | None = None, *path: str) -> str:
    s = f"/subscriptions/{sub}"
    if rg:
        s += f"/resourceGroups/{rg}"
    if path:
        s += "/providers/" + "/".join(path)
    return s


# --------------------------------------------------------------------------- world model


class World:
    def __init__(self, taxonomies: dict[str, Taxonomy], org_key: str, display: str, seq_base: int) -> None:
        self.tax = taxonomies
        self.org_key = org_key
        self.seq = seq_base
        self.org_id = self._id("org", org_key)
        self.org = {"id": self.org_id, "key": org_key, "display_name": display}
        self.t: dict[str, list[dict[str, Any]]] = {k: [] for k in TABLES if k != "organizations"}
        self.ids: dict[str, str] = {}          # entity key -> id
        self.rel_ids: dict[str, str] = {}      # relationship key -> id
        self.ev_ids: dict[str, str] = {}
        self.ev_spec: dict[str, dict[str, Any]] = {}
        self.rev = 0
        self.tax_version = TAXONOMY_VERSION

    # ---- ids and helpers
    def _id(self, kind: str, key: str) -> str:
        self.seq += 1
        return uuid7(self.seq, f"{self.org_key}|{kind}|{key}")

    def T(self) -> Taxonomy:
        return self.tax[self.tax_version]

    def begin(self, kind: str, channel: str, actor: dict[str, Any], source_ref: str, reason: str, change_reference: str | None = None,
              reverts: int | None = None, input_hash: str | None = None, tax_version: str = TAXONOMY_VERSION) -> int:
        self.rev += 1
        self.tax_version = tax_version
        self.t["change_sets"].append({
            "org_id": self.org_id, "revision": self.rev, "kind": kind, "channel": channel, "actor": actor, "source_ref": source_ref,
            "input_hash": input_hash, "reverts_revision": reverts, "reason": reason, "change_reference": change_reference,
            "created_at": f"2026-10-{self.rev:02d}T09:00:00Z", "db_role": "atlas_test_ingest"})
        return self.rev

    def evidence(self, key: str, kind: str, source_ref: str, method: str, artifact: str | None, observed: str) -> None:
        self.ev_spec[key] = {"kind": kind, "source_ref": source_ref, "method": method, "artifact_ref": artifact, "observed_at": observed}

    def ev(self, key: str) -> str:
        if key not in self.ev_ids:
            s = self.ev_spec[key]
            eid = self._id("evidence", key)
            self.ev_ids[key] = eid
            self.t["evidence"].append({
                "org_id": self.org_id, "id": eid, "kind": s["kind"], "source_ref": s["source_ref"], "artifact_ref": s["artifact_ref"],
                "artifact_hash": sha256_of(f"{self.org_key}|{key}".encode()) if s["artifact_ref"] else None, "method": s["method"],
                "confidence": 1.0, "observed_at": s["observed_at"], "valid_from": None, "valid_to": None, "change_revision": self.rev})
        return self.ev_ids[key]

    def ev_kind(self, key: str) -> str:
        return self.ev_spec[key]["kind"]

    def _assert(self, fact_kind: str, fact_id: str, ev_key: str, field_path: str | None = None, value: Any = None) -> None:
        self.t["fact_assertions"].append({
            "org_id": self.org_id, "id": self._id("assertion", f"{fact_id}|{ev_key}|{field_path}|{self.rev}"), "fact_kind": fact_kind,
            "fact_id": fact_id, "field_path": field_path, "asserted_value": value, "evidence_id": self.ev(ev_key),
            "evidence_kind": self.ev_kind(ev_key), "revision_from": self.rev, "revision_to": None})

    def current(self, table: str, fid: str, key: str) -> dict[str, Any]:
        for v in reversed(self.t[table]):
            if v[key] == fid and v["revision_to"] is None:
                return v
        raise KeyError(fid)

    def _kinds(self, fid: str) -> set[str]:
        return {a["evidence_kind"] for a in self.t["fact_assertions"] if a["fact_id"] == fid and a["revision_to"] is None and a["field_path"] is None}

    @staticmethod
    def _verification(v: dict[str, Any] | None) -> dict[str, Any]:
        if not v:
            return {"verification_state": "unverified", "verified_by": None, "verified_at": None, "expires_at": None}
        return {"verification_state": "verified", "verified_by": STEWARD_REF, "verified_at": v["at"], "expires_at": v.get("expires")}

    # ---- entities
    def entity(self, key: str, type_key: str, name: str, ev: list[str], *, env: str | None = None, shared: list[str] | None = None,
               scope: str | None = None, parent: str | None = None, provider: str | None = None, native: str | None = None,
               attrs: dict[str, Any] | None = None, ids: list[tuple[str, str]] = (), lifecycle: str = "active",
               trust: str | None = None, verified: dict[str, Any] | None = None, eid: str | None = None) -> str:
        t = self.T().types[type_key]
        eid = eid or self._id("entity", key)
        if type_key == "k8s.namespace":
            native = native or "Namespace"          # Kubernetes objects: native_type is the Kubernetes kind
        elif type_key == "k8s.workload":
            native = native or (attrs or {})["workload_kind"]
        self.ids[key] = eid
        if t["kind"] == "physical":
            if "native_type" in t:
                native = t["native_type"]
            if provider is None and parent:
                provider = self.current("entity_versions", self.ids[parent], "entity_id")["provider"]
        if t["environment_scope"] == "none":
            env_scope = None
        elif shared:
            env_scope = "shared"
        elif env:
            env_scope = "single"
        else:
            env_scope = scope or "unknown"
        self.t["entities"].append({"org_id": self.org_id, "id": eid, "created_revision": self.rev})
        for e in ev:
            self._assert("entity", eid, e)
        version = {
            "org_id": self.org_id, "entity_id": eid, "revision_from": self.rev, "revision_to": None, "type_key": type_key,
            "category": t["category"], "provider": provider, "native_type": native, "record_state": "present", "merged_into": None,
            "display_name": name, "lifecycle": lifecycle, "environment_scope": env_scope,
            "environment_id": self.ids[env] if env_scope == "single" else None,
            "container_id": self.ids[parent] if parent else None, "attributes": attrs or {},
            "trust_state": trust or default_trust(self._kinds(eid)), **self._verification(verified), "taxonomy_version": self.tax_version}
        self.t["entity_versions"].append(version)
        for ns, orig in ids:
            self.identity(key, ns, orig, "provider_id" if ns not in ("org.key",) and not ns.startswith("source.") else "org_key")
        if parent:
            self.rel(f"contains:{parent}>{key}", "CONTAINS", parent, key, ev=ev, trust="stale" if trust == "stale" else None)
        for s in shared or []:
            self.rel(f"member:{key}>{s}", "MEMBER_OF", key, s, ev=ev)
        return eid

    def identity(self, key: str, ns: str, orig: str, method: str) -> None:
        nkey, parts, rule = normalize_identity(self.T(), ns, orig)
        self.t["external_identities"].append({
            "org_id": self.org_id, "id": self._id("identity", f"{ns}|{nkey}"), "entity_id": self.ids[key], "namespace": ns,
            "original_key": orig, "normalized_key": nkey, "normalization_version": rule, "key_parts": parts, "match_method": method,
            "revision_from": self.rev, "revision_to": None})

    def _new_version(self, table: str, idkey: str, fid: str, **changes: Any) -> dict[str, Any]:
        cur = self.current(table, fid, idkey)
        if cur["revision_from"] == self.rev:   # several edits of one fact in one change set: one version
            cur.update(changes, taxonomy_version=self.tax_version)
            return cur
        cur["revision_to"] = self.rev
        new = {**cur, **changes, "revision_from": self.rev, "revision_to": None, "taxonomy_version": self.tax_version}
        self.t[table].append(new)
        return new

    def update_entity(self, key: str, ev: list[str], **changes: Any) -> None:
        eid = self.ids[key]
        for field_name, value in changes.items():
            for e in ev:
                self._assert("entity", eid, e, field_name if field_name != "attributes" else "attributes", value)
        self._new_version("entity_versions", "entity_id", eid, **changes)

    # ---- relationships
    def rel(self, key: str, rel_type: str, frm: str, to: str, *, ev: list[str], attrs: dict[str, Any] | None = None,
            trust: str | None = None, verified: dict[str, Any] | None = None, rid: str | None = None) -> str:
        tax = self.T()
        fv = self.current("entity_versions", self.ids[frm], "entity_id")
        tv = self.current("entity_versions", self.ids[to], "entity_id")
        attrs = attrs or {}
        reasons = check_pair(tax, rel_type, fv, tv, attrs)
        kinds = {self.ev_kind(e) for e in ev}
        bad = kinds - set(tax.rels[rel_type]["allowed_evidence_kinds"])
        if reasons or bad:
            raise ValueError(f"generator bug: {key}: {reasons} {sorted(bad)}")
        rid = rid or self._id("relationship", key)
        self.rel_ids[key] = rid
        self.t["relationships"].append({"org_id": self.org_id, "id": rid, "rel_type": rel_type, "from_id": fv["entity_id"],
                                        "to_id": tv["entity_id"], "discriminator": discriminator_of(tax, rel_type, attrs),
                                        "created_revision": self.rev})
        for e in ev:
            self._assert("relationship", rid, e)
        self.t["relationship_versions"].append({
            "org_id": self.org_id, "relationship_id": rid, "revision_from": self.rev, "revision_to": None, "record_state": "present",
            "lifecycle": "active", **relationship_flags(fv, tv), "attributes": attrs,
            "trust_state": trust or default_trust(self._kinds(rid)), **self._verification(verified), "taxonomy_version": self.tax_version})
        return rid

    def retire_rel(self, key: str, ev: list[str]) -> None:
        rid = self.rel_ids[key]
        for a in self.t["fact_assertions"]:
            if a["fact_id"] == rid and a["revision_to"] is None:
                a["revision_to"] = self.rev
        for e in ev:
            self._assert("relationship", rid, e, "record_state", "removed")
        self._new_version("relationship_versions", "relationship_id", rid, record_state="removed",
                          trust_state="curated", verification_state="unverified", verified_by=None, verified_at=None, expires_at=None)
        if key.startswith("contains:"):
            child = self.ids[key.split(">", 1)[1]]
            self._new_version("entity_versions", "entity_id", child, container_id=None)

    def revert(self, target: int) -> None:
        """New versions equal to the state at target-1 for every fact changed at target (ADR-0008 §7)."""
        for table, idkey in (("entity_versions", "entity_id"), ("relationship_versions", "relationship_id")):
            touched = sorted({v[idkey] for v in self.t[table] if v["revision_from"] == target})
            for fid in touched:
                later = [v for v in self.t[table] if v[idkey] == fid and target < v["revision_from"] < self.rev]
                if later:
                    raise ValueError(f"revert conflict on {fid}")
                prior = [v for v in self.t[table] if v[idkey] == fid and v["revision_to"] == target]
                restore = {k: v for k, v in prior[0].items() if k not in ("revision_from", "revision_to", "taxonomy_version")} if prior else {"record_state": "removed"}
                self._new_version(table, idkey, fid, **restore)
        for a in [a for a in self.t["fact_assertions"] if a["revision_from"] == target and a["revision_to"] is None]:
            a["revision_to"] = self.rev
        for a in [a for a in self.t["fact_assertions"] if a["revision_to"] == target]:
            self.t["fact_assertions"].append({**a, "id": self._id("assertion", f"{a['id']}|restore|{self.rev}"), "revision_from": self.rev, "revision_to": None})

    def close_identity(self, key: str, ns: str) -> None:
        for i in self.t["external_identities"]:
            if i["entity_id"] == self.ids[key] and i["namespace"] == ns and i["revision_to"] is None:
                i["revision_to"] = self.rev

    def add_existence_evidence(self, key: str, ev_key: str) -> None:
        eid = self.ids[key]
        self._assert("entity", eid, ev_key)
        self._new_version("entity_versions", "entity_id", eid, trust_state=default_trust(self._kinds(eid)))

    def retype(self, key: str, new_type: str, ev: list[str], **changes: Any) -> None:
        t = self.T().types[new_type]
        extra = {"type_key": new_type, "category": t["category"], **changes}
        if "native_type" in t:
            extra["native_type"] = t["native_type"]
        for e in ev:
            self._assert("entity", self.ids[key], e, "type_key", new_type)
        self._new_version("entity_versions", "entity_id", self.ids[key], **extra)

    def snapshot(self, label: str, ds_builder) -> None:
        self.t["graph_snapshots"].append({"org_id": self.org_id, "id": self._id("snapshot", label), "revision": self.rev, "label": label,
                                          "status": "published", "graph_hash": None})


# --------------------------------------------------------------------------- org A content


def build_org_a(world: World) -> dict[str, Any]:
    w = world
    E = w.evidence
    E("arg-nonprod", "provider_configuration", "azure-resource-graph (synthetic export)", "export:arg:v1", "synthetic://azure/arg/nonprod-2026-09-30.json", "2026-09-30T06:00:00Z")
    E("arg-prod", "provider_configuration", "azure-resource-graph (synthetic export)", "export:arg:v1", "synthetic://azure/arg/prod-2026-09-30.json", "2026-09-30T06:00:00Z")
    E("aks-config", "provider_configuration", "kubernetes-api (synthetic export)", "export:k8s:v1", "synthetic://azure/aks/manifests-2026-09-30.json", "2026-09-30T06:10:00Z")
    E("apim-config", "provider_configuration", "apim-management-api (synthetic export)", "export:apim:v1", "synthetic://azure/apim/config-2026-09-30.json", "2026-09-30T06:20:00Z")
    E("app-config", "provider_configuration", "azure-app-configuration (synthetic export)", "export:appconfig:v1", "synthetic://azure/appconfig/settings-2026-09-30.json", "2026-09-30T06:30:00Z")
    E("cmdb", "provider_configuration", "on-premises CMDB (synthetic export)", "export:cmdb:v1", "synthetic://onprem/cmdb/export-2026-09-29.csv", "2026-09-29T22:00:00Z")
    E("doc-claims", "documentation", "architecture document: claims platform (synthetic)", "import:document:v1", "synthetic://docs/claims-platform-architecture.md", "2026-08-15T12:00:00Z")
    E("doc-policy", "documentation", "architecture document: policy and billing (synthetic)", "import:document:v1", "synthetic://docs/policy-billing-architecture.md", "2026-08-20T12:00:00Z")
    E("doc-multicloud", "documentation", "architecture document: multi-cloud integrations (synthetic)", "import:document:v1", "synthetic://docs/multicloud-integrations.md", "2026-09-01T12:00:00Z")
    E("doc-legacy", "documentation", "architecture document: legacy messaging (synthetic, 2024)", "import:document:v1", "synthetic://docs/legacy-messaging-2024.md", "2024-03-01T12:00:00Z")
    E("spec-policy-sync", "documentation", "integration specification: policy sync (synthetic)", "import:document:v1", "synthetic://docs/policy-sync-integration-spec.md", "2026-09-05T12:00:00Z")
    E("openapi", "contract", "OpenAPI contracts (synthetic)", "import:openapi:v1", "synthetic://contracts/openapi-bundle-2026-09.yaml", "2026-09-10T12:00:00Z")
    E("asyncapi", "contract", "AsyncAPI contracts (synthetic)", "import:asyncapi:v1", "synthetic://contracts/asyncapi-bundle-2026-09.yaml", "2026-09-10T12:00:00Z")
    E("iac-gcp", "contract", "IaC manifests: GCP (synthetic)", "import:iac:v1", "synthetic://iac/gcp/main.tf", "2026-09-12T12:00:00Z")
    E("ownership", "documentation", "team ownership register (synthetic)", "import:register:v1", "synthetic://registers/ownership-2026-09.csv", "2026-09-15T12:00:00Z")
    E("capmap", "human_assertion", "EA steward: capability map review (synthetic)", "steward:review", None, "2026-09-18T12:00:00Z")
    E("netarch", "human_assertion", "network architect assertion, steward-accepted (synthetic)", "steward:review", None, "2026-09-19T12:00:00Z")
    E("membership", "human_assertion", "domain architect: system membership (synthetic)", "steward:review", None, "2026-09-18T13:00:00Z")
    E("doc-aliyun", "documentation", "architecture document: pricing batch on Alibaba Cloud (synthetic)", "import:document:v1", "synthetic://docs/pricing-batch-aliyun.md", "2026-09-02T12:00:00Z")
    E("steward-rename", "human_assertion", "EA steward: rename (synthetic)", "steward:edit", None, "2026-10-03T08:30:00Z")
    E("steward-owner", "human_assertion", "EA steward: ownership change (synthetic)", "steward:edit", None, "2026-10-03T08:40:00Z")
    E("steward-retire", "human_assertion", "EA steward: relationship retirement (synthetic)", "steward:edit", None, "2026-10-04T08:30:00Z")
    E("steward-link", "human_assertion", "EA steward: identity link and re-type (synthetic)", "steward:edit", None, "2026-10-06T08:30:00Z")
    E("arg-billing", "provider_configuration", "azure-resource-graph (synthetic export)", "export:arg:v1", "synthetic://azure/arg/prod-2026-10-06.json", "2026-10-06T06:00:00Z")
    E("iac-analytics", "contract", "IaC manifests: analytics (synthetic)", "import:iac:v1", "synthetic://iac/gcp/analytics.tf", "2026-10-08T12:00:00Z")
    E("aws-config", "provider_configuration", "aws-config (synthetic export)", "export:aws-config:v1", "synthetic://aws/config/inventory-2026-10-01.json", "2026-10-01T06:00:00Z")

    V = {"at": "2026-09-20T10:00:00Z", "expires": "2027-03-20T10:00:00Z"}
    w.begin("fixture_load", "fixture_cli", LOADER, "fixture:canonical-golden-v1", "Golden fixture baseline (synthetic)", input_hash=None)
    ent, rel = w.entity, w.rel

    # environments: organization-defined names, classified by environment_kind
    for k, name, kind in [("env.dev", "DEV", "dev"), ("env.sit", "SIT", "sit"), ("env.uat", "UAT", "uat"), ("env.uat2", "UAT-2", "uat"),
                          ("env.prod", "PROD", "prod"), ("env.dr", "DR", "dr"), ("env.perf", "PERF-LAB", "other")]:
        ent(k, "core.environment", name, ["ownership"], attrs={"environment_kind": kind}, ids=[("org.key", f"ENV-{name}")])

    # business layer
    caps = [("cap.ops", "Insurance Operations", None), ("cap.claims", "Claims Management", "cap.ops"), ("cap.intake", "Claims Intake", "cap.claims"),
            ("cap.settle", "Claims Settlement", "cap.claims"), ("cap.policy", "Policy Administration", "cap.ops"), ("cap.quote", "Quoting", "cap.policy"),
            ("cap.uw", "Underwriting", "cap.policy"), ("cap.billing", "Billing and Payments", "cap.ops"), ("cap.invoice", "Invoicing", "cap.billing"),
            ("cap.customer", "Customer Self-Service", "cap.ops")]
    for k, n, p in caps:
        ent(k, "core.capability", n, ["capmap"], parent=p)
    for k, n, p in [("dom.claims", "Claims", None), ("dom.claims-analytics", "Claims Analytics", "dom.claims"), ("dom.policy", "Policy", None),
                    ("dom.billing", "Billing", None), ("dom.customer", "Customer", None), ("dom.platform", "Shared Platforms", None)]:
        ent(k, "core.business_domain", n, ["capmap"], parent=p)
    teams = ["claims", "policy", "billing", "customer", "platform", "data", "integration", "security"]
    for tm in teams:
        ent(f"team.{tm}", "core.team", f"{tm.capitalize()} Team", ["ownership"], ids=[("org.key", f"TEAM-{tm.upper()}")])
    systems = {"sys.claims": ("Claims Platform", "dom.claims"), "sys.policy": ("Policy Platform", "dom.policy"),
               "sys.billing": ("Billing Platform", "dom.billing"), "sys.customer": ("Customer Portal Suite", "dom.customer"),
               "sys.data": ("Data Platform", "dom.platform")}
    for k, (n, d) in systems.items():
        ent(k, "core.system", n, ["membership"])
        rel(f"member:{k}>{d}", "MEMBER_OF", k, d, ev=["membership"])

    apps = [  # key, name, org key, systems, domains, owner (None = deliberately missing)
        ("app.claims-portal", "Claims Portal", "APP-0101", ["sys.claims", "sys.customer"], ["dom.claims"], "claims"),
        ("app.claims-engine", "Claims Engine", "APP-0102", ["sys.claims"], ["dom.claims"], "claims"),
        ("app.claims-analytics", "Claims Analytics", "APP-0103", ["sys.claims", "sys.data"], ["dom.claims-analytics"], None),
        ("app.policy-admin", "Policy Admin", "APP-0201", ["sys.policy"], ["dom.policy"], "policy"),
        ("app.quoting", "Quoting Engine", "APP-0202", ["sys.policy"], ["dom.policy"], "policy"),
        ("app.underwriting", "Underwriting Rules", "APP-0203", ["sys.policy"], ["dom.policy"], "policy"),
        ("app.billing-hub", "Billing Hub", "APP-0301", ["sys.billing"], ["dom.billing"], "billing"),
        ("app.payments", "Payments Gateway", "APP-0302", ["sys.billing"], ["dom.billing"], "billing"),
        ("app.customer-portal", "Customer Portal", "APP-0401", ["sys.customer"], ["dom.customer"], "customer"),
        ("app.notifications", "Notification Hub", "APP-0402", ["sys.customer"], ["dom.customer", "dom.platform"], None),
        ("app.documents", "Document Store", "APP-0501", ["sys.data"], ["dom.platform"], "data"),
        ("app.pricing", "Pricing Batch", "APP-0203B", ["sys.policy"], ["dom.policy"], "policy"),
    ]
    for k, n, okey, syss, doms, owner in apps:
        ent(k, "core.application", n, ["doc-claims" if "claims" in k else "doc-policy"], attrs={"org_key": okey}, ids=[("org.key", okey)])
        for s in syss:
            rel(f"member:{k}>{s}", "MEMBER_OF", k, s, ev=["membership"])
        for d in doms:
            rel(f"member:{k}>{d}", "MEMBER_OF", k, d, ev=["membership"])
        if owner:
            rel(f"owns:{owner}>{k}", "OWNS", f"team.{owner}", k, ev=["ownership"], attrs={"ownership_role": "accountable"})
    rel("owns:platform>app.notifications", "OWNS", "team.platform", "app.notifications", ev=["ownership"], attrs={"ownership_role": "technical"})
    for k, (n, d) in systems.items():
        owner = {"sys.claims": "claims", "sys.policy": "policy", "sys.billing": "billing", "sys.customer": "customer", "sys.data": None}[k]
        if owner:
            rel(f"owns:{owner}>{k}", "OWNS", f"team.{owner}", k, ev=["ownership"], attrs={"ownership_role": "accountable"})

    services = [  # key, name, application, owner team or None
        ("svc.claims-portal-bff", "Claims Portal BFF", "app.claims-portal", "claims"),
        ("svc.claims-portal-ui", "Claims Portal UI", "app.claims-portal", "claims"),
        ("svc.claims-api", "Claims API Service", "app.claims-engine", "claims"),
        ("svc.claims-intake", "Claims Intake Worker", "app.claims-engine", "claims"),
        ("svc.claims-settlement", "Settlement Service", "app.claims-engine", None),
        ("svc.claims-reporting", "Claims Reporting", "app.claims-analytics", "data"),
        ("svc.policy-api", "Policy API Service", "app.policy-admin", "policy"),
        ("svc.policy-sync", "Policy Sync", "app.policy-admin", "integration"),
        ("svc.quote", "Quote Service", "app.quoting", "policy"),
        ("svc.rating-client", "Rating Client", "app.quoting", None),
        ("svc.uw-rules", "Underwriting Rules Service", "app.underwriting", "policy"),
        ("svc.billing-api", "Billing API Service", "app.billing-hub", "billing"),
        ("svc.invoice-batch", "Invoice Batch", "app.billing-hub", "billing"),
        ("svc.payments-api", "Payments API Service", "app.payments", "billing"),
        ("svc.customer-api", "Customer API Service", "app.customer-portal", "customer"),
        ("svc.customer-web", "Customer Web", "app.customer-portal", "customer"),
        ("svc.notify", "Notification Service", "app.notifications", None),
        ("svc.notify-fn", "Notification Dispatcher", "app.notifications", "platform"),
        ("svc.docs-index", "Document Indexer", "app.documents", "data"),
        ("svc.docs-api", "Document API Service", "app.documents", "data"),
        ("svc.pricing-batch", "Pricing Batch Job", "app.pricing", "policy"),
        ("svc.billing-mainframe", "Billing Mainframe Batch", "app.billing-hub", "billing"),
    ]
    for k, n, app, owner in services:
        ent(k, "core.service", n, ["doc-claims" if "claims" in app else "doc-policy"], parent=app)
        if owner:
            rel(f"owns:{owner}>{k}", "OWNS", f"team.{owner}", k, ev=["ownership"], attrs={"ownership_role": "technical"})
    for k, n, s in [("cmp.claims-validation", "Claim Validation", "svc.claims-api"), ("cmp.claims-fraud", "Fraud Scoring Hook", "svc.claims-api"),
                    ("cmp.quote-calc", "Quote Calculator", "svc.quote"), ("cmp.quote-cache", "Quote Cache", "svc.quote"),
                    ("cmp.invoice-render", "Invoice Renderer", "svc.invoice-batch"), ("cmp.notify-templates", "Notification Templates", "svc.notify")]:
        ent(k, "core.component", n, ["doc-claims" if "claims" in s else "doc-policy"], parent=s)

    apis = [("api.claims", "Claims API", "v1", "svc.claims-api", "dom.claims"), ("api.quotes", "Quotes API", "v2", "svc.quote", "dom.policy"),
            ("api.policy", "Policy API", "v1", "svc.policy-api", "dom.policy"), ("api.billing", "Billing API", "v1", "svc.billing-api", "dom.billing"),
            ("api.payments", "Payments API", "v1", "svc.payments-api", "dom.billing"), ("api.customer", "Customer API", "v1", "svc.customer-api", "dom.customer"),
            ("api.notify", "Notification API", "v1", "svc.notify", "dom.customer"), ("api.rating", "Rating API", "v3", None, "dom.policy")]
    for k, n, ver, svc, dom in apis:
        ent(k, "core.api", n, ["openapi"], attrs={"api_version": ver}, ids=[("org.key", "API-" + k.split(".", 1)[1].upper())])
        if svc:
            rel(f"exposes:{svc}>{k}", "EXPOSES_API", svc, k, ev=["openapi"])
        rel(f"member:{k}>{dom}", "MEMBER_OF", k, dom, ev=["membership"])
    for api, ops in {"api.claims": [("GET", "/claims/{id}"), ("POST", "/claims")], "api.quotes": [("GET", "/quotes/{id}"), ("POST", "/quotes")],
                     "api.policy": [("GET", "/policies/{id}"), ("PUT", "/policies/{id}")], "api.billing": [("GET", "/invoices/{id}"), ("POST", "/invoices")],
                     "api.payments": [("POST", "/payments")], "api.customer": [("GET", "/customers/{id}"), ("PATCH", "/customers/{id}")],
                     "api.notify": [("POST", "/notifications")]}.items():
        for m, p in ops:
            # the OpenAPI document evidences the API's structure (taxonomy 1.1.0, owner decision U-1): documented, never observed
            ent(f"op.{api}.{m}.{p}", "core.api_operation", f"{m} {p}", ["openapi"], parent=api, attrs={"http_method": m, "path_template": p})

    channels = [("ch.claim-submitted", "ClaimSubmitted", "topic", "dom.claims"), ("ch.quote-issued", "QuoteIssued", "topic", "dom.policy"),
                ("ch.policy-bound", "PolicyBound", "topic", "dom.policy"), ("ch.payment-received", "PaymentReceived", "queue", "dom.billing"),
                ("ch.notify-req", "NotificationRequested", "queue", "dom.customer"), ("ch.doc-indexed", "DocumentIndexed", "topic", "dom.platform")]
    for k, n, ck, dom in channels:
        ent(k, "core.event_channel", n, ["asyncapi"], attrs={"channel_kind": ck})
        rel(f"member:{k}>{dom}", "MEMBER_OF", k, dom, ev=["membership"])
    datasets = [("ds.claims", "Claim Records", "dom.claims", "claims"), ("ds.quotes", "Quote Records", "dom.policy", "policy"),
                ("ds.policies", "Policy Records", "dom.policy", "policy"), ("ds.ledger", "Billing Ledger", "dom.billing", "billing"),
                ("ds.customers", "Customer Profiles", "dom.customer", None), ("ds.documents", "Documents", "dom.platform", "data"),
                ("ds.analytics", "Analytics Events", "dom.claims-analytics", "data"), ("ds.rating", "Rating Tables", "dom.policy", None)]
    for k, n, dom, owner in datasets:
        ent(k, "core.dataset", n, ["doc-claims" if "claims" in k else "doc-policy"])
        rel(f"member:{k}>{dom}", "MEMBER_OF", k, dom, ev=["membership"])
        if owner:
            rel(f"owns:{owner}>{k}", "OWNS", f"team.{owner}", k, ev=["ownership"], attrs={"ownership_role": "data_steward"})

    sup = [("sys.claims", "cap.claims", "direct"), ("app.claims-portal", "cap.intake", "direct"), ("app.claims-engine", "cap.intake", "direct"),
           ("app.claims-engine", "cap.settle", "direct"), ("app.claims-analytics", "cap.settle", "enabling"), ("sys.policy", "cap.policy", "direct"),
           ("app.quoting", "cap.quote", "direct"), ("app.underwriting", "cap.uw", "direct"), ("app.pricing", "cap.quote", "enabling"),
           ("sys.billing", "cap.billing", "direct"), ("app.billing-hub", "cap.invoice", "direct"), ("app.payments", "cap.billing", "direct"),
           ("sys.customer", "cap.customer", "direct"), ("app.customer-portal", "cap.customer", "direct"), ("app.notifications", "cap.customer", "enabling"),
           ("app.documents", "cap.claims", "enabling"), ("svc.claims-settlement", "cap.settle", "direct"), ("svc.claims-api", "cap.intake", "direct"),
           ("svc.quote", "cap.quote", "direct"), ("svc.uw-rules", "cap.uw", "direct"), ("svc.invoice-batch", "cap.invoice", "direct"),
           ("svc.payments-api", "cap.billing", "direct"), ("svc.customer-web", "cap.customer", "direct")]
    for f, c, kind in sup:
        rel(f"supports:{f}>{c}:{kind}", "SUPPORTS_CAPABILITY", f, c, ev=["capmap"], attrs={"support_kind": kind})

    # logical integrations (documented or contracted)
    cons = [("svc.claims-portal-bff", "api.claims"), ("svc.claims-portal-bff", "api.customer"), ("svc.claims-portal-bff", "api.quotes"),
            ("svc.claims-portal-ui", "api.claims"), ("svc.claims-intake", "api.policy"), ("svc.claims-settlement", "api.payments"),
            ("svc.claims-settlement", "api.policy"), ("svc.claims-reporting", "api.claims"), ("svc.quote", "api.rating"), ("svc.rating-client", "api.rating"),
            ("svc.uw-rules", "api.policy"), ("svc.policy-api", "api.customer"), ("svc.billing-api", "api.policy"), ("svc.invoice-batch", "api.billing"),
            ("svc.payments-api", "api.billing"), ("svc.customer-web", "api.customer"), ("svc.customer-web", "api.notify"), ("svc.customer-api", "api.notify"),
            ("svc.docs-api", "api.customer"), ("svc.notify-fn", "api.notify"), ("svc.pricing-batch", "api.quotes"),
            ("svc.claims-intake", "api.customer"), ("svc.claims-api", "api.customer"), ("svc.claims-settlement", "api.billing"), ("svc.quote", "api.customer"),
            ("svc.uw-rules", "api.quotes"), ("svc.billing-api", "api.customer"), ("svc.payments-api", "api.customer"), ("svc.customer-api", "api.policy"),
            ("svc.customer-api", "api.claims"), ("svc.customer-web", "api.claims"), ("svc.customer-web", "api.quotes"), ("svc.docs-index", "api.claims"),
            ("svc.notify", "api.customer"), ("svc.invoice-batch", "api.customer"), ("svc.policy-sync", "api.policy")]
    for f, a in cons:
        rel(f"consumes:{f}>{a}", "CONSUMES_API", f, a, ev=["openapi"])
    pub = [("svc.claims-intake", "ch.claim-submitted"), ("svc.quote", "ch.quote-issued"), ("svc.policy-api", "ch.policy-bound"),
           ("svc.payments-api", "ch.payment-received"), ("svc.customer-api", "ch.notify-req"), ("svc.claims-api", "ch.notify-req"),
           ("svc.docs-index", "ch.doc-indexed"), ("svc.billing-api", "ch.notify-req"), ("svc.claims-settlement", "ch.notify-req")]
    sub = [("svc.claims-api", "ch.claim-submitted"), ("svc.claims-reporting", "ch.claim-submitted"), ("svc.claims-portal-bff", "ch.quote-issued"),
           ("svc.billing-api", "ch.policy-bound"), ("svc.invoice-batch", "ch.payment-received"), ("svc.notify", "ch.notify-req"),
           ("svc.claims-reporting", "ch.doc-indexed"), ("svc.uw-rules", "ch.quote-issued"), ("svc.policy-api", "ch.quote-issued"),
           ("svc.customer-api", "ch.policy-bound"), ("svc.notify-fn", "ch.notify-req"), ("svc.claims-settlement", "ch.payment-received")]
    for f, c in pub:
        rel(f"publishes:{f}>{c}", "PUBLISHES_TO", f, c, ev=["asyncapi"])
    for f, c in sub:
        rel(f"subscribes:{f}>{c}", "SUBSCRIBES_TO", f, c, ev=["asyncapi"])
    reads = [("svc.claims-api", "ds.claims"), ("svc.claims-api", "ds.policies"), ("svc.claims-intake", "ds.customers"), ("svc.claims-settlement", "ds.claims"),
             ("svc.claims-reporting", "ds.claims"), ("svc.claims-reporting", "ds.analytics"), ("svc.policy-api", "ds.policies"), ("svc.quote", "ds.quotes"),
             ("svc.quote", "ds.rating"), ("svc.uw-rules", "ds.policies"), ("svc.billing-api", "ds.ledger"), ("svc.invoice-batch", "ds.ledger"),
             ("svc.customer-api", "ds.customers"), ("svc.docs-api", "ds.documents"), ("svc.notify", "ds.customers"), ("svc.pricing-batch", "ds.rating"),
             ("svc.policy-sync", "ds.policies"), ("svc.billing-mainframe", "ds.ledger"), ("svc.claims-portal-bff", "ds.claims"), ("svc.uw-rules", "ds.rating"),
             ("svc.policy-api", "ds.customers"), ("svc.billing-api", "ds.policies"), ("svc.payments-api", "ds.customers"), ("svc.notify-fn", "ds.customers"),
             ("svc.claims-reporting", "ds.policies"), ("svc.quote", "ds.customers")]
    writes = [("svc.claims-api", "ds.claims"), ("svc.claims-intake", "ds.claims"), ("svc.claims-settlement", "ds.ledger"), ("svc.claims-reporting", "ds.analytics"),
              ("svc.policy-api", "ds.policies"), ("svc.quote", "ds.quotes"), ("svc.billing-api", "ds.ledger"), ("svc.invoice-batch", "ds.ledger"),
              ("svc.payments-api", "ds.ledger"), ("svc.customer-api", "ds.customers"), ("svc.docs-index", "ds.documents"), ("svc.policy-sync", "ds.policies"),
              ("svc.pricing-batch", "ds.rating"), ("svc.billing-mainframe", "ds.ledger"), ("svc.docs-api", "ds.documents")]
    for f, d in reads:
        rel(f"reads:{f}>{d}", "READS_FROM", f, d, ev=["doc-claims" if "claims" in f else "doc-policy"])
    for f, d in writes:
        rel(f"writes:{f}>{d}", "WRITES_TO", f, d, ev=["doc-claims" if "claims" in f else "doc-policy"])
    rel("stores:svc.notify>ds.documents", "STORES_IN", "svc.notify", "ds.documents", ev=["doc-policy"])
    rel("stores:svc.docs-index>ds.analytics", "STORES_IN", "svc.docs-index", "ds.analytics", ev=["doc-claims"])
    rel("stores:svc.customer-web>ds.customers", "STORES_IN", "svc.customer-web", "ds.customers", ev=["doc-policy"])
    rel("reads:svc.notify>ds.documents", "READS_FROM", "svc.notify", "ds.documents", ev=["doc-policy"])
    for f, to, why in [("app.claims-engine", "app.policy-admin", "Claim validation needs active policy terms"),
                       ("app.quoting", "api.rating", "Quotes cannot be priced without the external rating service"),
                       ("sys.billing", "sys.policy", "Invoices are generated from bound policies"),
                       ("app.customer-portal", "app.notifications", "Customer journeys rely on notifications")]:
        rel(f"depends:{f}>{to}", "DEPENDS_ON", f, to, ev=["capmap"], attrs={"rationale": why})

    # ---------------- Azure (provider configuration)
    ent("az.tenant", "azure.tenant", "Example Tenant (synthetic)", ["arg-prod"], provider="azure", ids=[("azure.tenant_id", TENANT)])
    ent("az.sub-np", "azure.subscription", "sub-claims-nonprod", ["arg-nonprod"], provider="azure", parent="az.tenant", scope="unknown",
        ids=[("azure.subscription_id", SUB_NP), ("azure.arm", arm(SUB_NP))])
    ent("az.sub-pr", "azure.subscription", "sub-claims-prod", ["arg-prod"], provider="azure", parent="az.tenant", env="env.prod",
        ids=[("azure.subscription_id", SUB_PR), ("azure.arm", arm(SUB_PR))])
    rgs = [("az.rg-plat-np", "rg-platform-nonprod", "az.sub-np", SUB_NP, "westeurope", None, ["env.dev", "env.sit", "env.uat"]),
           ("az.rg-claims-np", "rg-claims-nonprod", "az.sub-np", SUB_NP, "westeurope", "env.uat", None),
           ("az.rg-plat-pr", "rg-platform-prod", "az.sub-pr", SUB_PR, "westeurope", "env.prod", None),
           ("az.rg-claims-pr", "rg-claims-prod", "az.sub-pr", SUB_PR, "westeurope", "env.prod", None),
           ("az.rg-claims-dr", "rg-claims-dr", "az.sub-pr", SUB_PR, "northeurope", "env.prod", None)]
    rg_sub = {}
    for k, n, s, sid, loc, env, shared in rgs:
        ev = "arg-nonprod" if sid == SUB_NP else "arg-prod"
        ent(k, "azure.resource_group", n, [ev], parent=s, env=env, shared=shared, attrs={"location": loc}, ids=[("azure.arm", arm(sid, n))])
        rg_sub[k] = (sid, n, ev)

    def az(key, type_key, name, rg, path, *, env=None, shared=None, attrs=None, parent=None, ev=None, verified=None, trust=None, extra_ids=()):
        sid, rgn, rgev = rg_sub[rg]
        ids = [("azure.arm", arm(sid, rgn, *path))] + list(extra_ids)
        return ent(key, type_key, name, [ev or rgev], parent=parent or rg, env=env, shared=shared, attrs=attrs, ids=ids, verified=verified, trust=trust)

    az("az.apim-np", "azure.apim_service", "apim-nonprod", "az.rg-plat-np", ["Microsoft.ApiManagement", "service", "apim-nonprod"],
       shared=["env.dev", "env.sit"], attrs={"location": "westeurope", "sku": "Developer"}, ev="apim-config")
    az("az.apim-pr", "azure.apim_service", "apim-prod", "az.rg-plat-pr", ["Microsoft.ApiManagement", "service", "apim-prod"],
       env="env.prod", attrs={"location": "westeurope", "sku": "Premium"}, ev="apim-config")
    apim_apis = [("az.apimapi-np-claims", "claims-api", "az.apim-np", "az.rg-plat-np", "apim-nonprod", "1", "api.claims", None, ["env.dev", "env.sit"]),
                 ("az.apimapi-np-quotes", "quotes-api", "az.apim-np", "az.rg-plat-np", "apim-nonprod", "2", "api.quotes", None, ["env.dev", "env.sit"]),
                 ("az.apimapi-pr-claims", "claims-api", "az.apim-pr", "az.rg-plat-pr", "apim-prod", "1", "api.claims", "env.prod", None),
                 ("az.apimapi-pr-quotes", "quotes-api", "az.apim-pr", "az.rg-plat-pr", "apim-prod", "2", "api.quotes", "env.prod", None),
                 ("az.apimapi-pr-policy", "policy-api", "az.apim-pr", "az.rg-plat-pr", "apim-prod", "1", "api.policy", "env.prod", None),
                 ("az.apimapi-pr-customer", "customer-api", "az.apim-pr", "az.rg-plat-pr", "apim-prod", "1", "api.customer", "env.prod", None)]
    for k, n, svc, rg, svcname, rev, api, env, shared in apim_apis:
        sid = rg_sub[rg][0]
        sarm = arm(sid, rg_sub[rg][1], "Microsoft.ApiManagement", "service", svcname)
        az(k, "azure.apim_api", n, rg, ["Microsoft.ApiManagement", "service", svcname, "apis", n], parent=svc, env=env, shared=shared,
           attrs={"api_revision": rev}, ev="apim-config", extra_ids=[("apim.api", f"{sarm}#api:{n};rev={rev}")])
        rel(f"deployed:{api}>{k}", "DEPLOYED_AS", api, k, ev=["apim-config"], attrs={"deployment_role": "primary"})

    for k, n, rg, loc, env, shared in [("az.aks-np", "aks-nonprod", "az.rg-plat-np", "westeurope", None, ["env.dev", "env.sit", "env.uat"]),
                                       ("az.aks-pr", "aks-prod", "az.rg-plat-pr", "westeurope", "env.prod", None),
                                       ("az.aks-dr", "aks-dr", "az.rg-claims-dr", "northeurope", "env.prod", None)]:
        az(k, "azure.aks_cluster", n, rg, ["Microsoft.ContainerService", "managedClusters", n], env=env, shared=shared,
           attrs={"location": loc, "kubernetes_version": "1.33"})
    UIDS = {}

    def k8s_uid(name: str) -> str:
        UIDS[name] = uuid7(10_000 + len(UIDS), f"k8s|{name}")
        return UIDS[name]

    def aks_arm(cluster_key: str) -> str:
        return {"az.aks-np": arm(SUB_NP, "rg-platform-nonprod", "Microsoft.ContainerService", "managedClusters", "aks-nonprod"),
                "az.aks-pr": arm(SUB_PR, "rg-platform-prod", "Microsoft.ContainerService", "managedClusters", "aks-prod"),
                "az.aks-dr": arm(SUB_PR, "rg-claims-dr", "Microsoft.ContainerService", "managedClusters", "aks-dr")}[cluster_key]

    namespaces = [("ns.np.claims-dev", "claims-dev", "az.aks-np", "env.dev"), ("ns.np.claims-sit", "claims-sit", "az.aks-np", "env.sit"),
                  ("ns.np.claims-uat", "claims-uat", "az.aks-np", "env.uat"), ("ns.np.policy-uat", "policy-uat", "az.aks-np", "env.uat"),
                  ("ns.np.claims-uat2", "claims-uat2", "az.aks-np", "env.uat2"),
                  ("ns.np.policy-dev", "policy-dev", "az.aks-np", "env.dev"), ("ns.np.policy-sit", "policy-sit", "az.aks-np", "env.sit"),
                  ("ns.pr.claims", "claims", "az.aks-pr", "env.prod"), ("ns.pr.policy", "policy", "az.aks-pr", "env.prod"),
                  ("ns.dr.claims", "claims", "az.aks-dr", "env.prod")]
    for k, n, cl, env in namespaces:
        ent(k, "k8s.namespace", n, ["aks-config"], parent=cl, env=env, ids=[("k8s.uid", f"azure.arm:{aks_arm(cl)}#{k8s_uid(k)}")])
    workloads = [  # key, name, namespace, env, kind, logical service, deployment role or None
        ("wl.claims-api.dev", "claims-api", "ns.np.claims-dev", "env.dev", "Deployment", "svc.claims-api", "primary"),
        ("wl.claims-api.sit", "claims-api", "ns.np.claims-sit", "env.sit", "Deployment", "svc.claims-api", "primary"),
        ("wl.claims-api.uat", "claims-api", "ns.np.claims-uat", "env.uat", "Deployment", "svc.claims-api", "primary"),
        ("wl.claims-api.uat2", "claims-api", "ns.np.claims-uat2", "env.uat2", "Deployment", "svc.claims-api", None),
        ("wl.claims-bff.uat", "claims-portal-bff", "ns.np.claims-uat", "env.uat", "Deployment", "svc.claims-portal-bff", "primary"),
        ("wl.policy-api.uat", "policy-api", "ns.np.policy-uat", "env.uat", "Deployment", "svc.policy-api", "primary"),
        ("wl.claims-api.prod", "claims-api", "ns.pr.claims", "env.prod", "Deployment", "svc.claims-api", "primary"),
        ("wl.claims-intake.prod", "claims-intake", "ns.pr.claims", "env.prod", "Deployment", "svc.claims-intake", "primary"),
        ("wl.claims-bff.prod", "claims-portal-bff", "ns.pr.claims", "env.prod", "Deployment", "svc.claims-portal-bff", "primary"),
        ("wl.claims-settle.prod", "settlement", "ns.pr.claims", "env.prod", "CronJob", "svc.claims-settlement", "unknown"),
        ("wl.policy-api.prod", "policy-api", "ns.pr.policy", "env.prod", "Deployment", "svc.policy-api", "primary"),
        ("wl.quote.prod", "quote-service", "ns.pr.policy", "env.prod", "Deployment", "svc.quote", "primary"),
        ("wl.uw.prod", "uw-rules", "ns.pr.policy", "env.prod", "Deployment", "svc.uw-rules", "primary"),
        ("wl.claims-api.dr", "claims-api", "ns.dr.claims", "env.prod", "Deployment", "svc.claims-api", "standby"),
        ("wl.claims-intake.dr", "claims-intake", "ns.dr.claims", "env.prod", "Deployment", "svc.claims-intake", "standby"),
        ("wl.claims-bff.dev", "claims-portal-bff", "ns.np.claims-dev", "env.dev", "Deployment", "svc.claims-portal-bff", "primary"),
        ("wl.claims-bff.sit", "claims-portal-bff", "ns.np.claims-sit", "env.sit", "Deployment", "svc.claims-portal-bff", "primary"),
        ("wl.claims-intake.sit", "claims-intake", "ns.np.claims-sit", "env.sit", "Deployment", "svc.claims-intake", "primary"),
        ("wl.claims-intake.uat", "claims-intake", "ns.np.claims-uat", "env.uat", "Deployment", "svc.claims-intake", "primary"),
        ("wl.policy-api.dev", "policy-api", "ns.np.policy-dev", "env.dev", "Deployment", "svc.policy-api", "primary"),
        ("wl.policy-api.sit", "policy-api", "ns.np.policy-sit", "env.sit", "Deployment", "svc.policy-api", "primary"),
        ("wl.quote.dev", "quote-service", "ns.np.policy-dev", "env.dev", "Deployment", "svc.quote", "primary"),
        ("wl.quote.sit", "quote-service", "ns.np.policy-sit", "env.sit", "Deployment", "svc.quote", "primary"),
        ("wl.quote.uat", "quote-service", "ns.np.policy-uat", "env.uat", "Deployment", "svc.quote", "primary"),
        ("wl.uw.uat", "uw-rules", "ns.np.policy-uat", "env.uat", "Deployment", "svc.uw-rules", None),
    ]
    ns_cluster = {k: cl for k, _, cl, _ in namespaces}
    for k, n, nsk, env, kind, svc, role in workloads:
        ent(k, "k8s.workload", n, ["aks-config"], parent=nsk, env=env, attrs={"workload_kind": kind},
            ids=[("k8s.uid", f"azure.arm:{aks_arm(ns_cluster[nsk])}#{k8s_uid(k)}")])
        rel(f"deployed:{svc}>{k}", "DEPLOYED_AS", svc, k, ev=["aks-config"], attrs={"deployment_role": role} if role else {})
    for k, n, rg, env, sk, svc in [("az.app-cust-pr", "app-customer-portal-prod", "az.rg-claims-pr", "env.prod", "app", "svc.customer-web"),
                                   ("az.app-cust-uat", "app-customer-portal-uat", "az.rg-claims-np", "env.uat", "app", "svc.customer-web"),
                                   ("az.func-notify-pr", "func-notification-prod", "az.rg-plat-pr", "env.prod", "functionapp", "svc.notify-fn"),
                                   ("az.app-custapi-pr", "app-customer-api-prod", "az.rg-claims-pr", "env.prod", "app", "svc.customer-api")]:
        az(k, "azure.app_service", n, rg, ["Microsoft.Web", "sites", n], env=env, attrs={"location": "westeurope", "site_kind": sk})
        rel(f"deployed:{svc}>{k}", "DEPLOYED_AS", svc, k, ev=["arg-prod" if env == "env.prod" else "arg-nonprod"], attrs={"deployment_role": "primary"})

    for k, n, rg, env, loc in [("az.sb-np", "sb-claims-nonprod", "az.rg-claims-np", "env.uat", "westeurope"),
                               ("az.sb-pr", "sb-claims-prod", "az.rg-claims-pr", "env.prod", "westeurope")]:
        az(k, "azure.service_bus_namespace", n, rg, ["Microsoft.ServiceBus", "namespaces", n], env=env, attrs={"location": loc, "sku": "Premium" if "pr" in k else "Standard"})
    sbents = [("az.sbt-np-claim", "azure.service_bus_topic", "claim-submitted", "az.sb-np", "az.rg-claims-np", "env.uat", "topics", "ch.claim-submitted"),
              ("az.sbt-pr-claim", "azure.service_bus_topic", "claim-submitted", "az.sb-pr", "az.rg-claims-pr", "env.prod", "topics", "ch.claim-submitted"),
              ("az.sbt-pr-bound", "azure.service_bus_topic", "policy-bound", "az.sb-pr", "az.rg-claims-pr", "env.prod", "topics", "ch.policy-bound"),
              ("az.sbq-pr-pay", "azure.service_bus_queue", "payment-received", "az.sb-pr", "az.rg-claims-pr", "env.prod", "queues", "ch.payment-received"),
              ("az.sbq-pr-notify", "azure.service_bus_queue", "notification-requested", "az.sb-pr", "az.rg-claims-pr", "env.prod", "queues", "ch.notify-req")]
    for k, tk, n, nsk, rg, env, coll, ch in sbents:
        nsname = {"az.sb-np": "sb-claims-nonprod", "az.sb-pr": "sb-claims-prod"}[nsk]
        az(k, tk, n, rg, ["Microsoft.ServiceBus", "namespaces", nsname, coll, n], parent=nsk, env=env)
        rel(f"deployed:{ch}>{k}", "DEPLOYED_AS", ch, k, ev=["arg-prod" if env == "env.prod" else "arg-nonprod"], attrs={"deployment_role": "primary"})

    for k, n, rg, env, loc in [("az.sql-pr", "sql-claims-prod", "az.rg-claims-pr", "env.prod", "westeurope"),
                               ("az.sql-dr", "sql-claims-dr", "az.rg-claims-dr", "env.prod", "northeurope"),
                               ("az.sql-uat", "sql-claims-uat", "az.rg-claims-np", "env.uat", "westeurope")]:
        az(k, "azure.sql_server", n, rg, ["Microsoft.Sql", "servers", n], env=env, attrs={"location": loc})
    dbs = [("az.db-claims-pr", "sqldb-claims", "az.sql-pr", "sql-claims-prod", "az.rg-claims-pr", "env.prod", "ds.claims", "primary"),
           ("az.db-claims-dr", "sqldb-claims", "az.sql-dr", "sql-claims-dr", "az.rg-claims-dr", "env.prod", "ds.claims", "active_secondary"),
           ("az.db-claims-uat", "sqldb-claims", "az.sql-uat", "sql-claims-uat", "az.rg-claims-np", "env.uat", "ds.claims", "primary"),
           ("az.db-policy-pr", "sqldb-policy", "az.sql-pr", "sql-claims-prod", "az.rg-claims-pr", "env.prod", "ds.policies", "primary"),
           ("az.db-quotes-pr", "sqldb-quotes", "az.sql-pr", "sql-claims-prod", "az.rg-claims-pr", "env.prod", "ds.quotes", "primary")]
    for k, n, srv, srvname, rg, env, ds, role in dbs:
        az(k, "azure.sql_database", n, rg, ["Microsoft.Sql", "servers", srvname, "databases", n], parent=srv, env=env)
        rel(f"deployed:{ds}>{k}", "DEPLOYED_AS", ds, k, ev=["arg-prod" if env == "env.prod" else "arg-nonprod"], attrs={"deployment_role": role})
    for k, n, rg, env, ds in [("az.st-docs-pr", "stdocsprod", "az.rg-claims-pr", "env.prod", "ds.documents"),
                              ("az.st-docs-uat", "stdocsuat", "az.rg-claims-np", "env.uat", "ds.documents")]:
        az(k, "azure.storage_account", n, rg, ["Microsoft.Storage", "storageAccounts", n], env=env, attrs={"location": "westeurope", "sku": "Standard_ZRS"})
        rel(f"deployed:{ds}>{k}", "DEPLOYED_AS", ds, k, ev=["arg-prod" if env == "env.prod" else "arg-nonprod"], attrs={"deployment_role": "primary"})
    for k, n, rg, env in [("az.kv-pr", "kv-claims-prod", "az.rg-claims-pr", "env.prod"), ("az.kv-np", "kv-claims-nonprod", "az.rg-claims-np", None)]:
        az(k, "azure.key_vault", n, rg, ["Microsoft.KeyVault", "vaults", n], env=env, shared=None if env else ["env.dev", "env.sit", "env.uat"],
           attrs={"location": "westeurope"})
    for k, n, rg, env, loc in [("az.vnet-pr", "vnet-prod", "az.rg-plat-pr", "env.prod", "westeurope"),
                               ("az.vnet-np", "vnet-nonprod", "az.rg-plat-np", None, "westeurope"),
                               ("az.vnet-dr", "vnet-dr", "az.rg-claims-dr", "env.prod", "northeurope")]:
        az(k, "azure.vnet", n, rg, ["Microsoft.Network", "virtualNetworks", n], env=env, shared=None if env else ["env.dev", "env.sit", "env.uat"], attrs={"location": loc})
    for k, n, vnet, vname, rg, env in [("az.snet-aks-pr", "snet-aks", "az.vnet-pr", "vnet-prod", "az.rg-plat-pr", "env.prod"),
                                       ("az.snet-app-pr", "snet-app", "az.vnet-pr", "vnet-prod", "az.rg-plat-pr", "env.prod"),
                                       ("az.snet-aks-np", "snet-aks", "az.vnet-np", "vnet-nonprod", "az.rg-plat-np", None),
                                       ("az.snet-aks-dr", "snet-aks", "az.vnet-dr", "vnet-dr", "az.rg-claims-dr", "env.prod")]:
        az(k, "azure.subnet", n, rg, ["Microsoft.Network", "virtualNetworks", vname, "subnets", n], parent=vnet, env=env,
           shared=None if env else ["env.dev", "env.sit", "env.uat"])
    # Azure resources without a specific type: neutral type of their mapped category, or the generic fallback
    az("az.vm-batch", "infra.compute", "vm-batch-prod", "az.rg-claims-pr", ["Microsoft.Compute", "virtualMachines", "vm-batch-prod"], env="env.prod",
       attrs={"compute_kind": "vm"}, trust="conflicted")
    # two sources disagree on its location and no precedence rule is approved: both assertions are kept and the stored
    # value is the prior approved one, here none (ADR-0018 conflict procedure; trust function TF-2)
    w.t["entity_versions"][-1]["native_type"] = "microsoft.compute/virtualmachines"
    w.t["entity_versions"][-1]["provider"] = "azure"
    w._assert("entity", w.ids["az.vm-batch"], "arg-prod", "attributes.location", "westeurope")
    w._assert("entity", w.ids["az.vm-batch"], "cmdb", "attributes.location", "northeurope")
    for k, tk, n, path, attrs in [
            ("az.cosmos-notify", "infra.data_store", "cosmos-notifications-prod", ["Microsoft.DocumentDB", "databaseAccounts", "cosmos-notifications-prod"], {"store_kind": "nosql_db"}),
            ("az.afd-customer", "infra.resource", "afd-customer-prod", ["Microsoft.Cdn", "profiles", "afd-customer-prod"], {})]:
        az(k, tk, n, "az.rg-claims-pr", path, env="env.prod", attrs=attrs)
        v = w.t["entity_versions"][-1]
        v["provider"] = "azure"
        v["native_type"] = normalize_identity(w.T(), "azure.arm", arm(SUB_PR, "rg-claims-prod", *path))[1]["provider_namespace"] + "/" + \
            normalize_identity(w.T(), "azure.arm", arm(SUB_PR, "rg-claims-prod", *path))[1]["type_path"]
    # documented-only billing database: neutral data store until its ARM ID is linked (R6)
    ent("az.db-billing", "infra.data_store", "sqldb-billing-prod", ["doc-policy"], parent="az.rg-plat-pr", provider="azure",
        native="microsoft.sql/servers/databases", env="env.prod", attrs={"store_kind": "relational_db"}, ids=[("source.arch-docs", "DB-BILLING-PROD")])
    rel("deployed:ds.ledger>az.db-billing", "DEPLOYED_AS", "ds.ledger", "az.db-billing", ev=["doc-policy"], attrs={"deployment_role": "primary"})

    # physical integrations on Azure
    phys = [
        ("CONSUMES_API", "wl.claims-bff.prod", "az.apimapi-pr-claims", "app-config", {}),
        ("CONSUMES_API", "wl.claims-bff.prod", "az.apimapi-pr-quotes", "app-config", {}),
        ("CONSUMES_API", "wl.claims-bff.uat", "az.apimapi-pr-quotes", "app-config", {}),   # evidenced UAT -> PROD
        ("CONSUMES_API", "az.app-cust-pr", "az.apimapi-pr-customer", "app-config", {}),
        ("CONSUMES_API", "wl.uw.prod", "az.apimapi-pr-policy", "app-config", {}),
        ("PUBLISHES_TO", "wl.claims-intake.prod", "az.sbt-pr-claim", "app-config", {}),
        ("SUBSCRIBES_TO", "wl.claims-api.prod", "az.sbt-pr-claim", "app-config", {"subscription_name": "claims-api"}),
        ("PUBLISHES_TO", "wl.policy-api.prod", "az.sbt-pr-bound", "app-config", {}),
        ("SUBSCRIBES_TO", "az.func-notify-pr", "az.sbq-pr-notify", "app-config", {}),
        ("PUBLISHES_TO", "az.app-custapi-pr", "az.sbq-pr-notify", "app-config", {}),
        ("PUBLISHES_TO", "wl.claims-api.uat", "az.sbt-np-claim", "app-config", {}),
        ("READS_FROM", "wl.claims-api.prod", "az.db-claims-pr", "app-config", {}),
        ("WRITES_TO", "wl.claims-api.prod", "az.db-claims-pr", "app-config", {}),
        ("WRITES_TO", "wl.claims-intake.prod", "az.db-claims-pr", "app-config", {}),
        ("READS_FROM", "wl.claims-api.dr", "az.db-claims-dr", "app-config", {}),
        ("READS_FROM", "wl.claims-bff.prod", "az.db-claims-dr", "app-config", {}),          # DR secondary also serves production reads
        ("READS_FROM", "wl.claims-api.uat", "az.db-claims-uat", "app-config", {}),
        ("WRITES_TO", "wl.claims-api.uat", "az.db-claims-uat", "app-config", {}),
        ("READS_FROM", "wl.policy-api.prod", "az.db-policy-pr", "app-config", {}),
        ("WRITES_TO", "wl.policy-api.prod", "az.db-policy-pr", "app-config", {}),
        ("READS_FROM", "wl.quote.prod", "az.db-quotes-pr", "app-config", {}),
        ("WRITES_TO", "wl.quote.prod", "az.db-quotes-pr", "app-config", {}),
        ("WRITES_TO", "az.func-notify-pr", "az.cosmos-notify", "app-config", {}),
        ("READS_FROM", "az.app-custapi-pr", "az.st-docs-pr", "app-config", {}),
        ("CONNECTS_TO", "az.aks-pr", "az.snet-aks-pr", "arg-prod", {"connectivity_kind": "subnet_placement"}),
        ("CONNECTS_TO", "az.aks-np", "az.snet-aks-np", "arg-nonprod", {"connectivity_kind": "subnet_placement"}),
        ("CONNECTS_TO", "az.aks-dr", "az.snet-aks-dr", "arg-prod", {"connectivity_kind": "subnet_placement"}),
        ("CONNECTS_TO", "az.app-cust-pr", "az.snet-app-pr", "arg-prod", {"connectivity_kind": "network_integration"}),
        ("CONNECTS_TO", "az.vnet-pr", "az.vnet-dr", "arg-prod", {"connectivity_kind": "network_peering"}),
        ("CONNECTS_TO", "az.apimapi-pr-claims", "wl.claims-api.prod", "apim-config", {"connectivity_kind": "gateway_backend"}),
        ("CONNECTS_TO", "az.apimapi-pr-policy", "wl.policy-api.prod", "apim-config", {"connectivity_kind": "gateway_backend"}),
        ("CONNECTS_TO", "az.apimapi-pr-quotes", "wl.quote.prod", "apim-config", {"connectivity_kind": "gateway_backend"}),
        ("CONNECTS_TO", "az.apimapi-np-claims", "wl.claims-api.sit", "apim-config", {"connectivity_kind": "gateway_backend"}),
        ("CONNECTS_TO", "wl.claims-api.prod", "az.kv-pr", "app-config", {"connectivity_kind": "private_link", "native_kind": "private endpoint"}),
        ("CONNECTS_TO", "wl.claims-api.uat", "az.sb-pr", "app-config", {"connectivity_kind": "configured_endpoint"}),  # evidenced UAT -> PROD
        ("CONNECTS_TO", "az.app-custapi-pr", "az.kv-pr", "app-config", {"connectivity_kind": "configured_endpoint"}),
        ("CONNECTS_TO", "az.vm-batch", "az.db-claims-pr", "app-config", {"connectivity_kind": "configured_endpoint"}),
        ("CONNECTS_TO", "az.app-cust-pr", "az.afd-customer", "app-config", {"connectivity_kind": "configured_endpoint"}),
    ]
    for rt, f, to, ev, attrs in phys:
        verified = V if (rt, f, to) == ("CONSUMES_API", "wl.claims-bff.uat", "az.apimapi-pr-quotes") else None
        rel(f"{rt.lower()}:{f}>{to}:{attrs.get('connectivity_kind', '')}", rt, f, to, ev=[ev], attrs=attrs, verified=verified)
    enrich = [
        ("CONSUMES_API", "wl.claims-bff.dev", "az.apimapi-np-claims", {}), ("CONSUMES_API", "wl.claims-bff.sit", "az.apimapi-np-claims", {}),
        ("CONSUMES_API", "wl.claims-bff.dev", "az.apimapi-np-quotes", {}), ("CONSUMES_API", "wl.claims-bff.sit", "az.apimapi-np-quotes", {}),
        ("CONSUMES_API", "wl.quote.uat", "az.apimapi-np-quotes", {}), ("CONSUMES_API", "wl.uw.uat", "az.apimapi-pr-policy", {}),  # UAT -> PROD
        ("CONSUMES_API", "wl.claims-api.prod", "az.apimapi-pr-policy", {}), ("CONSUMES_API", "wl.claims-intake.prod", "az.apimapi-pr-customer", {}),
        ("CONSUMES_API", "wl.policy-api.prod", "az.apimapi-pr-customer", {}),
        ("READS_FROM", "wl.policy-api.uat", "az.db-policy-pr", {}),                                                              # UAT -> PROD
        ("PUBLISHES_TO", "wl.claims-intake.uat", "az.sbt-np-claim", {}), ("WRITES_TO", "wl.claims-intake.uat", "az.db-claims-uat", {}),
        ("READS_FROM", "wl.claims-settle.prod", "az.db-claims-pr", {}), ("WRITES_TO", "wl.claims-settle.prod", "az.db-claims-pr", {}),
        ("READS_FROM", "wl.uw.prod", "az.db-policy-pr", {}), ("WRITES_TO", "az.app-custapi-pr", "az.st-docs-pr", {}),
        ("CONNECTS_TO", "az.apimapi-np-quotes", "wl.quote.sit", {"connectivity_kind": "gateway_backend"}),
        ("CONNECTS_TO", "az.apimapi-np-claims", "wl.claims-api.dev", {"connectivity_kind": "gateway_backend"}),
        ("CONNECTS_TO", "wl.claims-api.dr", "az.kv-pr", {"connectivity_kind": "configured_endpoint"}),
    ] + [("CONNECTS_TO", wl, "az.kv-np", {"connectivity_kind": "configured_endpoint"}) for wl in
         ["wl.claims-api.dev", "wl.claims-api.sit", "wl.claims-api.uat", "wl.claims-bff.dev", "wl.claims-bff.sit", "wl.claims-bff.uat",
          "wl.claims-intake.sit", "wl.claims-intake.uat", "wl.policy-api.dev", "wl.policy-api.sit", "wl.policy-api.uat", "wl.quote.dev",
          "wl.quote.sit", "wl.quote.uat", "wl.uw.uat"]] + [
        ("CONNECTS_TO", wl, "az.kv-pr", {"connectivity_kind": "configured_endpoint"}) for wl in
        ["wl.claims-intake.prod", "wl.claims-bff.prod", "wl.claims-settle.prod", "wl.policy-api.prod", "wl.quote.prod", "wl.uw.prod"]]
    for rt, f, to, attrs in enrich:
        rel(f"{rt.lower()}:{f}>{to}:{attrs.get('connectivity_kind', '')}", rt, f, to, ev=["app-config" if not f.startswith("az.apimapi") else "apim-config"], attrs=attrs)
    rel("deployed:svc.invoice-batch>az.vm-batch", "DEPLOYED_AS", "svc.invoice-batch", "az.vm-batch", ev=["arg-prod"], attrs={"deployment_role": "primary"})

    # ---------------- Google Cloud (documented / IaC)
    ent("gcp.org", "infra.scope", "example-gcp-org", ["iac-gcp"], provider="gcp", native="cloudresourcemanager.googleapis.com/Organization",
        attrs={"scope_kind": "organization"}, ids=[("gcp.resource_name", "//cloudresourcemanager.googleapis.com/organizations/000000000001")])
    ent("gcp.folder", "infra.scope", "claims", ["iac-gcp"], parent="gcp.org", native="cloudresourcemanager.googleapis.com/Folder",
        attrs={"scope_kind": "folder"}, ids=[("gcp.resource_name", "//cloudresourcemanager.googleapis.com/folders/000000000002")])
    ent("gcp.project", "infra.scope", "claims-events-prod", ["iac-gcp"], parent="gcp.folder", native="cloudresourcemanager.googleapis.com/Project",
        env="env.prod", attrs={"scope_kind": "project"}, ids=[("gcp.resource_name", "//cloudresourcemanager.googleapis.com/projects/claims-events-prod")])
    ent("gcp.topic", "infra.messaging_channel", "document-indexed", ["iac-gcp"], parent="gcp.project", native="pubsub.googleapis.com/Topic",
        env="env.prod", attrs={"channel_kind": "topic"}, ids=[("gcp.resource_name", "//pubsub.googleapis.com/projects/claims-events-prod/topics/document-indexed")])
    gke = "//container.googleapis.com/projects/claims-events-prod/locations/europe-west1/clusters/gke-docs-prod"
    ent("gcp.gke", "infra.cluster", "gke-docs-prod", ["iac-gcp"], parent="gcp.project", native="container.googleapis.com/Cluster", env="env.prod",
        attrs={"cluster_kind": "kubernetes", "location": "europe-west1"}, ids=[("gcp.resource_name", gke)])
    ent("gcp.ns", "k8s.namespace", "docs", ["iac-gcp"], parent="gcp.gke", env="env.prod", ids=[("k8s.uid", f"gcp.resource_name:{gke}#{k8s_uid('gcp.ns')}")])
    ent("gcp.indexer", "k8s.workload", "doc-indexer", ["iac-gcp"], parent="gcp.ns", env="env.prod", attrs={"workload_kind": "Deployment"},
        ids=[("k8s.uid", f"gcp.resource_name:{gke}#{k8s_uid('gcp.indexer')}")])
    ent("gcp.bq", "infra.resource", "analytics-warehouse", ["iac-gcp"], parent="gcp.project", native="bigquery.googleapis.com/Dataset", env="env.prod",
        ids=[("gcp.resource_name", "//bigquery.googleapis.com/projects/claims-events-prod/datasets/analytics_warehouse")])
    rel("deployed:ch.doc-indexed>gcp.topic", "DEPLOYED_AS", "ch.doc-indexed", "gcp.topic", ev=["doc-multicloud"], attrs={"deployment_role": "primary"})
    rel("deployed:svc.docs-index>gcp.indexer", "DEPLOYED_AS", "svc.docs-index", "gcp.indexer", ev=["doc-multicloud"], attrs={"deployment_role": "primary"})
    rel("publishes:gcp.indexer>gcp.topic", "PUBLISHES_TO", "gcp.indexer", "gcp.topic", ev=["iac-gcp"])
    rel("connects:az.app-custapi-pr>gcp.topic", "CONNECTS_TO", "az.app-custapi-pr", "gcp.topic", ev=["netarch"], attrs={"connectivity_kind": "configured_endpoint"})

    # ---------------- Alibaba Cloud (documented, human-asserted connectivity)
    ent("ali.acct", "infra.scope", "example-aliyun", ["doc-aliyun"], provider="alibaba", native="ACS::ResourceManager::Account",
        attrs={"scope_kind": "account"}, ids=[("source.arch-docs", "ALIYUN-ACCOUNT-01")])
    ent("ali.rg", "infra.scope", "rg-pricing", ["doc-aliyun"], parent="ali.acct", native="ACS::ResourceManager::ResourceGroup", attrs={"scope_kind": "resource_group"},
        ids=[("alibaba.arn", "acs:resourcemanager::1000000000000001:resourcegroup/rg-exmp0001")])
    for k, n, loc, role in [("ali.ecs1", "ecs-pricing-01", "cn-hangzhou", "primary"), ("ali.ecs2", "ecs-pricing-02", "cn-shanghai", "standby")]:
        ent(k, "infra.compute", n, ["doc-aliyun"], parent="ali.rg", native="ACS::ECS::Instance", env="env.prod",
            attrs={"compute_kind": "vm", "location": loc}, ids=[("alibaba.arn", f"acs:ecs:{loc}:1000000000000001:instance/i-{n}")])
    ent("ali.batch", "infra.workload", "pricing-batch", ["doc-aliyun"], parent="ali.ecs1", native="process", env="env.prod", attrs={"workload_kind": "process"},
        ids=[("source.arch-docs", "ALIYUN-PRICING-BATCH")])
    rel("deployed:svc.pricing-batch>ali.batch", "DEPLOYED_AS", "svc.pricing-batch", "ali.batch", ev=["doc-aliyun"], attrs={"deployment_role": "primary"})
    rel("deployed:svc.pricing-batch>ali.ecs2", "DEPLOYED_AS", "svc.pricing-batch", "ali.ecs2", ev=["doc-aliyun"], attrs={"deployment_role": "standby"})
    rel("connects:ali.ecs1>az.sb-pr", "CONNECTS_TO", "ali.ecs1", "az.sb-pr", ev=["netarch"], attrs={"connectivity_kind": "configured_endpoint"})
    rel("publishes:ali.batch>az.sbt-pr-bound", "PUBLISHES_TO", "ali.batch", "az.sbt-pr-bound", ev=["doc-aliyun"])

    # ---------------- Oracle Cloud (documented integration with on-premises)
    ent("oci.tenancy", "infra.scope", "example-oci-tenancy", ["spec-policy-sync"], provider="oci", native="Tenancy", attrs={"scope_kind": "tenancy"},
        ids=[("oci.ocid", "ocid1.tenancy.oc1..exmptenancy0001")])
    ent("oci.cmp", "infra.scope", "claims", ["spec-policy-sync"], parent="oci.tenancy", native="Compartment", attrs={"scope_kind": "compartment"},
        ids=[("oci.ocid", "ocid1.compartment.oc1..exmpcompartment0001")])
    oke = "ocid1.cluster.oc1.eu-frankfurt-1.exmpcluster0001"
    ent("oci.oke", "infra.cluster", "oke-claims", ["spec-policy-sync"], parent="oci.cmp", native="ContainerEngine::Cluster", env="env.prod",
        attrs={"cluster_kind": "kubernetes", "location": "eu-frankfurt-1"}, ids=[("oci.ocid", oke)])
    ent("oci.ns", "k8s.namespace", "policy-sync", ["spec-policy-sync"], parent="oci.oke", env="env.prod", ids=[("k8s.uid", f"oci.ocid:{oke}#{k8s_uid('oci.ns')}")])
    ent("oci.sync", "k8s.workload", "policy-sync", ["spec-policy-sync"], parent="oci.ns", env="env.prod", attrs={"workload_kind": "Deployment"},
        ids=[("k8s.uid", f"oci.ocid:{oke}#{k8s_uid('oci.sync')}")])
    rel("deployed:svc.policy-sync>oci.sync", "DEPLOYED_AS", "svc.policy-sync", "oci.sync", ev=["spec-policy-sync"], attrs={"deployment_role": "primary"})

    # ---------------- On-premises (CMDB configuration; DR site as its own environment)
    for k, n, kind, parent, env in [("op.dc-north", "dc-north", "site", None, None), ("op.dc-north-z1", "dc-north-z1", "zone", "op.dc-north", None),
                                    ("op.dc-south", "dc-south", "site", None, None)]:
        ent(k, "infra.scope", n, ["cmdb"], parent=parent, provider="on_premises", native="cmdb:site" if kind == "site" else "cmdb:zone",
            attrs={"scope_kind": kind, "platform": "owned data centre"}, ids=[("source.cmdb", f"SITE-{n.upper()}")], scope="unknown" if env is None else None)
    for k, n, parent, env, ci in [("op.db-host-07", "db-host-07", "op.dc-north-z1", "env.prod", "CI-004211"), ("op.db-host-17", "db-host-17", "op.dc-south", "env.dr", "CI-004217")]:
        ent(k, "infra.compute", n, ["cmdb"], parent=parent, provider="on_premises", native="cmdb:server", env=env,
            attrs={"compute_kind": "physical", "location": "north" if "07" in n else "south", "platform": "Linux server"}, ids=[("source.cmdb", ci)])
    for k, n, parent, env, ci, role in [("op.policydb", "POLICYDB", "op.db-host-07", "env.prod", "CI-004212", "primary"),
                                        ("op.policydb-dr", "POLICYDB-DR", "op.db-host-17", "env.dr", "CI-004218", "standby")]:
        ent(k, "infra.data_store", n, ["cmdb"], parent=parent, provider="on_premises", native="cmdb:database", env=env,
            attrs={"store_kind": "relational_db", "platform": "Oracle Database"}, ids=[("source.cmdb", ci)])
        rel(f"deployed:ds.policies>{k}", "DEPLOYED_AS", "ds.policies", k, ev=["cmdb"], attrs={"deployment_role": role})
    rel("reads:oci.sync>op.policydb", "READS_FROM", "oci.sync", "op.policydb", ev=["spec-policy-sync"])
    rel("writes:oci.sync>op.policydb", "WRITES_TO", "oci.sync", "op.policydb", ev=["spec-policy-sync"])
    ent("op.mq", "infra.resource", "mq-legacy-01", ["doc-legacy"], parent="op.dc-north", provider="on_premises", native="cmdb:message-broker",
        env="env.prod", attrs={"platform": "IBM MQ"}, ids=[("source.cmdb", "CI-003100")], trust="stale")
    rel("connects:op.db-host-07>op.mq", "CONNECTS_TO", "op.db-host-07", "op.mq", ev=["cmdb"], attrs={"connectivity_kind": "configured_endpoint"})

    # ---------------- private cloud and custom technology
    ent("pc.os", "infra.scope", "openstack-01", ["cmdb"], provider="private_cloud", native="openstack:region", attrs={"scope_kind": "platform_instance", "platform": "OpenStack"},
        ids=[("source.cmdb", "PC-OPENSTACK-01")])
    ent("pc.vm", "infra.compute", "pc-reporting-vm", ["cmdb"], parent="pc.os", native="openstack:server", env="env.perf",
        attrs={"compute_kind": "vm", "location": "region-one", "platform": "OpenStack"}, ids=[("source.cmdb", "PC-VM-0042")])
    rel("deployed:svc.claims-reporting>pc.vm", "DEPLOYED_AS", "svc.claims-reporting", "pc.vm", ev=["cmdb"])
    ent("ot.mainframe", "infra.scope", "mainframe-01", ["cmdb"], provider="other", native="cmdb:mainframe-lpar", attrs={"scope_kind": "platform_instance", "platform": "z/OS mainframe"},
        ids=[("source.cmdb", "MF-LPAR-01")])
    ent("ot.cobol", "infra.workload", "billing-batch-cobol", ["cmdb"], parent="ot.mainframe", native="cmdb:batch-job", env="env.prod",
        attrs={"workload_kind": "process", "platform": "z/OS mainframe"}, ids=[("source.cmdb", "MF-JOB-0007")])
    rel("deployed:svc.billing-mainframe>ot.cobol", "DEPLOYED_AS", "svc.billing-mainframe", "ot.cobol", ev=["cmdb"], attrs={"deployment_role": "primary"})

    # cross-provider integrations (one-sided or documented evidence; never verified automatically)
    rel("consumes:az.app-cust-pr>api.rating", "CONSUMES_API", "az.app-cust-pr", "api.rating", ev=["doc-multicloud"])

    # ownership of physical estates (platform team), deliberately incomplete
    for k in ["az.sub-np", "az.sub-pr", "az.rg-plat-np", "az.rg-plat-pr", "az.aks-np", "az.aks-pr", "az.aks-dr", "az.apim-np", "az.apim-pr", "az.vnet-pr", "az.vnet-np"]:
        rel(f"owns:platform>{k}", "OWNS", "team.platform", k, ev=["ownership"], attrs={"ownership_role": "technical"})
    for k in ["az.rg-claims-pr", "az.rg-claims-np", "az.rg-claims-dr", "az.sql-pr", "az.sb-pr"]:
        rel(f"owns:claims>{k}", "OWNS", "team.claims", k, ev=["ownership"], attrs={"ownership_role": "technical"})
    for nsk, tm in [("ns.np.claims-dev", "claims"), ("ns.np.claims-sit", "claims"), ("ns.np.claims-uat", "claims"), ("ns.np.policy-uat", "policy"),
                    ("ns.np.policy-dev", "policy"), ("ns.np.policy-sit", "policy"), ("ns.pr.claims", "claims"), ("ns.pr.policy", "policy"), ("ns.dr.claims", "claims")]:
        rel(f"owns:{tm}>{nsk}", "OWNS", f"team.{tm}", nsk, ev=["ownership"], attrs={"ownership_role": "technical"})
    for ds_, dom in [("ds.customers", "dom.claims"), ("ds.documents", "dom.claims"), ("ds.rating", "dom.billing")]:
        rel(f"member:{ds_}>{dom}", "MEMBER_OF", ds_, dom, ev=["membership"])
    rel("owns:security>az.kv-pr", "OWNS", "team.security", "az.kv-pr", ev=["ownership"], attrs={"ownership_role": "accountable"})
    rel("owns:integration>oci.oke", "OWNS", "team.integration", "oci.oke", ev=["ownership"])
    w.snapshot("pilot-baseline", None)

    # ---------------- R2: AWS inventory import (batch input; replay is a no-op)
    batch = aws_batch(w)
    w.batch_r2 = batch
    rev = w.begin("import", "import", IMPORTER, "aws-config (synthetic export)", "AWS inventory import (synthetic)",
                  change_reference="CHG-SYN-0002", input_hash=sha256_of(batch))
    apply_plan(w, batch)

    # ---------------- R3: steward rename and ownership change
    w.begin("steward_edit", "api", STEWARD, "atlas-api", "Rename after product renaming; move underwriting ownership to the data team",
            change_reference="CHG-SYN-0003")
    w.update_entity("svc.quote", ["steward-rename"], display_name="Quotation Service")
    w.retire_rel("owns:policy>app.underwriting", ["steward-owner"])
    rel("owns:data>app.underwriting", "OWNS", "team.data", "app.underwriting", ev=["steward-owner"], attrs={"ownership_role": "accountable"})
    w.retire_rel("stores:svc.notify>ds.documents", ["steward-owner"])

    # ---------------- R4: steward retires a relationship (a mistake, reverted in R5)
    w.begin("steward_edit", "api", STEWARD, "atlas-api", "Claims API no longer reads policy records", change_reference="CHG-SYN-0004")
    w.retire_rel("reads:svc.claims-api>ds.policies", ["steward-retire"])

    # ---------------- R5: revert R4
    w.begin("revert", "api", STEWARD, "atlas-api", "Revert CHG-SYN-0004: the read dependency still exists", change_reference="CHG-SYN-0005", reverts=4)
    w.revert(4)
    w.snapshot("after-revert", None)

    # ---------------- R6: provider-specific reclassification (neutral data store -> azure.sql_database), same entity ID
    w.begin("steward_edit", "api", STEWARD, "atlas-api", "Link the billing database to its ARM resource and re-type it", change_reference="CHG-SYN-0006")
    w.ev("arg-billing")
    w.identity("az.db-billing", "azure.arm", arm(SUB_PR, "rg-claims-prod", "Microsoft.Sql", "servers", "sql-claims-prod", "databases", "sqldb-billing"), "steward")
    w.close_identity("az.db-billing", "source.arch-docs")   # azure.sql_database takes azure.arm only (ADR-0017 §2.2)
    w.retire_rel("contains:az.rg-plat-pr>az.db-billing", ["steward-link"])
    w.retype("az.db-billing", "azure.sql_database", ["steward-link", "arg-billing"], attributes={})
    w.add_existence_evidence("az.db-billing", "arg-billing")
    rel("contains:az.sql-pr>az.db-billing", "CONTAINS", "az.sql-pr", "az.db-billing", ev=["arg-billing"])
    w._new_version("entity_versions", "entity_id", w.ids["az.db-billing"], container_id=w.ids["az.sql-pr"])

    # ---------------- R7: taxonomy-aware migration (synthetic test-only 1.2.0-test.1): generic -> data store, same ID
    w.begin("migration", "migration", MIGRATOR, "taxonomy 1.2.0-test.1 (synthetic)", "Apply native type mapping bigquery Dataset -> data_store",
            tax_version=OVERLAY["taxonomy_version"])
    w.retype("gcp.bq", "infra.data_store", [], attributes={"store_kind": "other"})

    # ---------------- R8: a read that was not representable before R7
    w.begin("import", "import", IMPORTER, "IaC manifests: analytics (synthetic)", "Analytics IaC import (synthetic)", change_reference="CHG-SYN-0008",
            input_hash=sha256_of(b"iac-analytics"), tax_version=OVERLAY["taxonomy_version"])
    rel("reads:gcp.indexer>gcp.bq", "READS_FROM", "gcp.indexer", "gcp.bq", ev=["iac-analytics"])
    w.snapshot("head", None)
    return batch


def aws_batch(w: World) -> dict[str, Any]:
    acct_p, acct_u = "111111111111", "222222222222"

    def e(ref, type_key, name, ids, *, parent=None, env=None, native=None, attrs=None):
        d = {"ref": ref, "id": uuid7(20_000 + len(ents), f"{w.org_key}|aws|{ref}"), "type_key": type_key, "display_name": name,
             "lifecycle": "active", "provider": "aws", "native_type": native,
             "environment_scope": None if type_key == "infra.scope" else ("single" if env else "unknown"),
             "attributes": attrs or {}, "identities": [{"namespace": n, "original_key": k} for n, k in ids], "evidence_refs": ["aws-config"]}
        if type_key == "infra.scope":
            d["environment_scope"] = "unknown"
        if parent:
            d["parent"] = {"ref": parent}
        if env:
            d["environment"] = {"org_key": env}
        ents.append(d)

    ents: list[dict[str, Any]] = []
    e("aws-org", "infra.scope", "example-aws-org", [("source.aws-org", "o-exmp0001")], native="AWS::Organizations::Organization", attrs={"scope_kind": "organization"})
    e("aws-ou", "infra.scope", "claims", [("source.aws-org", "ou-exmp-claims")], parent="aws-org", native="AWS::Organizations::OrganizationalUnit",
      attrs={"scope_kind": "organizational_unit"})
    e("aws-acct-prod", "infra.scope", "rating-prod", [("aws.account", f"aws:{acct_p}")], parent="aws-ou", native="AWS::Organizations::Account",
      attrs={"scope_kind": "account"})
    e("aws-acct-uat", "infra.scope", "rating-nonprod", [("aws.account", f"aws:{acct_u}")], parent="aws-ou", native="AWS::Organizations::Account",
      attrs={"scope_kind": "account"})
    for env, acct, ref in [("ENV-PROD", acct_p, "prod"), ("ENV-UAT", acct_u, "uat")]:
        e(f"ecs-{ref}", "infra.cluster", f"rating-ecs-{ref}", [("aws.arn", f"arn:aws:ecs:eu-west-1:{acct}:cluster/rating-ecs-{ref}")],
          parent=f"aws-acct-{ref}", env=env, native="AWS::ECS::Cluster", attrs={"cluster_kind": "ecs", "location": "eu-west-1"})
        e(f"rating-svc-{ref}", "infra.workload", "rating-api-svc", [("aws.arn", f"arn:aws:ecs:eu-west-1:{acct}:service/rating-ecs-{ref}/rating-api-svc")],
          parent=f"ecs-{ref}", env=env, native="AWS::ECS::Service", attrs={"workload_kind": "container_service"})
        e(f"rating-api-{ref}", "infra.api_endpoint", "rating-api", [("aws.arn", f"arn:aws:apigateway:eu-west-1::/restapis/rating{ref}exmp")],
          parent=f"aws-acct-{ref}", env=env, native="AWS::ApiGateway::RestApi")
    e("quote-consumer", "infra.workload", "quote-events-consumer", [("aws.arn", f"arn:aws:ecs:eu-west-1:{acct_p}:service/rating-ecs-prod/quote-events-consumer")],
      parent="ecs-prod", env="ENV-PROD", native="AWS::ECS::Service", attrs={"workload_kind": "container_service"})
    e("refresh-fn", "infra.workload", "rate-refresh-fn", [("aws.arn", f"arn:aws:lambda:eu-west-1:{acct_p}:function:rate-refresh-fn")],
      parent="aws-acct-prod", env="ENV-PROD", native="AWS::Lambda::Function", attrs={"workload_kind": "function"})
    e("rating-tables", "infra.resource", "rating-tables", [("aws.arn", f"arn:aws:dynamodb:eu-west-1:{acct_p}:table/rating-tables")],
      parent="aws-acct-prod", env="ENV-PROD", native="AWS::DynamoDB::Table")
    e("cdn", "infra.resource", "rating-cdn", [("aws.arn", f"arn:aws:cloudfront::{acct_p}:distribution/EXMP0001")],
      parent="aws-acct-prod", env="ENV-PROD", native="AWS::CloudFront::Distribution")

    def r(ref, rel_type, frm, to, attrs=None):
        rels.append({"ref": ref, "id": uuid7(21_000 + len(rels), f"{w.org_key}|aws-rel|{ref}"), "rel_type": rel_type, "from": frm, "to": to,
                     "attributes": attrs or {}, "evidence_refs": ["aws-config"]})

    rels: list[dict[str, Any]] = []
    ref = lambda x: {"ref": x}  # noqa: E731
    org = lambda k: {"org_key": k}  # noqa: E731
    ident = lambda ns, k: {"identity": {"namespace": ns, "original_key": k}}  # noqa: E731
    r("deploy-rating-api-prod", "DEPLOYED_AS", org("API-RATING"), ref("rating-api-prod"), {"deployment_role": "primary"})
    r("deploy-rating-api-uat", "DEPLOYED_AS", org("API-RATING"), ref("rating-api-uat"), {"deployment_role": "primary"})
    r("gw-prod", "CONNECTS_TO", ref("rating-api-prod"), ref("rating-svc-prod"), {"connectivity_kind": "gateway_backend"})
    r("gw-uat", "CONNECTS_TO", ref("rating-api-uat"), ref("rating-svc-uat"), {"connectivity_kind": "gateway_backend"})
    r("consumer-sub", "SUBSCRIBES_TO", ref("quote-consumer"),
      ident("gcp.resource_name", "//pubsub.googleapis.com/projects/claims-events-prod/topics/document-indexed"), {"subscription_name": "quote-consumer-sub"})
    r("fn-calls-api", "CONSUMES_API", ref("refresh-fn"), ref("rating-api-prod"))
    r("fn-to-cdn", "CONNECTS_TO", ref("refresh-fn"), ref("cdn"), {"connectivity_kind": "configured_endpoint"})
    # an imperfect observation: reading a resource with no data-store category is not representable; reported, never stored
    r("svc-reads-tables", "READS_FROM", ref("rating-svc-prod"), ref("rating-tables"))
    # evidenced cross-provider: the Azure UAT BFF's configuration names the AWS endpoint (one-sided evidence)
    r("azure-uat-bff-calls-aws", "CONSUMES_API",
      ident("k8s.uid", f"azure.arm:{arm(SUB_NP, 'rg-platform-nonprod', 'Microsoft.ContainerService', 'managedClusters', 'aks-nonprod')}#{w_uid(w, 'wl.claims-bff.uat')}"),
      ref("rating-api-prod"))
    return {"batch_format": "atlas.import-batch.v1", "org_key": w.org_key, "source_ref": "aws-config (synthetic export)", "channel": "import",
            "taxonomy_version": TAXONOMY_VERSION, "reason": "AWS inventory import (synthetic)", "change_reference": "CHG-SYN-0002",
            "evidence": [{"ref": "aws-config", "kind": "provider_configuration", "source_ref": "aws-config (synthetic export)",
                          "artifact_ref": "synthetic://aws/config/inventory-2026-10-01.json", "artifact_hash": sha256_of(f"{w.org_key}|aws-config".encode()),
                          "method": "export:aws-config:v1", "confidence": 1.0, "observed_at": "2026-10-01T06:00:00Z"}],
            "entities": ents, "relationships": rels}


def w_uid(w: World, key: str) -> str:
    for i in w.t["external_identities"]:
        if i["entity_id"] == w.ids[key] and i["namespace"] == "k8s.uid":
            return i["original_key"].rsplit("#", 1)[1]
    raise KeyError(key)


def apply_plan(w: World, batch: dict[str, Any]) -> None:
    """Apply an import batch to the world as the loader would: one change set with exactly the plan's differences."""
    ds = Dataset({"organizations": [w.org], **w.t})
    st = as_of(ds, w.org_id, w.rev - 1)
    plan = plan_batch(w.T(), batch, st)
    w.last_plan = plan
    evkey = batch["evidence"][0]["ref"]
    for d in plan.new_entities:
        parent_key = next((k for k, v in w.ids.items() if v == d["container_id"]), None) if d["container_id"] else None
        env_key = next((k for k, v in w.ids.items() if v == d["environment_id"]), None) if d["environment_id"] else None
        key = f"aws.{d['ref']}"
        w.entity(key, d["type_key"], d["display_name"], [evkey], env=env_key if d["environment_scope"] == "single" else None,
                 scope=d["environment_scope"], parent=parent_key, provider=d["provider"], native=d["native_type"], attrs=d["attributes"],
                 ids=[(i["namespace"], i["original_key"]) for i in d["identities"]], eid=d["entity_id"])
    for r in plan.new_relationships:
        fk = next(k for k, v in w.ids.items() if v == r["from_id"])
        tk = next(k for k, v in w.ids.items() if v == r["to_id"])
        w.rel(f"aws-rel:{r['id']}", r["rel_type"], fk, tk, ev=[evkey], attrs=r["attributes"], rid=r["id"])
    if plan.changed_entities or plan.changed_relationships:
        raise ValueError("fixture R2 batch is expected to create facts only")


# --------------------------------------------------------------------------- org B (similar names, separate identities)


def build_org_b(w: World) -> None:
    w.evidence("arg-b", "provider_configuration", "azure-resource-graph (synthetic export)", "export:arg:v1", "synthetic://azure/arg/subsidiary-2026-09-30.json", "2026-09-30T06:00:00Z")
    w.evidence("doc-b", "documentation", "architecture document: subsidiary portal (synthetic)", "import:document:v1", "synthetic://docs/subsidiary-portal.md", "2026-09-01T12:00:00Z")
    w.begin("fixture_load", "fixture_cli", LOADER, "fixture:canonical-golden-v1", "Golden fixture baseline, second organization (synthetic)")
    ent = w.entity
    ent("env.prod", "core.environment", "PROD", ["doc-b"], attrs={"environment_kind": "prod"}, ids=[("org.key", "ENV-PROD")])
    ent("team.claims", "core.team", "Claims Team", ["doc-b"], ids=[("org.key", "TEAM-CLAIMS")])
    ent("app.claims-portal", "core.application", "Claims Portal", ["doc-b"], attrs={"org_key": "APP-0101"}, ids=[("org.key", "APP-0101")])
    ent("svc.claims-portal-bff", "core.service", "Claims Portal BFF", ["doc-b"], parent="app.claims-portal")
    # same Azure tenant GUID as organization A (a shared provider arrangement): a separate entity here
    ent("az.tenant", "azure.tenant", "Example Tenant (synthetic)", ["arg-b"], provider="azure", ids=[("azure.tenant_id", TENANT)])
    ent("az.sub", "azure.subscription", "sub-claims-prod", ["arg-b"], provider="azure", parent="az.tenant", env="env.prod",
        ids=[("azure.subscription_id", SUB_B), ("azure.arm", arm(SUB_B))])
    ent("az.rg", "azure.resource_group", "rg-claims-prod", ["arg-b"], parent="az.sub", env="env.prod", attrs={"location": "westeurope"},
        ids=[("azure.arm", arm(SUB_B, "rg-claims-prod"))])
    ent("az.app", "azure.app_service", "app-claims-portal-prod", ["arg-b"], parent="az.rg", env="env.prod", attrs={"location": "westeurope", "site_kind": "app"},
        ids=[("azure.arm", arm(SUB_B, "rg-claims-prod", "Microsoft.Web", "sites", "app-claims-portal-prod"))])
    # same AWS account key as organization A: unique per organization only
    ent("aws.acct", "infra.scope", "rating-prod", ["doc-b"], provider="aws", native="AWS::Organizations::Account", attrs={"scope_kind": "account"},
        ids=[("aws.account", "aws:111111111111")])
    ent("aws.api", "infra.api_endpoint", "rating-api", ["doc-b"], parent="aws.acct", native="AWS::ApiGateway::RestApi", env="env.prod",
        ids=[("aws.arn", "arn:aws:apigateway:eu-west-1::/restapis/ratingprodexmp")])
    w.rel("deployed", "DEPLOYED_AS", "svc.claims-portal-bff", "az.app", ev=["arg-b"], attrs={"deployment_role": "primary"})
    w.rel("consumes", "CONSUMES_API", "az.app", "aws.api", ev=["doc-b"])
    w.rel("owns", "OWNS", "team.claims", "app.claims-portal", ev=["doc-b"])
    w.snapshot("baseline", None)


# --------------------------------------------------------------------------- output


def build(out: Path) -> None:
    base = Taxonomy.load()
    if base.version != TAXONOMY_VERSION:
        raise SystemExit(f"generator targets taxonomy {TAXONOMY_VERSION}, artifact is {base.version}")
    taxes = {base.version: base, OVERLAY["taxonomy_version"]: base.with_overlay(OVERLAY)}
    a = World(taxes, "default", "Example Insurance Group (synthetic)", 0)
    batch = build_org_a(a)
    b = World(taxes, "example-subsidiary", "Example Subsidiary (synthetic)", 50_000)
    build_org_b(b)

    tables: dict[str, list[dict[str, Any]]] = {"organizations": [a.org, b.org]}
    for t in TABLES:
        if t != "organizations":
            tables[t] = a.t[t] + b.t[t]
    ds = Dataset(tables, TRUST_POLICY)
    for snap in tables["graph_snapshots"]:
        snap["graph_hash"] = graph_hash(as_of(ds, snap["org_id"], snap["revision"]))
    for cs in tables["change_sets"]:
        if cs["kind"] == "fixture_load":
            created = sorted(canonical_json(v) for v in tables["entity_versions"] + tables["relationship_versions"]
                             if v["org_id"] == cs["org_id"] and v["revision_from"] == cs["revision"])
            cs["input_hash"] = sha256_of(created)

    out.mkdir(parents=True, exist_ok=True)
    (out / "inputs").mkdir(exist_ok=True)
    keyfn = {"organizations": lambda r: r["key"], "change_sets": lambda r: (r["org_id"], r["revision"]),
             "entity_versions": lambda r: (r["org_id"], r["entity_id"], r["revision_from"]),
             "relationship_versions": lambda r: (r["org_id"], r["relationship_id"], r["revision_from"])}
    files = []
    for t, schema in TABLES.items():
        rows = sorted(tables[t], key=keyfn.get(t, lambda r: (r["org_id"], r["id"])))
        text = dump_records(rows)
        (out / f"{t}.json").write_text(text, encoding="utf-8")
        files.append({"path": f"{t}.json", "schema": f"urn:atlas:schema:canonical:{schema}:v1", "records": len(rows), "sha256": sha256_of(text.encode())})

    def write(name: str, value: Any, schema: str | None) -> None:
        text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        (out / name).write_text(text, encoding="utf-8")
        files.append({"path": name, "schema": schema, "records": len(value) if isinstance(value, list) else 1, "sha256": sha256_of(text.encode())})

    write(OVERLAY_NAME, OVERLAY, "urn:atlas:schema:canonical:taxonomy-overlay:v1")
    write(TRUST_POLICY_FILE, TRUST_POLICY, None)
    write("inputs/aws-inventory.r2.json", batch, "urn:atlas:schema:canonical:import-batch:v1")
    plan = a.last_plan
    write("inputs/aws-inventory.r2.expected-report.json", {
        "batch": "inputs/aws-inventory.r2.json", "org_key": "default",
        "first_apply": {"against_revision": 1, "creates_revision": 2, "new_entities": len(plan.new_entities),
                        "new_relationships": len(plan.new_relationships), "changed_entities": 0, "changed_relationships": 0},
        "replay": {"against_revision": 2, "change_set": None, "new_entities": 0, "new_relationships": 0},
        "rejected": [{"ref": r["item"].get("ref"), "rule": r["rule"], "reasons": r["reasons"]} for r in plan.rejected],
    }, None)
    expected = []
    for org in tables["organizations"]:
        for rev in range(1, ds.head(org["id"]) + 1):
            st = as_of(ds, org["id"], rev)
            expected.append({"org_key": org["key"], "revision": rev, "entities": len(st.entities), "relationships": len(st.relationships),
                             "graph_hash": graph_hash(st)})
    write("expected-as-of.json", expected, None)
    from canonical_rules import advisory_findings, advisory_summary
    write("expected-findings.json", {"hard": 0, "domain": 0, "advisory": advisory_summary(advisory_findings(ds, taxes))}, None)
    manifest = {"fixture": FIXTURE, "fixture_version": FIXTURE_VERSION, "generator": "tools/generate_golden.py",
                "taxonomy_versions": sorted(taxes), "files": files, "counts": counts(ds, taxes)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def counts(ds: Dataset, taxes: dict[str, Taxonomy]) -> dict[str, Any]:
    res: dict[str, Any] = {"organizations": len(ds.tables["organizations"]), "entities": len(ds.tables["entities"]),
                           "relationships": len(ds.tables["relationships"]), "change_sets": len(ds.tables["change_sets"]),
                           "by_org": {}}
    for org in ds.tables["organizations"]:
        st = as_of(ds, org["id"], ds.head(org["id"]))
        by_provider: dict[str, int] = {}
        by_category: dict[str, int] = {}
        by_env: dict[str, int] = {}
        envname = {i: v["display_name"] for i, v in st.entities.items() if v["type_key"] == "core.environment"}
        for v in st.entities.values():
            by_provider[v["provider"] or "logical"] = by_provider.get(v["provider"] or "logical", 0) + 1
            by_category[v["category"]] = by_category.get(v["category"], 0) + 1
            if v["environment_scope"] == "single":
                by_env[envname[v["environment_id"]]] = by_env.get(envname[v["environment_id"]], 0) + 1
            elif v["environment_scope"]:
                by_env[v["environment_scope"]] = by_env.get(v["environment_scope"], 0) + 1
        by_rel: dict[str, int] = {}
        for r in st.relationships.values():
            by_rel[r["rel_type"]] = by_rel.get(r["rel_type"], 0) + 1
        res["by_org"][org["key"]] = {
            "head_revision": ds.head(org["id"]), "entities_at_head": len(st.entities), "relationships_at_head": len(st.relationships),
            "by_provider": dict(sorted(by_provider.items())), "by_category": dict(sorted(by_category.items())),
            "by_environment_scope": dict(sorted(by_env.items())), "by_relationship_type": dict(sorted(by_rel.items())),
            "cross_environment": sum(r["version"]["cross_environment"] for r in st.relationships.values()),
            "cross_provider": sum(r["version"]["cross_provider"] for r in st.relationships.values()),
            "shared_endpoint": sum(r["version"]["shared_endpoint"] for r in st.relationships.values())}
    return res


def main(argv: list[str]) -> int:
    out = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUT
    build(out)
    print(f"generated {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
