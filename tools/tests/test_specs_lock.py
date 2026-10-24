"""Tests for check_specs_lock.py (AC-02): valid pins pass; every bad pin fails distinctly."""

from __future__ import annotations

from pathlib import Path

import pytest

from check_specs_lock import check_lock, main
from conftest import git

CONTRACT = "openapi: 3.1.0\ninfo:\n  title: Atlas API\n  version: {version}\npaths: {{}}\n"


def _commit(repo: Path, version: str, message: str) -> str:
    (repo / "contracts" / "openapi").mkdir(parents=True, exist_ok=True)
    (repo / "contracts" / "schemas").mkdir(parents=True, exist_ok=True)
    (repo / "design").mkdir(exist_ok=True)
    (repo / "contracts" / "openapi" / "atlas-api.yaml").write_text(CONTRACT.format(version=version))
    (repo / "contracts" / "schemas" / "error.v1.json").write_text("{}\n")
    (repo / "design" / "tokens.json").write_text("{}\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def specs(tmp_path: Path) -> dict[str, object]:
    repo = tmp_path / "atlas-specs"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    released = _commit(repo, "0.1.0", "release 0.1.0")
    git(repo, "tag", "contract-v0.1.0", released)
    dev = _commit(repo, "0.2.0-dev.1", "additive change")
    git(repo, "switch", "-q", "-c", "feature/x")
    unmerged = _commit(repo, "0.2.0-dev.2", "unmerged change")
    git(repo, "switch", "-q", "main")
    return {"repo": repo, "released": released, "dev": dev, "unmerged": unmerged}


def _lock(tmp_path: Path, **overrides: str) -> Path:
    fields = {
        "specs_repo": "atlas-specs",
        "specs_commit": "0" * 40,
        "api_contract": "contracts/openapi/atlas-api.yaml",
        "schemas_dir": "contracts/schemas",
        "tokens": "design/tokens.json",
        "contract_version": "0.1.0",
    }
    fields.update(overrides)
    path = tmp_path / "specs.lock"
    path.write_text("".join(f'{k}: "{v}"\n' for k, v in fields.items()))
    return path


def _codes(findings: list[object]) -> list[str]:
    return [f.code for f in findings]  # type: ignore[attr-defined]


def test_valid_release_commit(specs: dict, tmp_path: Path) -> None:
    lock = _lock(tmp_path, specs_commit=specs["released"])
    assert check_lock(lock, specs["repo"]) == []
    assert check_lock(lock, specs["repo"], release=True) == []


def test_valid_development_commit_on_main(specs: dict, tmp_path: Path) -> None:
    lock = _lock(tmp_path, specs_commit=specs["dev"], contract_version="0.2.0-dev.1")
    assert check_lock(lock, specs["repo"]) == []


def test_branch_name_rejected(specs: dict, tmp_path: Path) -> None:
    assert _codes(check_lock(_lock(tmp_path, specs_commit="main"), specs["repo"])) == ["LOCK_BRANCH_NAME"]


def test_tag_name_rejected(specs: dict, tmp_path: Path) -> None:
    assert _codes(check_lock(_lock(tmp_path, specs_commit="contract-v0.1.0"), specs["repo"])) == ["LOCK_TAG_NAME"]


def test_short_sha_rejected(specs: dict, tmp_path: Path) -> None:
    short = str(specs["released"])[:12]
    assert _codes(check_lock(_lock(tmp_path, specs_commit=short), specs["repo"])) == ["LOCK_SHORT_SHA"]


@pytest.mark.parametrize("value", ["not-a-sha", "G" * 40, "ABCDEF0123456789ABCDEF0123456789ABCDEF01"])
def test_invalid_sha_rejected(specs: dict, tmp_path: Path, value: str) -> None:
    assert _codes(check_lock(_lock(tmp_path, specs_commit=value), specs["repo"])) == ["LOCK_INVALID_SHA"]


def test_unknown_sha_rejected(specs: dict, tmp_path: Path) -> None:
    assert _codes(check_lock(_lock(tmp_path, specs_commit="a" * 40), specs["repo"])) == ["LOCK_UNKNOWN_SHA"]


def test_version_mismatch_rejected(specs: dict, tmp_path: Path) -> None:
    lock = _lock(tmp_path, specs_commit=specs["released"], contract_version="0.2.0")
    assert _codes(check_lock(lock, specs["repo"])) == ["LOCK_VERSION_MISMATCH"]


def test_commit_not_on_main_rejected(specs: dict, tmp_path: Path) -> None:
    lock = _lock(tmp_path, specs_commit=specs["unmerged"], contract_version="0.2.0-dev.2")
    assert _codes(check_lock(lock, specs["repo"])) == ["LOCK_NOT_ON_MAIN"]


def test_missing_file_at_commit_rejected(specs: dict, tmp_path: Path) -> None:
    lock = _lock(tmp_path, specs_commit=specs["released"], api_contract="contracts/openapi/missing.yaml")
    assert _codes(check_lock(lock, specs["repo"])) == ["LOCK_FILE_MISSING"]


def test_schema_errors_rejected(specs: dict, tmp_path: Path) -> None:
    path = tmp_path / "specs.lock"
    path.write_text('specs_repo: "atlas-specs"\nspecs_commit: "x"\nextra: "y"\n')
    codes = _codes(check_lock(path, specs["repo"]))
    assert codes == ["LOCK_SCHEMA", "LOCK_SCHEMA"]


def test_unquoted_version_rejected(specs: dict, tmp_path: Path) -> None:
    path = _lock(tmp_path, specs_commit=specs["released"])
    path.write_text(path.read_text().replace('contract_version: "0.1.0"', "contract_version: 0.1"))
    assert _codes(check_lock(path, specs["repo"])) == ["LOCK_SCHEMA"]


def test_release_requires_tag(specs: dict, tmp_path: Path) -> None:
    lock = _lock(tmp_path, specs_commit=specs["dev"], contract_version="0.2.0-dev.1")
    assert _codes(check_lock(lock, specs["repo"], release=True)) == ["LOCK_NOT_RELEASE"]


def test_cli_exit_codes(specs: dict, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = _lock(tmp_path, specs_commit=specs["released"])
    assert main([str(good), "--specs-dir", str(specs["repo"]), "--release"]) == 0
    bad = _lock(tmp_path, specs_commit="main")
    assert main([str(bad), "--specs-dir", str(specs["repo"])]) == 1
    assert "LOCK_BRANCH_NAME" in capsys.readouterr().err
