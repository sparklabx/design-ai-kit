"""Photo-scene banner builder (brands whose posters are one photo + lettering: café chains, F&B, retail KVs).
Config JSON → VectorCraft steps JSON (+ document.save).

    python3 -E scene_template.py config.json steps.json out.vectorcraft
    vectorcraft-cli run --commands steps.json --export /tmp/preview.png

Layers: SCENE (full-bleed photo, zoomed about an anchor, ALWAYS clipped to the artboard) · TEXT + LOGO
(logo, outlined lettering, copy lines, pills, decor images, footer). Seasonal touches (snow, leaves, stars,
ribbons) are `decor`: transparent PNGs placed by rect, so the template stays theme-free. No thin frames by design.
"""
import json
import sys

cfg = json.load(open(sys.argv[1]))
W, H = cfg["canvas"]
S = []


def add(cmd, params=None):
    S.append({"command": cmd, "params": params or {}})
    return len(S) - 1


shadow = lambda o, x, y, b, c: {"effect": "stylize.dropShadow", "params": {"mode": "multiply", "opacity": o, "x": x, "y": y, "blur": b, "color": c}}
halo = lambda o, b: {"effect": "stylize.dropShadow", "params": {"mode": "normal", "opacity": o, "x": 0, "y": 0, "blur": b, "color": "#FFFFFF"}}


def text(t):
    add("text.create", {"x": t["xy"][0], "y": t["xy"][1], "text": t["text"], "size": t["size"], "font": t["font"],
                        "style": t.get("style", "Regular"), "color": t["color"], "justify": t.get("justify", "left")})
    if t.get("halo"):  # [opacity %, blur] white glow so copy reads on a busy photo
        add("effect.apply", halo(*t["halo"]))
    if t.get("gradient"):  # [top colour, bottom colour]
        add("paint.setFill", {"gradient": {"kind": "linear", "angle": -90, "stops": [{"offset": 0, "color": t["gradient"][0]}, {"offset": 1, "color": t["gradient"][1]}]}})


def lettering(t):
    # outlined lettering: white copy with a white stroke + soft shadow behind, clean fill on top
    text({**t, "color": t.get("outline_color", "#FFFFFF"), "halo": None, "gradient": None})
    add("paint.setStroke", {"color": t.get("outline_color", "#FFFFFF")}); add("stroke.set", {"weight": t.get("outline", 10), "join": "round"})
    add("effect.apply", shadow(30, 3, 5, 8, t.get("shadow", "#000000")))
    text(t)


def place(path, rect, name, effects=()):
    add("file.place", {"path": path, "rect": rect})
    add("links.embed"); add("object.setProps", {"name": name})
    for e in effects:
        add("effect.apply", e)


add("file.new", {"name": cfg["name"], "width": W, "height": H, "units": "Pixels", "colorMode": "rgb", "rasterEffectsPpi": 150})

# ── scene: zoom about (anchor_x, bottom); clip to the artboard so the app never shows a frame line ──
add("layer.setProps", {"name": "SCENE"})
sc = cfg["scene"]
k, ax = sc.get("zoom", 1.0), sc.get("anchor_x", W / 2)
img = add("file.place", {"path": sc["path"], "rect": [ax * (1 - k), H * (1 - k), W * k, H * k]})
add("links.embed"); add("object.setProps", {"name": sc.get("name", "Scene")})
clip = add("shape.rectangle", {"x": 0, "y": 0, "width": W, "height": H})
add("select.set", {"ids": [f"${img}.ids.0", f"${clip}.id"]})
add("object.clippingMask.make")

add("layer.new", {"name": "TEXT + LOGO", "top": True})
if cfg.get("logo"):
    place(cfg["logo"]["path"], cfg["logo"]["rect"], "Logo")
for t in cfg.get("lettering", []):
    lettering(t)
for t in cfg.get("lines", []):
    text(t)
for p in cfg.get("pills", []):  # solid rounded block behind a line of copy (dates, price, CTA)
    x, y, w, h = p["rect"]
    add("shape.rectangle", {"x": x, "y": y, "width": w, "height": h, "radius": h / 2})
    add("paint.setFill", {"color": p["color"]}); add("paint.setStroke", {"none": True})
    if p.get("shadow"):
        add("effect.apply", shadow(35, 0, 4, 10, p["shadow"]))
    text(p["text"])
for d in cfg.get("decor", []):  # transparent PNGs: seasonal props, stickers, texture caps on lettering…
    place(d["path"], d["rect"], d.get("name", "Decor"), [shadow(*d["shadow"])] if d.get("shadow") else ())
for t in cfg.get("footer", []):
    text(t)

add("select.none")
if len(sys.argv) > 3:
    add("document.save", {"path": sys.argv[3]})
json.dump(S, open(sys.argv[2], "w"), ensure_ascii=False)
print(sys.argv[2], len(S), "steps")
