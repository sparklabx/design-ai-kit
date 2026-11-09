"""Title lettering effects VectorCraft can't draw, rendered as a transparent PNG to place as `decor`.

  sign <font.ttf> <size> <text> <out.png> [--arch px] [--extrude px] [--bold px] [--fill #top,#bottom] [--line #hex] [--depth #hex]
        retro sign: gradient fill, dark outline, 3D extrusion down-right, optional arch
  ink  <font.ttf> <size> <text> <out.png> [--arch px] [--bold px] [--fill #hex]
        brush-pen: wobbly hand-drawn stroke, rough ink edge, uneven density, thin dark rim

Arch is the rise of the middle in px at output size; on a long title it needs ~0.5× the font size to read as a curve.
Thin scripts need --bold 2–3 or the effect swallows them. Check Vietnamese marks on the PNG before placing it.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

hexrgb = lambda h: np.array([int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def text_masks(font, size, text, ss, grows, pad):
    """One mask per stroke growth, all on the same origin so the layers line up."""
    f = ImageFont.truetype(font, size * ss)
    x0, y0, x1, y1 = f.getbbox(text, stroke_width=max(grows))
    out = []
    for g in grows:
        m = Image.new("L", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), 0)
        ImageDraw.Draw(m).text((pad - x0, pad - y0), text, font=f, fill=255, stroke_width=g, stroke_fill=255)
        out.append(np.asarray(m, np.float32) / 255)
    return out


def finish(rgb, alpha, ss, out):
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(alpha, 0, 1) * 255]).astype(np.uint8))
    im = im.resize((im.width // ss, im.height // ss), Image.LANCZOS)
    box = im.getchannel("A").getbbox()
    assert box, "empty render: font has no glyphs for this text?"
    im = im.crop(box); im.save(out); print(out, im.size)


def sign(font, size, text, out, arch=0.0, extrude=None, bold=0.0, fill="#EEDEAA,#D6BA70", line="#341E10", depth="#4A2C18"):
    ss = 2
    ext, stroke, b = int((extrude or max(4, size // 14)) * ss), max(2, size * ss // 22), int(bold * ss)
    pad = stroke + b + ext + int(arch * ss) + 40
    body, edge = text_masks(font, size, text, ss, (b, b + stroke), pad)
    H, W = body.shape
    lift = (arch * ss * (1 - np.linspace(-1, 1, W) ** 2)).astype(int)  # ends stay, middle rises by `arch`
    rows = np.clip(np.arange(H)[:, None] + lift[None, :], 0, H - 1)
    body, edge = body[rows, np.arange(W)], edge[rows, np.arange(W)]
    ext_m = np.zeros_like(edge)
    for k in range(1, ext + 1):  # outline repeated down and slightly right = extrusion
        dx = k // 3
        ext_m[k:, dx:] = np.maximum(ext_m[k:, dx:], edge[:-k, :W - dx])
    top, bot = (hexrgb(c) for c in fill.split(","))
    t = np.linspace(0, 1, H)[:, None, None]
    rgb = np.zeros((H, W, 3), np.float32)
    for m, c in ((ext_m, hexrgb(depth)), (edge, hexrgb(line)), (body, top * (1 - t) + bot * t)):
        rgb = rgb * (1 - m[..., None]) + c * m[..., None]
    finish(rgb, np.maximum(ext_m, edge), ss, out)


def ink(font, size, text, out, arch=0.0, bold=2.0, fill="#ECE0C0"):
    ss = 3
    a, = text_masks(font, size, text, ss, (int(bold * ss),), int(size * ss * 0.25 + arch * ss))
    H, W = a.shape
    rng = np.random.default_rng(4)

    def noise(cell, amp):
        n = rng.random((max(2, H // cell), max(2, W // cell))).astype(np.float32)
        return np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255 * amp

    dx, dy = noise(20 * ss, 4 * ss) - 2 * ss, noise(20 * ss, 4 * ss) - 2 * ss  # hand wobble
    dy -= arch * ss * (1 - np.linspace(-1, 1, W)[None, :] ** 2)
    yy, xx = np.mgrid[0:H, 0:W]
    a = a[np.clip(yy - dy, 0, H - 1).astype(int), np.clip(xx + dx, 0, W - 1).astype(int)]
    soft = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2 * ss)), np.float32) / 255
    a = np.clip((soft - 0.5 + noise(3, 0.35) - 0.175) * 6 + 0.5, 0, 1)  # rough ink edge
    dens = 0.92 + noise(40, 0.07) - (noise(2, 1) > 0.97) * 0.35  # uneven density + dry-brush specks
    grown = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * ss + 1)).filter(ImageFilter.GaussianBlur(ss))
    rim = np.clip(np.asarray(grown, np.float32) / 255 - a, 0, 1)  # thin dark rim so it reads on busy art
    al = np.clip(a + rim * 0.7, 0, 1)
    rgb = hexrgb(fill) * dens[..., None] * a[..., None] + np.array([30, 26, 18], np.float32) * rim[..., None]
    finish(rgb / np.maximum(al, 1e-3)[..., None], al, ss, out)


if __name__ == "__main__":
    if len(sys.argv) < 6 or sys.argv[1] not in ("sign", "ink"):
        sys.exit(__doc__)
    kind, font, size, text, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
    rest, kw = iter(sys.argv[6:]), {}
    for flag in rest:
        k, v = flag[2:], next(rest)
        kw[k] = v if k in ("fill", "line", "depth") else float(v)
    (sign if kind == "sign" else ink)(font, size, text, out, **kw)
