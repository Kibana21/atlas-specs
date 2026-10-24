"""Validate design/tokens.json: WCAG contrast of every declared pair, plus completeness (FR-08).

Usage:
    python check_tokens.py [TOKENS_JSON]   (default: design/tokens.json)

Checks:
  * every contrast pair meets its WCAG threshold (thresholds.text / large_text / non_text)
  * required groups, entity kinds (accent/text/tint) and status kinds (fg/tint) exist
  * every token has a value and a status of "proposed" or "approved"; colours are #RRGGBB
  * light colour scheme only; motion <= 220 ms with a reduced-motion rule; minimum font size,
    target size and focus-ring width respect the declared thresholds
Exit status 0 when valid; 1 with one line per finding ("CODE: message") otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "design" / "tokens.json"
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
ENTITY_KINDS = ("application", "api", "compute", "messaging", "data", "security", "capability")
STATUS_KINDS = ("success", "warning", "danger", "info")
COLOR_GROUPS = {"surface": ("app", "canvas", "subtle", "raised"), "ink": ("primary", "secondary", "muted", "inverse"),
                "line": ("subtle", "strong"), "brand": ("primary", "primary-hover", "on-primary"), "focus": ("ring",),
                "relationship": ("default", "selected", "muted")}
TOP_GROUPS = ("meta", "thresholds", "color", "typography", "space", "size", "radius", "border-width", "focus",
              "elevation", "motion", "contrast_pairs")
MAX_MOTION_MS = 220.0


@dataclass(frozen=True)
class Finding:
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(a: str, b: str) -> float:
    hi, lo = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _resolve(tokens: dict[str, Any], ref: str) -> Any:
    node: Any = tokens
    for part in ref.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(ref)
        node = node[part]
    return node


def _leaves(node: Any, path: str) -> list[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict) and "value" in node:
        return [(path, node)]
    if isinstance(node, dict):
        out: list[tuple[str, dict[str, Any]]] = []
        for key, child in node.items():
            out += _leaves(child, f"{path}.{key}" if path else key)
        return out
    return []


def _px(value: str) -> float:
    match = re.fullmatch(r"([0-9.]+)px", str(value))
    return float(match.group(1)) if match else -1.0


def _ms(value: str) -> float:
    match = re.fullmatch(r"([0-9.]+)ms", str(value))
    return float(match.group(1)) if match else -1.0


def check_tokens(tokens: dict[str, Any]) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    for group in TOP_GROUPS:
        if group not in tokens:
            findings.append(Finding("MISSING_GROUP", f"top-level group {group!r} is missing"))
    if findings:
        return findings, 0
    meta, thresholds, color = tokens["meta"], tokens["thresholds"], tokens["color"]
    if meta.get("color_scheme") != "light":
        findings.append(Finding("COLOR_SCHEME", f"meta.color_scheme must be 'light', got {meta.get('color_scheme')!r}"))

    for group, names in COLOR_GROUPS.items():
        for name in names:
            if name not in color.get(group, {}):
                findings.append(Finding("MISSING_TOKEN", f"color.{group}.{name}"))
    for kind in ENTITY_KINDS:
        for part in ("accent", "text", "tint"):
            if part not in color.get("entity", {}).get(kind, {}):
                findings.append(Finding("MISSING_TOKEN", f"color.entity.{kind}.{part}"))
    for kind in STATUS_KINDS:
        for part in ("fg", "tint"):
            if part not in color.get("status", {}).get(kind, {}):
                findings.append(Finding("MISSING_TOKEN", f"color.status.{kind}.{part}"))

    leaves = _leaves({k: v for k, v in tokens.items() if k not in ("meta", "thresholds", "contrast_pairs")}, "")
    for path, leaf in leaves:
        if leaf.get("status") not in ("proposed", "approved"):
            findings.append(Finding("TOKEN_STATUS", f"{path} has status {leaf.get('status')!r}"))
        if path.startswith("color.") and not HEX.match(str(leaf.get("value"))):
            findings.append(Finding("COLOR_FORMAT", f"{path} = {leaf.get('value')!r} is not #RRGGBB"))

    for name, leaf in tokens["motion"].get("duration", {}).items():
        if not 0 < _ms(leaf["value"]) <= MAX_MOTION_MS:
            findings.append(Finding("MOTION", f"motion.duration.{name} = {leaf['value']} must be within (0, {MAX_MOTION_MS:g}ms]"))
    reduced = tokens["motion"].get("reduced", {})
    if "duration" not in reduced or _ms(reduced["duration"]["value"]) > 0.01:
        findings.append(Finding("MOTION", "motion.reduced.duration must exist and be <= 0.01ms"))
    if reduced.get("transform", {}).get("value") != "none":
        findings.append(Finding("MOTION", "motion.reduced.transform must be 'none'"))

    sizes = [_px(v["value"]) for v in tokens["typography"].get("size", {}).values()]
    if not sizes or min(sizes) < thresholds["font_size_min_px"]:
        findings.append(Finding("TYPOGRAPHY", f"smallest font size {min(sizes, default=0):g}px < {thresholds['font_size_min_px']}px"))
    target = _px(tokens["size"].get("control-sm", {}).get("value", ""))
    if target < thresholds["target_size_min_px"]:
        findings.append(Finding("TARGET_SIZE", f"size.control-sm {target:g}px < {thresholds['target_size_min_px']}px"))
    ring = _px(tokens["focus"].get("ring-width", {}).get("value", ""))
    if ring < thresholds["focus_ring_min_width_px"]:
        findings.append(Finding("FOCUS", f"focus.ring-width {ring:g}px < {thresholds['focus_ring_min_width_px']}px"))

    checked = 0
    for pair in tokens["contrast_pairs"]:
        try:
            fg, bg = _resolve(tokens, pair["fg"])["value"], _resolve(tokens, pair["bg"])["value"]
            minimum = float(thresholds[pair["min"]])
        except KeyError as exc:
            findings.append(Finding("UNKNOWN_REFERENCE", f"contrast pair {pair} references unknown {exc}"))
            continue
        ratio = contrast_ratio(fg, bg)
        checked += 1
        if ratio + 1e-9 < minimum:
            findings.append(Finding("CONTRAST", f"{pair['fg']} {fg} on {pair['bg']} {bg} = {ratio:.2f}:1 < {minimum}:1 ({pair['purpose']})"))
    return findings, checked


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else DEFAULT_PATH
    try:
        tokens = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"TOKENS_UNREADABLE: {path}: {exc}", file=sys.stderr)
        return 1
    findings, checked = check_tokens(tokens)
    for finding in findings:
        print(finding, file=sys.stderr)
    if not findings:
        leaves = len(_leaves({k: v for k, v in tokens.items() if k not in ("meta", "thresholds", "contrast_pairs")}, ""))
        print(f"OK: {leaves} tokens valid; {checked} contrast pairs meet their WCAG thresholds")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
