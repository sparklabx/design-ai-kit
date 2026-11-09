# VectorCraft — headless build

## Run

```bash
python3 -E build.py steps.json out.vectorcraft      # script writes steps JSON (+ a document.save step)
vectorcraft-cli run --commands steps.json --export /tmp/preview.png       # render to look at
vectorcraft-cli run --in out.vectorcraft --export a.ai --export a.psd --export a.png --export a.jpg   # on approval
vectorcraft-cli run --in out.vectorcraft --scale 2 --export a@2x.png
```

## Live preview for the user (one tab, always current)

After each headless rebuild, refresh the user's app view through the GUI MCP — close the stale tab, open the new file:

1. `inspect_document` / `document.activate {index}` to find the tab whose `path` is the working file.
2. `file.close {index}` that tab (it is unmodified; if `dirty: true` the user edited it — **stop and ask**).
3. `open_file {path}`.

Never `file.revert` for this (it only reloads modified documents). Never open a new tab per round.

No GUI MCP in this agent? Add it (stdio server `"$VC" mcp`, full path from Step 0), keeping any servers already there:

- Claude Code: `claude mcp add -s user vectorcraft -- "$VC" mcp`
- Antigravity / others with an `mcpServers` JSON (Antigravity: `~/.gemini/config/mcp_config.json`, may be empty):
  merge `"vectorcraft": {"command": "<VC>", "args": ["mcp"]}` into `mcpServers`.

It loads when the agent restarts — tell the user. Until then, after a rebuild that changes what the user is looking
at, open the file with the OS (macOS `open <file>.vectorcraft`) and tell the user to close the stale tab first.

## Hand-off to Adobe

| Deliver | Opens in | Editable there | Baked |
|---|---|---|---|
| `.ai` (PDF-compatible, default) | Illustrator | vectors, gradients, clipping, embedded images; text stays text if fonts installed (may split per line) | live effects (shadow, blur, glow, warp) |
| `.psd` (`options.maxEditability: true` → one layer per object, named) | Photoshop | layer order, position, opacity, blend | everything is pixels, text included |
| `.pdf` / `.eps` / `.svg` | any | vectors | effects |

Ship the font files with the `.ai`. VectorCraft also **opens** `.ai/.psd/.pdf/.eps`, so a designer's Adobe file can come back.

- `steps.json` = array of `{"command": id, "params": {...}}`. `"$N.id"` / `"$N.ids.0"` reference step N's result.
- Each run is a fresh document: the script is the source of truth. Overwrite the same `.vectorcraft`.
- **Use headless, not the GUI-connected MCP**, for edits. The user switches tabs in the app; GUI commands then hit
  the wrong document. If you must drive the GUI, start every batch with `document.activate {index}` and
  `select_tool selection` (with the Type tool active, `edit.clear` deletes characters and canvas clicks create
  "Sample copy…" text objects).
- After a headless rebuild, refresh the user's view (below) so they never save a stale tab over the new file.

## Commands that matter

| Need | Command |
|---|---|
| New doc | `file.new {name,width,height,units:"Pixels",colorMode:"rgb",rasterEffectsPpi:150}` |
| Layer | `layer.setProps {name}` (first) · `layer.new {name, top:true}` |
| Shapes | `shape.rectangle {x,y,width,height,radius?}` · `shape.ellipse` · `shape.star {cx,cy,radius1,radius2,points}` · `path.create {d}` |
| Paint (selection) | `paint.setFill {color}|{gradient:{kind,start,end,stops}}|{none:true}` · `paint.setStroke` · `stroke.set {weight,cap,join,dash}` |
| Props | `object.setProps {id?, name, opacity, blend}` |
| Effects | `effect.apply {effect, params}` — `blur.gaussian {radius}`, `stylize.dropShadow {mode,opacity,x,y,blur,color}`, `stylize.outerGlow`, `warp.arc {bend}` |
| Text | `text.create {x,y,text,size,font,style,color,justify,rotation?}` (x,y = baseline; justify center centres on x) |
| Images | `file.place {path, rect:[x,y,w,h]}` then `links.embed` |
| Clip | `select.set {ids}` → `object.clippingMask.make` (top object clips) |
| Order | `object.arrange.sendToBack|bringToFront` |

## Gotchas

- `file.place` of an **SVG fits the content bbox, not the viewBox** — make the viewBox tight or compute rects from content.
- PNG placed with `rect` keeps the full canvas incl. transparent margins — measure the **alpha bbox** (Pillow) and
  compute positions from it (`x = cx − centerPx·k`, `y = bottom − bboxBottomPx·k`).
- Fonts: install `.ttf` into `~/Library/Fonts` (static instances; make one from a variable font with
  `fontTools.varLib.instancer`). Check `text.create` result for a `warning` (fallback font).
- Stock "PSD with transparent background" often has the checkerboard **baked in** (3 channels, no alpha):
  export to PNG, then run a background remover.
- A full-bleed image that is zoomed or offset **must be clipped to the artboard** (rectangle W×H on top →
  `object.clippingMask.make`); otherwise the app shows the artboard edge as a line ("khung line") although the
  export looks clean. `scene_template.py` does this.
- `shape.ellipse {rotation}` was ignored once — rotate after drawing with `object.rotate {angle}`.
- Closed loops drawn as Bézier paths (bow loops) may not render — use ellipses.
- Gradient on text works: select the text → `paint.setFill {gradient:{kind:"linear", angle:-90, stops:[…]}}`.
- **No colour emoji** in text: render the emoji with Pillow (`/System/Library/Fonts/Apple Color Emoji.ttc`, size 160,
  `embedded_color=True`), tint it to the text colour if asked, and place it as a PNG between two text runs
  (measure the runs with `ImageFont.getlength`).
- Outlines, 3D extrusion, brush-ink texture and arched text: not native — `scripts/lettering.py` (fonts.md §Choosing).
- Python: run scripts with `python3 -E` (not `-I`: it hides user-site Pillow/numpy; there is no `-P` on 3.9) and
  never from inside a folder holding downloaded files.
- Exports are big (PSD 2–5 MB, @2x PNG 3 MB). Don't export intermediates.
