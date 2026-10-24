# Atlas OpenAPI Style Guide

**Applies to:** `contracts/openapi/atlas-api.yaml` · **Status:** Approved for ATLAS-001 (spec v0.2.1, FR-01/FR-03, DEC-095)

The backend proves conformance by comparing its FastAPI-generated OpenAPI with this contract after normalization (spec §6.7). The contract is therefore written in the **dialect FastAPI and Pydantic v2 emit**, so the comparison stays exact without loosening.

## 1. Document

- `openapi: 3.1.0`. `info.version` follows `contracts/compatibility.md`.
- One `paths` entry per route. There are no `servers`-dependent semantics.
- Every reusable schema lives in `components/schemas`. **No inline object schemas for shared shapes.**
- The shared response header lives in `components/headers`.

## 2. Operations

| Rule | Example |
|---|---|
| Every operation has an explicit `operationId` in lowerCamelCase, verb first | `getHealthLive`, `getDiagnosticsBuild` |
| The backend sets the same value as FastAPI's `operation_id` | `@router.get(..., operation_id="getHealthLive")` |
| Every operation declares **every** response it can return, including `500` | `200` and `500` for liveness |
| Error responses (`4xx`/`5xx`) reference `#/components/schemas/ErrorEnvelope` | — |
| `422` is declared **only** when the operation has parameters or a body. It then uses `ErrorEnvelope`, never FastAPI's default `HTTPValidationError` | Contract 0.1.0 has no inputs, so no `422` |
| **Every** response declares header `X-Correlation-ID` via `$ref: '#/components/headers/X-Correlation-ID'` | — |
| Each response has a short `description`. Descriptions are documentation only and are excluded from conformance | — |

## 3. Schemas (Pydantic v2 dialect)

| Concept | Write it as | Pydantic source |
|---|---|---|
| Object | `type: object`, `properties`, `required` (all non-defaulted fields) | `class X(BaseModel)` |
| Required field | listed in `required` | field without default |
| Optional field | omitted from `required`, with `default` | field with default |
| **Nullable** field | `anyOf: [{<type>}, {type: 'null'}]` (never `type: [x, 'null']`, never `nullable: true`) | `str \| None` |
| Single fixed value | `const: <value>` plus `type` | `Literal["ok"]` |
| Several fixed values | `enum: [...]` plus `type` | `Literal["a", "b"]` |
| Pattern | `pattern: '<regex>'` | `Annotated[str, StringConstraints(pattern=...)]` |
| Free-form object | `type: object`, `additionalProperties: true` | `dict[str, Any]` |
| Reference | `$ref: '#/components/schemas/<Name>'` | nested model |
| Titles | optional; ignored by conformance | Pydantic adds them automatically |

**Component names** equal the Pydantic model names in PascalCase: `ErrorEnvelope`, `ErrorBody`, `HealthLive`, `HealthReady`, `ReadinessChecks`, `BuildInfo`. Do not rename one side only.

## 4. What conformance ignores, and what it never ignores

| Ignored (cosmetic) | Never ignored (meaningful) |
|---|---|
| `title`, `description`, `summary`, `example`, `examples`, `externalDocs`, `tags`, `servers`, `info` (except `version`) **when they are OpenAPI/JSON Schema keywords** | Any property, path, parameter, header, component or response, including a property *named* `title` or `description` |
| Key order; order of `required`, `enum` and `anyOf` members; parameter order | Types, formats, patterns, `const`/`enum` values, `required` membership, defaults, status codes, media types, headers, `$ref` targets, `additionalProperties` |
| Nullable spelling (`type: [x, 'null']` is canonicalized to `anyOf`) | `info.version`, `openapi` version, operationIds |

The conformance tool's self-tests (`tools/tests/test_conformance.py`) prove both columns.
