"""Validate a consumer's specs.lock against an atlas-specs clone (ATLAS-001 FR-05, spec §6.4).

Usage:
    python check_specs_lock.py LOCKFILE [--specs-dir DIR] [--main-ref REF] [--release]

Rules (contracts/compatibility.md §2-§3):
  * specs_commit is a full 40-character lowercase SHA of a commit reachable from main;
    branch names, tag names, short SHAs and unknown SHAs are rejected.
  * every referenced file exists at that commit.
  * contract_version equals info.version of the contract at that commit.
  * --release additionally requires a contract-v<contract_version> tag on that commit
    and a plain X.Y.Z version (no pre-release suffix).

Exit status 0 when valid; 1 with one line per finding ("CODE: message") otherwise.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REQUIRED_KEYS = ("specs_repo", "specs_commit", "api_contract", "schemas_dir", "tokens", "contract_version")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
HEXISH = re.compile(r"^[0-9a-fA-F]+$")
RELEASE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def _git(specs_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(specs_dir), *args], capture_output=True, text=True, check=False)


def _ref_exists(specs_dir: Path, ref: str) -> bool:
    return _git(specs_dir, "show-ref", "--verify", "--quiet", ref).returncode == 0


def _resolve_main(specs_dir: Path, main_ref: str) -> str | None:
    for candidate in (f"refs/heads/{main_ref}", f"refs/remotes/origin/{main_ref}"):
        if _ref_exists(specs_dir, candidate):
            return candidate
    return None


def check_lock(lock_path: Path, specs_dir: Path, main_ref: str = "main", release: bool = False) -> list[Finding]:
    try:
        data = yaml.safe_load(lock_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [Finding("LOCK_UNREADABLE", f"cannot read {lock_path}: {exc.__class__.__name__}")]
    if not isinstance(data, dict):
        return [Finding("LOCK_SCHEMA", "lock file must be a YAML mapping")]

    missing = [k for k in REQUIRED_KEYS if k not in data]
    unknown = sorted(set(data) - set(REQUIRED_KEYS))
    bad_types = [k for k in REQUIRED_KEYS if k in data and not isinstance(data[k], str)]
    findings: list[Finding] = []
    if missing:
        findings.append(Finding("LOCK_SCHEMA", f"missing keys: {', '.join(missing)}"))
    if unknown:
        findings.append(Finding("LOCK_SCHEMA", f"unknown keys: {', '.join(unknown)}"))
    if bad_types:
        findings.append(Finding("LOCK_SCHEMA", f"values must be strings (quote them): {', '.join(bad_types)}"))
    if findings:
        return findings
    if data["specs_repo"] != "atlas-specs":
        return [Finding("LOCK_SCHEMA", f"specs_repo must be 'atlas-specs', got {data['specs_repo']!r}")]

    sha = data["specs_commit"]
    if not FULL_SHA.match(sha):
        if _ref_exists(specs_dir, f"refs/heads/{sha}") or _ref_exists(specs_dir, f"refs/remotes/origin/{sha}"):
            return [Finding("LOCK_BRANCH_NAME", f"specs_commit {sha!r} is a branch name; pin a full commit SHA")]
        if _ref_exists(specs_dir, f"refs/tags/{sha}"):
            return [Finding("LOCK_TAG_NAME", f"specs_commit {sha!r} is a tag name; pin the full commit SHA it points to")]
        if HEXISH.match(sha) and sha.lower() == sha and len(sha) < 40:
            return [Finding("LOCK_SHORT_SHA", f"specs_commit {sha!r} is a short SHA ({len(sha)} chars); use all 40")]
        return [Finding("LOCK_INVALID_SHA", f"specs_commit {sha!r} is not a 40-character lowercase hex SHA")]

    if _git(specs_dir, "cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        return [Finding("LOCK_UNKNOWN_SHA", f"commit {sha} does not exist in {specs_dir} (fetch, or fix the pin)")]

    main = _resolve_main(specs_dir, main_ref)
    if main is None:
        findings.append(Finding("LOCK_NO_MAIN_REF", f"cannot find {main_ref!r} or origin/{main_ref} to verify reachability"))
    elif _git(specs_dir, "merge-base", "--is-ancestor", sha, main).returncode != 0:
        findings.append(Finding("LOCK_NOT_ON_MAIN", f"commit {sha} is not reachable from {main}; pin a reviewed main commit"))

    for key in ("api_contract", "tokens"):
        if _git(specs_dir, "cat-file", "-e", f"{sha}:{data[key]}").returncode != 0:
            findings.append(Finding("LOCK_FILE_MISSING", f"{key} {data[key]!r} does not exist at {sha}"))
    tree = _git(specs_dir, "cat-file", "-t", f"{sha}:{data['schemas_dir']}")
    if tree.returncode != 0 or tree.stdout.strip() != "tree":
        findings.append(Finding("LOCK_FILE_MISSING", f"schemas_dir {data['schemas_dir']!r} is not a directory at {sha}"))
    if findings:
        return findings

    contract = _git(specs_dir, "show", f"{sha}:{data['api_contract']}")
    try:
        version = str((yaml.safe_load(contract.stdout) or {}).get("info", {}).get("version"))
    except yaml.YAMLError:
        return [Finding("LOCK_CONTRACT_INVALID", f"{data['api_contract']} at {sha} is not valid YAML")]
    if version != data["contract_version"]:
        return [Finding("LOCK_VERSION_MISMATCH",
                        f"contract_version {data['contract_version']!r} != info.version {version!r} at {sha}")]

    if release:
        if not RELEASE_VERSION.match(version):
            return [Finding("LOCK_NOT_RELEASE", f"release builds need a released version, got pre-release {version!r}")]
        tags = _git(specs_dir, "tag", "--points-at", sha).stdout.split()
        if f"contract-v{version}" not in tags:
            return [Finding("LOCK_NOT_RELEASE", f"commit {sha} carries no contract-v{version} release tag")]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("lockfile", type=Path)
    parser.add_argument("--specs-dir", type=Path, default=Path("../atlas-specs"))
    parser.add_argument("--main-ref", default="main")
    parser.add_argument("--release", action="store_true", help="require an approved contract-v* release tag")
    args = parser.parse_args(argv)
    findings = check_lock(args.lockfile, args.specs_dir, args.main_ref, args.release)
    for finding in findings:
        print(finding, file=sys.stderr)
    if not findings:
        print(f"OK: {args.lockfile} pins a valid atlas-specs commit" + (" (release)" if args.release else ""))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
