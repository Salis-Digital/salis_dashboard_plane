# Cashatti Brand Theme

Fork brand tokens for light/dark themes, mapped from the [Enhanced Login UI/UX](https://www.figma.com/design/5Ji6bAkauQDQb7TeTN6cDw/Enhanced-Login-UI-UX?node-id=58-2) Figma board.

## Product name

Fork product name is **Salis Plane** (`PRODUCT_NAME` in [`packages/constants/src/metadata.ts`](../packages/constants/src/metadata.ts)).

## Seed

| Token          | Value                                                                                   |
| -------------- | --------------------------------------------------------------------------------------- |
| Brand primary  | `#DD4A48` → `oklch(0.6139 0.1838 25.02)`                                                |
| Brand gradient | `linear-gradient(168deg, #e05550 0%, #da4c45 60%, #c94040 100%)` via `--brand-gradient` |

Defined in [`packages/tailwind-config/variables.css`](../packages/tailwind-config/variables.css). All apps import this through `@plane/tailwind-config`.

## Figma → Plane token mapping

| Role              | Figma                             | Plane token / class                                                                           |
| ----------------- | --------------------------------- | --------------------------------------------------------------------------------------------- |
| Brand primary     | `#DD4A48` / `#DA4C45`             | `--brand-default` → `bg-accent-primary`, `text-accent-primary`, `border-accent-strong`, links |
| Brand gradient    | `#E05550` → `#DA4C45` → `#C94040` | `--brand-gradient` (for login chrome)                                                         |
| Soft accent fill  | light pink-red                    | `--brand-100` / `bg-accent-subtle` (`#ffe8e4`)                                                |
| Hover / active    | darker red                        | `--brand-900` / `--brand-1000`                                                                |
| On-brand text     | `#FFFFFF`                         | `--txt-on-color` / `text-on-color`                                                            |
| Light card        | `#FFFFFF`                         | `--bg-surface-1` (unchanged neutrals)                                                         |
| Light muted track | `#F3F4F6`                         | `--bg-layer-*` / neutrals (unchanged)                                                         |
| Light border      | `#E5E7EB`                         | `--border-subtle*` (unchanged)                                                                |
| Light tertiary    | `#99A1AF`                         | `--txt-tertiary` (unchanged)                                                                  |
| Light body        | `#364153`                         | `--txt-primary` (unchanged)                                                                   |
| Dark surfaces     | charcoal                          | existing `@variant dark` neutrals (unchanged)                                                 |

**Scope:** brand/accent only. Canvas / surface / layer neutrals stay Plane’s greys (already close to Figma).

## Light vs dark

- **Light:** `--brand-100`…`--brand-1200` and `--brand-default` generated from `#DD4A48` (OKLCH hue ~25°).
- **Dark:** inverted brand scale for subtle/hover stops; `--brand-default` kept at the seed so primary buttons stay vivid red on charcoal (matches Figma dark login).

Mode switch remains `data-theme` on `<html>` (`light` / `dark` / contrast variants).

## Usage

Prefer semantic classes, not raw hex:

```tsx
<button className="bg-accent-primary hover:bg-accent-primary-hover text-on-color">
  Continue
</button>
<a className="text-accent-primary hover:text-accent-primary">Forgot password?</a>
```

For login header chrome later:

```tsx
<div style={{ backgroundImage: "var(--brand-gradient)" }} />
```

## Updating the brand

1. Regenerate OKLCH scales from a new hex (see `packages/utils/src/theme/` palette helpers).
2. Replace `--brand-*` in `variables.css` (light `:root` and `@variant dark`).
3. Replace leftover `#dd4a48` defaults in constants, theme picker, PDF/chart helpers, and propel icons.
