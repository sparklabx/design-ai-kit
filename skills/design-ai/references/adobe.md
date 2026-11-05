# Illustrator / Photoshop engine (macOS)

> **UNTESTED in the apps.** `steps_to_svg.py` is verified against VectorCraft renders (a flat promo with a colour wave and a
> photo-scene banner: mean pixel diff < 1/255 via `rsvg-convert`). `adobe.py` (open/export through ExtendScript) was
> written without Illustrator or Photoshop installed. On first use, tell the user, and check the first export
> closely: fonts, shadows, clipping, image placement. Note what breaks in "Gotchas" below.

Same build scripts and configs as VectorCraft — only the last hop changes:

```bash
"$PY" -E scripts/build_template.py my.json steps.json            # or scene_template.py / the project script
"$PY" -E scripts/steps_to_svg.py steps.json 02_PSD/<name>.svg    # the working file (overwrite every run)
"$PY" -E scripts/adobe.py open illustrator 02_PSD/<name>.svg     # refresh the user's tab (live preview)
rsvg-convert 02_PSD/<name>.svg -o /tmp/preview.png              # self-check render, if installed
```

No `rsvg-convert`? Self-check with `adobe.py export <app> 02_PSD/<name>.svg /tmp/preview/<name>` and look at the PNG.

`adobe.py open` closes the tab showing that SVG only if it is unmodified; if it prints "unsaved edits", the user
edited it in the app — **stop and ask** (same rule as the VectorCraft live preview).

## Deliver (approval only)

`"$PY" -E scripts/adobe.py export illustrator|photoshop 02_PSD/<name>.svg 03_Export/<name>` →
`<name>.ai` or `.psd`, `.png`, `@2x.png`, `.jpg`. Move the `.ai`/`.psd` into `02_PSD/`.

| Engine | What the native file keeps |
|---|---|
| Illustrator | Vectors, live text, gradients, clipping groups; shadows/blur as SVG filters; inlined SVG logos stay vector |
| Photoshop | **One flat layer** (Photoshop rasterises SVG on open); `@2x.png` is an upscale. Prefer Illustrator or VectorCraft when layers matter |

## Limits of `steps_to_svg.py`

Supported: everything `build_template.py` and `scene_template.py` emit — rect/ellipse/star/path, text (one line per
`text.create`), solid/linear/radial fills, strokes (weight/cap/join/dash), placed PNG/JPG/SVG, drop shadow, gaussian
blur, opacity, clipping masks, `object.rotate`. Anything else (warp, outer glow, multi-line text…) stops with an
error: bake that effect into a `decor` PNG instead.

Shortcuts: shadow blend mode (multiply) is ignored; fonts are written as `'PostScriptName', 'Family'` + CSS weight —
check that Illustrator picked the right weight.

## Gotchas

(none recorded yet — add what the first real run shows)
