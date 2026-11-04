"""Promo banner builder: config JSON → VectorCraft steps JSON (+ document.save).

    python3 -I build_template.py config.json steps.json out.vectorcraft
    vectorcraft-cli run --commands steps.json --export /tmp/preview.png

Layout (from the brand's own poster system): light base, awning stripes, brand-colour wave with faint
woven pattern, script headline, offer pill + numeral stamp, condition badge, product group with glow,
particles and shadows, info + CTA on the wave. Every position lives in the config — edit, re-run, look.
"""
import json
import sys

cfg = json.load(open(sys.argv[1]))
W, H = cfg["canvas"]
P = cfg["palette"]          # base, brand, brand_light, accent, text_on_brand, muted_on_brand
F = cfg["fonts"]            # sans, script
S = []


def add(cmd, params=None):
    S.append({"command": cmd, "params": params or {}})
    return len(S) - 1


def paint(fill, name, opacity=None, effects=(), stroke=None):
    add("paint.setFill", fill)
    add("paint.setStroke", stroke or {"none": True})
    add("object.setProps", {"name": name, **({"opacity": opacity} if opacity is not None else {})})
    for e in effects:
        add("effect.apply", e)


def rect(x, y, w, h, fill, name, radius=None, **kw):
    i = add("shape.rectangle", {"x": x, "y": y, "width": w, "height": h, **({"radius": radius} if radius else {})})
    paint(fill, name, **kw)
    return i


def ellipse(x, y, w, h, fill, name, **kw):
    i = add("shape.ellipse", {"x": x, "y": y, "width": w, "height": h})
    paint(fill, name, **kw)
    return i


def text(x, y, s, size, style, color, font=None, justify="left", **extra):
    return add("text.create", {"x": x, "y": y, "text": s, "size": size, "font": font or F["sans"], "style": style,
                               "color": color, "justify": justify, **extra})


blur = lambda r: {"effect": "blur.gaussian", "params": {"radius": r}}
shadow = lambda o, y, b, c=P["shadow"]: {"effect": "stylize.dropShadow", "params": {"mode": "multiply", "opacity": o, "x": 0, "y": y, "blur": b, "color": c}}
col = lambda c: {"color": c}

add("file.new", {"name": cfg["name"], "width": W, "height": H, "units": "Pixels", "colorMode": "rgb", "rasterEffectsPpi": 150})

