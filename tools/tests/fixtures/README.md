# Conformance fixtures

`fastapi-generated-0.1.0.json` is real FastAPI 0.162.0 / Pydantic 2.14.1 output for a throwaway
probe app that mirrors contract 0.1.0. It follows spec FR-22: explicit `operation_id`, router-level
error envelope responses, and an OpenAPI hook adding `X-Correlation-ID`. It proves that the
contract's dialect matches what the backend will emit, so conformance can be exact. The probe
application itself is not part of any repository. `atlas-backend` regenerates this output from
the real app in task B-19.
