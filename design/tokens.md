# Atlas Bright Design Tokens and Accessibility Rules

**Status:** All values **proposed** (DEC-065 palette approval pending). The rules in this document are approved for ATLAS-001 (spec v0.2.1 §7). · **Machine-readable source:** `design/tokens.json` (normative values). · **Validation:** `tools/check_tokens.py` verifies every contrast pair declared in `tokens.json`.

The frontend never hand-copies these values. It generates CSS from `tokens.json` at its pinned `specs.lock` commit (DEC-099). Trust and evidence-state styling is **not** defined here; it depends on DEC-056.

## 1. Design direction

- **Bright and light only.** `color-scheme: light`. No dark-mode rules until a dark theme is approved (DEC-011).
- White and very light blue-grey surfaces. Vivid colour is reserved for entity identity, status and focus, used with restraint.
- Diagrams get the space. Chrome is quiet: neutral lines, few borders, subtle elevation.

## 2. Token groups

| Group | Tokens | Notes |
|---|---|---|
| Surfaces | `color.surface.{app, canvas, subtle, raised}` | `canvas #F8FAFE` is the drawing field |
| Ink | `color.ink.{primary, secondary, muted, inverse}` | All three text inks are ≥ 4.5:1 on every surface |
| Lines | `color.line.subtle`, `color.line.strong` | `subtle` is decorative only. Control and container boundaries use `strong` (≥ 3:1) |
| Brand and focus | `color.brand.{primary, primary-hover, on-primary}`, `color.focus.ring` | One accent colour for actions, links, selection and focus |
| Entities | `color.entity.<kind>.{accent, text, tint}` for application, api, compute, messaging, data, security, capability | `accent` = fills, borders and icons only. `text` = the text-safe variant. `tint` = 10% background |
| Relationships | `color.relationship.{default, selected, muted}`; `border-width.relationship-{default, selected}` | Neutral slate by default; brand blue when selected; all ≥ 3:1 on surfaces. Category accents reuse entity accents |
| Status | `color.status.<success\|warning\|danger\|info>.{fg, tint}` | Always shown with an icon **and** a text label (§4) |
| Typography | `typography.font-family.{sans, mono}`, `typography.size.{xs…2xl}` (12–32 px), `typography.weight`, `typography.line-height` | System font stack: no external font origins |
| Spacing and sizing | `space.*` (4-px scale), `size.control-{sm,md,lg}` (24/32/40 px), `size.icon-*` | `control-sm` is the minimum target size |
| Shape and depth | `radius.*`, `border-width.*`, `focus.ring-{width,offset}`, `elevation.{1,2,3}` | |
| Motion | `motion.duration.{fast, base, slow}` (120/160/220 ms), `motion.easing.*`, `motion.reduced.*` | See §5 |

## 3. Accessibility rules (WCAG 2.2 AA target)

| ID | Rule | WCAG |
|---|---|---|
| AR-01 | Text contrast ≥ **4.5:1**; large text (≥ 24 px, or ≥ 18.66 px bold) ≥ 3:1 | 1.4.3 |
| AR-02 | Non-text contrast ≥ **3:1** for control boundaries, focus indicators, relationship lines and meaningful icons | 1.4.11 |
| AR-03 | Entity **accent** colours never colour text. Text in an entity hue uses `color.entity.<kind>.text` | 1.4.3 |
| AR-04 | Colour is never the only carrier of meaning. Status = icon + text (§4); selection = colour + 2 px weight change | 1.4.1 |
| AR-05 | Visible focus on every interactive element. House rule: `focus.ring-width` 2 px solid `color.focus.ring`, offset 2 px, ≥ 3:1 against adjacent colours. Never `outline: none` without a replacement; focus never obscured | 2.4.7, 2.4.11 |
| AR-06 | All functionality keyboard-operable in a logical order; no keyboard traps; a skip link to `main` | 2.1.1, 2.1.2, 2.4.1 |
| AR-07 | Interactive targets ≥ 24 × 24 CSS px (`size.control-sm`) | 2.5.8 |
| AR-08 | Semantics: `lang`; one `h1` per page; landmarks; native `<button>`/`<a>`; asynchronous status in an `aria-live="polite"` region | 1.3.1, 4.1.2, 4.1.3 |
| AR-09 | Minimum 12 px text (captions/metadata), 14 px default UI, 16 px long-form. Layout survives 200% zoom and text-spacing overrides; simple pages reflow to 320 CSS px | 1.4.4, 1.4.10, 1.4.12 |
| AR-10 | Light only (`color-scheme: light`). Under `forced-colors: active`, focus indicators and status icons stay visible (system colours) | 1.4.11 |

The thresholds are machine-readable in `tokens.json` → `thresholds`. Every pair in `contrast_pairs` is checked by `tools/check_tokens.py`.

## 4. Status indicators: never colour alone

| Status | Icon (shape carries meaning) | Text label | Colour tokens |
|---|---|---|---|
| Success / ready | Check mark in a circle | e.g. "Ready" | `color.status.success.*` |
| Warning / degraded | Triangle with exclamation mark | e.g. "Degraded: Redis" | `color.status.warning.*` |
| Danger / error / unreachable | Octagon or circle with a cross | e.g. "Unreachable" | `color.status.danger.*` |
| Info / neutral | Circle with "i" | e.g. "Diagnostics disabled" | `color.status.info.*` |

Icons are decorative to assistive technology (`aria-hidden`); the text label carries the meaning.

## 5. Motion and reduced motion

- Transitions use only `motion.duration.*` and `motion.easing.*`, on opacity, colour and shadow. ATLAS-001 has no layout-shifting animation. The maximum duration is 220 ms.
- Under `@media (prefers-reduced-motion: reduce)`:
  - every transition and animation duration becomes `motion.reduced.duration` (0.01 ms);
  - `transform` is removed (`motion.reduced.transform: none`);
  - smooth scrolling is disabled.
- No auto-playing animation longer than 5 s, and nothing flashes more than three times per second (2.2.2, 2.3.1).

## 6. Change rules

- Every value stays `"status": "proposed"` until DEC-065 is approved. Approval changes the status, not silently the value.
- A new foreground/background combination used in UI must be added to `contrast_pairs` first, so CI proves it.
- Renaming or removing a token is breaking for the frontend (`contracts/compatibility.md` §7).
