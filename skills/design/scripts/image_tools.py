"""Image helpers for compositing (Pillow + numpy). Run with `python3 -E`.

  bbox     <img>                          alpha bbox + body centre at 60 % height → use for placement maths
  feather  <in> <out> <px> [all|topleft]  alpha ramp on edges so a scene blends into the layout background
  harmonize <in> <out> [--gain r,g,b] [--sat 1] [--contrast 1] [--bright 1] [--light left|right|none]
                                          one white balance + one light direction across mixed sources
  sheet    <out> <img> [<img> …]          side-by-side contact sheet on the layout base colour, for picking
"""
import sys
import numpy as np
from PIL import Image


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


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
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
    else:
        sys.exit(__doc__)
