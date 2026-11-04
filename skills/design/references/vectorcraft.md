# VectorCraft — headless build

## Run

```bash
python3 -I build.py steps.json out.vectorcraft      # script writes steps JSON (+ a document.save step)
vectorcraft-cli run --commands steps.json --export /tmp/preview.png       # render to look at
vectorcraft-cli run --in out.vectorcraft --export a.psd --export a.png --export a.jpg   # on approval
vectorcraft-cli run --in out.vectorcraft --scale 2 --export a@2x.png
```

- `steps.json` = array of `{"command": id, "params": {...}}`. `"$N.id"` / `"$N.ids.0"` reference step N's result.
- Each run is a fresh document: the script is the source of truth. Overwrite the same `.vectorcraft`.
- **Use headless, not the GUI-connected MCP**, for edits. The user switches tabs in the app; GUI commands then hit
  the wrong document. If you must drive the GUI, start every batch with `document.activate {index}` and
  `select_tool selection` (with the Type tool active, `edit.clear` deletes characters and canvas clicks create
  "Sample copy…" text objects).
- After a headless rebuild, tell the user to close/reopen the file in the app; do not let them save the stale tab over it.

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
- Exports are big (PSD 2–5 MB, @2x PNG 3 MB). Don't export intermediates.
