#!/usr/bin/env python3
"""Square 1024x1024 recomposition of 'The Day in World News — Wed 18 Nov 2026'.
Fresh PIL renderer (supersampled 2x, downscaled to 1024). Written from scratch.
"""
import math, random
from PIL import Image, ImageDraw, ImageFont

SS = 2                      # supersample factor
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
    h = max(1, int(y1 - y0))
    for i in range(h):
        t = i / h
        c = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
        draw.line([S(x0), S(y0 + i), S(x1), S(y0 + i)], fill=c)

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
    vgrad((x, y, x + w, y + h), (246, 169, 59), (251, 211, 141))
    ell(x + w * 0.82, y + h * 0.10, w * 0.09, h * 0.28, fill=(253, 243, 208))
    # skyline
    blds = [(0,.62,.06,.40),(.07,.52,.05,.50),(.14,.66,.045,.36),(.20,.48,.06,.54),
            (.27,.60,.04,.42),(.33,.70,.06,.32),(.41,.56,.05,.46),(.48,.68,.06,.34),
            (.55,.50,.05,.52),(.62,.64,.045,.38),(.68,.58,.06,.44),(.76,.68,.05,.34),
            (.82,.54,.055,.48),(.89,.66,.05,.36),(.95,.58,.05,.44)]
    for bx, by, bw, bh in blds:
        rect(x + w * bx, y + h * by, w * bw, h * bh, fill=(43, 33, 64))
    rnd = random.Random(7)
    for bx, by, bw, bh in blds:
        for _ in range(3):
            wx = x + w * (bx + rnd.random() * bw * 0.7)
            wy = y + h * (by + 0.08 + rnd.random() * bh * 0.55)
            rect(wx, wy, 2.5, 3.5, fill=(255, 217, 77))
    # plane
    px, py = x + w * 0.18, y + h * 0.30
    poly([(px, py), (px + w * 0.28, py - h * 0.03), (px + w * 0.44, py + h * 0.015),
          (px + w * 0.28, py + h * 0.05), (px + w * 0.11, py + h * 0.07),
          (px + w * 0.06, py + h * 0.13), (px + w * 0.03, py + h * 0.07),
          (px, py + h * 0.045)], fill=(244, 246, 248))
    poly([(px + w * 0.28, py - h * 0.04), (px + w * 0.34, py - h * 0.22),
          (px + w * 0.365, py - h * 0.04)], fill=(29, 78, 216))
    for i in range(3):
        ell(px + w * (0.17 + i * 0.04), py + h * 0.015, 2.2, 2.2, fill=(29, 78, 216))
    # tag chip
    rect(x + 5, y + h - 18, 118, 14, fill=(255, 255, 255))
    txt(x + 11, y + h - 16.5, "XI · TRUMP · PUTIN", SANS_B, 9.5)

def art_gulf(x, y, w, h):
    rect(x, y, w, h, fill=(10, 28, 61))
    poly([(x + w * .09, y + h * .30), (x + w * .38, y + h * .12), (x + w * .67, y + h * .22),
          (x + w * .91, y + h * .47), (x + w * .94, y + h * .76), (x + w * .56, y + h * .94),
          (x + w * .19, y + h * .86), (x + w * .06, y + h * .61)], fill=(18, 41, 79))
    poly([(x + w * .47, y + h * .20), (x + w * .73, y + h * .26), (x + w * .89, y + h * .51),
          (x + w * .56, y + h * .88), (x + w * .38, y + h * .39)], fill=(14, 34, 66))
    txt(x + w * .16, y + h * .22, "IRAQ", SANS_B, 9, (143, 168, 200))
    txt(x + w * .74, y + h * .20, "IRAN", SANS_B, 9, (143, 168, 200))
    txt(x + w * .43, y + h * .36, "KUWAIT", SANS_B, 10, (255, 255, 255))
    txt(x + w * .37, y + h * .68, "SAUDI ARABIA", SANS_B, 9, (143, 168, 200))
    txt(x + w * .66, y + h * .60, "BAHRAIN", SANS_B, 9, C["gold"])
    txt(x + w * .69, y + h * .82, "THE GULF", SANS_B, 9, (91, 123, 166))
    star(x + w * .58, y + h * .42, 7, 3)
    star(x + w * .43, y + h * .58, 4.5, 2)
    # white star bahrain
    pts = []
    for i in range(10):
        r = 5.5 if i % 2 == 0 else 2.4
        a = math.radians(-90 + i * 36)
        pts.append((S(x + w * .66 + r * math.cos(a)), S(y + h * .76 + r * math.sin(a))))
    draw.polygon(pts, fill=(255, 255, 255))

