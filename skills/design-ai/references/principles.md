# Design principles (learned from real client rounds)

Each rule below came from a client rejecting a draft. Apply them before the client has to say it.

## Brand

- **Match the brand's own marketing style first**, then improve. Ask for / find one of their recent posters and
  mirror its system (background tone, curve shapes, script + sans pairing, badge style). Drafts invented from
  scratch ("dark cinematic", "lava") were rejected as "quá lố" (overdone).
- Use the brand's **current** identity: packaging and logo change on rebrands. Check the date of your references.
- Download 2–3 of the brand's own posters as references yourself; it worked better than describing a style.
- A logo pulled from the brand website is usually a 512 px PNG, often white-on-transparent: recolour it, and say it
  is a web file, not a brand master.
- Brand palette only. An off-palette accent (gold/orange on a green brand) reads as "not pretty / not matching".
  To make something pop, use **contrast inside the palette** (white on brand colour, a darker/lighter brand tint),
  size and placement — not a new hue.

## Colour & light

- **Fresh beats dark** for F&B/retail: light cream/white base + brand-colour shapes. Heavy dark backgrounds read
  as "màu quá đậm, chưa tươi".
- **One light source**, consistent across every element: highlights on the light side, shadows cast away from it,
  back objects slightly darker than front ones.
- Lighting effects stay **subtle**. If the client notices the effect before the product, it is too strong.
- Never stack effects to fix a weak composition (rays + halo + bokeh + mist = "quá lố").

## Hierarchy

- The offer (e.g. "MUA 1 TẶNG 1", the discount, the date) is the **largest, highest-contrast** element.
  A script headline is decoration: one line, above or beside the offer, never overlapping it.
- Big number inside an offer badge: make it a **stamp/seal** (filled brand-colour circle, white numeral,
  slight tilt, drop shadow) overlapping the pill edge.
- Keep a clear gap (≥ 16 px at 1080) between every text block and its neighbours; script fonts have tall
  ascenders and swashes — measure, don't guess.

## Space

- No large empty zones. If a corner is empty, move a secondary element there (condition badge, logo, sparkle
  cluster) or raise the brand-colour wave / enlarge the product. Balanced, not crowded.
- Product group is the visual anchor: 40–60 % of the canvas, overlapping the colour boundary (wave) so the
  two halves connect.

## Product shots

- Several products: front hero bigger and lower, others behind, spaced so **each logo is fully visible**
  and centred on its own product.
- Logo on a product must be **part of the photo** (printed/curved/lit/with condensation). A flat sticker or
  vector logo on top always reads as "không dính vào cốc".
- Logo size on packaging ≈ 30–40 % of product width. Bigger looks fake.

## Frames & effects

- Thin decorative frames, dotted rings, hairline outlines around badges read as "vô duyên" (cheap). Prefer solid
  colour blocks, or no frame at all.
- **One effect per element.** When the client asks for "special effects", offer a short menu and recommend at most 2.
- A texture on lettering (snow, drip, glow): build it from a 2× mask of the text so it follows the letters, keep
  diacritics clear, and place it as a `decor` PNG.

## Rhythm / "đơn điệu"

- Add life with **on-theme particles** (ice cubes, leaves, beans, fruit slices) around the product, behind it,
  never over text.
- A faint brand pattern (≤ 5 % opacity) in large flat colour areas.
- A soft glow behind the product group to separate it from the background.

## Copy (Vietnamese)

- Use fonts with full Vietnamese coverage: `image_tools.py fontcheck` (choosing, pairing and text colour: `fonts.md`).
- Short lines; one idea per line; date in a pill; one CTA button.
