#!/usr/bin/env python3
"""Square 1024x1024 recomposition of 'The Day in World News — Wed 18 Nov 2026'.
Fresh PIL renderer (supersampled 2x, downscaled to 1024). Written from scratch.
"""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from geo_data import WORLD_LAND, WORLD_LAKES, GULF_LAND

SS = 3                      # supersample factor
W, H = 1024, 1024
PAPER = (247, 242, 227)
INK = (17, 17, 17)
import os
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"

def S(v): return int(round(v * SS))

FONTS = {}
def F(name, size):
    key = (name, size)
    if key not in FONTS:
        FONTS[key] = ImageFont.truetype(FONT_DIR + name, S(size))
    return FONTS[key]

SERIF      = "NotoSerif-Regular.ttf"
SERIF_B    = "NotoSerif-Bold.ttf"
SERIF_I    = "NotoSerif-Italic.ttf"
DISPLAY_BK = "NotoSerifDisplay-Black.ttf"
SANS       = "NotoSans-Regular.ttf"
SANS_B     = "NotoSans-Bold.ttf"
SANS_SB    = "NotoSans-SemiBold.ttf"
PF_BK      = "PlayfairDisplay-Black.ttf"    # masthead date, stat figures
PF_B       = "PlayfairDisplay-Bold.ttf"     # hero headlines
EBG        = "EBGaramond-Regular.ttf"       # deks
EBG_M      = "EBGaramond-Medium.ttf"
EBG_I      = "EBGaramond-Italic.ttf"        # subtitle line
DMS_I      = "DMSerifDisplay-Italic.ttf"    # italic emphasis

# region colors
C = {
 "asia":  (123, 45, 142), "me":    (194, 65, 12),  "eu":   (29, 78, 216),
 "af":    (21, 128, 61),  "am":    (185, 28, 28),  "oc":   (13, 148, 136),
 "gl":    (107, 114, 128), "sp":   (17, 24, 39),   "red":  (180, 35, 24),
 "gold":  (255, 217, 77),
}

def wrap(text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= S(maxw):
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def text_w(t, font): return draw.textlength(t, font=font) / SS

def fit_text(x, y, w, text, font_name, sizes, lh, max_h, color=INK, align="left"):
    """Try font sizes (desc) until wrapped text fits max_h. Draw it. Return used height."""
    for size in sizes:
        font = F(font_name, size)
        lines = wrap(text, font, w)
        used = len(lines) * size * lh
        if used <= max_h:
            yy = y
            for ln in lines:
                if align == "center":
                    draw.text((S(x + (w - text_w(ln, font)) / 2), S(yy)), ln, font=font, fill=color)
                else:
                    draw.text((S(x), S(yy)), ln, font=font, fill=color)
                yy += size * lh
            return used
    # fallback: smallest size even if it overflows
    size = sizes[-1]; font = F(font_name, size)
    lines = wrap(text, font, w); yy = y
    for ln in lines:
        draw.text((S(x), S(yy)), ln, font=font, fill=color)
        yy += size * lh
    return len(lines) * size * lh

def draw_kicker(x, y, w, num, color, kick, src=None, num_size=15, kick_size=10.5):
    r = num_size / 2
    cx, cy = x + r, y + r
    draw.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=color)
    fnum = F(SANS_B, num_size * 0.68)
    t = str(num)
    draw.text((S(cx - text_w(t, fnum) / 2), S(cy - num_size * 0.34)), t, font=fnum, fill=(255, 255, 255))
    fk = F(SANS_B, kick_size)
    draw.text((S(x + num_size + 5), S(y + 1)), kick, font=fk, fill=color)
    if src:
        fs = F(SANS, 9.5)
        draw.text((S(x + w - text_w(src, fs)), S(y + 1.5)), src, font=fs, fill=(102, 102, 102))

def vgrad(box, c1, c2):
    x0, y0, x1, y1 = box
    Y0, Y1 = S(y0), S(y1)
    h = max(1, Y1 - Y0)
    for i in range(h):
        t = i / h
        c = tuple(int(round(c1[j] + (c2[j] - c1[j]) * t)) for j in range(3))
        draw.line([S(x0), Y0 + i, S(x1), Y0 + i], fill=c)

def soft(x, y, w, h, painter, blur=0, opacity=1.0):
    """Paint into an RGBA layer covering box (x,y,w,h), optionally blur it, and
    composite onto the page, clipped to the box. painter(d, ox, oy) draws with
    page coordinates via the offset helpers."""
    global draw
    X, Y, Wd, Ht = S(x), S(y), S(x + w) - S(x), S(y + h) - S(y)
    layer = Image.new("RGBA", (Wd, Ht), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    painter(d, X, Y)
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(S(blur)))
    if opacity < 1:
        a = layer.getchannel("A").point(lambda v: int(v * opacity))
        layer.putalpha(a)
    img.paste(layer, (X, Y), layer)
    draw = ImageDraw.Draw(img)

def star(cx, cy, ro, ri, rot=-90):
    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = math.radians(rot + i * 36)
        pts.append((S(cx + r * math.cos(a)), S(cy + r * math.sin(a))))
    draw.polygon(pts, fill=C["gold"])

def poly(pts, fill=None, outline=None):
    draw.polygon([(S(a), S(b)) for a, b in pts], fill=fill, outline=outline)

def rect(x, y, w, h, fill=None, outline=None, width=1):
    draw.rectangle([S(x), S(y), S(x + w), S(y + h)], fill=fill, outline=outline, width=S(width))

def ell(x, y, w, h, fill=None, outline=None):
    draw.ellipse([S(x), S(y), S(x + w), S(y + h)], fill=fill, outline=outline)

def line(pts, fill, width=1):
    draw.line([(S(a), S(b)) for a, b in pts], fill=fill, width=S(width))

def txt(x, y, s, font_name, size, color=INK, anchor_left=True):
    f = F(font_name, size)
    draw.text((S(x), S(y)), s, font=f, fill=color)

