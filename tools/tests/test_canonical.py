"""Tests for the canonical graph contracts, validator and golden fixture (ATLAS-002 CP2)."""

from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import pytest

from canonical_model import (
    HUMAN_ACTOR_NAMESPACES, Claim, Dataset, NormalizationError, Taxonomy, as_of, normalize_identity, plan_batch, trust_v1, uuid7,
)
from canonical_rules import (
    fixture_findings, import_findings, manifest_findings, schema_findings, snapshot_findings, taxonomy_findings,
)
from check_canonical import DEFAULT_FIXTURE, load_taxonomies, run
from generate_golden import build

FIXTURE = DEFAULT_FIXTURE


@lru_cache(maxsize=1)
def _base() -> tuple[Dataset, dict[str, Taxonomy]]:
    ds = Dataset.load(FIXTURE)
    taxes, _ = load_taxonomies(FIXTURE)
    return ds, taxes


def dataset() -> tuple[Dataset, dict[str, Taxonomy]]:
    ds, taxes = _base()
    return Dataset(copy.deepcopy(ds.tables), copy.deepcopy(ds.policy)), taxes


def rules(ds: Dataset, taxes: dict[str, Taxonomy]) -> set[str]:
    return {f.rule for f in fixture_findings(ds, taxes)}


def by(ds: Dataset, table: str, **match: Any) -> dict[str, Any]:
    return next(r for r in ds.tables[table] if all(r.get(k) == v for k, v in match.items()))


def entity_named(ds: Dataset, name: str, type_key: str | None = None) -> dict[str, Any]:
    return next(v for v in ds.tables["entity_versions"]
                if v["display_name"] == name and v["revision_to"] is None and (type_key is None or v["type_key"] == type_key))


# --------------------------------------------------------------------------- positive


def test_committed_contracts_and_fixture_pass() -> None:
    blocking, advisories, info = run(FIXTURE, determinism=False)
    assert blocking == []
    assert info["examples"] >= 40
    assert advisories, "the fixture deliberately contains advisory findings (missing owners, cross-environment, ...)"


def test_fixture_generation_is_deterministic(tmp_path: Path) -> None:
    build(tmp_path / "a")
    build(tmp_path / "b")
    files = sorted(p.relative_to(tmp_path / "a") for p in (tmp_path / "a").rglob("*") if p.is_file())
    assert files == sorted(p.relative_to(tmp_path / "b") for p in (tmp_path / "b").rglob("*") if p.is_file())
    for p in files:
        assert (tmp_path / "a" / p).read_bytes() == (tmp_path / "b" / p).read_bytes()
        assert (tmp_path / "a" / p).read_bytes() == (FIXTURE / p).read_bytes(), f"committed fixture is stale: {p}"


def test_fixture_size_and_coverage() -> None:
    m = json.loads((FIXTURE / "manifest.json").read_text())
    c = m["counts"]
    assert 230 <= c["entities"] <= 270 and c["relationships"] >= 600
    a = c["by_org"]["default"]
    assert {"azure", "aws", "gcp", "alibaba", "oci", "on_premises", "private_cloud", "other"} <= set(a["by_provider"])
    assert {"DEV", "SIT", "UAT", "UAT-2", "PROD", "DR", "PERF-LAB", "shared"} <= set(a["by_environment_scope"])
    assert a["cross_environment"] > 0 and a["cross_provider"] > 0 and a["shared_endpoint"] > 0
    assert {"READS_FROM", "WRITES_TO", "MEMBER_OF", "CONTAINS", "DEPLOYED_AS"} <= set(a["by_relationship_type"])
    roles = {v["attributes"].get("deployment_role") for v in json.loads((FIXTURE / "relationship_versions.json").read_text())
             if v["revision_to"] is None and v["record_state"] == "present"}
    assert {"primary", "active_secondary", "standby", "unknown", None} <= roles