def art_voyager(x, y, w, h):
    rect(x, y, w, h, fill=(11, 11, 38))
    rnd = random.Random(11)
    for _ in range(46):
        dx, dy = rnd.random() * w, rnd.random() * h
        r = 0.9 + rnd.random() * 0.8
        ell(x + dx, y + dy, r, r, fill=(255, 255, 255))
    # earth
    ex, ey, er = x + w * 0.16, y + h * 0.72, h * 0.18
    ell(ex - er, ey - er, er * 2, er * 2, fill=(59, 130, 246))
    ell(ex - er * 0.45, ey - er * 0.5, er * 0.7, er * 0.55, fill=(74, 222, 128))
    ell(ex + er * 0.1, ey + er * 0.25, er * 0.55, er * 0.45, fill=(74, 222, 128))
    # path + voyager
    vx, vy = x + w * 0.90, y + h * 0.26
    line([(ex + er * 0.5, ey - er * 0.6), (vx, vy)], (199, 210, 254), 1.5)
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
for sz in (54, 52, 50, 48):
    ft = F(DISPLAY_BK, sz)
    if text_w(title, ft) <= CW: break
draw.text((S(X0), S(32)), title, font=ft, fill=INK)
txt(X0, 92, "Everything on this page happened, or was first reported, on Wednesday 18 November 2026.",
    SERIF_I, 14.5, (34, 34, 34))

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
    used = fit_text(hx, HY + 127, hcol_w, st["head"], SERIF_B, [19, 18, 17], 1.12, 64)
    fit_text(hx, HY + 127 + used + 3, hcol_w, st["dek"], SERIF, [12.5, 12, 11.5], 1.32, 44)

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
        fit_text(cx, y + 75 + used + 2, ccol_w, st["dek"], SERIF, [10.5, 10, 9.5], 1.3, 42)

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
poly(mp([(18,62),(62,34),(112,36),(142,56),(132,88),(112,106),(86,96),(72,122),(46,112),(22,84)]), fill=land)
poly(mp([(138,26),(152,22),(162,30),(154,40),(140,38)]), fill=land)
poly(mp([(116,132),(152,126),(166,152),(156,196),(136,216),(121,182),(111,152)]), fill=land)
poly(mp([(206,116),(252,106),(276,130),(266,176),(241,206),(216,182),(201,146)]), fill=land)
poly(mp([(216,72),(242,50),(266,60),(261,86),(241,96),(221,88)]), fill=land)
poly(mp([(272,62),(322,32),(382,36),(432,56),(422,96),(372,116),(322,112),(286,96),(266,82)]), fill=land)
poly(mp([(356,132),(372,128),(382,136),(374,146),(358,144)]), fill=land)
poly(mp([(392,142),(404,139),(412,145),(406,153),(394,152)]), fill=land)
poly(mp([(376,172),(422,166),(436,186),(411,201),(381,196)]), fill=land)
poly(mp([(446,206),(454,204),(459,209),(455,215),(447,214)]), fill=land)
txt(MX + 8, BY + 6, "WHERE IT HAPPENED", SANS_B, 9, (68, 68, 68))
dots = [(62,86,"14","am"),(44,58,"31","am"),(128,164,"34","am"),(232,54,"28","eu"),
        (264,66,"29","eu"),(240,88,"30","eu"),(276,126,"19","me"),(244,152,"27","af"),
        (382,90,"16","asia"),(398,72,"15","asia"),(402,184,"36","oc"),
        (446,160,"38","oc"),(420,206,"39","oc")]
for dx, dy, num, col in dots:
    px, py = MX + dx * scx, BY + dy * scy
    ell(px - 7.5, py - 7.5, 15, 15, fill=C[col])
    fn = F(SANS_B, 8.5)
    txt(px - text_w(num, fn) / 2, py - 4.6, num, SANS_B, 8.5, (255, 255, 255))
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
    fnum = F(DISPLAY_BK, 26)
    draw.text((S(tx), S(sy)), num, font=fnum, fill=INK)
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