# ---------------------------------------------------------------- art panels
def art_apec(x, y, w, h):
    """Dusk over Shenzhen: layered skyline, Ping An tower, and a VC-25-style
    jumbo on the tarmac with airstairs and a red carpet."""
    vgrad((x, y, x + w, y + h * 0.78), (240, 150, 74), (253, 222, 168))
    # sun with a soft halo
    sx, sy, sr = x + w * 0.865, y + h * 0.26, h * 0.13
    soft(x, y, w, h, lambda d, X, Y: d.ellipse([S(sx - sr * 2.4) - X, S(sy - sr * 2.4) - Y,
         S(sx + sr * 2.4) - X, S(sy + sr * 2.4) - Y], fill=(255, 238, 190, 150)), blur=7)
    ell(sx - sr, sy - sr, sr * 2, sr * 2, fill=(255, 246, 220))
    # far skyline (hazy)
    rnd = random.Random(7)
    def skyline(d, X, Y, base, col, n, hmin, hmax, seed):
        r = random.Random(seed); cx = x - 4
        while cx < x + w:
            bw = w * (0.025 + r.random() * 0.035); bh = h * (hmin + r.random() * (hmax - hmin))
            d.rectangle([S(cx) - X, S(base - bh) - Y, S(cx + bw) - X, S(base) - Y], fill=col)
            if r.random() < 0.3:   # stepped crown
                d.rectangle([S(cx + bw * 0.25) - X, S(base - bh - h * 0.04) - Y,
                             S(cx + bw * 0.75) - X, S(base - bh) - Y], fill=col)
            cx += bw + w * 0.004
    base = y + h * 0.80
    soft(x, y, w, h, lambda d, X, Y: skyline(d, X, Y, base, (188, 120, 128, 255), 0, .18, .38, 3), blur=0.6)
    # Ping An Finance Centre silhouette (tallest, with spire)
    pa = x + w * 0.60
    def pingan(d, X, Y):
        pts = [(pa - w * .022, base), (pa - w * .016, y + h * .16), (pa - w * .006, y + h * .10),
               (pa, y + h * .02), (pa + w * .006, y + h * .10), (pa + w * .016, y + h * .16),
               (pa + w * .022, base)]
        d.polygon([(S(a) - X, S(b) - Y) for a, b in pts], fill=(92, 62, 98, 255))
    soft(x, y, w, h, pingan)
    soft(x, y, w, h, lambda d, X, Y: skyline(d, X, Y, base, (66, 46, 82, 255), 0, .12, .30, 9))
    # lit windows on the near skyline
    for _ in range(70):
        wx = x + rnd.random() * w; wy = base - rnd.random() * h * 0.22
        if abs(wx - pa) < w * 0.03: continue
        rect(wx, wy, 1.6, 2.2, fill=(255, 214, 120))
    # tarmac
    vgrad((x, base, x + w, y + h), (92, 92, 104), (60, 60, 70))
    line([(x, base + 0.5), (x + w, base + 0.5)], (140, 138, 150), 0.8)
    for i in range(8):
        lx = x + w * (0.04 + i * 0.12)
        line([(lx, y + h * 0.93), (lx + w * 0.05, y + h * 0.93)], (235, 220, 150), 1.1)
    # aircraft (nose left), drawn as a masked layer for clean anti-aliased edges
    L = w * 0.50; px0 = x + w * 0.05; cy = y + h * 0.60; fh = h * 0.13
    def plane(d, X, Y):
        P = lambda pts: [(S(a) - X, S(b) - Y) for a, b in pts]
        # shadow
        pass
    # shadow under the jet
    soft(x, y, w, h, lambda d, X, Y: d.ellipse([S(px0 + L * .05) - X, S(y + h * .845) - Y,
         S(px0 + L * .98) - X, S(y + h * .905) - Y], fill=(20, 20, 30, 150)), blur=2.2)
    X, Y = S(x), S(y)
    lw, lh = S(x + w) - X, S(y + h) - Y
    m = Image.new("L", (lw, lh), 0); md = ImageDraw.Draw(m)
    Pp = lambda pts: [(S(a) - X, S(b) - Y) for a, b in pts]
    top, bot = cy - fh / 2, cy + fh / 2
    # fuselage body + rounded nose + tapering tail cone
    md.rounded_rectangle([S(px0 + fh * .2) - X, S(top) - Y, S(px0 + L * .86) - X, S(bot) - Y], radius=S(fh / 2), fill=255)
    md.polygon(Pp([(px0 + L * .80, top), (px0 + L * 1.0, cy - fh * .28), (px0 + L * 1.0, cy - fh * .05),
                   (px0 + L * .80, bot)]), fill=255)
    # 747 upper-deck hump
    md.ellipse([S(px0 + fh * .25) - X, S(top - fh * .42) - Y, S(px0 + L * .36) - X, S(top + fh * .5) - Y], fill=255)
    md.polygon(Pp([(px0 + L * .20, top - fh * .40), (px0 + L * .36, top + fh * .02), (px0 + L * .20, top + fh * .2)]), fill=255)
    col = Image.new("RGB", (lw, lh), (247, 248, 250)); cd = ImageDraw.Draw(col)
    cd.rectangle([0, S(cy + fh * .06) - Y, lw, lh], fill=(126, 186, 222))          # robin's-egg belly
    cd.rectangle([0, S(cy - fh * .02) - Y, lw, S(cy + fh * .10) - Y], fill=(28, 52, 110))  # cheatline
    img.paste(col, (X, Y), m)
    draw2 = ImageDraw.Draw(img)
    # tail fin, stabiliser, wing, engines
    poly([(px0 + L * .80, top + 0.5), (px0 + L * .90, top - fh * 1.45), (px0 + L * .99, top - fh * 1.45),
          (px0 + L * .97, top + 0.5)], fill=(28, 52, 110))
    for k in range(3):   # flag stripes on the fin
        line([(px0 + L * (.885 + k * .003), top - fh * (1.1 - k * .22)),
              (px0 + L * (.965 + k * .002), top - fh * (1.1 - k * .22))], (196, 40, 48), 0.9)
    poly([(px0 + L * .86, cy - fh * .05), (px0 + L * 1.02, cy - fh * .30), (px0 + L * 1.02, cy - fh * .12),
          (px0 + L * .90, cy + fh * .08)], fill=(205, 212, 222))
    poly([(px0 + L * .36, cy + fh * .30), (px0 + L * .62, cy + fh * .55), (px0 + L * .66, cy + fh * .48),
          (px0 + L * .46, cy + fh * .22)], fill=(170, 180, 194))
    for ex in (.40, .50):
        draw.rounded_rectangle([S(px0 + L * ex), S(cy + fh * .48), S(px0 + L * (ex + .075)), S(cy + fh * .98)],
                               radius=S(fh * .22), fill=(200, 206, 216), outline=(120, 128, 140), width=S(0.6))
        ell(px0 + L * ex - 0.2, cy + fh * .52, fh * .35, fh * .42, fill=(70, 76, 90))
    # windows, cockpit
    for k in range(26):
        wx = px0 + L * (.10 + k * .027)
        if wx > px0 + L * .80: break
        ell(wx, cy - fh * .30, 1.25, 1.35, fill=(40, 52, 80))
    for k in range(5):
        ell(px0 + L * (.08 + k * .028), top - fh * .12, 1.15, 1.25, fill=(40, 52, 80))
    poly([(px0 + fh * .30, top - fh * .02), (px0 + fh * .75, top - fh * .12), (px0 + fh * .85, top + fh * .12),
          (px0 + fh * .35, top + fh * .16)], fill=(30, 36, 52))
    # landing gear
    for gx in (.12, .48, .56):
        line([(px0 + L * gx, bot), (px0 + L * gx, y + h * .855)], (60, 60, 66), 0.9)
        ell(px0 + L * gx - 2.2, y + h * .835, 4.4, 4.4, fill=(28, 28, 32))
    # airstairs + red carpet
    sx0 = px0 + L * .17
    poly([(sx0, cy - fh * .1), (sx0 + w * .07, y + h * .89), (sx0 + w * .085, y + h * .89), (sx0 + w * .012, cy - fh * .1)],
         fill=(236, 236, 240))
    for k in range(6):
        t = (k + 1) / 7
        line([(sx0 + w * .07 * t, cy - fh * .1 + (y + h * .89 - cy + fh * .1) * t),
              (sx0 + w * .07 * t + w * .014, cy - fh * .1 + (y + h * .89 - cy + fh * .1) * t)], (150, 150, 160), 0.7)
    poly([(sx0 + w * .07, y + h * .89), (sx0 + w * .30, y + h * .93), (sx0 + w * .30, y + h * .955),
          (sx0 + w * .07, y + h * .91)], fill=(196, 34, 44))
    # tag chip
    draw.rounded_rectangle([S(x + 5), S(y + 5), S(x + 123), S(y + 19)], radius=S(2), fill=(255, 255, 255))
    txt(x + 11, y + 6.5, "XI · TRUMP · PUTIN", SANS_B, 9.5)

