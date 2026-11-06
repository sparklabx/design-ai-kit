"""Image helpers for compositing (Pillow + numpy). Run with `python3 -E`.

  bbox     <img>                          alpha bbox + body centre at 60 % height → use for placement maths
  feather  <in> <out> <px> [all|topleft]  alpha ramp on edges so a scene blends into the layout background
  harmonize <in> <out> [--gain r,g,b] [--sat 1] [--contrast 1] [--bright 1] [--light left|right|none]
                                          one white balance + one light direction across mixed sources
  sheet    <out> <img> [<img> …]          side-by-side contact sheet on the layout base colour, for picking
  emptiness <render.png> [--grid 3] [--ratio 0.5]
                                          detail score per grid cell; flags cells far emptier than the median
  textw    <font.ttf> <size> <text>       rendered text width/height in px (VectorCraft Pixels: 1 pt = 1 px)
  fontcheck <font.ttf> [<copy>]           glyphs missing for the full Vietnamese alphabet (+ the copy); needs fontTools
  contrast <render.png> <x,y,w,h> <#text> <size px> [bold]
                                          WCAG contrast of a text colour against what is really behind it in the render
  contrast <#text> <#background> <size px> [bold]
                                          two colours (gradient ends, palette planning before a render)
"""
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageFont


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255


def save(a, p):
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(p)


def bbox(p):
    a = load(p)[..., 3]
    ys, xs = np.nonzero(a > 0.15)
    yb = int(ys.min() + 0.6 * (ys.max() - ys.min()))
    row = np.nonzero(a[yb] > 0.15)[0]
    print(f"size {a.shape[1]}x{a.shape[0]} bbox {xs.min()} {ys.min()} {xs.max()} {ys.max()} "
          f"center_px {(row.min() + row.max()) // 2} bottom_px {ys.max()}")


def feather(src, dst, px, edges="topleft"):
    a = load(src)
    h, w = a.shape[:2]
    ss = lambda t: np.clip(t, 0, 1) ** 2 * (3 - 2 * np.clip(t, 0, 1))  # smoothstep
    rx, ry = ss(np.arange(w) / px), ss(np.arange(h) / px)
    if edges == "all":
        rx, ry = np.minimum(rx, rx[::-1]), np.minimum(ry, ry[::-1])
    a[..., 3] *= np.minimum(ry[:, None], rx[None, :])
    save(a, dst)