def test_revision_scenarios_present() -> None:
    ds, _ = dataset()
    kinds = [(c["revision"], c["kind"], c["actor"]["kind"]) for c in ds.tables["change_sets"] if c["org_id"] == ds.org_ids()[0]]
    assert [k for _, k, _ in kinds] == ["fixture_load", "import", "steward_edit", "steward_edit", "revert", "steward_edit", "migration", "import"]
    assert {a for _, k, a in kinds if k in ("fixture_load", "import")} == {"service"}
    renamed = [v for v in ds.tables["entity_versions"] if v["display_name"] in ("Quote Service", "Quotation Service")]
    assert len({v["entity_id"] for v in renamed}) == 1 and len(renamed) == 2, "rename keeps the entity ID"
    billing = [v for v in ds.tables["entity_versions"] if v["display_name"] == "sqldb-billing-prod"]
    assert len({v["entity_id"] for v in billing}) == 1
    assert {v["type_key"] for v in billing} == {"infra.data_store", "azure.sql_database"}
    bq = [v for v in ds.tables["entity_versions"] if v["display_name"] == "analytics-warehouse"]
    assert [(v["type_key"], v["taxonomy_version"]) for v in bq] == [("infra.resource", TAX.version), ("infra.data_store", "1.2.0-test.1")]


def test_historical_reconstruction_differs_by_revision() -> None:
    ds, _ = dataset()
    org = ds.org_ids()[0]
    reads = next(r for r in ds.tables["relationships"] if r["rel_type"] == "READS_FROM"
                 and entity_named(ds, "Claims API Service")["entity_id"] == r["from_id"]
                 and entity_named(ds, "Policy Records")["entity_id"] == r["to_id"])
    present = [rev for rev in range(1, 9) if reads["id"] in as_of(ds, org, rev).relationships]
    assert present == [1, 2, 3, 5, 6, 7, 8], "retired in r4, restored by the revert in r5"


# --------------------------------------------------------------------------- normalization


TAX = Taxonomy.load()
SUB = "00000000-0000-4000-8000-00000000a001"


@pytest.mark.parametrize("original,expected", [
    (f"/subscriptions/{SUB}/resourceGroups/RG-Claims/providers/Microsoft.Sql/servers/S1/databases/D1/",
     f"/subscriptions/{SUB}/resourcegroups/rg-claims/providers/microsoft.sql/servers/s1/databases/d1"),
    (f"  /subscriptions/{SUB.upper()}  ", f"/subscriptions/{SUB}"),
    ("/providers/Microsoft.Management/managementGroups/MG1", "/providers/microsoft.management/managementgroups/mg1"),
])
def test_arm_1_normalizes(original: str, expected: str) -> None:
    assert normalize_identity(TAX, "azure.arm", original)[0] == expected


@pytest.mark.parametrize("original", [
    f"/subscriptions/{SUB}//resourceGroups/rg", f"/subscriptions/{SUB}/resourceGroups/rg/providers/Microsoft.Sql/servers",
    f"/subscriptions/{SUB}/resourceGroups/../providers/Microsoft.Sql/servers/s1", "/subscriptions/not-a-guid",
    f"/subscriptions/{SUB}/resourceGroups/rg?api-version=1", "subscriptions/x", f"/subscriptions/{SUB}/resource Groups/rg",
])
def test_arm_1_rejects_never_repairs(original: str) -> None:
    with pytest.raises(NormalizationError):
        normalize_identity(TAX, "azure.arm", original)


def test_validation_only_namespaces_preserve_case() -> None:
    arn = "arn:aws:s3:::Example-Bucket"
    assert normalize_identity(TAX, "aws.arn", arn)[0] == arn
    assert normalize_identity(TAX, "oci.ocid", " ocid1.instance.oc1.eu-frankfurt-1.abc123 ")[0] == "ocid1.instance.oc1.eu-frankfurt-1.abc123"
    with pytest.raises(NormalizationError):
        normalize_identity(TAX, "aws.arn", "arn:aws:s3")


@pytest.mark.parametrize("namespace", ["huawei.resource", "tencent.qcs", "ibm.crn", "apim.operation", "unknown.ns"])
def test_planned_reserved_and_unknown_namespaces_are_rejected(namespace: str) -> None:
    with pytest.raises(NormalizationError):
        normalize_identity(TAX, namespace, "anything")