def art_gulf(x, y, w, h):
    """The northern Gulf from Natural Earth 1:50m coastlines: Ali Al Salem air
    base (Kuwait), Bahrain, and Qeshm island, with the drone track."""
    lon0, lat0, k = 51.2, 28.0, h / 5.0          # px per degree latitude
    kx = k * math.cos(math.radians(lat0))
    def pr(lon, lat): return (x + w / 2 + (lon - lon0) * kx, y + h / 2 - (lat - lat0) * k)
    vgrad((x, y, x + w, y + h), (14, 38, 80), (8, 24, 54))
    def land(d, X, Y):
        for ring in GULF_LAND:
            pts = [(S(pr(a, b)[0]) - X, S(pr(a, b)[1]) - Y) for a, b in ring]
            if len(pts) > 2:
                d.polygon(pts, fill=(44, 70, 114, 255), outline=(120, 152, 196, 255))
    soft(x, y, w, h, land)
    # faint graticule
    for lo in range(44, 60, 2):
        xx = pr(lo, 0)[0]
        if x < xx < x + w: line([(xx, y), (xx, y + h)], (40, 66, 108), 0.4)
    for la in range(26, 31, 1):
        yy = pr(0, la)[1]
        if y < yy < y + h: line([(x, yy), (x + w, yy)], (40, 66, 108), 0.4)
    kw, bh, qs = pr(47.52, 29.35), pr(50.55, 26.07), pr(55.90, 26.85)
    # drone track Iran -> Kuwait (dashed arc), soft
    src = pr(50.3, 29.6)
    def track(d, X, Y):
        n = 28
        for i in range(n):
            if i % 2: continue
            t0, t1 = i / n, (i + 1) / n
            def q(t):
                mx, my = (src[0] + kw[0]) / 2, min(src[1], kw[1]) - h * 0.16
                return ((1 - t) ** 2 * src[0] + 2 * (1 - t) * t * mx + t * t * kw[0],
                        (1 - t) ** 2 * src[1] + 2 * (1 - t) * t * my + t * t * kw[1])
            a0, a1 = q(t0), q(t1)
            d.line([(S(a0[0]) - X, S(a0[1]) - Y), (S(a1[0]) - X, S(a1[1]) - Y)], fill=(255, 140, 90, 230), width=S(1.3))
    soft(x, y, w, h, track)
    # strike burst on Qeshm (US strike)
    soft(x, y, w, h, lambda d, X, Y: d.ellipse([S(qs[0] - 11) - X, S(qs[1] - 11) - Y, S(qs[0] + 11) - X,
         S(qs[1] + 11) - Y], fill=(255, 90, 60, 170)), blur=3)
    ell(qs[0] - 3, qs[1] - 3, 6, 6, fill=(255, 220, 200))
    # Kuwait glow + star
    soft(x, y, w, h, lambda d, X, Y: d.ellipse([S(kw[0] - 13) - X, S(kw[1] - 13) - Y, S(kw[0] + 13) - X,
         S(kw[1] + 13) - Y], fill=(255, 217, 77, 120)), blur=3.5)
    star(kw[0], kw[1], 7, 3)
    pts = []
    for i in range(10):
        r = 5.5 if i % 2 == 0 else 2.4
        a_ = math.radians(-90 + i * 36)
        pts.append((S(bh[0] + r * math.cos(a_)), S(bh[1] + r * math.sin(a_))))
    draw.polygon(pts, fill=(255, 255, 255))
    lab = (150, 175, 208)
    txt(pr(45.6, 30.35)[0], pr(0, 30.35)[1], "IRAQ", SANS_B, 9, lab)
    txt(pr(52.6, 30.4)[0], pr(0, 30.4)[1], "IRAN", SANS_B, 9, lab)
    txt(kw[0] - 52, kw[1] - 6, "KUWAIT", SANS_B, 10, (255, 255, 255))
    txt(kw[0] - 52, kw[1] + 5, "Ali Al Salem", SANS, 7.5, (210, 222, 240))
    txt(pr(44.2, 26.6)[0], pr(0, 26.6)[1], "SAUDI ARABIA", SANS_B, 9, lab)
    txt(bh[0] + 7, bh[1] - 5, "BAHRAIN", SANS_B, 9, C["gold"])
    txt(qs[0] - 30, qs[1] + 6, "QESHM", SANS_B, 8.5, (255, 175, 150))
    txt(qs[0] - 30, qs[1] + 15.5, "US strike", SANS, 7.5, (255, 200, 185))
    txt(pr(50.9, 27.55)[0], pr(0, 27.55)[1], "THE GULF", SANS_B, 8.5, (100, 135, 182))

