# Fonts and text colour — pick, check, install

> **Defaults, not yet client-tested.** Sourced: contrast thresholds and luminance (WCAG 2.x SC 1.4.3), Vietnamese
> coverage (Google Fonts metadata + `fontcheck`), licence (OFL). The rest is common typography practice or our own
> estimate (sizes, spacing, colour counts). When a job confirms or overturns a rule, update it (Step 8).

## Rules

1. **Brand font first.** Brand guide › the brand's own posters › the site CSS (`font-family`, a Google Fonts
   `<link>`). Proprietary or unlicensed for this use (SF Pro, custom brand faces) → the closest open font from the
   table below, and say so in the reply.
2. **Two families at most** (display + text), **three weights at most**. Hierarchy comes from size and weight,
   not from a third font.
3. **Pair by contrast**: script or serif display + sans text. Never two scripts, never two similar sans.
4. **Script = decoration**: ≤ 4 words, one line, never all caps, never the offer, price, date or CTA (principles §Hierarchy).
   Only the title gets a script; greetings, wishes and body copy stay upright — script and italics there were rejected.
5. **Offer and numbers** in the heaviest sans weight (ExtraBold/Black); check the digits and `%`, `K`, `₫` look right.
   Lists of numbers (tracklist, price list, schedule) need **lining figures**: old-style figures (Cormorant) make
   `1001` and `01…13` look jumbled.
6. **Sizes at 1080 px wide**: nothing under 20 px; body/footer ≥ 24 px; offer ≥ 80 px.
7. **Vietnamese**: every font must pass `image_tools.py fontcheck` (full alphabet + the copy). Caps with stacked
   marks (Ặ Ầ Ỗ Ữ) need line spacing ≥ 1.2× size — measure with `textw`, check the render for marks touching the line above.
8. **Licence**: Google Fonts are OFL (commercial use OK). Record the source; ship the TTFs with the `.ai`.
9. Put the pairing in each Step 3 direction ("type: Playfair Display + Be Vietnam Pro").

## Choosing the title font (the slow part — do it this way)

1. **Start from the brand's own lettering** (logo, official poster, packaging): name its kind — hand-inked script,
   retro sign script, Roman caps, geometric sans — and search inside that kind. Fonts picked by mood alone took
   many rounds; the client signed off only when the title matched the official lettering.
2. **Show a sheet, never one font**: 6–8 candidates, numbered, the real copy on the real background (crop of the
   render), all `fontcheck`-clean. One-by-one proposals cost a round each; from a sheet the client picks in one.
3. **Font and effect are two choices**: "the effect is fine, the font isn't artistic enough" is common. Keep the
   effect, swap the font (another sheet); or keep the font, show the effects side by side.
4. **Effects VectorCraft can't draw** (3D sign extrusion, brush-pen ink, arch): `scripts/lettering.py sign|ink` →
   transparent PNG → place as `decor`. Zoom the PNG to check every Vietnamese mark. Thin scripts need `--bold 2–3`;
   an arch needs a rise of ~0.5× the font size on a long line to read as a curve.
5. **One type system across sides/pages**: front and back of one piece use the same title font (effect may differ);
   a different face on the back read as "two designs".

## Text colour

1. **Brand palette + white + one brand-tinted dark** (deep green/brown/navy, not `#000`) — no new hues for text.
2. **Three text colours at most**: dark for copy, one accent for the offer, white on solid blocks.
3. **The offer gets the strongest pair** (accent on light, or white on a brand block). Nothing else uses the accent
   at that size.
4. **Contrast on the real background** (WCAG AA): ≥ 4.5:1, or ≥ 3:1 for large text — at 1080 px wide that is ≥ 65 px,
   or ≥ 50 px bold (a post shows ~2.7× smaller on a phone). Measure every line on the render:
   `image_tools.py contrast preview.png x,y,w,h #hex <size> [bold]`. Light-tint text (a pale brand
   green on wood or cream) is the usual fail — use the dark tone for small lines.
5. **Text on a photo**: place it on a calm area first; if it still fails, a white halo or a solid pill — not a thick
   outline, not a darker photo.
6. **Gradient text** only at 60 px and above, two close tints of one hue; both ends must pass rule 4 — check each
   end against the background colour with `contrast #end #background <size> [bold]` (render mode can't isolate it).
7. Never put two colours of equal brightness together (red on green, orange on pink): they vibrate. A pair that fails
   in greyscale fails.

## Shortlist (all have Google Fonts' Vietnamese subset)

| Mood / category | Display | Text |
|---|---|---|
| F&B fresh, casual | Dancing Script, Pacifico, Charm | Be Vietnam Pro, Nunito |
| Premium, beauty, Tết sang | Playfair Display, Cormorant Garamond, Fraunces | Be Vietnam Pro, Montserrat |
| Tech, product (Apple-like) | Inter or Manrope — one family, weight contrast | same |
| Sale, retail, bold | Montserrat Black, Big Shoulders, Oswald | Be Vietnam Pro, Barlow |
| Kids, playful | Baloo 2, Grandstander | Nunito |
| Handwritten, friendly | Patrick Hand, Pangolin | Nunito, Lexend |
| Hand-inked / calligraphic script (music, gift, fairy-tale) | Mea Culpa, Imperial Script, Great Vibes, Alex Brush, Moon Dance, Ballet (instance `opsz=72`), Corinthia, Ephesis, Lavishly Yours | Cormorant Garamond (upright) |
| Retro sign script (bold, for 3D effects) | Lobster, Sansita Swashed, Playball | Be Vietnam Pro |

All scripts in the last two rows passed `fontcheck` (full Vietnamese).

**No Vietnamese — don't use for Vietnamese copy:** Abril Fatface, Cinzel, Cinzel Decorative, Sora, Marcellus, Forum,
Damion, Yellowtail, Norican, Courgette, Kaushan Script, Grand Hotel, Yesteryear. Most of these still render a short
title with a few marks (`Ánh Sáng`) and fail on `ơ ư ạ ả…` — always check the full alphabet, not just the copy.
Cinzel is fine for Latin-only small caps (artist name, "THE 1ST ALBUM").
`fontcheck` catches others. Yeseva One has no `₫`; Playfair Display and Lora have no `℗`. Google's subset flag is not proof.

## Install a Google font

```bash
curl -sL -o /tmp/F-VF.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/<family>/<File>%5Bwght%5D.ttf"   # list: api.github.com/repos/google/fonts/contents/ofl/<family>
"$PY" -E -m fontTools.varLib.instancer /tmp/F-VF.ttf wght=800 --update-name-table -o 01_Material/Fonts/F-ExtraBold.ttf
"$PY" -E scripts/image_tools.py fontcheck 01_Material/Fonts/F-ExtraBold.ttf "<all copy>"
cp 01_Material/Fonts/F-ExtraBold.ttf ~/Library/Fonts/   # then text.create {font: "F", style: "ExtraBold"}
```

`<family>` is the lowercase name without spaces (`bevietnampro`). Static families ship `F-Bold.ttf` directly.
Run the instancer from outside the download folder.

- `--update-name-table` fails on some fonts ("Cannot find Axis Values", e.g. Cinzel `wght=500`): instance without it
  and set name IDs 1/2/4/6/16/17 yourself (fontTools `name.setName`), or the app shows it as "Regular".
- Fonts with an optical-size axis (`opsz`, e.g. Ballet) default to the small text size: instance the display end
  (`opsz=72`) for titles, and give it its own family name so it doesn't clash with the default instance.
