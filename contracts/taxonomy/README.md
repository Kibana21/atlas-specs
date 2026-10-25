# Atlas taxonomy

`atlas-taxonomy.v1.json` is the versioned canonical taxonomy and provider registry (**taxonomy 1.1.0**; 1.0.0 accepted with DEC-050 and DEC-070, 1.1.0 by owner decision U-1 at Gate G2). Its schema is `contracts/schemas/canonical/taxonomy.v1.json` (JSON Schema 2020-12, `urn:atlas:schema:canonical:taxonomy:v1`).

| Section | Content | Source |
|---|---|---|
| `enumerations` | Lifecycles, record states, environment scopes and kinds, deployment roles, evidence kinds, trust and verification states, completeness, match methods, change-set kinds, channels, actor kinds | ADR-0008, ADR-0017, ADR-0018 |
| `providers` | 11 providers; `private_cloud`, `on_premises` and `other` require a `platform` attribute | ADR-0019 §1 |
| `categories` | 15 provider-neutral physical categories (logical types are their own category) | ADR-0019 §2 |
| `entity_types` | 38 types: 12 logical, 16 Azure, 2 Kubernetes (any provider's cluster), 8 provider-neutral `infra.*` | ADR-0017 §2, ADR-0019 |
| `relationship_types` | 14 active, 4 reserved; pairs written against types and `category:` references; allowed evidence kinds; cross-environment allowance; discriminators | ADR-0017 §4 |
| `provider_scope_rules` | `scope_kind` vocabulary and nesting per provider. Marked `intended_shape`: confirmed per provider at onboarding | ADR-0019 §4 |
| `native_type_mappings` | Seed `native_type → category` mappings: only those named in the ADRs | ADR-0017 G-T2, ADR-0019 scenarios |
| `identity_namespaces` | Namespace registry: status (`implemented`, `validation_only`, `planned`, `reserved`), approved rule, case rule, uniqueness scope | ADR-0003 |
| `actor_namespaces` | `oidc` (human), `atlas.service` (service), `atlas.system` (system) | ADR-0008 §10 |
| `retyping` | Automatic re-typing transitions | ADR-0017 §2.4 |

## Rules

- **Identity normalization:** only the approved rules are implemented (`arm-1`, `guid-1`, `apim-api-1`, `preserve-1`, `k8s-uid-1`, `org-key-1`, `source-1`; reference: `tools/canonical_model.py`). `validation_only` namespaces (AWS, Google Cloud, Alibaba Cloud, OCI) check the approved format and preserve case. `planned` (Huawei, Tencent, IBM) and `reserved` (`apim.operation`) namespaces are rejected until a rule is approved.
- **Versioning:** semver. MINOR adds; MAJOR removes, renames or narrows and needs a migration plan and owner approval. Entity and relationship IDs never change across versions; every version row records the taxonomy version that validated it.
- **Test overlays** (for example `acceptance/test-data/canonical-golden-v1/taxonomy-overlay.1.2.0-test.1.json`, schema `taxonomy-overlay.v1.json`) are synthetic, test-only deltas. They are never approved taxonomy versions.
- **Consumers** pin this file through `specs.lock` and seed their reference tables from it (CP3); a CI check compares the seed and the artifact.
- Validation rules and their HARD / DOMAIN / ADVISORY classes: `contracts/canonical-validation-rules.md`.

## Version history

| Version | Date | Change | Class |
|---|---|---|---|
| 1.0.0 | 25 Oct 2026 | Initial artifact (CP2), from the Accepted ADRs | — |
| 1.1.0 | 25 Oct 2026 | `contract` added to the allowed evidence of `CONTAINS` and `DEPLOYED_AS` (owner decision U-1, ADR-0017 §4.1). Widens a rule, so no stored fact becomes invalid. 1.0.0 was never seeded into any database | MINOR |