def art_voyager(x, y, w, h):
    rect(x, y, w, h, fill=(11, 11, 38))
    rnd = random.Random(11)
    for _ in range(46):
        dx, dy = rnd.random() * w, rnd.random() * h
        r = 0.9 + rnd.random() * 0.8
        ell(x + dx, y + dy, r, r, fill=(255, 255, 255))
    # faint Milky Way band
    soft(x, y, w, h, lambda d, X, Y: d.polygon([(0, S(h * .95)), (S(w * .35), 0), (S(w * .55), 0),
         (S(w * .2), S(h))], fill=(70, 70, 130, 90)), blur=8)
    # earth with an atmosphere glow
    ex, ey, er = x + w * 0.16, y + h * 0.72, h * 0.18
    soft(x, y, w, h, lambda d, X, Y: d.ellipse([S(ex - er * 1.6) - X, S(ey - er * 1.6) - Y,
         S(ex + er * 1.6) - X, S(ey + er * 1.6) - Y], fill=(110, 170, 255, 130)), blur=4)
    ell(ex - er, ey - er, er * 2, er * 2, fill=(59, 130, 246))
    ell(ex - er * 0.45, ey - er * 0.5, er * 0.7, er * 0.55, fill=(74, 222, 128))
    ell(ex + er * 0.1, ey + er * 0.25, er * 0.55, er * 0.45, fill=(74, 222, 128))
    # path + voyager
    vx, vy = x + w * 0.90, y + h * 0.26
    line([(ex + er * 0.5, ey - er * 0.6), (vx, vy)], (199, 210, 254), 1.5)
    soft(x, y, w, h, lambda d, X, Y: d.ellipse([S(vx - 22) - X, S(vy - 22) - Y, S(vx + 22) - X,
         S(vy + 22) - Y], fill=(255, 255, 230, 110)), blur=5)
    ell(vx - 10, vy - 10, 20, 20, fill=(229, 231, 235))
    draw.ellipse([S(vx - 15), S(vy - 15), S(vx + 15), S(vy + 15)], outline=(229, 231, 235), width=S(1.5))
    t = "VOYAGER 1"
    f = F(SANS_B, 9.5)
    txt(x + w - text_w(t, f) - 6, y + h * 0.06, t, SANS_B, 9.5, (255, 255, 255))
    t2 = "1 LIGHT-DAY · 25.9 BILLION KM"
    f2 = F(SANS_B, 10)
    txt(x + w - text_w(t2, f2) - 6, y + h * 0.52, t2, SANS_B, 10, C["gold"])
    txt(x + 6, y + h - 13, "EARTH", SANS_B, 9, (255, 255, 255))

def art_eu(x, y, w, h):
    rect(x, y, w, h, fill=(30, 64, 175))
    cx, cy, r = x + w * 0.23, y + h * 0.5, h * 0.36
    for i in range(12):
        a = math.radians(-90 + i * 30)
        star(cx + r * math.cos(a), cy + r * math.sin(a), 3.4, 1.5)
    txt(x + w * 0.40, y + h * 0.30, "€45bn", SANS_B, 24, C["gold"])

def art_drones(x, y, w, h):
    rect(x, y, w, h, fill=(11, 11, 38))
    rnd = random.Random(5)
    for _ in range(14):
        ell(x + rnd.random() * w, y + rnd.random() * h * 0.6, 1.6, 1.6, fill=(255, 255, 255))
    for fx, fy in [(0.19, 0.32), (0.47, 0.40), (0.68, 0.28), (0.88, 0.42), (0.37, 0.58)]:
        ell(x + w * fx - 2, y + h * fy - 2, 4, 4, fill=(239, 68, 68))
    star(x + w * 0.63, y + h * 0.55, 6, 2.6)
    rect(x, y + h - 13, w, 13, fill=(0, 0, 0))
    t = "141 FIRED · 126 DOWNED"
    f = F(SANS_B, 8.5)
    txt(x + (w - text_w(t, f)) / 2, y + h - 11.5, t, SANS_B, 8.5, (255, 255, 255))

def art_senate(x, y, w, h):
    rect(x, y, w, h, fill=(255, 255, 255))
    rect(x + 6, y + 7, w - 12, 22, fill=(29, 78, 216))
    rect(x + w * 0.5, y + 7, w * 0.5 - 6, 22, fill=(185, 28, 28))
    txt(x + 14, y + 10.5, "56", SANS_B, 14, (255, 255, 255))
    txt(x + w * 0.44, y + 12, "D–R", SANS_B, 10, (255, 255, 255))
    txt(x + w - 26, y + 10.5, "44", SANS_B, 14, (255, 255, 255))
    t = "US SENATE"
    f = F(SANS_B, 9)
    txt(x + (w - text_w(t, f)) / 2, y + h - 13, t, SANS_B, 9, (102, 102, 102))

def art_cop(x, y, w, h):
    rect(x, y, w, h, fill=(238, 246, 246))
    ex, ey, er = x + w * 0.25, y + h * 0.5, h * 0.32
    ell(ex - er, ey - er, er * 2, er * 2, fill=(59, 130, 246))
    ell(ex - er * 0.4, ey - er * 0.45, er * 0.6, er * 0.5, fill=(74, 222, 128))
    ell(ex + er * 0.15, ey + er * 0.2, er * 0.5, er * 0.4, fill=(74, 222, 128))
    # thermometer
    tx = x + w * 0.55
    rect(tx, y + 7, 7, 30, fill=(255, 255, 255), outline=(185, 28, 28), width=1.5)
    rect(tx + 2, y + 9, 3, 16, fill=(239, 68, 68))
    ell(tx - 2.5, y + h - 15, 12, 12, fill=(239, 68, 68))
    # draft doc
    dx = x + w * 0.68
    rect(dx, y + h * 0.42, w * 0.26, h * 0.46, fill=(255, 255, 255), outline=(153, 153, 153))
    txt(dx + 5, y + h * 0.46, "DRAFT", SANS_B, 7, (185, 28, 28))
    line([(dx + 5, y + h * 0.68), (dx + w * 0.22, y + h * 0.68)], (153, 153, 153))
    line([(dx + 5, y + h * 0.78), (dx + w * 0.19, y + h * 0.78)], (153, 153, 153))
    txt(x + 6, y + h - 11, "ANTALYA · 18 pp.", SANS_B, 8, (68, 68, 68))

