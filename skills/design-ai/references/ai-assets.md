# Assets: stock + AI (Magnific MCP recipes)

Always: check credits (`account_balance`), estimate (`simulate_cost`), tell the user what you spend.
Name downloaded files by the **creation identifier** you waited on — results do not come back in call order.

## Sourcing order

1. Client's official files (logo, product photos, brand guide).
2. Stock (`stock_search` → `stock_download format:source`): real photos, licensed. Check licence/premium cost.
3. AI generation for what stock cannot give: the product **with the logo printed on it**, a full scene, particles.
4. Never AI-generate real people's faces or a brand's logo from scratch — use the real logo file as a reference.

## Recipes (Nano Banana / any image-edit model with references)

**Print a logo onto a product photo** (the fix for "logo doesn't stick to the cup"):
refs = [product on white, logo PNG]. Prompt: *"Edit the first image only. Keep the product, framing, size, position
and white background exactly the same. Print the logo from the second image directly onto the product as real
factory printing: centred, at mid-height, logo width about 30 % of the product width. It wraps around the curved
surface, same lighting (brighter on the light side), reflections and condensation pass over it, opaque white ink
underlayer so small text stays readable. Keep the logo design exactly. No other changes."*
Then remove background. One call per product (~65 cr + 3 cr).

**Particles** (ice, leaves, beans…): *"…isolated on pure white, scattered around an empty centre (centre 50 % empty),
soft light from upper left, no shadows, no text."* → remove background → place behind the product.

**Fix one thing in an AI scene** (blurred back object, too-strong light): edit with the previous result as the only
reference and say *"keep everything identical; only …"*. Light direction: describe it in words
("one soft key light from the upper left, shadows to the lower right") — the dedicated relight tool gave weak direction.

**Thin objects** (wire, cable, straw, string, antenna): say it in the prompt — *"hair-thin, light grey, low
contrast, partly lost in haze"*. Pixel repair in a script is the last resort: one wire took 4
repair rounds where a re-generation is ~65 cr.

**Adding an object to a scene**: state the zones to keep clear in %, e.g. *"keep the top-right 15 % empty for the
logo"* (an added cable car once covered the logo). Zoom/crop the scene **last**, after all AI additions, or new
objects get cropped or collide with the logo.

## Gotchas

- AI scenes with a baked background rarely blend into a vector layout; prefer cut-out products on the layout's own
  background. If you do use a scene, feather its edges (`scripts/image_tools.py feather`) and keep layout colours sampled from it.
- Outpainting/expanding a scene invented garbage text — avoid.
- AI misses sizes: "logo 30 %" gave ~20 % smaller; "logo 32 % of the cup" came out ~60 %. Ask for **less** than
  the target, measure the result, report it.
- "Failed to download image from the provided URL": the AI service fetches URLs itself, so local paths, localhost,
  expired presigned links and hotlink-blocked sites (Wikipedia) fail. Upload the file instead (Magnific:
  `creations_request_upload` → `curl -X PUT --upload-file` → `creations_finalize_upload`) and pass the creation id.
- Always generate **2 variants** per paid edit: one often re-composes the scene, the other is usable.
- Harmonise mixed sources before compositing: `scripts/image_tools.py harmonize` (white balance, saturation, one light direction,
  back items darker).