def test_k8s_uid_and_org_key() -> None:
    uid = "7A1C0000-0000-4000-8000-000000000001"
    key = normalize_identity(TAX, "k8s.uid", f"azure.arm:/subscriptions/{SUB}/resourceGroups/RG/providers/Microsoft.ContainerService/managedClusters/AKS#{uid}")[0]
    assert key == f"azure.arm:/subscriptions/{SUB}/resourcegroups/rg/providers/microsoft.containerservice/managedclusters/aks#{uid.lower()}"
    assert normalize_identity(TAX, "org.key", " APP-0042 ")[0] == "app-0042"
    assert normalize_identity(TAX, "source.cmdb", "CI-0001")[0] == "CI-0001"


def test_uuid7_is_valid_and_deterministic() -> None:
    a, b = uuid7(1, "x"), uuid7(1, "x")
    assert a == b and a[14] == "7" and a[19] in "89ab"


# --------------------------------------------------------------------------- negative mutations (fixture)


def m_cross_org(ds: Dataset) -> None:
    a, b = ds.org_ids()
    env_a = next(v["entity_id"] for v in ds.tables["entity_versions"] if v["org_id"] == a and v["type_key"] == "core.environment")
    v = next(v for v in ds.tables["entity_versions"] if v["org_id"] == b and v["environment_scope"] == "single")
    v["environment_id"] = env_a


def m_bad_interval(ds: Dataset) -> None:
    v = next(v for v in ds.tables["entity_versions"] if v["revision_to"] is not None)
    v["revision_to"] = v["revision_from"]


def m_two_current(ds: Dataset) -> None:
    next(v for v in ds.tables["entity_versions"] if v["revision_to"] is not None)["revision_to"] = None


def m_duplicate_identity(ds: Dataset) -> None:
    i = copy.deepcopy(by(ds, "external_identities", namespace="azure.arm"))
    i["id"] = uuid7(99_999, "dup")
    i["entity_id"] = next(e["id"] for e in ds.tables["entities"] if e["org_id"] == i["org_id"] and e["id"] != i["entity_id"])
    ds.tables["external_identities"].append(i)


def m_unnormalized(ds: Dataset) -> None:
    i = next(i for i in ds.tables["external_identities"] if i["namespace"] == "azure.arm" and i["original_key"] != i["normalized_key"])
    i["normalized_key"] = i["original_key"]


def m_planned_namespace(ds: Dataset) -> None:
    i = by(ds, "external_identities", namespace="aws.arn")
    i["namespace"] = "huawei.resource"


def m_duplicate_relationship(ds: Dataset) -> None:
    r = copy.deepcopy(by(ds, "relationships", rel_type="READS_FROM"))
    v = copy.deepcopy(by(ds, "relationship_versions", relationship_id=r["id"], revision_to=None))
    r["id"] = v["relationship_id"] = uuid7(99_998, "dup-rel")
    ds.tables["relationships"].append(r)
    ds.tables["relationship_versions"].append(v)


def m_dangling(ds: Dataset) -> None:
    r = by(ds, "relationships", rel_type="WRITES_TO")
    v = next(v for v in ds.tables["entity_versions"] if v["entity_id"] == r["to_id"] and v["revision_to"] is None)
    v["record_state"] = "removed"


def m_two_parents(ds: Dataset) -> None:
    child = entity_named(ds, "Claims Intake", "core.capability")
    other = entity_named(ds, "Quoting", "core.capability")
    r = copy.deepcopy(next(r for r in ds.tables["relationships"] if r["rel_type"] == "CONTAINS" and r["to_id"] == child["entity_id"]))
    v = copy.deepcopy(by(ds, "relationship_versions", relationship_id=r["id"], revision_to=None))
    r["id"] = v["relationship_id"] = uuid7(99_997, "two-parents")
    r["from_id"] = other["entity_id"]
    ds.tables["relationships"].append(r)
    ds.tables["relationship_versions"].append(v)