def art_inflation(x, y, w, h):
    rect(x, y, w, h, fill=(255, 255, 255))
    for cx, val, col, lab in [(0.25, "3.6%", (156, 163, 175), "UK"),
                              (0.75, "4.0%", (29, 78, 216), "EURO AREA")]:
        f = F(SANS_B, 10)
        txt(x + w * cx - text_w(val, f) / 2, y + 2, val, SANS_B, 10)
        rect(x + w * cx - 20, y + 16, 40, 22, fill=col)
        f2 = F(SANS_B, 8)
        txt(x + w * cx - text_w(lab, f2) / 2, y + h - 10, lab, SANS_B, 8, (68, 68, 68))

def art_cyclone(x, y, w, h):
    poly([(x, y), (x + w * 0.5, y), (x + w * 0.37, y + h), (x, y + h)], fill=(242, 227, 179))
    poly([(x + w * 0.5, y), (x + w, y), (x + w, y + h), (x + w * 0.63, y + h),
          (x + w * 0.5, y + h * 0.38)], fill=(191, 227, 234))
    cx, cy = x + w * 0.67, y + h * 0.45
    for r, a0, a1 in [(16, 40, 330), (10, 200, 120), (5, 20, 300)]:
        draw.arc([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], a0, a1, fill=(255, 255, 255), width=S(2.4))
    ell(cx - 2, cy - 2, 4, 4, fill=(255, 255, 255))
    txt(x + 6, y + 3, "INDIA", SANS_B, 8, (68, 68, 68))
    t = "BAY OF BENGAL"
    f = F(SANS_B, 8)
    txt(x + w - text_w(t, f) - 4, y + h - 11, t, SANS_B, 8, (29, 78, 216))

def art_sudan(x, y, w, h):
    rect(x, y, w, h, fill=(232, 201, 143))
    for bx, by, bw, bh in [(0.04,.55,.14,.45),(.21,.42,.11,.58),(.35,.60,.16,.40),
                           (.54,.48,.12,.52),(.68,.62,.15,.38),(.86,.52,.11,.48)]:
        rect(x + w * bx, y + h * by, w * bw, h * bh, fill=(138, 109, 59))
    poly([(x + w * 0.26, y + h * 0.18), (x + w * 0.285, y + h * 0.42),
          (x + w * 0.235, y + h * 0.42)], fill=(107, 79, 29))
    txt(x + 6, y + 3, "EL OBEID", SANS_B, 8, (68, 68, 68))

def art_gold(x, y, w, h):
    rect(x, y, w, h, fill=(253, 246, 227))
    pts = [(x + w * 0.05, y + h * 0.14), (x + w * 0.29, y + h * 0.20),
           (x + w * 0.50, y + h * 0.18), (x + w * 0.74, y + h * 0.36),
           (x + w * 0.93, y + h * 0.52)]
    line(pts, (185, 28, 28), 2.4)
    ex, ey = pts[-1]
    poly([(ex, ey), (ex - 12, ey - 2), (ex - 5, ey + 9)], fill=(185, 28, 28))
    txt(x + 8, y + h * 0.46, "$3,800", SERIF_B, 14)
    txt(x + 8, y + h - 9, "14-MONTH LOW", SANS_B, 7, (185, 28, 28))

def art_gta(x, y, w, h):
    vgrad((x, y, x + w, y + h), (91, 42, 110), (194, 65, 12))
    vgrad((x, y + h * 0.55, x + w, y + h), (194, 65, 12), (31, 41, 55))
    ell(x + w * 0.86, y + h * 0.08, w * 0.07, h * 0.26, fill=(253, 230, 138))
    for bx, by, bw, bh in [(0,.72,.07,.28),(.09,.60,.06,.40),(.18,.75,.08,.25),
                           (.28,.64,.06,.36),(.37,.78,.09,.22),(.48,.68,.07,.32),
                           (.57,.56,.07,.44),(.66,.75,.08,.25),(.77,.64,.06,.36),
                           (.85,.78,.08,.22),(.94,.72,.06,.28)]:
        rect(x + w * bx, y + h * by, w * bw, h * bh, fill=(17, 24, 39))
    # controller
    cx, cy, cw, chh = x + w * 0.33, y + h * 0.22, w * 0.35, h * 0.28
    draw.rounded_rectangle([S(cx), S(cy), S(cx + cw), S(cy + chh)], radius=S(7),
                           fill=(244, 246, 248), outline=INK, width=S(1))
    ell(cx + cw * 0.14, cy + chh * 0.32, 7, 7, outline=INK)
    for dx, dy in [(0.68, 0.28), (0.76, 0.40), (0.68, 0.52), (0.60, 0.40)]:
        ell(cx + cw * dx, cy + chh * dy, 3, 3, fill=INK)
    txt(x + 6, y + 3, "MIDNIGHT IN NZ", SANS_B, 8, (255, 255, 255))

def art_ethiopia(x, y, w, h):
    rect(x, y, w, h, fill=(242, 227, 179))
    poly([(x + w * 0.50, y), (x + w, y), (x + w, y + h), (x + w * 0.74, y + h),
          (x + w * 0.58, y + h * 0.50)], fill=(191, 227, 234))
    # green arrow right
    poly([(x + w * 0.07, y + h * 0.30), (x + w * 0.60, y + h * 0.30), (x + w * 0.60, y + h * 0.20),
          (x + w * 0.70, y + h * 0.40), (x + w * 0.60, y + h * 0.60), (x + w * 0.60, y + h * 0.50),
          (x + w * 0.07, y + h * 0.50)], fill=(21, 128, 61))
    # red arrow left
    poly([(x + w * 0.93, y + h * 0.62), (x + w * 0.40, y + h * 0.62), (x + w * 0.40, y + h * 0.52),
          (x + w * 0.30, y + h * 0.72), (x + w * 0.40, y + h * 0.92), (x + w * 0.40, y + h * 0.82),
          (x + w * 0.93, y + h * 0.82)], fill=(185, 28, 28))
    txt(x + 6, y + 3, "ETHIOPIA", SANS_B, 8, (68, 68, 68))
    t = "ERITREA"
    f = F(SANS_B, 8)
    txt(x + w - text_w(t, f) - 4, y + h - 11, t, SANS_B, 8, (185, 28, 28))

