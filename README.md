# design-ai-kit

Teach your AI agent to design marketing visuals that clients accept — social banners, promo posts, posters,
event recaps. One skill, distilled from real client revision rounds.

What it gives the agent:

1. **A workflow** (`skills/design-ai/SKILL.md`) — brief → brand research → assets → scripted build → self-check →
   deliver. Asks for a reference early, verifies offers/dates, never exports before approval.
2. **Design principles** (`references/principles.md`) — rules learned from rejected drafts: match the brand's own
   style, fresh over dark, one light source, offer is the hero, no empty zones, logos printed *into* product photos.
3. **A re-runnable build** — `scripts/build_template.py` turns a JSON config into a
   VectorCraft document headless; every revision is a config edit + re-run.
4. **Image tools** — `scripts/image_tools.py`: alpha bbox for placement maths, edge feathering, lighting
   harmonisation across mixed photos, contact sheets.
5. **AI asset recipes** (`references/ai-assets.md`) — stock first; AI to print a logo onto a product, generate
   particles, fix one thing in a scene. Tested with the Magnific MCP; any reference-capable image model works.

## Install

```bash
git clone https://github.com/sparklabx/design-ai-kit
mkdir -p ~/.claude/skills && cp -r design-ai-kit/skills/design-ai ~/.claude/skills/
```

Other agents: point them at `skills/design-ai/SKILL.md`.

**Requirements:** `vectorcraft-cli` on PATH, Python 3.9+ with Pillow and numpy. Optional: an image-generation MCP.

## Try it

```bash
cd skills/design-ai/scripts
# edit promo-square.example.json: asset paths, copy, palette
python3 -I build_template.py promo-square.example.json steps.json out.vectorcraft
vectorcraft-cli run --commands steps.json --export preview.png
```

## License

MIT. Brand names in the docs are examples only; no third-party logos or product images are included.