def m_cycle(ds: Dataset) -> None:
    root, leaf = entity_named(ds, "Insurance Operations"), entity_named(ds, "Claims Intake", "core.capability")
    r = copy.deepcopy(next(r for r in ds.tables["relationships"] if r["rel_type"] == "CONTAINS" and r["to_id"] == leaf["entity_id"]))
    v = copy.deepcopy(by(ds, "relationship_versions", relationship_id=r["id"], revision_to=None))
    r["id"] = v["relationship_id"] = uuid7(99_996, "cycle")
    r["from_id"], r["to_id"] = leaf["entity_id"], root["entity_id"]
    root["container_id"] = leaf["entity_id"]
    ds.tables["relationships"].append(r)
    ds.tables["relationship_versions"].append(v)


def _add_rel(ds: Dataset, rel_type: str, frm: str, to: str, attrs: dict[str, Any], ev_kind: str = "documentation") -> None:
    fv, tv = entity_named(ds, frm), entity_named(ds, to)
    rid = uuid7(99_990, f"{rel_type}{frm}{to}")
    ev = next(e for e in ds.tables["evidence"] if e["org_id"] == fv["org_id"] and e["kind"] == ev_kind)
    ds.tables["relationships"].append({"org_id": fv["org_id"], "id": rid, "rel_type": rel_type, "from_id": fv["entity_id"], "to_id": tv["entity_id"],
                                       "discriminator": attrs.get("connectivity_kind", ""), "created_revision": 8})
    ds.tables["relationship_versions"].append({
        "org_id": fv["org_id"], "relationship_id": rid, "revision_from": 8, "revision_to": None, "record_state": "present", "lifecycle": "active",
        "environment_id": None, "cross_environment": False, "shared_endpoint": False, "cross_provider": False, "attributes": attrs,
        "trust_state": "documented", "verification_state": "unverified", "verified_by": None, "verified_at": None, "expires_at": None,
        "taxonomy_version": TAX.version})
    ds.tables["fact_assertions"].append({"org_id": fv["org_id"], "id": uuid7(99_991, f"a{rid}"), "fact_kind": "relationship", "fact_id": rid,
                                         "field_path": None, "asserted_value": None, "evidence_id": ev["id"], "evidence_kind": ev["kind"],
                                         "revision_from": 8, "revision_to": None})


def m_generic_read(ds: Dataset) -> None:
    _add_rel(ds, "READS_FROM", "Claims API Service", "afd-customer-prod", {})


def m_reserved(ds: Dataset) -> None:
    _add_rel(ds, "PROTECTS", "kv-claims-prod", "sqldb-claims", {})


def m_depends_on_provider(ds: Dataset) -> None:
    _add_rel(ds, "DEPENDS_ON", "Claims Engine", "Billing Hub", {"rationale": "x"}, ev_kind="provider_configuration")


def m_cross_provider_containment(ds: Dataset) -> None:
    _add_rel(ds, "CONTAINS", "example-oci-tenancy", "rg-claims-dr", {})


def m_wrong_flag(ds: Dataset) -> None:
    next(v for v in ds.tables["relationship_versions"] if v["cross_environment"])["cross_environment"] = False


def m_retype_by_import(ds: Dataset) -> None:
    """A non-automatic re-type (service -> application) inside an import change set (ADR-0017 §2.4)."""
    org = ds.org_ids()[0]
    v = next(v for v in ds.tables["entity_versions"] if v["display_name"] == "Quotation Service")
    v.update(type_key="core.application", category="core.application", attributes={"org_key": "APP-X"})
    cs = by(ds, "change_sets", org_id=org, revision=3)
    cs.update(kind="import", channel="import", actor={"kind": "service", "namespace": "atlas.service", "key": "import-worker", "label": None})


def m_human_import(ds: Dataset) -> None:
    by(ds, "change_sets", revision=2)["actor"] = {"kind": "human", "namespace": "oidc", "key": "https://login.example.invalid/x|y", "label": None}


def m_trust_without_evidence(ds: Dataset) -> None:
    entity_named(ds, "Claims Portal", "core.application")["trust_state"] = "discovered"


