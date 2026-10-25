# atlas-specs validation (ATLAS-001 FR-07, S-10). Requires only Docker and uv; no Node.
# Container images are digest-pinned in tools/images.lock; Python tools run in a
# project-local uv environment (tools/.venv) from tools/uv.lock.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

IMAGES := tools/images.lock
image = $(shell awk '/^  $(1):/{f=1} f && /ref:/{print $$2; exit}' $(IMAGES))
OASDIFF := $(call image,oasdiff)
REDOCLY := $(call image,redocly)
MARKDOWNLINT := $(call image,markdownlint)

UV := uv run --quiet --locked --project tools
CONTAINER := docker run --rm --network none
SCHEMAS := error health-live health-ready build-info

.PHONY: check docs-lint contract schemas tools canonical golden tokens registry breaking

## check: run every specs CI gate locally
check: docs-lint contract schemas tools canonical tokens registry breaking
	@echo "make check: all atlas-specs gates passed"

## docs-lint: markdownlint on non-baseline documents (brd/, ux/, technical/ excluded)
docs-lint:
	$(CONTAINER) -v "$(CURDIR)":/workdir:ro $(MARKDOWNLINT) "**/*.md"

## contract: Redocly lint of contracts/openapi/atlas-api.yaml (rules in redocly.yaml)
contract:
	$(CONTAINER) -e REDOCLY_TELEMETRY=off -e REDOCLY_SUPPRESS_UPDATE_NOTICE=true \
		-v "$(CURDIR)":/spec:ro $(REDOCLY) lint

## schemas: every valid example passes and every invalid example fails its JSON Schema
schemas:
	@$(UV) check-jsonschema --check-metaschema contracts/schemas/*.json
	@for name in $(SCHEMAS); do \
		for f in contracts/examples/$$name/valid-*.json; do \
			$(UV) check-jsonschema --schemafile contracts/schemas/$$name.v1.json "$$f" >/dev/null \
				|| { echo "FAIL: valid example rejected: $$f"; exit 1; }; \
		done; \
		for f in contracts/examples/$$name/invalid-*.json; do \
			if $(UV) check-jsonschema --schemafile contracts/schemas/$$name.v1.json "$$f" >/dev/null 2>&1; then \
				echo "FAIL: invalid example accepted: $$f"; exit 1; fi; \
		done; \
	done
	@echo "schemas: all valid examples accepted, all invalid examples rejected"

## tools: self-tests of every tool (lock, conformance, tokens, registry); uses Docker for oasdiff
tools:
	$(UV) pytest tools/tests

## canonical: canonical graph schemas, taxonomy, golden fixture rules and determinism (ATLAS-002 CP2)
canonical:
	$(UV) python tools/check_canonical.py

## golden: regenerate the canonical golden fixture (deterministic; commit the result)
golden:
	$(UV) python tools/generate_golden.py

## tokens: WCAG contrast and completeness of design/tokens.json
tokens:
	$(UV) python tools/check_tokens.py design/tokens.json

## registry: requirement, backlog, decision and deviation identifiers
registry:
	$(UV) python tools/check_registry.py

## breaking: contract vs the latest approved release tag (skipped with a notice if none exists)
breaking:
	@base=$$(git tag --list 'contract-v*' --sort=-v:refname | head -n1); \
	if [ -z "$$base" ]; then \
		echo "breaking: no contract-v* release tag yet - check skipped (first release pending owner approval)"; \
	else \
		mkdir -p build; \
		git show "$$base:contracts/openapi/atlas-api.yaml" > build/contract-base.yaml; \
		echo "breaking: comparing against $$base"; \
		$(UV) python tools/contract_conformance.py breaking \
			--base build/contract-base.yaml --revision contracts/openapi/atlas-api.yaml; \
	fi
