"""VectorCraft steps JSON → one SVG, so the same build script feeds Illustrator and Photoshop (both open SVG).

    python3 -E steps_to_svg.py steps.json out.svg

Covers the commands the kit's templates emit. Anything else stops with an error — never silently dropped.
Images are embedded (PNG/JPG as data URIs, SVG logos inlined so they stay vector). Layers become top-level groups.
"""
import base64
import json
import math
import os
import re
import sys
from xml.sax.saxutils import escape, quoteattr

WEIGHT = {"thin": 100, "extralight": 200, "light": 300, "regular": 400, "medium": 500, "semibold": 600,
          "bold": 700, "extrabold": 800, "black": 900}


class El:
    def __init__(self, tag, attrs=None, text=None, raw=None, bbox=None):
        self.tag, self.attrs, self.text, self.raw, self.bbox = tag, dict(attrs or {}), text, raw, bbox
        self.children, self.parent, self.wrapper = [], None, False

    def add(self, child, at=None):
        child.parent = self
        self.children.insert(len(self.children) if at is None else at, child)
        return child

    def outer(self):  # an element plus the filter groups wrapped around it
        e = self
        while e.parent and e.parent.wrapper:
            e = e.parent
        return e

    def xml(self):
        if self.raw is not None:
            return self.raw
        a = "".join(f" {k}={quoteattr(str(v))}" for k, v in self.attrs.items())
        body = escape(self.text) if self.text is not None else "".join(c.xml() for c in self.children)
        return f"<{self.tag}{a}>{body}</{self.tag}>" if body else f"<{self.tag}{a}/>"


steps = json.load(open(sys.argv[1]))
defs, layers, objs, used_ids = El("defs"), [], {}, set()
cur, sel, W, H = None, [], 612, 792
n_defs = 0


def new_id(prefix):
    global n_defs
    n_defs += 1
    return f"{prefix}{n_defs}"


def name_id(name):
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "obj"
    i, nid = 1, base
    while nid in used_ids:
        i += 1
        nid = f"{base}_{i}"
    used_ids.add(nid)
    return nid


def new_layer(name):
    g = El("g", {"id": name_id(name), "data-name": name})
    layers.append(g)
    return g


def ref(r):  # "$N.id" / "$N.ids.0" → the object created by step N
    m = re.fullmatch(r"\$(\d+)\.ids?(?:\.0)?", r)
    if not m or int(m.group(1)) not in objs:
        sys.exit(f"steps_to_svg: unresolved reference {r}")
    return objs[int(m.group(1))]


def place_obj(i, el):
    global cur
    layer.add(el)
    objs[i] = cur = el
    el.attrs.setdefault("fill", "#FFFFFF")  # app defaults: white fill, 1pt black stroke
    el.attrs.setdefault("stroke", "#000000")


def gradient(g):
    gid = new_id("grad")
    stops = "".join(f'<stop offset="{s["offset"]}" stop-color="{s["color"]}" stop-opacity="{s.get("opacity", 1)}"/>'
                    for s in g["stops"])
    if g.get("kind") == "radial":
        defs.add(El("radialGradient", {"id": gid}, raw=f'<radialGradient id="{gid}">{stops}</radialGradient>'))
    else:
        a = math.radians(g.get("angle", 0))  # angle like Illustrator: 0 = left→right, -90 = top→bottom
        dx, dy = math.cos(a) / 2, -math.sin(a) / 2
        defs.add(El("linearGradient", {}, raw=f'<linearGradient id="{gid}" x1="{.5 - dx:.4f}" y1="{.5 - dy:.4f}" '
                                               f'x2="{.5 + dx:.4f}" y2="{.5 + dy:.4f}">{stops}</linearGradient>'))
    return f"url(#{gid})"


def shadow_filter(p, blur_scale):
    fid = new_id("fx")
    op = p.get("opacity", 75) / 100
    # shortcut: blend mode (multiply/normal) is ignored; shadow composites normally, close on light backgrounds
    defs.add(El("filter", {}, raw=(
        f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">'
        f'<feGaussianBlur in="SourceAlpha" stdDeviation="{p.get("blur", 5) * blur_scale:.2f}"/>'
        f'<feOffset dx="{p.get("x", 0)}" dy="{p.get("y", 0)}" result="o"/>'
        f'<feFlood flood-color="{p.get("color", "#000000")}" flood-opacity="{op}"/>'
        f'<feComposite in2="o" operator="in" result="s"/>'
        f'<feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')))
    return fid


