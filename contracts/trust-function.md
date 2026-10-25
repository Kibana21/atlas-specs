# Trust function v1 (`trust-1`)

**Status:** **Approved for CP3** (owner, G2 closure, 25 Oct 2026). It implements owner decision U-3 and the G2-closure decisions below. **Reference:** `tools/canonical_model.py` (`trust_v1`). **Truth table:** `acceptance/test-data/trust-function-v1/cases.json` (36 cases). **Built on:** ADR-0018 (dimensions 2 and 3, the conflict procedure) and the taxonomy's allowed evidence kinds (ADR-0017 §4.1, taxonomy 1.1.0).

The function is pure and deterministic. It is never decided by an LLM (invariant 7). Its inputs are:

- the fact's **current assertions**, each with its evidence's `method`, `observed_at` and `valid_to`;
- the **claim**;
- the **recorded verification**;
- the **trust policy**;
- the **evaluation time** `at`;
- the fact's **prior approved values**.

`at` is the publishing change set's time, never the wall clock. The function returns:

- the trust state;
- the verification state the evidence supports;
- the deciding rule;
- the selected value of every asserted field.

## Owner decision U-3, as applied

| Owner rule | Where |
|---|---|
| VERIFIED needs evidence applicable and sufficiently authoritative for the claim, and no unresolved material contradiction | TF-A, TF-V |
| UNVERIFIED when the evidence is insufficient | TF-V: any failed condition leaves `unverified` |
| CONFLICTED for unresolved, materially incompatible assertions | TF-2 |
| STALE by the approved freshness policy | TF-3 (freshness values are not approved yet: TF-F) |
| No universal source ranking | TF-2 never picks a winner; TF-A is per claim; TF-4…TF-7 only name how a fact is known |
| Never verify by evidence count | TF-V needs a recorded human verification; no count is an input |
| Undefined authority or freshness never promotes to VERIFIED | TF-F `unassessed`; TF-V support sets; no precedence rule (DEC-034 Proposed) |

"VERIFIED" and "UNVERIFIED" are the verification dimension (ADR-0018 §3). "CONFLICTED" and "STALE" are trust states (ADR-0018 §2). They stay separate dimensions.

## Claim classes

| Claim | Physical? | Applicable evidence kinds (TF-A) |
|---|---|---|
| Entity | Physical iff its type is physical | Physical: all five kinds. Logical: all except `provider_configuration`: a logical application, service or capability is never "discovered" from provider configuration, names or tags |
| Relationship | Physical iff at least one endpoint is physical | The taxonomy's `allowed_evidence_kinds` for the type, minus `provider_configuration` when both endpoints are logical. In 1.1.0 no active type accepts `inferred` |

An assertion of a kind that is not applicable is kept, but it never establishes the fact.

## Rules, in order

| Rule | Condition | Result |
|---|---|---|
| TF-0 | The fact originates from a draft | `proposed` (never in the published graph) |
| TF-1 | No current applicable existence assertion. Current means `revision_to` is unset at the evaluated revision and the evidence's `valid_to` is after `at` | No trust state. The fact must not be published (D-12) |
| TF-2 | Two or more current assertions give different values for the same field. Values are compared as canonical JSON. No precedence rule resolves it (v1 has none) | `conflicted`. Each conflicting field's selected value is the prior approved value, or none. Every assertion is kept (ADR-0018 conflict procedure) |
| TF-3a | The recorded verification has `expires_at` ≤ `at` | `stale` (ADR-0018 §3, UX-PASS-011) |
| TF-3b | Every applicable existence assertion is `expired` under TF-F | `stale` |
| TF-4 | Remaining usable existence evidence includes `provider_configuration` | `discovered` |
| TF-5 | Otherwise it includes `human_assertion` | `curated` |
| TF-6 | Otherwise it includes `documentation` or `contract` | `documented` (UI: "documented" or "from contract", never "observed") |
| TF-7 | Otherwise (only `inferred`) | `inferred` |

TF-4…TF-7 decide only the trust **label**. They never select a value: value disagreements are TF-2. Expired assertions are kept and listed; they only stop counting for TF-3b…TF-7.

### TF-F: freshness

- An assertion is `fresh` or `expired` against the policy entry for its evidence's `method` (`stale_after_days`).
- With no entry it is `unassessed`. It never makes a fact stale, and it is never promoted.
- Real per-source values are **DEC-072 (Open)**. Until then, only the golden fixture has a policy: the synthetic `trust-policy.json`, with documents imported by `import:document:v1` stale after 365 days.

### TF-V: verification

A recorded verification (`verification_state = verified`) counts only if **all** of the following hold:

1. `verified_by` is a human actor (`oidc` namespace; ADR-0008 §10);
2. `verified_at` ≤ `at`;
3. the trust state is `discovered`, `curated` or `documented`. A fact that is conflicted, stale, inferred or proposed is never verified;
4. a current, usable applicable existence assertion supports it:

| Claim | Supporting kinds |
|---|---|
| Physical (resources, containment, deployment, connectivity, any relationship with a physical endpoint) | `provider_configuration`, `human_assertion` |
| Logical (logical entities, API structure, ownership, capability support, curated dependencies) | `human_assertion`, `documentation`, `contract` |

Consequences:

- Declared evidence (IaC manifests, OpenAPI) can never alone support verifying a physical claim. A steward must first add a `human_assertion`, which is explicit, never silent.
- Publishing a version stored as `verified` that fails TF-V is rejected (D-19).
- When a later change makes a verified fact conflicted, the new version is written `unverified`.
- An expired verification stays recorded on its version for history. Its trust state is `stale` and it is shown as expired.

## Storage and recomputation

- **Stored state:** each version stores the result for its publication. D-12 requires the stored trust state to equal the function's result at every revision where the version is current. The publishing procedure therefore writes a new version whenever an assertion change alters the result.
- **Time-driven changes:** verification expiry and evidence ageing are written by a recompute change set (system actor). Its schedule depends on DEC-072. Until it runs, a read must never present an expired verification as verified (ATLAS-003).
- **Function changes:** a new function version is applied in one change set (ADR-0018).

## Owner decisions at G2 closure (25 Oct 2026)

| # | Point | Decision | Applied |
|---|---|---|---|
| C-1 | IaC state was listed under `provider_configuration` in ADR-0018 §1 | Approved: templates, plans and state files are `contract` (declared) evidence. Their subtype and source metadata are preserved in `method`, `source_ref` and `artifact_ref`. IaC alone never proves live deployment or supports verifying a physical fact | ADR-0018 §1 amended; TC-04, TC-05, TC-34 |
| C-2 | `discovered` for any claim with provider configuration | Approved: evidence authority is claim-specific. Provider configuration never establishes a logical or business fact (ownership, logical membership, business responsibility) on its own | ADR-0018 §2 amended; TF-A now also excludes provider configuration from relationships between logical entities (previously only logical entities). Cases TC-09, TC-31, TC-32, TC-35, TC-36 |
| I-6 | A required field whose sources disagree, with no prior approved value | Approved: keep both values and their evidence and choose no winner. The fact is `conflicted` and the field is **unresolved**, using the approved representation (ADR-0018: selected value none, so it is absent from the stored attributes). The required-field rule (D-01) accepts an unresolved field and rejects one that is simply missing | ADR-0018 conflict procedure amended; D-01; mutation `m_unresolved_without_conflict` |
