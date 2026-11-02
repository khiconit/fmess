"""fMess icon: a speech bubble in the pink-violet-blue gradient with a white,
round-stroked f, on a light tile, drawn per size: soft shadows when large,
a bigger bubble and bolder f with no shadows when small, as Apple's own icons are.

    python3 branding/icon.py OUT_DIR   # icon-16.svg ... icon-1024.svg

Render each SVG at its own size (Chrome headless keeps the transparency:
--headless=new --force-device-scale-factor=1 --default-background-color=00000000
--window-size=N,N --screenshot=icon-N.png), copy icon-1024.png to app-icon.png
and run `npx tauri icon app-icon.png` for the Windows and Linux icons, then
replace icon.icns (iconutil -c icns on an .iconset of the per-size PNGs) and
32x32, 64x64, 128x128 and 128x128@2x.png with the per-size renders.

    python3 branding/icon.py --site OUT_DIR   # mark-128.svg, favicon-32.svg ...

The website's copies (site/assets/): the tile alone, cropped to its edges, for
the header mark and the favicons; icon-256 and icon-512 are the app's renders.

    python3 branding/icon.py --themes OUT_DIR   # zalo-256.svg ... whatsapp-512.svg

The icons the app shows while it runs with the Zalo, WhatsApp or Teams theme (see
icon.rs): that app's own logo (brands/: Zalo's and WhatsApp's public domain on
Wikimedia Commons, Teams' as Teams draws it) with fMess's icon as a badge in the corner, at 512 for the Dock and
256 for the window and tray. Render them as above into src-tauri/icons/themes/."""
import math, pathlib, re, sys

def superellipse(cx, cy, w, h, n, steps=720):
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        pts.append(f"{cx + (w/2) * math.copysign(abs(c) ** (2/n), c):.2f},{cy + (h/2) * math.copysign(abs(s) ** (2/n), s):.2f}")
    return "M" + " L".join(pts) + " Z"

SQUIRCLE = superellipse(512, 512, 824, 824, 5.0)
CX, CY = 512, 488

def bubble(w, h):
    """A soft squircle with a tail curling out of its bottom left."""
    bottom = CY + h / 2
    tail = (f"M{CX-200},{bottom-90} C{CX-210},{bottom+20} {CX-250},{bottom+70} {CX-290},{bottom+95} "
            f"C{CX-190},{bottom+100} {CX-110},{bottom+60} {CX-60},{bottom-20} Z")
    return superellipse(CX, CY, w, h, 2.6), tail

# The f, about the bubble's centre: a stem curling over at the top, and a bar.
F_STEM = "M-20,170 V-10 C-20,-80 15,-115 75,-115 H105"
F_BAR = "M-95,15 H65"
# One gradient across the whole drawing, top left to bottom right.
INK = [("0", "#FF4FA3"), ("0.5", "#9D4DFF"), ("1", "#2E8BFF")]
INK_FROM, INK_TO = (150, 120), (874, 904)

def gradient(id_, a, b):
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in INK)
    return f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}">{stops}</linearGradient>'

def svg(size, crop=False):
    small = size <= 32
    w, h = (660, 580) if small else (600, 520)
    stem, bar = (104, 96) if small else (88, 80)
    shape, tail = bubble(w, h)
    # Cropped to the tile for the website, where nothing frames it.
    box = "100 100 824 824" if crop else "0 0 1024 1024"
    tile_shadow = "" if crop else 'filter="url(#iconshadow)"'
    bubble_shadow = "" if small else 'filter="url(#bubbleshadow)"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="{box}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#ECECF2"/></linearGradient>
  {gradient("ink", INK_FROM, INK_TO)}
  <clipPath id="body"><path d="{SQUIRCLE}"/></clipPath>
  <filter id="iconshadow" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"><feDropShadow dx="0" dy="10" stdDeviation="{10 if size >= 256 else 6}" flood-color="#000" flood-opacity="0.3"/></filter>
  <filter id="bubbleshadow" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"><feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#2A0A5E" flood-opacity="0.35"/></filter>
</defs>
<g {tile_shadow}><path d="{SQUIRCLE}" fill="url(#bg)"/></g>
<path d="{SQUIRCLE}" fill="none" stroke="#000" stroke-opacity="0.08" stroke-width="{12 if small else 4}" clip-path="url(#body)"/>
<g {bubble_shadow}><path d="{shape}" fill="url(#ink)"/><path d="{tail}" fill="url(#ink)"/></g>
<g transform="translate({CX},{CY})" fill="none" stroke="#FFFFFF" stroke-linecap="round" stroke-linejoin="round">
  <path d="{F_STEM}" stroke-width="{stem}"/><path d="{F_BAR}" stroke-width="{bar}"/>
</g>
</svg>'''

BRANDS = pathlib.Path(__file__).parent / "brands"

def inner(svg_text):
    """What is inside an SVG's outer <svg> element."""
    return svg_text[svg_text.index(">", svg_text.index("<svg")) + 1:svg_text.rindex("</svg>")]

def brand(name):
    """The brand's logo, drawn in the icon's 1024 square like fMess's own."""
    logo = (BRANDS / f"{name}.svg").read_text()
    if name == "zalo":
        # Zalo's logo is its whole app icon, a rounded square (50 units).
        return f'<g filter="url(#logoshadow)"><g transform="translate(100,100) scale({824 / 50})">{inner(logo)}</g></g>'
    if name == "teams":
        # Teams' logo alone (20 units from 2,2), on a white square as its app shows it.
        return f'''<g filter="url(#logoshadow)"><path d="{SQUIRCLE}" fill="#ffffff"/></g>
<g transform="translate(176,176) scale(28)">{inner(logo)}</g>'''
    # WhatsApp's is the bubble alone: on a green square, as its app shows it,
    # without the logo's grey shadow (filter a) or the path drawn under the
    # same one again (its gradient isn't in the file).
    paths = [p for p in re.findall(r"<path[^>]*/>", logo) if 'filter="url(#a)"' not in p and "linearGradient1780" not in p]
    defs = re.search(r"<defs>.*?</defs>", logo).group(0)
    return f'''<g filter="url(#logoshadow)"><path d="{SQUIRCLE}" fill="url(#wa)"/></g>
{defs}<g transform="translate({512 - 87.2 * 3.6:.1f},{512 - 87.2 * 3.6:.1f}) scale(3.6)">{"".join(paths)}</g>'''

def themed(size, name):
    """A brand's logo with fMess's icon as a badge on its bottom right corner."""
    badge = inner(svg(64))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 1024 1024">
<defs>
  <filter id="logoshadow" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"><feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#000" flood-opacity="0.35"/></filter>
  <linearGradient id="wa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5FE07A"/><stop offset="1" stop-color="#1FAF4B"/></linearGradient>
</defs>
{brand(name)}
<g transform="translate(600,600) scale(0.41)">{badge}</g>
</svg>'''

if __name__ == "__main__":
    if sys.argv[1] == "--themes":
        out = pathlib.Path(sys.argv[2])
        for name in ("zalo", "whatsapp", "teams"):
            for size in (256, 512):
                (out / f"{name}-{size}.svg").write_text(themed(size, name))
        sys.exit()
    if sys.argv[1] == "--site":
        out = pathlib.Path(sys.argv[2])
        for name, size in (("mark-128", 128), ("favicon-32", 32), ("favicon-64", 64)):
            (out / f"{name}.svg").write_text(svg(size, crop=True))
        sys.exit()
    out = pathlib.Path(sys.argv[1])
    for size in (16, 32, 64, 128, 256, 512, 1024):
        (out / f"icon-{size}.svg").write_text(svg(size))