def harmonize(src, dst, gain=(1, 1, 1), sat=1.0, contrast=1.0, bright=1.0, light="left"):
    im = load(src)
    rgb, al = im[..., :3] * np.array(gain, np.float32), im[..., 3]
    lum = (rgb @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    rgb = 0.5 + ((lum + (rgb - lum) * sat) - 0.5) * contrast
    if light != "none":
        ys, xs = np.nonzero(al > 0.15)
        u = np.clip((np.arange(im.shape[1]) - xs.min()) / max(1, xs.max() - xs.min()), 0, 1)
        v = np.clip((np.arange(im.shape[0]) - ys.min()) / max(1, ys.max() - ys.min()), 0, 1)
        u = u if light == "left" else 1 - u
        rgb = rgb * ((1.08 - 0.18 * u)[None, :] * (1.03 - 0.06 * v)[:, None])[..., None]
    out = np.concatenate([np.clip(rgb * bright, 0, 1), al[..., None]], -1)
    assert np.allclose(out[..., 3], im[..., 3])  # alpha untouched
    save(out, dst)


def sheet(dst, paths, cell=400, bg=(248, 245, 236)):
    s = Image.new("RGBA", (cell * len(paths), cell), bg + (255,))
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGBA")
        im.thumbnail((cell, cell))
        s.alpha_composite(im, (i * cell + (cell - im.width) // 2, (cell - im.height) // 2))
    s.convert("RGB").save(dst)


def emptiness(p, grid=3, ratio=0.5):
    L = load(p)[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32) * 255
    g = np.abs(np.diff(L, axis=0))[:, :-1] + np.abs(np.diff(L, axis=1))[:-1, :]
    h, w = g.shape
    sc = np.array([[g[r * h // grid:(r + 1) * h // grid, c * w // grid:(c + 1) * w // grid].mean() for c in range(grid)] for r in range(grid)])
    med = np.median(sc)
    for r in range(grid):
        print("  ".join(f"{v:6.1f}{'*' if v < ratio * med else ' '}" for v in sc[r]))
    empty = [(r, c) for r in range(grid) for c in range(grid) if sc[r, c] < ratio * med]
    print(f"median {med:.1f}; empty cells (row,col): {empty or 'none'}  → fill or justify each")


def textw(font, size, s):
    x0, y0, x1, y1 = ImageFont.truetype(font, int(size)).getbbox(s)
    print(f"width {x1 - x0} height {y1 - y0} (left {x0}, top {y0} from origin)")


def vietnamese():
    import unicodedata
    tones = ["", "\u0300", "\u0301", "\u0303", "\u0309", "\u0323"]  # huyền sắc ngã hỏi nặng
    s = {unicodedata.normalize("NFC", v + t) for v in "aăâeêioôơuưy" for t in tones} | set("đ")
    return "".join(sorted(s | {c.upper() for c in s}))


def fontcheck(font, copy=""):
    from fontTools.ttLib import TTFont
    cmap = TTFont(font, fontNumber=0).getBestCmap()
    need = vietnamese() + copy
    missing = sorted({c for c in need if not c.isspace() and ord(c) not in cmap})
    print(f"{font}: " + ("OK, full Vietnamese" if not missing else f"MISSING {len(missing)}: {''.join(missing)}"))
    return missing


def luminance(rgb):
    c = np.asarray(rgb, np.float32)
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return c @ np.array([0.2126, 0.7152, 0.0722], np.float32)


def rgb(color):
    return np.array([int(color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def contrast(p, rect, color, size, bold=False):
    t = rgb(color)
    if p.startswith("#"):  # colour vs colour
        bg = rgb(p)[None]
    else:
        x, y, w, h = map(int, rect)
        a = load(p)[y:y + h, x:x + w, :3]
        m = Image.fromarray((np.abs(a - t).max(axis=2) <= 0.12).astype(np.uint8) * 255)  # the text's own pixels
        near = lambda n: np.asarray(m.filter(ImageFilter.MaxFilter(n))) > 0
        bg = a[near(9) & ~near(3)]  # 2–4 px ring around the glyphs = what the eye reads them against
        if bg.size == 0:
            sys.exit("no pixels of the text colour in rect — check the rect and the colour (gradient text: use colour mode)")
    lt, lb = luminance(t), luminance(bg)
    r = (np.maximum(lt, lb) + 0.05) / (np.minimum(lt, lb) + 0.05)
    # WCAG large text = 24 px (18.7 px bold) on screen; a 1080 post shows ~2.7x smaller on a phone → 65 / 50 px here
    large = size >= (50 if bold else 65)
    worst, need = float(np.percentile(r, 10)), 3.0 if large else 4.5  # 10th pct: ignore stray anti-alias pixels
    print(f"contrast {worst:.2f}:1 (median {float(np.median(r)):.2f}) need {need}:1 → {'OK' if worst >= need else 'FAIL'}")
    return worst


def flags(args):
    kw, rest = {}, iter(args)
    for f in rest:
        kw.setdefault(f[2:], []).append(next(rest))
    return kw


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("help", [])
    if cmd == "bbox":
        for p in args:
            bbox(p)
    elif cmd == "feather":
        feather(args[0], args[1], int(args[2]), args[3] if len(args) > 3 else "topleft")
    elif cmd == "harmonize":
        kw, rest = {}, iter(args[2:])
        for flag in rest:
            v = next(rest)
            kw[flag[2:]] = tuple(map(float, v.split(","))) if flag == "--gain" else (v if flag == "--light" else float(v))
        harmonize(args[0], args[1], **kw)
    elif cmd == "sheet":
        sheet(args[0], args[1:])
    elif cmd == "emptiness":
        kw = flags(args[1:])
        emptiness(args[0], int(kw.get("grid", ["3"])[0]), float(kw.get("ratio", ["0.5"])[0]))
    elif cmd == "textw":
        textw(args[0], float(args[1]), " ".join(args[2:]))
    elif cmd == "fontcheck":
        fontcheck(args[0], " ".join(args[1:]))
    elif cmd == "contrast":
        if args[0].startswith("#"):
            contrast(args[1], None, args[0], float(args[2]), "bold" in args[3:])
        else:
            contrast(args[0], args[1].split(","), args[2], float(args[3]), "bold" in args[4:])
    else:
        sys.exit(__doc__)