def blur_filter(r):
    fid = new_id("fx")
    defs.add(El("filter", {}, raw=f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
                                  f'<feGaussianBlur stdDeviation="{r:.2f}"/></filter>'))
    return fid


def wrap_filter(el, fid):  # several effects stack: each one wraps the previous result
    o = el.outer()
    parent, at = o.parent, o.parent.children.index(o)
    parent.children.remove(o)
    g = parent.add(El("g", {"filter": f"url(#{fid})"}), at)
    g.wrapper = True
    g.add(o)


def image(path, rect):
    x, y, w, h = rect
    path = os.path.abspath(path)
    box = {"x": x, "y": y, "width": w, "height": h, "preserveAspectRatio": "xMidYMid meet"}
    if path.lower().endswith(".svg"):  # inline so a vector logo stays vector in Illustrator
        src = open(path, encoding="utf-8").read()
        src = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>|<!--.*?-->", "", src, flags=re.S).strip()
        root = re.match(r"<svg\b[^>]*>", src).group(0)
        if "viewBox" not in root:
            sw, sh = (float(re.search(fr'{k}="([\d.]+)', root).group(1)) for k in ("width", "height"))
            root2 = root[:-1] + f' viewBox="0 0 {sw} {sh}">'
        else:
            root2 = root
        root2 = re.sub(r'\s(width|height|x|y|preserveAspectRatio)="[^"]*"', "", root2)
        root2 = root2[:-1] + "".join(f' {k}="{v}"' for k, v in box.items()) + ">"
        return El("svg", raw=src.replace(root, root2, 1), bbox=(x, y, w, h))
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    data = base64.b64encode(open(path, "rb").read()).decode()
    return El("image", {**box, "xlink:href": f"data:{mime};base64,{data}"}, bbox=(x, y, w, h))


