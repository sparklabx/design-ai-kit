"""Generate or edit an image with Antigravity's built-in image tool (billed to the user's Google plan, not an API key).
Run with `python3 -E`. Needs the Antigravity CLI `agy`, signed in.

  agy_image.py <out.png|jpg> "<prompt>" [--ref <img> …] [--agy <path to agy>]

agy's print mode refuses shell commands, so it only generates; this script finds the file and copies it to <out>.
"""
import pathlib, re, shutil, subprocess, sys, time
from PIL import Image

BRAIN = pathlib.Path.home() / ".gemini/antigravity-cli/brain"
EXT = (".png", ".jpg", ".jpeg", ".webp")


def main(a):
    agy = a.pop(a.index("--agy") + 1) if "--agy" in a else shutil.which("agy") or str(pathlib.Path.home() / ".local/bin/agy")
    a = [x for x in a if x != "--agy"]
    refs = []
    while "--ref" in a:
        i = a.index("--ref")
        refs.append(pathlib.Path(a.pop(i + 1)).resolve())
        a.pop(i)
    if len(a) != 2:
        sys.exit(__doc__)
    out, prompt = pathlib.Path(a[0]).resolve(), a[1]
    for r in refs:
        if not r.is_file():
            sys.exit(f"reference not found: {r}")
    ask = "Use your generate_image tool"
    if refs:
        ask += " with these reference images: " + ", ".join(map(str, refs))
    ask += (f". {prompt}\nDo not run shell commands and do not copy or move files. "
            "Reply with only the absolute path of the generated image, or the exact error.")
    cmd = [agy, "--print-timeout", "5m"]
    for d in {r.parent for r in refs}:
        cmd += ["--add-dir", str(d)]
    start = time.time()
    r = subprocess.run(cmd + ["-p", ask], capture_output=True, text=True)
    reply = r.stdout + r.stderr
    found = [pathlib.Path(p) for p in re.findall(r"(/[^\s'\"`]+)", reply) if p.lower().endswith(EXT)]
    found = [p for p in found if p.is_file() and p.stat().st_mtime >= start - 1]
    if not found:  # reply had prose instead of a path: take the newest image agy wrote during this run
        found = sorted((p for p in BRAIN.rglob("*") if p.suffix.lower() in EXT and ".tempmediaStorage" not in p.parts
                        and p.stat().st_mtime >= start - 1), key=lambda p: p.stat().st_mtime)[-1:]
    if not found:
        sys.exit(f"no image produced (agy exit {r.returncode}):\n{reply.strip()[-1500:]}")
    src = found[-1]
    out.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == out.suffix.lower():
        shutil.copyfile(src, out)
    else:
        Image.open(src).convert("RGB" if out.suffix.lower() in (".jpg", ".jpeg") else "RGBA").save(out)
    w, h = Image.open(out).size
    print(f"{out} {w}x{h} (from {src})")


if __name__ == "__main__":
    main(sys.argv[1:])