def _rel_version(ds: Dataset, rel_type: str, frm: str, to: str) -> dict[str, Any]:
    f, t = entity_named(ds, frm)["entity_id"], entity_named(ds, to)["entity_id"]
    r = by(ds, "relationships", rel_type=rel_type, from_id=f, to_id=t)
    return next(v for v in ds.tables["relationship_versions"] if v["relationship_id"] == r["id"] and v["revision_to"] is None)


def m_stale_recorded_as_documented(ds: Dataset) -> None:
    entity_named(ds, "mq-legacy-01")["trust_state"] = "documented"     # its only evidence is past the fixture's freshness policy


def m_declared_as_observed(ds: Dataset) -> None:
    _rel_version(ds, "CONTAINS", "claims-events-prod", "document-indexed")["trust_state"] = "discovered"   # IaC only (U-1)


def m_verified_declared_only(ds: Dataset) -> None:
    _rel_version(ds, "CONTAINS", "claims-events-prod", "document-indexed").update(
        verification_state="verified", verified_by={"namespace": "oidc", "key": "https://login.example.invalid/synthetic|steward-0001"},
        verified_at="2026-09-20T10:00:00Z", expires_at=None)


def m_verified_by_service(ds: Dataset) -> None:
    v = next(v for v in ds.tables["relationship_versions"] if v["verification_state"] == "verified" and v["revision_to"] is None)
    v["verified_by"] = {"namespace": "atlas.service", "key": "import-worker"}


def m_conflicted_value_stored(ds: Dataset) -> None:
    entity_named(ds, "vm-batch-prod")["attributes"]["location"] = "westeurope"   # picks a winner no approved rule chose


def m_unresolved_without_conflict(ds: Dataset) -> None:
    vm = entity_named(ds, "vm-batch-prod")
    ds.tables["fact_assertions"] = [a for a in ds.tables["fact_assertions"]   # one source only: no longer unresolved
                                    if not (a["fact_id"] == vm["entity_id"] and a["asserted_value"] == "northeurope")]


def m_logical_from_provider_only(ds: Dataset) -> None:
    app = entity_named(ds, "Claims Portal", "core.application")
    prov = next(e for e in ds.tables["evidence"] if e["org_id"] == app["org_id"] and e["kind"] == "provider_configuration")
    for a in ds.tables["fact_assertions"]:
        if a["fact_id"] == app["entity_id"] and a["field_path"] is None:
            a.update(evidence_id=prov["id"], evidence_kind="provider_configuration")
    app["trust_state"] = "discovered"


def m_environment_not_env(ds: Dataset) -> None:
    v = next(v for v in ds.tables["entity_versions"] if v["environment_scope"] == "single" and v["revision_to"] is None)
    v["environment_id"] = entity_named(ds, "Claims Portal", "core.application")["entity_id"]


def m_scope_nesting(ds: Dataset) -> None:
    entity_named(ds, "claims", "infra.scope")["attributes"]["scope_kind"] = "project"   # GCP folder 'claims' becomes a project in an organization: allowed
    gproj = entity_named(ds, "claims-events-prod")
    gproj["attributes"]["scope_kind"] = "organization"                                   # organization inside a project: not allowed


def m_revert_mismatch(ds: Dataset) -> None:
    org = ds.org_ids()[0]
    v = next(v for v in ds.tables["relationship_versions"] if v["org_id"] == org and v["revision_from"] == 5)
    v["attributes"] = {"unexpected": True}


def m_secret_attribute(ds: Dataset) -> None:
    entity_named(ds, "kv-claims-prod")["attributes"]["client_secret"] = "x"


