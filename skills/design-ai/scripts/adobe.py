"""Open / export a steps_to_svg.py SVG in Illustrator or Photoshop (macOS, via osascript + ExtendScript).

    python3 -E adobe.py detect
    python3 -E adobe.py open   illustrator|photoshop design.svg                 # live preview: refresh the user's tab
    python3 -E adobe.py export illustrator|photoshop design.svg 03_Export/Name  # Name.ai|.psd + .png + @2x.png + .jpg

UNTESTED: written without either app installed — see references/adobe.md before relying on it.
"""
import json
import os
import subprocess
import sys

APPS = {"illustrator": "com.adobe.illustrator", "photoshop": "com.adobe.Photoshop"}

# close the tab showing this design if untouched; a modified tab means the user edited it → refuse
REOPEN = """
var f = new File(%(svg)s), dirty = false;
for (var i = app.documents.length - 1; i >= 0; i--) {
  var d = app.documents[i], p = '';
  try { p = d.fullName.fsName; } catch (e) {}
  if (p == f.fsName) { if (d.saved) d.close(%(nosave)s); else dirty = true; }
}
if (dirty) 'DIRTY'; else { app.open(f); 'OK'; }
"""
EXPORT = {
    "illustrator": """
var d = app.open(new File(%(svg)s));
d.saveAs(new File(%(base)s + '.ai'), new IllustratorSaveOptions());
var o = new ExportOptionsPNG24(); o.artBoardClipping = true; o.antiAliasing = true;
d.exportFile(new File(%(base)s + '.png'), ExportType.PNG24, o);
o.horizontalScale = o.verticalScale = 200; d.exportFile(new File(%(base)s + '@2x.png'), ExportType.PNG24, o);
var j = new ExportOptionsJPEG(); j.qualitySetting = 90; j.artBoardClipping = true;
d.exportFile(new File(%(base)s + '.jpg'), ExportType.JPEG, j);
'OK';
""",
    # Photoshop rasterises SVG on open: one flat layer; @2x is an upscale (shortcut: re-open at 2x when tested)
    "photoshop": """
app.displayDialogs = DialogModes.NO;
var d = app.open(new File(%(svg)s));
d.saveAs(new File(%(base)s + '.psd'), new PhotoshopSaveOptions(), true);
d.saveAs(new File(%(base)s + '.png'), new PNGSaveOptions(), true);
var j = new JPEGSaveOptions(); j.quality = 10; d.saveAs(new File(%(base)s + '.jpg'), j, true);
d.resizeImage(UnitValue(d.width.as('px') * 2, 'px'), UnitValue(d.height.as('px') * 2, 'px'), null, ResampleMethod.BICUBIC);
d.saveAs(new File(%(base)s + '@2x.png'), new PNGSaveOptions(), true);
d.close(SaveOptions.DONOTSAVECHANGES);
'OK';
""",
}


def installed(app):
    out = subprocess.run(["mdfind", f"kMDItemCFBundleIdentifier == '{APPS[app]}'"], capture_output=True, text=True)
    return [p for p in out.stdout.splitlines() if p.endswith(".app")]


def run(app, js):
    r = subprocess.run(["osascript", "-e", f'tell application id "{APPS[app]}" to do javascript {json.dumps(js)}'],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"adobe.py: {app}: {r.stderr.strip()}")
    return r.stdout.strip()


cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
if cmd == "detect":
    for a in APPS:
        print(a, installed(a) or "not installed")
elif cmd in ("open", "export") and len(sys.argv) >= 4:
    app, svg = sys.argv[2], os.path.abspath(sys.argv[3])
    if app not in APPS or not installed(app):
        sys.exit(f"adobe.py: {app} not installed")
    if cmd == "open":
        nosave = "SaveOptions.DONOTSAVECHANGES"
        res = run(app, REOPEN % {"svg": json.dumps(svg), "nosave": nosave})
        print("tab has unsaved edits by the user — ask before reloading" if res == "DIRTY" else f"opened in {app}")
    else:
        base = os.path.abspath(sys.argv[4])
        os.makedirs(os.path.dirname(base), exist_ok=True)
        print(run(app, EXPORT[app] % {"svg": json.dumps(svg), "base": json.dumps(base)}), base + ".*")
else:
    print(__doc__)
