---
name: design-ai
version: 0.1.0
description: Use when the user asks for a marketing visual — social banner, promo post, poster, key visual, event recap, product ad — for a brand or campaign. Researches the brand, sources real/stock/AI assets, builds the layout as a re-runnable script with VectorCraft (headless), self-checks the render, and exports only when the design is approved.
license: MIT
---

# Marketing visual design

You design by writing **one build script** that turns a config (copy, palette, asset paths, positions)
into a VectorCraft document. Every revision is an edit to that script, re-run headless, rendered,
and looked at. You never hand-place objects in the GUI and never keep a pile of versions.

Follow the steps in order. Each step names the one reference to read.

## Step 0 — Tools

```bash
command -v vectorcraft-cli >/dev/null && vectorcraft-cli --help | head -1 || echo "MISSING vectorcraft-cli"
python3 -E -c "import PIL, numpy" 2>/dev/null || echo "MISSING Pillow/numpy"
```

Missing → tell the user, stop. Never install system packages yourself.
AI image tools (Magnific MCP or similar) are optional; check the account and credits before the first paid call.

## Step 1 — Brief (ask before you draw)

| Fact | If missing |
|---|---|
| **Brand + purpose** (promo, launch, schedule, recap…) | Ask. |
| **Copy facts** (offer, dates, venue, numbers) | Ask, or research — **verify** it is current. Never invent an offer or a date; if you must, mark it `TẠM/placeholder` in the reply. |
| **Format** (1080×1080, 1080×1350, 1920×1080…) | Ask. |
| **Assets** (logo file, product photos, brand guide) | Ask. If "find it yourself": Step 2. |
| **A reference** the client likes | **Always ask early.** One reference image saves five revision rounds. |

Check the brief is still true (an event already ended, a season already aired) and say so before designing.

## Step 2 — Brand research → `references/principles.md` §Brand

Find the brand's **current** identity (rebrands happen), its own recent posters, palette, type style, packaging.
Record sources and licence of every asset (logo from Wikipedia is "fair use", not a brand file).

## Step 3 — Agree a direction (before any build or paid AI call)

If the request is vague ("make a banner for X", "make it prettier", "more impressive") or allows more than one
reading, **do not pick for the user**. Propose 2–3 directions and wait for a choice:

- One short line each: concept · mood · background tone · layout (where offer, product, text sit) · assets it needs
  · AI credits it would cost. Put the one closest to the brand's own posters first, marked *(recommended)*.
- Use the agent's question tool when it has one; otherwise a numbered list and stop.
- For a revision note ("chưa đẹp", "đơn điệu", "lighting wrong"), restate what you will change in one line per
  item before doing it; if a note has two readings, ask which.

Skip this only when the user already fixed the direction (gave a reference to follow, or chose an option).

## Step 4 — Assets → `references/ai-assets.md`

Priority: client's official assets › stock (licensed) › AI-generated. Product shots and anything with a logo on it
must look like one photograph — never paste a vector logo onto a photo.

## Step 5 — Build → `references/vectorcraft.md`

Copy `scripts/build_template.py` + `scripts/promo-square.example.json` into `01_Material/Scripts/`, fill the config (positions from `image_tools.py bbox`), run headless. One working
`.vectorcraft` file, overwritten on every run. If the app is open, refresh the user's single tab after each run
(close stale tab → open file; see "Live preview").

## Step 6 — Self-check → `references/checklist.md`

Render, look at the whole image **and** zoomed crops (seams, overlaps, logo placement). Fix before showing.

## Step 7 — Deliver

- Show the render (a preview in a temp folder, not in the project); list what is placeholder/unverified,
  asset licences, AI credits spent.
- **No export until the design is approved or the user asks for one.** Then export one set into
  `03_Export/`, overwriting the previous set: PNG/JPG to post, `.ai` + fonts for a designer (Illustrator),
  `.psd` for retouching (see "Hand-off to Adobe"). Never create v2, v3… copies — the build script is the history.
- Write to `LOG.md` **only after a large change** (new direction, new assets, many rounds) — a few lines,
  feedback → decision, so the next agent can continue. Small tweaks don't get a log entry.

## Project layout

```
<Project>_Banner/
  01_Material/{Logo,Fonts,Images,Scripts}   # sources + build script (the design lives here)
  02_PSD/<name>.vectorcraft (+ .ai/.psd on approval)
  03_Export/<name>.png|@2x.png|.jpg          # approval only
  LOG.md
```