@pytest.mark.parametrize("mutate,rule", [
    (m_cross_org, "H-03"), (m_bad_interval, "H-05"), (m_two_current, "H-06"), (m_duplicate_identity, "H-07"), (m_unnormalized, "H-08"),
    (m_planned_namespace, "H-08"), (m_duplicate_relationship, "H-09"), (m_dangling, "H-10"), (m_two_parents, "H-14"), (m_cycle, "H-14"),
    (m_secret_attribute, "H-01"), (m_generic_read, "D-04"), (m_reserved, "D-04"), (m_depends_on_provider, "D-05"),
    (m_cross_provider_containment, "D-04"), (m_wrong_flag, "D-08"), (m_retype_by_import, "D-10"), (m_human_import, "D-13"),
    (m_trust_without_evidence, "D-12"), (m_environment_not_env, "D-03"), (m_scope_nesting, "D-16"), (m_revert_mismatch, "D-14"),
    (m_stale_recorded_as_documented, "D-12"), (m_declared_as_observed, "D-12"), (m_logical_from_provider_only, "D-12"),
    (m_verified_declared_only, "D-19"), (m_verified_by_service, "D-19"), (m_conflicted_value_stored, "D-20"), (m_unresolved_without_conflict, "D-01"),
])
def test_negative_mutation_is_detected(mutate: Callable[[Dataset], None], rule: str) -> None:
    ds, taxes = dataset()
    mutate(ds)
    assert rule in rules(ds, taxes)


def test_actor_kind_mismatch_is_hard() -> None:
    ds, taxes = dataset()
    by(ds, "change_sets", revision=1)["actor"]["kind"] = "human"
    assert {"H-01", "H-11"} <= rules(ds, taxes)


def test_snapshot_tamper_is_detected() -> None:
    ds, _ = dataset()
    ds.tables["graph_snapshots"][0]["graph_hash"] = "sha256:" + "0" * 64
    assert any(f.rule == "H-15" for f in snapshot_findings(ds, FIXTURE))


def test_manifest_tamper_is_detected(tmp_path: Path) -> None:
    build(tmp_path)
    (tmp_path / "evidence.json").write_text((tmp_path / "evidence.json").read_text().replace("synthetic://", "synthetic:/", 1))
    assert any(f.rule == "H-15" for f in manifest_findings(tmp_path))


# --------------------------------------------------------------------------- import: no-op, rejection, anti-spoofing


def _batch() -> dict[str, Any]:
    return json.loads((FIXTURE / "inputs" / "aws-inventory.r2.json").read_text())


def test_import_replay_is_a_noop_and_rejections_are_reported() -> None:
    ds, taxes = dataset()
    assert import_findings(ds, taxes, FIXTURE) == []
    report = json.loads((FIXTURE / "inputs" / "aws-inventory.r2.expected-report.json").read_text())
    assert report["replay"]["change_set"] is None and report["rejected"], "an imperfect observation is reported, never dropped silently"


def test_changed_batch_is_not_a_noop() -> None:
    ds, taxes = dataset()
    batch = _batch()
    batch["entities"][-1]["display_name"] = "renamed-at-source"
    plan = plan_batch(taxes[TAX.version], batch, as_of(ds, ds.org_ids()[0], 8))
    assert len(plan.changed_entities) == 1 and not plan.new_entities


def test_name_alone_never_matches() -> None:
    ds, taxes = dataset()
    batch = _batch()
    item = batch["entities"][-1]
    item["identities"] = [{"namespace": "source.other", "original_key": "different-key"}]
    item.pop("id")
    plan = plan_batch(taxes[TAX.version], batch, as_of(ds, ds.org_ids()[0], 8))
    assert any(r["rule"] == "D-18" for r in plan.rejected), "same display name, no identity match: not linked"


@pytest.mark.parametrize("field,value", [("actor", {"kind": "human", "namespace": "oidc", "key": "https://x|y", "label": None}),
                                         ("created_at", "2026-10-01T00:00:00Z"), ("db_role", "atlas_app"), ("revision", 3)])
def test_import_payload_cannot_carry_attribution(field: str, value: Any) -> None:
    batch = _batch()
    batch[field] = value
    assert schema_findings("import-batch", batch, "batch")


# --------------------------------------------------------------------------- taxonomy


def test_taxonomy_is_self_consistent() -> None:
    assert taxonomy_findings(TAX) == []
    assert len(TAX.types) == 38
    assert sum(t["kind"] == "physical" and t["type_key"].startswith("infra.") for t in TAX.types.values()) == 8