ART = {"apec": art_apec, "gulf": art_gulf, "voyager": art_voyager, "eu": art_eu,
       "drones": art_drones, "senate": art_senate, "cop": art_cop,
       "inflation": art_inflation, "cyclone": art_cyclone, "sudan": art_sudan,
       "gold": art_gold, "gta": art_gta, "ethiopia": art_ethiopia}

# ---------------------------------------------------------------- data
HEROES = [
 dict(num=1, col="asia", kick="ASIA · APEC SUMMIT", src="AFP · AP", art="apec",
      head="Xi meets Trump on the tarmac as APEC opens in Shenzhen",
      dek="The two men hug at the airport; Trump shakes hands with Putin at the banquet, and the first three-way talks are set for Thursday."),
 dict(num=2, col="me", kick="MIDDLE EAST · IRAN WAR", src="REUTERS", art="gulf",
      head="Iran claims drone hits on a US air base in Kuwait",
      dek="Tehran calls it payback for the US strike on Qeshm. Kuwait says its defences held; Bahrain turns back another wave."),
 dict(num=3, col="sp", kick="SPACE · SCIENCE", src="NASA", art="voyager",
      head="Voyager 1, first craft one light-day from Earth",
      dek="At 10:16 UTC it passed 25.9bn km. A command sent today arrives tomorrow."),
]
ROWS = [
 dict(num=4, col="eu", kick="EUROPE · UKRAINE AID", art="eu",
      head="EU proposes a €45bn loan for Ukraine in 2027",
      dek="Repayment waits until Russia pays war reparations, von der Leyen says."),
 dict(num=5, col="eu", kick="EUROPE · UKRAINE WAR", art="drones",
      head="Russia fires 141 drones at Ukraine",
      dek="126 downed, Kyiv says; strikes on Odesa kill four."),
 dict(num=6, col="am", kick="AMERICAS · US POLITICS", art="senate",
      head="Democrats take Alaska; Senate 56–44",
      dek="AP calls it for Mary Peltola over Dan Sullivan."),
 dict(num=7, col="gl", kick="GLOBAL · CLIMATE", art="cop",
      head="Draft deal splits COP31 talks in Antalya",
      dek="Fossil-fuel wording and a $120bn finance goal divide the room."),
 dict(num=8, col="eu", kick="EUROPE · ECONOMY", art="inflation",
      head="Inflation climbs: UK 3.6%, euro area 4.0%",
      dek="Energy drives both; UK core holds at 2.8%."),
 dict(num=9, col="asia", kick="ASIA · WEATHER", art="cyclone",
      head="India braces for Cyclone Akvan",
      dek="Rescuers on standby; landfall due 20 November."),
 dict(num=10, col="af", kick="AFRICA · SUDAN WAR", art="sudan",
      head="Amnesty: RSF drones killed 37 in El Obeid",
      dek="It urges a war crimes probe of nine strikes."),
 dict(num=11, col="gl", kick="GLOBAL · MARKETS", art="gold",
      head="Gold falls below $3,800, a 14-month low",
      dek="Fed officials signal more rate rises."),
 dict(num=12, col="oc", kick="OCEANIA · CULTURE", art="gta",
      head="GTA VI unlocks first in New Zealand",
      dek="13 years after GTA V; launch rolls west from 11:00 GMT."),
 dict(num=13, col="af", kick="AFRICA · HORN OF AFRICA", art="ethiopia",
      head="Ethiopia and Eritrea mass troops on the border",
      dek="Reuters: both armies gather; no clashes confirmed."),
]
INDEX = [
 (14,"am","Washington:","Democrats nominate Jeffries for speaker, 251–11"),
 (15,"asia","Seoul:","Kospi jumps 2.7% as Asian chip stocks rally"),
 (16,"asia","Shenzhen:","Xi backs US–North Korea talks in meeting with Lee"),
 (17,"asia","Shenzhen:","Japan’s Takaichi makes first China visit as PM"),
 (18,"asia","Shenzhen:","Trump announces Philippine trade deal, no terms"),
 (19,"me","Yemen:","Saudi-led coalition says it hit 60 Houthi sites"),
 (20,"me","Israel:","Katz: troops stay in Lebanon, Syria, Gaza zones"),
 (21,"asia","Dhaka:","troops deployed as unrest over Hasina grows"),
 (22,"asia","Jakarta:","Bank Indonesia raises rates to 6.00%"),
 (23,"asia","Kashmir:","top LeT commander killed in Kulgam"),
 (24,"asia","Myanmar:","junta to “review” its ties with ASEAN"),
 (25,"af","Sudan:","army advances to within 60 km of Al Nuhud"),
 (26,"af","South Africa:","inflation rises to 5.2%"),
 (27,"af","Uganda:","EACOP oil pipeline fast-tracked"),
 (28,"eu","Berlin:","coalition cuts electricity tax to EU minimum"),
 (29,"eu","Romania:","M5.7 Vrancea quake; two lightly hurt"),
 (30,"eu","Turin:","Alcaraz beats Medvedev at the ATP Finals"),
 (31,"am","New York:","Anthropic prices its IPO; trading starts Thursday"),
 (32,"am","Santiago:","ECLAC: Latin American poverty falls to 24.4%"),
 (33,"am","Chile:","economy shrinks 1.1% in the third quarter"),
 (34,"am","Peru:","M6.0 quake offshore; no damage reported"),
 (35,"am","Bogotá:","Hegseth visits to deepen military ties"),
 (36,"oc","Australia:","wages rise 1.1%; settler groups sanctioned"),
 (37,"oc","Fiji:","national drought disaster declared"),
 (38,"oc","Cook Islands:","Cyclone Xavier holds at Category 5"),
 (39,"oc","Hobart:","England beat Australia to win ODI series 2–1"),
]
STATS = [
 ("141", "Russian drones fired at Ukraine overnight; 126 downed"),
 ("56–44", "Democratic Senate after AP calls Alaska"),
 ("25.9bn km", "Voyager 1 from Earth: one light-day"),
 ("$3,800", "gold breaks below it for the first time in 14 months"),
]

# ---------------------------------------------------------------- render
img = Image.new("RGB", (S(W), S(H)), (255, 255, 255))
draw = ImageDraw.Draw(img)
# paper + frame
rect(0, 0, W, H, fill=PAPER)
draw.rectangle([S(1.5), S(1.5), S(W - 1.5), S(H - 1.5)], outline=INK, width=S(3))

X0, X1 = 16, 1008
CW = X1 - X0  # 992

