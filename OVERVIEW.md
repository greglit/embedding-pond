# Embedding Pond Overview

## Mental Model

Each waterlily represents a single input item:

- `sourceType`: `text` or `image`
- `content`: the original text, or a local URL for the chosen image
- `embedding`: a normalized CLIP vector
- `shapePath`: an SVG path derived from the embedding values
- `fill`, `outline`: colors derived deterministically from the embedding (constrained to a pink-to-near-white palette)
- `x`, `y`: 2D coordinates produced by PCA over all lilies

The UI is intentionally simple: grow a lily (compute an embedding), preview it, then plant it into the pond. Hover for a quick peek; click for details.

## User Flow

1. Click `New Waterlily` (or `Grow your first Waterlily!` when the pond is empty).
2. In the modal (`src/components/LilyCreator.vue`), choose Text or Image and provide input.
3. Click `Grow waterlily`.
4. The app computes an embedding and shows an “embedding numbers” animation.
   - First lily is intentionally slower (~8s) so the process is legible.
   - Later lilies are faster (~2–3s) so the app stays snappy.
5. A preview appears (lily shape + lily pads).
6. Click `Plant waterlily` to place it into the pond (manual planting; no auto-plant).
7. Hover any lily for a lightweight preview popover.
8. Click any lily to open the detailed inspector popover.
9. Optional: open the bottom-left Info panel for plain-language explanations.

## Data Flow (Code)

- `src/components/LilyCreator.vue` emits `grow` with `{ type, data }`.
- `src/App.vue` handles `grow`:
  - `computeEmbedding(type, data)` -> embedding vector
  - `embeddingToPath(embedding)` -> lily SVG path
  - derive deterministic colors from embedding
  - keep the result as a “draft” until the user plants
- Planting in `src/App.vue`:
  - append the draft lily to the list
  - `computePcaLayout(lilies.map(l => l.embedding))` -> `{x,y}` for each lily
  - animate the new lily from the “plant” origin into its PCA target
  - persist final `{x,y}` into the stored lily list
- `src/components/PondScene.vue`:
  - renders lilies as positioned buttons centered in the viewport
  - emits `hover` on pointer enter/leave and `select` on click
- `src/components/LilyPopover.vue`:
  - click mode: shows the original input and the full embedding vector (with a scrollable values box)
  - hover mode: shows a compact preview only (no embedding values; no close button)
- `src/components/InfoPopover.vue`:
  - centered, light-background panel with neutral/scientific explanations

## Layout Details

- PCA is recomputed on every planting so positions are consistent for all lilies.
- PCA output is normalized into screen space using the current `window.innerWidth/innerHeight`.

## Rendering Notes

- Lily shapes are radial polygons: each embedding component maps to a radius at a fixed angle.
- Lily pad geometry is shared between pond + preview via `src/utils/lilyPad.ts`.
- Decorative lily pads, drift, and ripples are generated procedurally for atmosphere.
- Ripples are triggered by both water clicks and planting a lily.
- A subtle “ambient” ripple is seeded on load near the `New Waterlily` button so the scene doesn’t start perfectly still.
- `src/components/CausticsCanvas.vue` contains an experimental Three.js ripple + caustics shader canvas (not currently mounted by default).
