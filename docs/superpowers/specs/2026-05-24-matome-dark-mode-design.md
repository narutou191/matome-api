# MATOME Simulador — Dark Mode Design Spec

**Date:** 2026-05-24  
**Project:** MATOME Simulador (Roukin/Consolidação de Dívidas)  
**Status:** Approved

---

## Overview

Convert the MATOME debt consolidation simulator from light theme to dark mode with intensified accent colors. Dark theme applies to both interactive UI and exported PNG screenshots.

**Success Criteria:**
- All text readable with pure white (#ffffff) on pure black (#0d0d0d)
- Accent colors (gold/blue) intensified and vibrant in dark context
- Inputs, buttons, and interactive elements clearly visible
- PNG export maintains dark theme styling
- No functionality changes — UI/UX remains identical

---

## Color Palette

### Old → New Mapping

| Element | Old | New | Ratio (WCAG) |
|---------|-----|-----|--------------|
| Background | #f5f3ef | #0d0d0d | 19.26:1 ✓ |
| Text (primary) | #2d2d2d | #ffffff | 19.26:1 ✓ |
| Gold (accent) | #c9a84c | #e0b85c | Intensified |
| Blue (accent) | #7ab4d4 | #6cc4e8 | Intensified |
| Borders/Dividers | #d0c8b8 | #333333 | Visible on dark |
| Card/Section BG | — | #1a1a1a | Subtle depth |
| Input border | #d0c8b8 | #555555 | Contrast on dark |
| Label text | #888888 | #aaaaaa | Contrast ✓ |

**WCAG AA Compliance:** All color pairs meet minimum 4.5:1 contrast ratio for normal text.

---

## Implementation Scope

### CSS Variables to Update
- `--bg`: #f5f3ef → #0d0d0d
- `--dark`: #2d2d2d → #1a1a1a (subtle, not pure black for cards)
- `--text`: #2d2d2d → #ffffff
- `--label`: #888888 → #aaaaaa
- `--border`: #d0c8b8 → #333333
- `--divider`: #e0d8c8 → #333333
- `--gold`: #c9a84c → #e0b85c
- `--gold-dim`: #8a6e28 → #a89030
- `--blue`: #7ab4d4 → #6cc4e8
- `--blue-dim`: #4a8aaa → #4a9fb5

### Before/After Color Blocks (for seções)
- Before BG: #fff5f5 → #1a0f0f (subtle red tint)
- After BG: #f5fff8 → #0f1a16 (subtle green tint)

### Input Fields
- Background: transparent (unchanged)
- Border: #d0c8b8 → #555555
- Focus border: --gold (new)
- Text: #2d2d2d → #ffffff

### Buttons
- `.mbtn` (primary): dark bg → #1a1a1a with gold text
- `.mbtn.sec` (secondary): border → #555555 with white text

### Special Elements
- Header (`.mh`): #2d2d2d bg → #0d0d0d (darker)
- Modal calc box (`.mcalc`): #000000 (pure black) — unchanged, already dark
- Economy box (`.meco`): #000000 → #0d0d0d for consistency

---

## PNG Export Behavior

When user clicks "📸 Baixar Imagem PNG":
- `onclone` callback hides buttons (unchanged)
- Shows header (`.mpdfh`) with dark styling
- Shows footer (`.mpdff`) with dark styling
- Canvas renders dark theme directly — no conversion needed
- File downloads as `MATOME-[nome]-[data].png`

No CSS `@media print` changes required — dark theme applies to both screen and export.

---

## Testing Checklist

- [ ] All text (labels, values, headers) readable at #ffffff on #0d0d0d
- [ ] Gold accent (#e0b85c) visible in headers and highlights
- [ ] Blue accent (#6cc4e8) visible in section B elements
- [ ] Input fields show clear border on focus
- [ ] Buttons clickable and text readable
- [ ] Inputs accept text and show values clearly
- [ ] Calculations update and display correctly
- [ ] PNG export includes header, calc box, economy box, footer
- [ ] No layout shift or missing elements in dark mode

---

## Files to Modify

- `matome/matome-simulador-roukin.html` — update `<style>` section CSS variables and color values

## Rollout

Single commit: "feat: dark mode theme for MATOME simulator with intensified accents"

No breaking changes. Existing HTML/JS/logic untouched.