# --- masthead
txt(X0, 13, "THE DAY IN WORLD NEWS", SANS_B, 14, C["red"])
t = "39 STORIES · 6 CONTINENTS · ONE DAY"
f = F(SANS_B, 13)
txt(X1 - text_w(t, f), 13.5, t, SANS_B, 13)
# title, auto-fit to full width
title = "Wednesday 18 November 2026"
LNUM = ["lnum"]   # lining figures so the date and stats sit on the baseline
for sz in [72 - 0.5 * i for i in range(50)]:
    ft = F(PF_BK, sz)
    if draw.textlength(title, font=ft, features=LNUM) / SS <= CW - 2: break
draw.text((S(X0), S(84)), title, font=ft, fill=INK, anchor="ls", features=LNUM)
pre = "Everything on this page happened, or was first reported, on "
fp, fe = F(EBG_I, 16.5), F(DMS_I, 15.5)
draw.text((S(X0), S(107)), pre, font=fp, fill=(34, 34, 34), anchor="ls")
draw.text((S(X0 + text_w(pre, fp)), S(107)), "Wednesday 18 November 2026.", font=fe, fill=C["red"], anchor="ls")

# --- region strip
strip = [("ASIA 10", "asia", 190), ("MIDDLE EAST 3", "me", 130), ("EUROPE 6", "eu", 135),
         ("AFRICA 5", "af", 125), ("AMERICAS 7", "am", 135), ("OCEANIA 5", "oc", 125),
         ("GLOBAL 2", "gl", 90), ("SPACE 1", "sp", 62)]
sx = X0
for label, col, wdt in strip:
    rect(sx, 116, wdt, 21, fill=C[col])
    fs = F(SANS_B, 10.5)
    txt(sx + (wdt - text_w(label, fs)) / 2, 120.5, label, SANS_B, 10.5, (255, 255, 255))
    sx += wdt

# --- heroes
HY, HH = 145, 228
hcol_w = (CW - 2 * 11) / 3
for i, st in enumerate(HEROES):
    hx = X0 + i * (hcol_w + 11)
    ART[st["art"]](hx, HY, hcol_w, 102)
    rect(hx, HY, hcol_w, 102, outline=INK, width=1.5)
    draw_kicker(hx, HY + 107, hcol_w, st["num"], C[st["col"]], st["kick"], st["src"])
    used = fit_text(hx, HY + 125, hcol_w, st["head"], PF_B, [20, 19.5, 19, 18], 1.13, 66)
    fit_text(hx, HY + 125 + used + 3, hcol_w, st["dek"], EBG, [14.5, 14, 13.5, 13], 1.2, 56, (40, 40, 40))

# --- rows 2 & 3
def draw_row(y, items):
    ccol_w = (CW - 4 * 11) / 5
    for i, st in enumerate(items):
        cx = X0 + i * (ccol_w + 11)
        ART[st["art"]](cx, y, ccol_w, 53)
        rect(cx, y, ccol_w, 53, outline=INK, width=1.5)
        draw_kicker(cx, y + 58, ccol_w, st["num"], C[st["col"]], st["kick"],
                    num_size=13, kick_size=9.5)
        used = fit_text(cx, y + 75, ccol_w, st["head"], SERIF_B, [13, 12.5, 12], 1.14, 46)
        fit_text(cx, y + 75 + used + 2, ccol_w, st["dek"], EBG, [12.5, 12, 11.5], 1.18, 44, (40, 40, 40))

draw_row(381, ROWS[:5])
draw_row(521, ROWS[5:])

# --- also section
AY = 661
line([(X0, AY), (X1, AY)], INK, 2.5)
txt(X0, AY + 5, "ALSO ON WEDNESDAY 18 NOVEMBER", SANS_B, 13)
BY = 686
# map panel
MX, MW, MH = X0, 336, 168
rect(MX, BY, MW, MH, fill=(216, 236, 243), outline=INK, width=1.5)
scx, scy = MW / 460, MH / 240
def mp(pts): return [(MX + a * scx, BY + b * scy) for a, b in pts]
land = (232, 217, 172)
# Natural Earth 1:110m land, equirectangular, centred on 10°E so the Pacific
# dots (Cook Islands, Fiji) sit inside the frame; lat 80N..60S.
LONC, LATN, LATS = 10.0, 80.0, -60.0
def geo(lon, lat):
    lx = (lon - LONC + 180) % 360
    return MX + lx / 360 * MW, BY + (LATN - lat) / (LATN - LATS) * MH
def paint_world(d, X, Y):
    for la in range(-60, 81, 30):     # graticule
        yy = BY + (LATN - la) / (LATN - LATS) * MH
        d.line([(0, S(yy) - Y), (S(MW), S(yy) - Y)], fill=(196, 222, 232, 255), width=S(0.5))
    for lo in range(-180, 180, 30):
        xx = MX + ((lo - LONC + 180) % 360) / 360 * MW
        d.line([(S(xx) - X, 0), (S(xx) - X, S(MH))], fill=(196, 222, 232, 255), width=S(0.5))
    for rings, fill, outl in ((WORLD_LAND, land + (255,), (196, 176, 128, 255)),
                              (WORLD_LAKES, (216, 236, 243, 255), (196, 176, 128, 255))):
        for ring in rings:
            for shift in (-360, 0, 360):
                pts = []
                for lon, lat in ring:
                    lx = lon - LONC + 180 + shift
                    pts.append((S(MX + lx / 360 * MW) - X, S(BY + (LATN - lat) / (LATN - LATS) * MH) - Y))
                if max(p[0] for p in pts) < 0 or min(p[0] for p in pts) > S(MW): continue
                if len(pts) > 2: d.polygon(pts, fill=fill, outline=outl)
soft(MX, BY, MW, MH, paint_world)
txt(MX + 8, BY + 6, "WHERE IT HAPPENED", SANS_B, 9, (68, 68, 68))
# numbered markers at true positions; overlapping discs are nudged apart
# (deterministic relaxation) and tied back to their spot with a leader line
PLACES = [(14, "am", -77.0, 38.9), (31, "am", -74.0, 40.7), (35, "am", -74.1, 4.7),
          (34, "am", -77.0, -12.0), (32, "am", -70.7, -33.4), (28, "eu", 13.4, 52.5),
          (30, "eu", 7.7, 45.1), (29, "eu", 26.5, 45.7), (20, "me", 35.2, 31.8),
          (19, "me", 44.2, 15.4), (25, "af", 29.0, 13.0), (27, "af", 32.6, 0.3),
          (26, "af", 28.0, -26.0), (23, "asia", 75.0, 33.7), (21, "asia", 90.4, 23.8),
          (16, "asia", 114.1, 22.5), (15, "asia", 127.0, 37.6), (22, "asia", 106.8, -6.2),
          (36, "oc", 149.1, -35.3), (39, "oc", 147.3, -42.9), (37, "oc", 178.4, -18.1),
          (38, "oc", -159.8, -21.2)]
