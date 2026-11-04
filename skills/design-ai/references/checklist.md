# Self-check before showing a render

Render to PNG, view the whole image, then **zoomed crops** (`scripts/image_tools.py sheet` for side-by-side candidates).

- [ ] Offer is the first thing you see; script headline does not touch it (≥ 16 px gap).
- [ ] No text collides with products, particles or edges (check descenders, swashes, diacritics).
- [ ] No large empty zone; nothing crammed against the canvas edge (≥ 50 px margin for text).
- [ ] Every logo on a product: centred, fully visible, looks printed (curved, lit, not a flat sticker).
- [ ] One light direction everywhere; shadows agree; back items darker than front.
- [ ] Colours from the brand palette only; background fresh/light unless the brand is dark.
- [ ] No visible seams where an image meets vector background (zoom the boundary).
- [ ] Fonts rendered (no fallback warning); Vietnamese diacritics correct.
- [ ] Placeholder copy listed in the reply; asset sources/licences noted; credits spent reported.
- [ ] After any structural change (zoom/crop an image, add/remove a frame or clip): look at an **app screenshot**
      (`ui_screenshot` / `render_preview` in the GUI), not only the export — artboard-edge lines show only there.
- [ ] Zoom **2×** on every seam between an edited region and the untouched original (tone shift, cut line, a
      sagging thin line left half-fixed next to a kept box).
- [ ] Empty space measured, not guessed: `image_tools.py emptiness preview.png` — every flagged cell is filled or
      justified in the reply.
- [ ] A fix changes **only** the reported defect, evenly along its whole length; no fade, gradient or new effect the
      client did not ask for.
- [ ] Only one working file; preview rendered to a temp folder; no export unless approved or requested.