# ── background ─────────────────────────────────────────────────────────────
add("layer.setProps", {"name": "BACKGROUND"})
rect(0, 0, W, H, col(P["base"]), "Base")
bg = cfg["background"]
if bg.get("awning"):
    sw = bg["awning"]["stripe"]
    for k in range(0, W // sw + 1, 2):
        rect(k * sw, 0, sw, bg["awning"]["height"], col(P["brand"]), "Awning stripe")
wave = bg["wave"]  # SVG path, closed, brand colour
add("path.create", {"d": wave}); paint(col(P["brand"]), "Brand wave")
if bg.get("pattern"):  # faint woven dots + strands, clipped to the wave
    pt, first = bg["pattern"], len(S)
    step, top = pt["step"], pt["top"]
    for gx in range(0, W + step, step):
        for gy in range(top, H + step, step):
            ellipse(gx - pt["dot"] / 2, gy - pt["dot"] / 2, pt["dot"], pt["dot"], col("#FFFFFF"), "Pattern dot")
    for gx in range(step // 2, W + step, step):
        rect(gx - 1, top, 2, H - top, col("#FFFFFF"), "Pattern strand")
    for gy in range(top + step // 2, H + step, step):
        rect(0, gy - 1, W, 2, col("#FFFFFF"), "Pattern strand")
    add("path.create", {"d": wave}); paint({"none": True}, "Pattern clip")
    add("select.set", {"ids": [f"${i}.id" for i in range(first, len(S)) if S[i]["command"].startswith(("shape.", "path."))]})
    cm = add("object.clippingMask.make")
    add("object.setProps", {"id": f"${cm}.id", "name": "Pattern", "opacity": pt["opacity"]})
if bg.get("ribbon"):
    add("path.create", {"d": bg["ribbon"]}); paint({"none": True}, "Ribbon", stroke=col(P["accent"]))
    add("stroke.set", {"weight": 6, "cap": "round"})

# ── products ───────────────────────────────────────────────────────────────
add("layer.new", {"name": "PRODUCTS", "top": True})
pr = cfg["products"]
if pr.get("glow"):
    g = pr["glow"]
    ellipse(*g, {"gradient": {"kind": "radial", "stops": [{"offset": 0, "color": "#FFFFFF", "opacity": 0.55}, {"offset": 1, "color": "#FFFFFF", "opacity": 0}]}}, "Glow")
if pr.get("particles"):
    add("file.place", {"path": pr["particles"]["path"], "rect": pr["particles"]["rect"]})
    add("links.embed")
for it in sorted(pr["items"], key=lambda i: i.get("z", 0)):  # back first
    # px → pt: image is placed at its full canvas; centre_px / bottom_px come from the alpha bbox
    k, cx, bottom = it["k"], it["cx"], it["bottom"]
    size = it["size_px"]
    x, y = cx - it["center_px"] * k, bottom - it["bottom_px"] * k
    sw = it.get("shadow_w", 0.55 * size * k)
    ellipse(cx - sw / 2 + pr.get("shadow_dx", 16), bottom - 13, sw, 28, col(P["shadow"]), "Shadow", opacity=50, effects=[blur(10)])
    add("file.place", {"path": it["path"], "rect": [x, y, size * k, size * k]})
    add("links.embed"); add("object.setProps", {"name": it.get("name", "Product")})
for sp in cfg.get("sparkles", []):
    add("shape.star", {"cx": sp[0], "cy": sp[1], "radius1": sp[2], "radius2": sp[2] * 0.28, "points": 4})
    paint(col(P["accent"]), "Sparkle")

# ── text + CTA ─────────────────────────────────────────────────────────────
add("layer.new", {"name": "TEXT + CTA", "top": True})
if cfg.get("logo"):
    add("file.place", {"path": cfg["logo"]["path"], "rect": cfg["logo"]["rect"]})
h = cfg["headline"]
text(*h["xy"], h["text"], h["size"], "Bold", P["brand"], F["script"])
o = cfg["offer"]  # pill with two lines + numeral stamp
px, py, pw, ph = o["pill"]
rect(px, py, pw, ph, col(P["brand"]), "Offer pill border", radius=ph / 2, effects=[shadow(40, 12, 22)])
rect(px + 6, py + 6, pw - 12, ph - 12, col("#FFFFFF"), "Offer pill", radius=ph / 2 - 6)
for (tx, ty, s) in o["lines"]:
    text(tx, ty, s, o["line_size"], "ExtraBold", P["brand"])
scx, scy, sr = o["stamp"]
ellipse(scx - sr, scy - sr, 2 * sr, 2 * sr, col(P["brand"]), "Stamp", effects=[shadow(45, 10, 18)])
ellipse(scx - sr + 14, scy - sr + 14, 2 * sr - 28, 2 * sr - 28, {"none": True}, "Stamp ring", stroke=col(P["accent"]))
add("stroke.set", {"weight": 4, "dash": [2, 7], "cap": "round"})
text(scx + 3, scy + 0.32 * o["numeral_size"], o["numeral"], o["numeral_size"], "ExtraBold", "#FFFFFF", justify="center", rotation=8)
if cfg.get("badge"):  # condition badge (top corner)
    b = cfg["badge"]
    add("shape.ellipse", {"x": b["rect"][0], "y": b["rect"][1], "width": b["rect"][2], "height": b["rect"][3], "rotation": -6})
    paint(col(P["brand"]), "Condition badge", effects=[shadow(30, 6, 12)])
    for (ty, s, size, style, c) in b["lines"]:
        text(b["rect"][0] + b["rect"][2] / 2, ty, s, size, style, P[c], justify="center")
i = cfg["info"]
dx, dy, dw = i["date_pill"]
rect(dx, dy, dw, 58, col(P["brand_light"]), "Date pill", radius=29)
text(dx + dw / 2, dy + 38, i["date"], 26, "Bold", P["brand"], justify="center")
ellipse(dx, i["bullet_y"] - 12, 10, 10, col(P["accent"]), "Bullet")
text(dx + 22, i["bullet_y"], i["bullet"], 20, "Regular", P["text_on_brand"])
cx_, cy_, cw = i["cta"]
rect(cx_, cy_, cw, 74, col("#FFFFFF"), "CTA", radius=37, effects=[shadow(35, 8, 14)])
text(cx_ + cw / 2, cy_ + 46, i["cta_text"], 26, "ExtraBold", P["brand"], justify="center")
text(dx, H - 40, i["disclaimer"], 16, "Regular", P["muted_on_brand"])

add("select.none")
if len(sys.argv) > 3:
    add("document.save", {"path": sys.argv[3]})
json.dump(S, open(sys.argv[2], "w"), ensure_ascii=False)
print(sys.argv[2], len(S), "steps")
