"""Validation rules for the canonical graph contracts (ATLAS-002 CP2). CI tooling, never deployed.

Every rule has an ID and a class (contracts/canonical-validation-rules.md):

* HARD      identity, referential integrity, organization isolation, revision consistency, security;
* DOMAIN    taxonomy and graph consistency required before publication;
* ADVISORY  architecture and data-quality findings; reported, never blocking.
"""

from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from canonical_model import (
    ADVISORY, DOMAIN, HARD, SCHEMA_DIR, TABLES, Dataset, Finding, NormalizationError, Taxonomy, as_of, check_pair,
    discriminator_of, graph_hash, normalize_identity, plan_batch, relationship_flags, sha256_of, trust_compatible, valid_at,
)



# --------------------------------------------------------------------------- schemas


@lru_cache(maxsize=1)
def load_registry() -> tuple[Registry, dict[str, dict[str, Any]]]:
    schemas = {}
    for p in sorted(SCHEMA_DIR.glob("*.v1.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        schemas[p.name.removesuffix(".v1.json")] = s
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas.values())
    return registry, schemas


@lru_cache(maxsize=None)
def validator_for(name: str) -> Draft202012Validator:
    registry, schemas = load_registry()
    return Draft202012Validator(schemas[name], registry=registry)


def schema_findings(name: str, instance: Any, label: str) -> list[Finding]:
    v = validator_for(name)
    return [Finding("H-01", HARD, f"{label}: {e.message} at /{'/'.join(map(str, e.absolute_path))}") for e in v.iter_errors(instance)]


# --------------------------------------------------------------------------- taxonomy self-checks


def taxonomy_findings(tax: Taxonomy) -> list[Finding]:
    f: list[Finding] = []
    doc = tax.doc
    f += schema_findings("taxonomy", doc, "taxonomy")
    if len(tax.types) != len(doc["entity_types"]):
        f.append(Finding("T-01", HARD, "duplicate type_key"))
    if len(tax.rels) != len(doc["relationship_types"]):
        f.append(Finding("T-01", HARD, "duplicate rel_type"))
    for t in doc["entity_types"]:
        k = t["type_key"]
        if t["kind"] == "physical" and t["category"] not in tax.categories:
            f.append(Finding("T-02", HARD, f"{k}: unknown category {t['category']}"))
        if t["kind"] == "logical" and t["category"] != k:
            f.append(Finding("T-02", HARD, f"{k}: a logical type is its own category"))
        for p in t["containment_parents"]:
            if not (p in tax.types or p == "category:physical" or (p.startswith("category:") and p.split(":", 1)[1] in tax.categories)):
                f.append(Finding("T-03", HARD, f"{k}: unknown containment parent {p}"))
        for a, spec in t["attribute_enums"].items():
            try:
                tax.enum_values(spec)
            except KeyError:
                f.append(Finding("T-04", HARD, f"{k}.{a}: unknown enumeration {spec}"))
        for ns in t["identity_namespaces"]:
            if ns not in tax.namespaces and ns not in ("provider_namespace",):
                f.append(Finding("T-05", HARD, f"{k}: unknown identity namespace {ns}"))
        if t["provider"] not in (None, "any", "@cluster") and t["provider"] not in tax.providers:
            f.append(Finding("T-06", HARD, f"{k}: unknown provider {t['provider']}"))
    for r in doc["relationship_types"]:
        for pair in r["pairs"]:
            for side in ("from", "to", "to_exclude"):
                for ref in pair.get(side, []):
                    if ref.startswith("@"):
                        continue
                    ok = ref == "*" or ref in tax.types or ref == "category:physical" or (ref.startswith("category:") and ref.split(":", 1)[1] in tax.categories)
                    if not ok:
                        f.append(Finding("T-07", HARD, f"{r['rel_type']}: unknown endpoint reference {ref}"))
        for a, spec in r["attribute_enums"].items():
            try:
                tax.enum_values(spec)
            except KeyError:
                f.append(Finding("T-04", HARD, f"{r['rel_type']}.{a}: unknown enumeration {spec}"))
        if r["status"] == "reserved" and r["pairs"]:
            f.append(Finding("T-08", HARD, f"{r['rel_type']}: reserved types have no pairs"))
    # type-level MEMBER_OF graph must be acyclic (ADR-0017 §3.2)
    edges = defaultdict(set)
    for pair in tax.rels["MEMBER_OF"]["pairs"]:
        for a in tax.types:
            if tax.matches(a, pair["from"]):
                for b in tax.types:
                    if tax.matches(b, pair["to"]):
                        edges[a].add(b)
    if _has_cycle(edges):
        f.append(Finding("T-09", HARD, "type-level MEMBER_OF graph has a cycle"))
    cedges = defaultdict(set)
    for k, t in tax.types.items():
        for p in tax.types:
            if p != k and tax.matches(p, t["containment_parents"]) and not (t["self_nesting"] and p == k):
                cedges[p].add(k)
    for k, t in tax.types.items():
        if k in t["containment_parents"] and not t["self_nesting"]:
            f.append(Finding("T-10", HARD, f"{k}: self-containment without self_nesting"))
    if _has_cycle({a: {b for b in bs if not (a == "infra.resource" or b == "infra.resource")} for a, bs in cedges.items()}):
        f.append(Finding("T-10", HARD, "type-level CONTAINS graph has a cycle beyond declared self-nesting and the generic fallback"))
    for prov, items in doc["native_type_mappings"].items():
        if prov not in tax.providers:
            f.append(Finding("T-06", HARD, f"mapping for unknown provider {prov}"))
        for m in items:
            if m["category"] not in tax.categories:
                f.append(Finding("T-02", HARD, f"mapping {m['native_type']}: unknown category"))
    for prov in doc["provider_scope_rules"]:
        if prov not in tax.providers:
            f.append(Finding("T-06", HARD, f"scope rules for unknown provider {prov}"))
    for ns in doc["identity_namespaces"]:
        if ns["provider"] not in (None, "@cluster") and ns["provider"] not in tax.providers:
            f.append(Finding("T-06", HARD, f"namespace {ns['namespace']}: unknown provider"))
        if ns["status"] in ("implemented", "validation_only") and not ns["normalization_rule"]:
            f.append(Finding("T-05", HARD, f"namespace {ns['namespace']}: usable namespace without a rule"))
        if ns["status"] in ("planned", "reserved") and ns["normalization_rule"]:
            f.append(Finding("T-05", HARD, f"namespace {ns['namespace']}: planned/reserved namespace must not define a rule"))
    return f


def _has_cycle(edges: dict[str, set[str]]) -> bool:
    state: dict[str, int] = {}

    def visit(n: str) -> bool:
        state[n] = 1
        for m in edges.get(n, ()):
            if state.get(m) == 1 or (state.get(m) is None and visit(m)):
                return True
        state[n] = 2
        return False

    return any(state.get(n) is None and visit(n) for n in list(edges))


# --------------------------------------------------------------------------- fixture rules


class Index:
    def __init__(self, ds: Dataset) -> None:
        t = ds.tables
        self.ds = ds
        self.entity_org = {e["id"]: e["org_id"] for e in t["entities"]}
        self.rel = {r["id"]: r for r in t["relationships"]}
        self.ev = {e["id"]: e for e in t["evidence"]}
        self.ev_versions: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for v in t["entity_versions"]:
            self.ev_versions[v["entity_id"]].append(v)
        self.rv_versions: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for v in t["relationship_versions"]:
            self.rv_versions[v["relationship_id"]].append(v)
        for d in (self.ev_versions, self.rv_versions):
            for vs in d.values():
                vs.sort(key=lambda v: v["revision_from"])
        self.cs = {(c["org_id"], c["revision"]): c for c in t["change_sets"]}
        self.heads = {o["id"]: ds.head(o["id"]) for o in t["organizations"]}

    def entity_at(self, eid: str, rev: int) -> dict[str, Any] | None:
        return next((v for v in self.ev_versions.get(eid, []) if valid_at(v, rev)), None)


def tax_for(taxes: dict[str, Taxonomy], version: str, label: str, f: list[Finding]) -> Taxonomy | None:
    tax = taxes.get(version)
    if tax is None:
        f.append(Finding("D-01", DOMAIN, f"{label}: unknown taxonomy version {version}"))
    return tax


def fixture_findings(ds: Dataset, taxes: dict[str, Taxonomy]) -> list[Finding]:
    f: list[Finding] = []
    t = ds.tables
    for table, schema in TABLES.items():
        for i, rec in enumerate(t[table]):
            f += schema_findings(schema, rec, f"{table}[{i}]")
    ix = Index(ds)
    orgs = {o["id"] for o in t["organizations"]}
    _hard_identity_and_refs(ds, ix, orgs, f)
    _hard_revisions(ds, ix, f)
    _hard_identities(ds, ix, taxes, f)
    _domain_entities(ds, ix, taxes, f)
    _domain_relationships(ds, ix, taxes, f)
    _per_revision(ds, ix, taxes, f)
    _domain_change_sets(ds, ix, taxes, f)
    return f


def _hard_identity_and_refs(ds: Dataset, ix: Index, orgs: set[str], f: list[Finding]) -> None:
    t = ds.tables
    for table, key in [("organizations", "id"), ("entities", "id"), ("relationships", "id"), ("evidence", "id"), ("fact_assertions", "id"),
                       ("external_identities", "id"), ("graph_snapshots", "id")]:
        ids = [r[key] for r in t[table]]
        if len(ids) != len(set(ids)):
            f.append(Finding("H-02", HARD, f"{table}: duplicate IDs"))
    for table in TABLES:
        if table == "organizations":
            continue
        for r in t[table]:
            if r["org_id"] not in orgs:
                f.append(Finding("H-04", HARD, f"{table}: unknown organization {r['org_id']}"))

    def same_org(label: str, org: str, ref: str | None, where: dict[str, str]) -> None:
        if ref is None:
            return
        if ref not in where:
            f.append(Finding("H-04", HARD, f"{label}: reference {ref} does not resolve"))
        elif where[ref] != org:
            f.append(Finding("H-03", HARD, f"{label}: reference {ref} crosses organizations"))

    for v in t["entity_versions"]:
        lbl = f"entity_version {v['entity_id']}@{v['revision_from']}"
        for fld in ("entity_id", "merged_into", "environment_id", "container_id"):
            same_org(lbl + f".{fld}", v["org_id"], v[fld], ix.entity_org)
    for r in t["relationships"]:
        for fld in ("from_id", "to_id"):
            same_org(f"relationship {r['id']}.{fld}", r["org_id"], r[fld], ix.entity_org)
        if r["from_id"] == r["to_id"]:
            f.append(Finding("H-09", HARD, f"relationship {r['id']}: self-relationship"))
    rel_org = {r["id"]: r["org_id"] for r in t["relationships"]}
    for v in t["relationship_versions"]:
        same_org(f"relationship_version {v['relationship_id']}", v["org_id"], v["relationship_id"], rel_org)
        same_org(f"relationship_version {v['relationship_id']}.environment_id", v["org_id"], v["environment_id"], ix.entity_org)
    for i in t["external_identities"]:
        same_org(f"identity {i['id']}", i["org_id"], i["entity_id"], ix.entity_org)
    ev_org = {e["id"]: e["org_id"] for e in t["evidence"]}
    for a in t["fact_assertions"]:
        same_org(f"assertion {a['id']}.evidence_id", a["org_id"], a["evidence_id"], ev_org)
        same_org(f"assertion {a['id']}.fact_id", a["org_id"], a["fact_id"], ix.entity_org if a["fact_kind"] == "entity" else rel_org)
        ev = ix.ev.get(a["evidence_id"])
        if ev and ev["kind"] != a["evidence_kind"]:
            f.append(Finding("H-12", HARD, f"assertion {a['id']}: evidence_kind differs from its evidence"))
        if ev and ev["change_revision"] > a["revision_from"]:
            f.append(Finding("H-12", HARD, f"assertion {a['id']}: evidence recorded after the assertion"))


def _hard_revisions(ds: Dataset, ix: Index, f: list[Finding]) -> None:
    t = ds.tables
    by_org = defaultdict(list)
    for c in t["change_sets"]:
        by_org[c["org_id"]].append(c["revision"])
    for org, revs in by_org.items():
        if sorted(revs) != list(range(1, len(revs) + 1)):
            f.append(Finding("H-05", HARD, f"organization {org}: revisions are not gap-free from 1"))

    def rev_ok(label: str, org: str, rev: int | None) -> None:
        if rev is not None and (org, rev) not in ix.cs:
            f.append(Finding("H-05", HARD, f"{label}: revision {rev} has no change set"))

    for table in ("entity_versions", "relationship_versions", "external_identities", "fact_assertions"):
        for r in t[table]:
            rev_ok(table, r["org_id"], r["revision_from"])
            rev_ok(table, r["org_id"], r["revision_to"])
            if r["revision_to"] is not None and r["revision_to"] <= r["revision_from"]:
                f.append(Finding("H-05", HARD, f"{table}: revision_to <= revision_from"))
    for c in t["change_sets"]:
        rev_ok("change_set.reverts_revision", c["org_id"], c["reverts_revision"])
        if c["reverts_revision"] is not None and c["reverts_revision"] >= c["revision"]:
            f.append(Finding("H-05", HARD, f"change set {c['revision']} reverts a later revision"))
    for e in t["evidence"]:
        rev_ok("evidence", e["org_id"], e["change_revision"])
    for s in t["graph_snapshots"]:
        rev_ok("graph_snapshot", s["org_id"], s["revision"])
    for table, versions, created in (("entity", ix.ev_versions, t["entities"]), ("relationship", ix.rv_versions, t["relationships"])):
        for rec in created:
            vs = versions.get(rec["id"], [])
            if not vs:
                f.append(Finding("H-06", HARD, f"{table} {rec['id']}: no versions"))
                continue
            if vs[0]["revision_from"] != rec["created_revision"]:
                f.append(Finding("H-05", HARD, f"{table} {rec['id']}: created_revision differs from its first version"))
            if sum(v["revision_to"] is None for v in vs) != 1 or vs[-1]["revision_to"] is not None:
                f.append(Finding("H-06", HARD, f"{table} {rec['id']}: exactly one current version required"))
            for a, b in zip(vs, vs[1:]):
                if a["revision_to"] != b["revision_from"]:
                    f.append(Finding("H-06", HARD, f"{table} {rec['id']}: versions overlap or leave a gap"))


def _hard_identities(ds: Dataset, ix: Index, taxes: dict[str, Taxonomy], f: list[Finding]) -> None:
    tax = taxes["1.0.0"]
    spans = defaultdict(list)
    for i in ds.tables["external_identities"]:
        try:
            key, parts, rule = normalize_identity(tax, i["namespace"], i["original_key"])
        except NormalizationError as exc:
            f.append(Finding("H-08", HARD, f"identity {i['id']}: {exc}"))
            continue
        if key != i["normalized_key"] or rule != i["normalization_version"]:
            f.append(Finding("H-08", HARD, f"identity {i['id']}: normalized_key/normalization_version do not follow rule {rule}"))
        if parts != i["key_parts"]:
            f.append(Finding("H-08", HARD, f"identity {i['id']}: key_parts differ from the rule's parse"))
        spans[(i["org_id"], i["namespace"], i["normalized_key"])].append(i)
    for key, items in spans.items():
        items.sort(key=lambda r: r["revision_from"])
        for a, b in zip(items, items[1:]):
            if a["revision_to"] is None or a["revision_to"] > b["revision_from"]:
                f.append(Finding("H-07", HARD, f"identity {key[1]}:{key[2]} is bound twice at the same time in one organization"))
    seen = set()
    for r in ds.tables["relationships"]:
        k = (r["org_id"], r["rel_type"], r["from_id"], r["to_id"], r["discriminator"])
        if k in seen:
            f.append(Finding("H-09", HARD, f"relationship {r['id']}: duplicate (rel_type, from, to, discriminator)"))
        seen.add(k)


def _domain_entities(ds: Dataset, ix: Index, taxes: dict[str, Taxonomy], f: list[Finding]) -> None:
    for v in ds.tables["entity_versions"]:
        lbl = f"entity {v['entity_id']}@{v['revision_from']}"
        tax = tax_for(taxes, v["taxonomy_version"], lbl, f)
        if tax is None:
            continue
        t = tax.type_def(v["type_key"])
        if t is None:
            f.append(Finding("D-01", DOMAIN, f"{lbl}: unknown type {v['type_key']} in taxonomy {tax.version}"))
            continue
        if v["record_state"] != "present":
            continue
        for a in t["required_attributes"]:
            if a not in v["attributes"]:
                f.append(Finding("D-01", DOMAIN, f"{lbl}: missing required attribute {a}"))
        for a, spec in t["attribute_enums"].items():
            if a in v["attributes"] and v["attributes"][a] not in tax.enum_values(spec):
                f.append(Finding("D-01", DOMAIN, f"{lbl}: {a}={v['attributes'][a]!r} not in vocabulary"))
        if v["category"] != t["category"]:
            f.append(Finding("D-02", DOMAIN, f"{lbl}: category {v['category']} differs from its type's {t['category']}"))
        if t["kind"] == "logical":
            if v["provider"] is not None or v["native_type"] is not None:
                f.append(Finding("D-02", DOMAIN, f"{lbl}: logical types have no provider or native_type"))
        else:
            if v["provider"] not in tax.providers:
                f.append(Finding("D-02", DOMAIN, f"{lbl}: unknown or missing provider {v['provider']}"))
            if not v["native_type"] and v["type_key"] != "azure.tenant":   # ADR-0017 §2.2: the tenant has no ARM type
                f.append(Finding("D-02", DOMAIN, f"{lbl}: physical entities need native_type"))
            if t["provider"] not in ("any", "@cluster") and v["provider"] != t["provider"]:
                f.append(Finding("D-02", DOMAIN, f"{lbl}: {v['type_key']} is a {t['provider']} type"))
            if "native_type" in t and v["native_type"] != t["native_type"]:
                f.append(Finding("D-02", DOMAIN, f"{lbl}: native_type must be {t['native_type']}"))
            if v["provider"] in tax.platform_providers and not v["attributes"].get("platform"):
                f.append(Finding("D-02", DOMAIN, f"{lbl}: provider {v['provider']} requires a platform attribute"))
            if t["provider"] == "@cluster" and v["container_id"]:
                parent = ix.entity_at(v["container_id"], v["revision_from"])
                if parent and parent["provider"] != v["provider"]:
                    f.append(Finding("D-02", DOMAIN, f"{lbl}: Kubernetes objects take their cluster's provider"))
        scope = t["environment_scope"]
        if scope == "none" and v["environment_scope"] is not None:
            f.append(Finding("D-03", DOMAIN, f"{lbl}: {v['type_key']} is environment-neutral"))
        if scope == "required" and v["environment_scope"] is None:
            f.append(Finding("D-03", DOMAIN, f"{lbl}: environment scope required (single, shared or unknown)"))
        if v["environment_id"]:
            env = ix.entity_at(v["environment_id"], v["revision_from"])
            if env is None or env["type_key"] != "core.environment":
                f.append(Finding("D-03", DOMAIN, f"{lbl}: environment_id is not a core.environment"))
        allowed_ns = t["identity_namespaces"]
        for i in ds.tables["external_identities"]:
            if i["entity_id"] != v["entity_id"] or not valid_at(i, v["revision_from"]):
                continue
            ns = tax.namespaces.get(i["namespace"]) or (tax.namespaces["source.*"] if i["namespace"].startswith("source.") else None)
            ok = i["namespace"] in allowed_ns or (i["namespace"].startswith("source.") and "source.*" in allowed_ns) or \
                ("provider_namespace" in allowed_ns and ns is not None and ns["provider"] == v["provider"])
            if not ok:
                f.append(Finding("D-15", DOMAIN, f"{lbl}: identity namespace {i['namespace']} not allowed for {v['type_key']}"))
        if v["type_key"] == "infra.scope" and v["provider"] in tax.scope_rules:
            kinds = {s["scope_kind"]: s["parents"] for s in tax.scope_rules[v["provider"]]["scope_kinds"]}
            kind = v["attributes"].get("scope_kind")
            if kind not in kinds:
                f.append(Finding("D-16", DOMAIN, f"{lbl}: scope_kind {kind!r} not defined for provider {v['provider']}"))
            elif v["container_id"]:
                parent = ix.entity_at(v["container_id"], v["revision_from"])
                if parent and parent["type_key"] == "infra.scope" and parent["attributes"].get("scope_kind") not in kinds[kind]:
                    f.append(Finding("D-16", DOMAIN, f"{lbl}: {kind} cannot sit in {parent['attributes'].get('scope_kind')}"))
        kinds = {a["evidence_kind"] for a in ds.tables["fact_assertions"]
                 if a["fact_id"] == v["entity_id"] and a["field_path"] is None and valid_at(a, v["revision_from"])}
        if not kinds:
            f.append(Finding("D-12", DOMAIN, f"{lbl}: present fact without any existence evidence"))
        elif not trust_compatible(v["trust_state"], kinds):
            f.append(Finding("D-12", DOMAIN, f"{lbl}: trust_state {v['trust_state']} incompatible with evidence {sorted(kinds)}"))
    # re-typing transitions (ADR-0017 §2.4)
    for eid, vs in ix.ev_versions.items():
        for a, b in zip(vs, vs[1:]):
            if a["type_key"] == b["type_key"]:
                continue
            cs = ix.cs.get((b["org_id"], b["revision_from"]))
            tax = taxes.get(b["taxonomy_version"])
            if tax is None:
                continue
            automatic = (a["type_key"].startswith("infra.") and b["provider"] == a["provider"] and
                         tax.types[b["type_key"]].get("native_type") == a["native_type"] and not b["type_key"].startswith("infra.")) or \
                        (a["type_key"] == "infra.resource" and tax.mappings.get(a["provider"], {}).get(a["native_type"]) == tax.types[b["type_key"]]["category"]
                         and b["type_key"].startswith("infra."))
            if not automatic and cs and cs["kind"] not in ("steward_edit", "migration"):
                f.append(Finding("D-10", DOMAIN, f"entity {eid}: re-type {a['type_key']} -> {b['type_key']} needs a steward or migration change set"))
            if cs and cs["kind"] == "migration" and not automatic:
                f.append(Finding("D-10", DOMAIN, f"entity {eid}: a migration may only apply automatic re-typing"))


def _domain_relationships(ds: Dataset, ix: Index, taxes: dict[str, Taxonomy], f: list[Finding]) -> None:
    asserts = defaultdict(list)
    for a in ds.tables["fact_assertions"]:
        asserts[a["fact_id"]].append(a)
    for v in ds.tables["relationship_versions"]:
        r = ix.rel[v["relationship_id"]]
        lbl = f"relationship {r['id']} {r['rel_type']}@{v['revision_from']}"
        tax = tax_for(taxes, v["taxonomy_version"], lbl, f)
        if tax is None or v["record_state"] != "present":
            continue
        fv, tv = ix.entity_at(r["from_id"], v["revision_from"]), ix.entity_at(r["to_id"], v["revision_from"])
        if fv is None or tv is None:
            continue  # reported by H-10
        for reason in check_pair(tax, r["rel_type"], fv, tv, v["attributes"]):
            f.append(Finding("D-04", DOMAIN, f"{lbl}: {reason}"))
        if r["rel_type"] in tax.rels and discriminator_of(tax, r["rel_type"], v["attributes"]) != r["discriminator"]:
            f.append(Finding("H-09", HARD, f"{lbl}: discriminator differs from the attribute that defines it"))
        rel = tax.rels.get(r["rel_type"])
        kinds = {a["evidence_kind"] for a in asserts[r["id"]] if a["field_path"] is None and valid_at(a, v["revision_from"])}
        if rel:
            bad = kinds - set(rel["allowed_evidence_kinds"])
            if bad:
                f.append(Finding("D-05", DOMAIN, f"{lbl}: evidence kinds {sorted(bad)} not allowed"))
        if not kinds:
            f.append(Finding("D-12", DOMAIN, f"{lbl}: present fact without any existence evidence"))
        elif not trust_compatible(v["trust_state"], kinds):
            f.append(Finding("D-12", DOMAIN, f"{lbl}: trust_state {v['trust_state']} incompatible with evidence {sorted(kinds)}"))
        if r["rel_type"] == "DEPENDS_ON" and v["trust_state"] == "discovered":
            f.append(Finding("D-11", DOMAIN, f"{lbl}: DEPENDS_ON can never be discovered"))
        expected = relationship_flags(fv, tv)
        for k, val in expected.items():
            if v[k] != val:
                f.append(Finding("D-08", DOMAIN, f"{lbl}: {k} is {v[k]!r}, endpoints imply {val!r}"))
        if v["cross_environment"] and rel and rel["cross_environment_allowed"] is False:
            f.append(Finding("D-08", DOMAIN, f"{lbl}: {r['rel_type']} is never cross-environment"))
        if r["rel_type"] == "CONTAINS":
            pk = _arm_key(ds, r["from_id"], v["revision_from"])
            ck = _arm_key(ds, r["to_id"], v["revision_from"])
            if pk and ck and not ck.startswith(pk + "/"):
                f.append(Finding("D-06", DOMAIN, f"{lbl}: the child's ARM ID is not inside the parent's"))


def _arm_key(ds: Dataset, eid: str, rev: int) -> str | None:
    for i in ds.tables["external_identities"]:
        if i["entity_id"] == eid and i["namespace"] == "azure.arm" and valid_at(i, rev):
            return i["normalized_key"]
    return None


def _per_revision(ds: Dataset, ix: Index, taxes: dict[str, Taxonomy], f: list[Finding]) -> None:
    """Endpoint validity, containment and environment membership at every revision (ADR-0008 §5)."""
    for org, head in ix.heads.items():
        for rev in range(1, head + 1):
            st = as_of(ds, org, rev)
            parents = defaultdict(list)
            for rid, r in st.relationships.items():
                if r["from_id"] not in st.entities or r["to_id"] not in st.entities:
                    f.append(Finding("H-10", HARD, f"r{rev}: relationship {rid} has an endpoint that is not present"))
                if r["rel_type"] == "CONTAINS":
                    parents[r["to_id"]].append(r["from_id"])
            for child, ps in parents.items():
                if len(ps) > 1:
                    f.append(Finding("H-14", HARD, f"r{rev}: entity {child} has {len(ps)} containment parents"))
            for eid, v in st.entities.items():
                expected = parents.get(eid, [None])[0]
                if v["container_id"] != expected:
                    f.append(Finding("D-09", DOMAIN, f"r{rev}: entity {eid} container_id differs from its CONTAINS parent"))
                if v["environment_scope"] == "shared":
                    envs = [r for r in st.relationships.values() if r["rel_type"] == "MEMBER_OF" and r["from_id"] == eid
                            and st.entities.get(r["to_id"], {}).get("type_key") == "core.environment"]
                    if not envs:
                        f.append(Finding("D-03", DOMAIN, f"r{rev}: shared entity {eid} is a member of no environment"))
            # acyclic containment
            for start in parents:
                seen, cur = set(), start
                while cur in parents and cur not in seen:
                    seen.add(cur)
                    cur = parents[cur][0]
                if cur in seen:
                    f.append(Finding("H-14", HARD, f"r{rev}: containment cycle through {start}"))
                    break


def _domain_change_sets(ds: Dataset, ix: Index, taxes: dict[str, Taxonomy], f: list[Finding]) -> None:
    for c in ds.tables["change_sets"]:
        lbl = f"change set {c['org_id']}#{c['revision']}"
        a = c["actor"]
        tax = taxes["1.0.0"]
        an = tax.actor_namespaces.get(a["namespace"])
        if an is None or an["actor_kind"] != a["kind"]:
            f.append(Finding("H-11", HARD, f"{lbl}: actor namespace {a['namespace']} is not bound to kind {a['kind']}"))
        if c["channel"] in ("fixture_cli", "import", "connector") and a["kind"] != "service":
            f.append(Finding("D-13", DOMAIN, f"{lbl}: channel {c['channel']} must be attributed to a service identity"))
        if c["channel"] == "migration" and a["kind"] not in ("system", "service"):
            f.append(Finding("D-13", DOMAIN, f"{lbl}: migrations are attributed to a system or service identity"))
        if c["kind"] in ("steward_edit", "merge", "split") and a["kind"] != "human":
            f.append(Finding("D-13", DOMAIN, f"{lbl}: {c['kind']} is a human decision"))
        if (c["kind"] == "migration") != (c["channel"] == "migration"):
            f.append(Finding("D-13", DOMAIN, f"{lbl}: kind migration and channel migration go together"))
        if c["kind"] == "revert":
            _check_revert(ds, ix, c, f)


def _content(v: dict[str, Any]) -> dict[str, Any]:
    return {k: x for k, x in v.items() if k not in ("revision_from", "revision_to", "taxonomy_version")}


def _check_revert(ds: Dataset, ix: Index, c: dict[str, Any], f: list[Finding]) -> None:
    target, rev = c["reverts_revision"], c["revision"]
    for versions in (ix.ev_versions, ix.rv_versions):
        for fid, vs in versions.items():
            if not any(v["org_id"] == c["org_id"] and v["revision_from"] == target for v in vs):
                continue
            before = next((v for v in vs if valid_at(v, target - 1)), None)
            after = next((v for v in vs if valid_at(v, rev)), None)
            if after is None or (before is None and after["record_state"] != "removed") or (before and _content(before) != _content(after)):
                f.append(Finding("D-14", DOMAIN, f"revert r{rev}: fact {fid} does not equal its state before r{target}"))


# --------------------------------------------------------------------------- advisory


def advisory_findings(ds: Dataset, taxes: dict[str, Taxonomy]) -> list[Finding]:
    f: list[Finding] = []
    ix = Index(ds)
    for org, head in ix.heads.items():
        st = as_of(ds, org, head)
        tax = taxes["1.0.0"]
        owned = {r["to_id"] for r in st.relationships.values() if r["rel_type"] == "OWNS"}
        deployed_from = {r["from_id"] for r in st.relationships.values() if r["rel_type"] == "DEPLOYED_AS"}
        parent_of = {r["to_id"]: r["from_id"] for r in st.relationships.values() if r["rel_type"] == "CONTAINS"}
        directional = {(r["from_id"], r["to_id"]) for r in st.relationships.values() if r["rel_type"] in ("READS_FROM", "WRITES_TO")}
        for eid, v in sorted(st.entities.items()):
            tk = v["type_key"]
            if tk in ("core.application", "core.system", "core.service", "core.dataset") and eid not in owned:
                f.append(Finding("A-01", ADVISORY, f"{v['display_name']} ({tk}) has no owner"))
            if v["environment_scope"] == "unknown" and tk != "infra.scope" and v["category"] != "scope":
                f.append(Finding("A-03", ADVISORY, f"{v['display_name']} ({tk}) has unknown environment scope"))
            if tk == "infra.resource":
                f.append(Finding("A-04", ADVISORY, f"{v['display_name']} ({v['provider']} {v['native_type']}) is uncategorized"))
            if v["category"] != "scope" and tax.types.get(tk, {}).get("kind") == "physical" and v["container_id"] is None:
                f.append(Finding("A-08", ADVISORY, f"{v['display_name']} ({tk}) has no known containment parent"))
            if tk == "core.application":
                svcs = [c for c, p in parent_of.items() if p == eid]
                if eid not in deployed_from and not any(s in deployed_from for s in svcs):
                    f.append(Finding("A-09", ADVISORY, f"{v['display_name']} has no known deployment"))
            if tk.startswith("infra.") and tk not in ("infra.resource", "infra.scope"):
                mapped = taxes.get(v["taxonomy_version"], tax).mappings.get(v["provider"], {}).get(v["native_type"])
                if mapped != v["category"]:
                    f.append(Finding("A-11", ADVISORY, f"{v['display_name']}: native type {v['native_type']} is not mapped to {v['category']}"))
            if v["trust_state"] in ("stale", "conflicted"):
                f.append(Finding("A-12", ADVISORY, f"{v['display_name']} is {v['trust_state']}"))
        for rid, r in sorted(st.relationships.items()):
            v = r["version"]
            names = f"{st.entities[r['from_id']]['display_name']} {r['rel_type']} {st.entities[r['to_id']]['display_name']}"
            if v["cross_environment"]:
                f.append(Finding("A-02", ADVISORY, f"cross-environment: {names}"))
            if v["cross_provider"] and v["verification_state"] != "verified":
                f.append(Finding("A-05", ADVISORY, f"unverified cross-provider: {names}"))
            if r["rel_type"] == "STORES_IN" and (r["from_id"], r["to_id"]) not in directional:
                f.append(Finding("A-06", ADVISORY, f"direction not established: {names}"))
            if r["rel_type"] == "DEPLOYED_AS" and not v["attributes"].get("deployment_role"):
                f.append(Finding("A-07", ADVISORY, f"deployment role not established: {names}"))
            if v["trust_state"] in ("stale", "conflicted"):
                f.append(Finding("A-12", ADVISORY, f"{names} is {v['trust_state']}"))
    return f


def advisory_summary(findings: list[Finding]) -> dict[str, int]:
    out: dict[str, int] = {}
    for x in findings:
        out[x.rule] = out.get(x.rule, 0) + 1
    return dict(sorted(out.items()))


# --------------------------------------------------------------------------- import, snapshots, manifest


def import_findings(ds: Dataset, taxes: dict[str, Taxonomy], directory: Path) -> list[Finding]:
    f: list[Finding] = []
    batch = json.loads((directory / "inputs" / "aws-inventory.r2.json").read_text(encoding="utf-8"))
    report = json.loads((directory / "inputs" / "aws-inventory.r2.expected-report.json").read_text(encoding="utf-8"))
    f += schema_findings("import-batch", batch, "inputs/aws-inventory.r2.json")
    org = next(o["id"] for o in ds.tables["organizations"] if o["key"] == batch["org_key"])
    rev = report["first_apply"]["creates_revision"]
    cs = next(c for c in ds.tables["change_sets"] if c["org_id"] == org and c["revision"] == rev)
    if cs["input_hash"] != sha256_of(batch):
        f.append(Finding("H-15", HARD, "import change set input_hash differs from the batch"))
    tax = taxes[batch["taxonomy_version"]]
    first = plan_batch(tax, batch, as_of(ds, org, rev - 1))
    created_e = {e["id"] for e in ds.tables["entities"] if e["org_id"] == org and e["created_revision"] == rev}
    created = [r for r in ds.tables["relationships"] if r["org_id"] == org and r["created_revision"] == rev]
    created_r = {r["id"] for r in created if r["rel_type"] != "CONTAINS"}
    created_c = {(r["from_id"], r["to_id"]) for r in created if r["rel_type"] == "CONTAINS"}
    if {d["entity_id"] for d in first.new_entities} != created_e or {d["id"] for d in first.new_relationships} != created_r \
            or set(first.new_containments) != created_c:
        f.append(Finding("H-15", HARD, f"revision {rev} does not contain exactly the batch's planned facts"))
    if [{"ref": r["item"].get("ref"), "rule": r["rule"], "reasons": r["reasons"]} for r in first.rejected] != report["rejected"]:
        f.append(Finding("H-15", HARD, "rejected items differ from the expected report"))
    for label, at in (("replay", rev), ("replay at head", ds.head(org))):
        p = plan_batch(tax, batch, as_of(ds, org, at))
        if not p.empty:
            f.append(Finding("H-15", HARD, f"{label}: re-importing the same batch is not a no-op"))
    return f


def snapshot_findings(ds: Dataset, directory: Path) -> list[Finding]:
    f: list[Finding] = []
    for s in ds.tables["graph_snapshots"]:
        if graph_hash(as_of(ds, s["org_id"], s["revision"])) != s["graph_hash"]:
            f.append(Finding("H-15", HARD, f"snapshot {s['label']}: graph_hash does not match the reconstructed graph"))
    keys = {o["key"]: o["id"] for o in ds.tables["organizations"]}
    for e in json.loads((directory / "expected-as-of.json").read_text(encoding="utf-8")):
        st = as_of(ds, keys[e["org_key"]], e["revision"])
        if (len(st.entities), len(st.relationships), graph_hash(st)) != (e["entities"], e["relationships"], e["graph_hash"]):
            f.append(Finding("H-15", HARD, f"as-of {e['org_key']}#{e['revision']} differs from expected"))
    return f


def manifest_findings(directory: Path) -> list[Finding]:
    f: list[Finding] = []
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    f += schema_findings("fixture-manifest", manifest, "manifest.json")
    for item in manifest["files"]:
        data = (directory / item["path"]).read_bytes()
        if sha256_of(data) != item["sha256"]:
            f.append(Finding("H-15", HARD, f"{item['path']}: content hash differs from the manifest"))
    return f