layer = None
for i, st in enumerate(steps):
    c, p = st["command"], st.get("params", {})
    if c == "file.new":
        W, H = p["width"], p["height"]
        layer = new_layer("Layer 1")
    elif c == "layer.setProps":
        layer.attrs["data-name"] = p["name"]
        used_ids.discard(layer.attrs["id"])
        layer.attrs["id"] = name_id(p["name"])
    elif c == "layer.new":
        layer = new_layer(p["name"])
    elif c == "shape.rectangle":
        a = {"x": p["x"], "y": p["y"], "width": p["width"], "height": p["height"]}
        if p.get("radius"):
            a["rx"] = p["radius"]
        place_obj(i, El("rect", a, bbox=(p["x"], p["y"], p["width"], p["height"])))
    elif c == "shape.ellipse":
        cx, cy = p["x"] + p["width"] / 2, p["y"] + p["height"] / 2
        a = {"cx": cx, "cy": cy, "rx": p["width"] / 2, "ry": p["height"] / 2}
        if p.get("rotation"):
            a["transform"] = f"rotate({p['rotation']} {cx} {cy})"
        place_obj(i, El("ellipse", a, bbox=(p["x"], p["y"], p["width"], p["height"])))
    elif c == "shape.star":
        n, r1, r2 = p["points"], p["radius1"], p["radius2"]
        pts = " ".join(f"{p['cx'] + r * math.cos(t):.2f},{p['cy'] + r * math.sin(t):.2f}"
                       for k in range(2 * n) for r, t in [((r1, r2)[k % 2], -math.pi / 2 + k * math.pi / n)])
        place_obj(i, El("polygon", {"points": pts}, bbox=(p["cx"] - r1, p["cy"] - r1, 2 * r1, 2 * r1)))
    elif c == "path.create":
        place_obj(i, El("path", {"d": p["d"]}))
    elif c == "text.create":
        style = p.get("style", "Regular").lower().replace(" ", "")
        # PostScript name first (what Illustrator matches on import), CSS family + weight as the fallback
        ps = p["font"].replace(" ", "") + "-" + p.get("style", "Regular").replace(" ", "")
        a = {"x": p["x"], "y": p["y"], "font-family": f"'{ps}', '{p['font']}'", "font-size": p["size"], "fill": p.get("color", "#000000"),
             "font-weight": WEIGHT.get(style.replace("italic", "") or "regular", 400), "xml:space": "preserve",
             "text-anchor": {"center": "middle", "right": "end"}.get(p.get("justify"), "start"), "stroke": "none"}
        if "italic" in style:
            a["font-style"] = "italic"
        if p.get("rotation"):
            a["transform"] = f"rotate({p['rotation']} {p['x']} {p['y']})"
        if "\n" in p["text"]:
            sys.exit("steps_to_svg: multi-line text not supported yet — one text.create per line")
        place_obj(i, El("text", a, text=p["text"]))
    elif c == "file.place":
        el = image(p["path"], p["rect"])
        layer.add(el)
        objs[i] = cur = el
    elif c in ("links.embed", "document.save"):
        pass  # images are always embedded; the SVG itself is the saved file
    elif c == "object.setProps":
        t = (ref(p["id"]) if p.get("id") else cur).outer()
        if "name" in p:
            t.attrs["id"], t.attrs["data-name"] = name_id(p["name"]), p["name"]
        if "opacity" in p:
            t.attrs["opacity"] = p["opacity"] / 100
    elif c == "paint.setFill":
        if cur.raw is not None:
            sys.exit(f"steps_to_svg: step {i}: cannot paint an inlined SVG")
        cur.attrs["fill"] = "none" if p.get("none") else gradient(p["gradient"]) if "gradient" in p else p["color"]
    elif c == "paint.setStroke":
        cur.attrs["stroke"] = "none" if p.get("none") else p["color"]
    elif c == "stroke.set":
        for k, v in (("weight", "stroke-width"), ("cap", "stroke-linecap"), ("join", "stroke-linejoin")):
            if k in p:
                cur.attrs[v] = p[k]
        if "dash" in p:
            cur.attrs["stroke-dasharray"] = " ".join(map(str, p["dash"]))
        if cur.tag == "text":
            cur.attrs["paint-order"] = "stroke"
    elif c == "effect.apply":
        e, ep = p["effect"], p.get("params", {})
        if e == "stylize.dropShadow":
            wrap_filter(cur, shadow_filter(ep, 0.5))
        elif e == "blur.gaussian":
            wrap_filter(cur, blur_filter(ep.get("radius", 5)))
        else:
            sys.exit(f"steps_to_svg: step {i}: effect {e} not supported — bake it into a decor PNG")
    elif c == "select.set":
        sel = [ref(r) for r in p["ids"]]
    elif c == "select.none":
        cur, sel = None, []
    elif c == "object.clippingMask.make":
        outs = [s.outer() for s in sel]
        parent = outs[0].parent
        order = sorted(outs, key=parent.children.index)
        mask, content = order[-1], order[:-1]  # topmost selected object is the mask, like the app
        at = parent.children.index(mask)
        cid = new_id("clip")
        m = El(mask.tag, {k: v for k, v in mask.attrs.items() if k not in ("fill", "stroke", "id", "data-name")})
        defs.add(El("clipPath", {"id": cid})).add(m)
        g = El("g", {"clip-path": f"url(#{cid})"})
        for o in order:
            parent.children.remove(o)
        parent.add(g, min(at, len(parent.children)))
        for o in content:
            g.add(o)
        objs[i] = cur = g
    elif c == "object.rotate":
        if not cur.bbox:
            sys.exit(f"steps_to_svg: step {i}: rotate needs a shape with a known box")
        x, y, w, h = cur.bbox
        # object.rotate is counter-clockwise (like Illustrator); the `rotation` param of shapes/text is clockwise
        cur.attrs["transform"] = f"rotate({-p['angle']} {x + w / 2} {y + h / 2}) " + cur.attrs.get("transform", "")
    else:
        sys.exit(f"steps_to_svg: step {i}: command {c} not supported")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}">' + defs.xml() + "".join(l.xml() for l in layers) + "</svg>")
open(sys.argv[2], "w", encoding="utf-8").write(svg)
print(sys.argv[2], f"{len(steps)} steps → {len(layers)} layers")
