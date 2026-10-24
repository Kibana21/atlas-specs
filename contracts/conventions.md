# Atlas API Conventions

**Applies to:** `contracts/openapi/atlas-api.yaml` and every Atlas HTTP API · **Status:** Approved for ATLAS-001 (spec v0.2.1, FR-03) · **Source:** Technical Design v1.1 §6

These conventions are normative. `contracts/style-guide.md` defines how they are expressed in OpenAPI.

## 1. Base path, format and versioning

- Every operation lives under `/api/v1`. A new major API version gets a new prefix (`/api/v2`) and runs in parallel until clients migrate (`contracts/compatibility.md`).
- Request and response bodies are JSON (`application/json`, UTF-8). There are no other media types in contract 0.1.0.
- The contract document version (`info.version`) follows `contracts/compatibility.md`.

## 2. Identifiers

- Resource identifiers in paths and bodies are **opaque strings**. Clients must not parse them.
- Canonical entities use immutable UUIDs (DEC-037; UUIDv7 preferred) when they appear in later contract versions.
- Commit SHAs are full 40-character lowercase hexadecimal strings.

## 3. Headers

| Header | Direction | Status in 0.1.0 | Rule |
|---|---|---|---|
| `X-Correlation-ID` | request (optional), **every response** (required) | In use | Inbound values matching `^[A-Za-z0-9_-]{8,64}$` are reused; anything else is replaced by a server-generated `req_<id>`. The value in the response header equals `error.correlation_id` in any error body |
| `If-Match` / `ETag` | request / response | Reserved | Optimistic concurrency for revisioned resources; failures return `REVISION_CONFLICT` |
| `Idempotency-Key` | request | Reserved | Required on non-idempotent creates once such operations exist; missing key returns `IDEMPOTENCY_KEY_REQUIRED` |

## 4. Pagination (reserved)

List operations, when they exist, use cursor pagination:

```json
{"items": [], "next_cursor": null}
```

`next_cursor` is an opaque string, or `null` on the last page. Page size is capped server-side whatever the client requests.

## 5. Status codes

| Code | Use |
|---|---|
| 200 | Success with body |
| 201 / 202 | Created / accepted for asynchronous processing (reserved) |
| 401 | Not authenticated (reserved until authentication exists) |
| 403 | Authenticated but forbidden (reserved) |
| 404 | Missing **or hidden** resource (anti-enumeration), or a disabled diagnostic endpoint |
| 409 / 412 | Revision conflict / precondition failed (reserved) |
| 422 | Request validation failed |
| 429 | Rate limited (reserved) |
| 500 | Unexpected server error |
| 503 | A required dependency is unavailable (recoverable) |

## 6. Error envelope

Every non-2xx response has this body (Tech §6.3; schema `contracts/schemas/error.v1.json`):

```json
{
  "error": {
    "code": "DEPENDENCY_UNAVAILABLE",
    "message": "A required dependency is unavailable.",
    "correlation_id": "req_0192f1b2c3d4",
    "details": {"failed_check": "redis"},
    "recoverable": true
  }
}
```

- All five fields are always present. `details` may be an empty object.
- `message` is human-readable and **never** contains stack traces, SQL, file paths, host names, credentials, settings values or restricted identifiers.

## 7. Error-code catalog

The catalog is **append-only**: codes are never renamed or reused.

| Code | HTTP | Recoverable | Status in 0.1.0 | Meaning |
|---|---|---|---|---|
| `NOT_FOUND` | 404 | false | In use | Resource does not exist, is hidden, or the endpoint is disabled |
| `VALIDATION_FAILED` | 422 | false | In use | Request failed validation; `details.errors` lists field problems |
| `DEPENDENCY_UNAVAILABLE` | 503 | true | In use | A required dependency did not respond; `details.failed_check` names it |
| `INTERNAL_ERROR` | 500 | false | In use | Unexpected failure; details withheld |
| `REVISION_CONFLICT` | 409 / 412 | true | Reserved | Resource changed since it was read |
| `IDEMPOTENCY_KEY_REQUIRED` | 422 | false | Reserved | Non-idempotent request lacks `Idempotency-Key` |
| `RATE_LIMITED` | 429 | true | Reserved | Quota exceeded |

Client-side codes, such as the frontend's `NETWORK_UNAVAILABLE`, are not part of this catalog and never appear in API responses.