def test_taxonomy_membership_cycle_is_detected() -> None:
    doc = copy.deepcopy(TAX.doc)
    for r in doc["relationship_types"]:
        if r["rel_type"] == "MEMBER_OF":
            r["pairs"].append({"from": ["core.business_domain"], "to": ["core.application"]})
    assert any(f.rule == "T-09" for f in taxonomy_findings(Taxonomy(doc)))


def test_overlay_must_extend_the_base_version() -> None:
    with pytest.raises(ValueError):
        TAX.with_overlay({"extends": "9.9.9", "taxonomy_version": "x", "status": "synthetic_test_only"})


def test_taxonomy_example_is_the_artifact() -> None:
    root = FIXTURE.parents[2]
    example = json.loads((root / "contracts/examples/canonical/taxonomy/valid-accepted-artifact.json").read_text())
    assert example == json.loads((root / "contracts/taxonomy/atlas-taxonomy.v1.json").read_text()), "regenerate the examples"


# --------------------------------------------------------------------------- trust function v1 and evidence compatibility (G2)


TRUST_CASES = json.loads((FIXTURE.parent / "trust-function-v1" / "cases.json").read_text(encoding="utf-8"))


def _claim(c: dict[str, Any]) -> Claim:
    if c["fact_kind"] == "relationship":
        return Claim("relationship", c["physical"], frozenset(TAX.rels[c["rel_type"]]["allowed_evidence_kinds"]))
    return Claim("entity", c["physical"])


def test_trust_cases_target_the_artifact() -> None:
    assert TRUST_CASES["taxonomy_version"] == TAX.version
    ids = [c["id"] for c in TRUST_CASES["cases"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("case", TRUST_CASES["cases"], ids=lambda c: c["id"])
def test_trust_function_v1_truth_table(case: dict[str, Any]) -> None:
    i, expected = case["input"], case["expected"]
    run_it = lambda: trust_v1(_claim(i["claim"]), i["assertions"], i["verification"], i["policy"], i["at"], i["prior_values"], i["origin"])  # noqa: E731
    if "error" in expected:
        with pytest.raises(ValueError, match=expected["error"]):
            run_it()
        return
    res = run_it()
    for key, value in expected.items():
        if key != "verification_reasons":
            assert res[key] == value, key
    assert res.get("verification_reasons", []) == expected.get("verification_reasons", [])


def test_human_actor_namespaces_match_the_taxonomy() -> None:
    assert HUMAN_ACTOR_NAMESPACES == {n["namespace"] for n in TAX.doc["actor_namespaces"] if n["actor_kind"] == "human"}


def test_contract_evidence_for_containment_and_deployment() -> None:
    """U-1: taxonomy 1.1.0 accepts contract evidence for CONTAINS and DEPLOYED_AS; such facts stay documented."""
    for rel in ("CONTAINS", "DEPLOYED_AS"):
        assert "contract" in TAX.rels[rel]["allowed_evidence_kinds"]
    ds, _ = dataset()
    kinds: dict[str, set[str]] = {}
    for a in ds.tables["fact_assertions"]:
        if a["field_path"] is None and a["revision_to"] is None:
            kinds.setdefault(a["fact_id"], set()).add(a["evidence_kind"])
    contains = {r["id"] for r in ds.tables["relationships"] if r["rel_type"] == "CONTAINS"}
    declared = [v for v in ds.tables["relationship_versions"]
                if v["relationship_id"] in contains and v["revision_to"] is None and kinds.get(v["relationship_id"]) == {"contract"}]
    assert len(declared) >= 7 + 12, "GCP hierarchy from IaC and API operations from OpenAPI"
    assert {v["trust_state"] for v in declared} == {"documented"}
    assert all(v["verification_state"] == "unverified" for v in declared)


def test_conflict_keeps_both_assertions_and_selects_nothing() -> None:
    ds, _ = dataset()
    vm = entity_named(ds, "vm-batch-prod")
    assert vm["trust_state"] == "conflicted" and "location" not in vm["attributes"]
    values = {a["asserted_value"] for a in ds.tables["fact_assertions"]
              if a["fact_id"] == vm["entity_id"] and a["field_path"] == "attributes.location" and a["revision_to"] is None}
    assert values == {"westeurope", "northeurope"}