R = 6.2
anchors = [geo(lo, la) for _, _, lo, la in PLACES]
pos = [list(p) for p in anchors]
for _ in range(400):
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            dx, dy = pos[j][0] - pos[i][0], pos[j][1] - pos[i][1]
            dd = math.hypot(dx, dy)
            if dd < 2 * R + 1.6:
                if dd < 1e-6: dx, dy, dd = 0.0, 1.0, 1.0
                push = (2 * R + 1.6 - dd) / 2
                pos[i][0] -= dx / dd * push; pos[i][1] -= dy / dd * push
                pos[j][0] += dx / dd * push; pos[j][1] += dy / dd * push
    for i, p in enumerate(pos):     # gentle pull home, stay in frame
        p[0] += (anchors[i][0] - p[0]) * 0.02; p[1] += (anchors[i][1] - p[1]) * 0.02
        p[0] = min(max(p[0], MX + R + 2), MX + MW - R - 2)
        p[1] = min(max(p[1], BY + 18 + R), BY + MH - 20 - R)
for (num, col, _, _), (ax, ay), (px, py) in zip(PLACES, anchors, pos):
    if math.hypot(px - ax, py - ay) > 3:
        line([(ax, ay), (px, py)], (90, 90, 90), 0.7)
        ell(ax - 1.4, ay - 1.4, 2.8, 2.8, fill=(60, 60, 60))
for (num, col, _, _), (px, py) in zip(PLACES, pos):
    soft(px - R - 3, py - R - 2, 2 * R + 6, 2 * R + 6, lambda d, X, Y, px=px, py=py: d.ellipse(
        [S(px - R) - X, S(py - R + 1) - Y, S(px + R) - X, S(py + R + 1) - Y], fill=(0, 0, 0, 70)), blur=0.9)
    ell(px - R, py - R, 2 * R, 2 * R, fill=C[col])
    draw.ellipse([S(px - R), S(py - R), S(px + R), S(py + R)], outline=(255, 255, 255), width=S(0.8))
    t = str(num); fn = F(SANS_B, 7.5)
    txt(px - text_w(t, fn) / 2, py - 5.2, t, SANS_B, 7.5, (255, 255, 255))
rect(MX + 5, BY + MH - 17, 168, 13, fill=(255, 255, 255), outline=INK)
txt(MX + 10, BY + MH - 15, "3 — VOYAGER 1, OFF THE MAP", SANS_B, 9)

# stats 2x2
SY = BY + MH + 8
sw = MW / 2
for i, (num, cap) in enumerate(STATS):
    sx = MX + (i % 2) * sw
    sy = SY + (i // 2) * 61
    if i % 2 == 0:
        line([(sx + sw - 6, sy + 2), (sx + sw - 6, sy + 56)], (153, 153, 153), 1)
    if i < 2:
        line([(sx, sy + 58), (sx + sw - (8 if i % 2 == 0 else 0), sy + 58)], (153, 153, 153), 1)
    tx = sx if i % 2 == 0 else sx + 10
    tw = sw - (16 if i % 2 == 0 else 10)
    fnum = F(PF_BK, 27)
    draw.text((S(tx), S(sy + 25)), num, font=fnum, fill=INK, anchor="ls", features=LNUM)
    fit_text(tx, sy + 30, tw, cap, SERIF, [9.5], 1.25, 28)

# --- index (two columns), auto-fit font
IX = MX + MW + 12
IW = X1 - IX
ICW = (IW - 12) / 2
def index_height(size):
    f = F(SERIF, size)
    total = 0
    for col in (INDEX[:13], INDEX[13:]):
        h = 0
        for num, colr, place, text in col:
            full = place + " " + text
            lines = wrap(full, f, ICW - 19)
            h += len(lines) * size * 1.28 + 4.5
        total = max(total, h)
    return total

avail = (BY + MH + 8 + 122) - BY  # bottom block height
for sz in (10, 9.5, 9, 8.5):
    if index_height(sz) <= avail + 6:
        break
fidx = F(SERIF, sz)
fidxb = F(SERIF_B, sz)
for ci, col in enumerate((INDEX[:13], INDEX[13:])):
    cx = IX + ci * (ICW + 12)
    yy = BY
    for num, colr, place, text in col:
        r = 7
        ell(cx, yy + 1, 14, 14, fill=C[colr])
        fn = F(SANS_B, 8)
        txt(cx + 7 - text_w(str(num), fn) / 2, yy + 3.6, str(num), SANS_B, 8, (255, 255, 255))
        # bold place + regular rest, wrapped together
        words = (place + " " + text).split()
        lines, cur = [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if text_w(t, fidx) <= ICW - 19:
                cur = t
            else:
                if cur: lines.append(cur)
                cur = wd
        if cur: lines.append(cur)
        ly = yy
        for li, ln in enumerate(lines):
            # bold the place part on first line
            if li == 0 and ln.startswith(place):
                draw.text((S(cx + 19), S(ly)), place, font=fidxb, fill=INK)
                rest = ln[len(place):]
                draw.text((S(cx + 19 + text_w(place, fidxb)), S(ly)), rest, font=fidx, fill=(26, 26, 26))
            else:
                draw.text((S(cx + 19), S(ly)), ln, font=fidx, fill=(26, 26, 26))
            ly += sz * 1.28
        yy = ly + 4.5

# --- footer
FY = 992
line([(X0, FY), (X1, FY)], INK, 1.5)
txt(X0, FY + 5, "Claims by warring sides are attributed. Original drawings; map from Natural Earth.",
    SANS, 8.5, (68, 68, 68))
t = "Sources: AP · Reuters · AFP · NASA · EU Commission · ONS · Eurostat · IMD · UNFCCC · Amnesty · Ukraine Air Force"
fr = F(SANS, 8.5)
txt(X1 - text_w(t, fr), FY + 5, t, SANS, 8.5, (68, 68, 68))

img = img.resize((W, H), Image.LANCZOS)
img.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png"), optimize=True)
print("saved", img.size)
