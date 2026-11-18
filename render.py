"""Render a deterministic, typeset 1024px world-news front page.

Requires Python 3, Pillow, and the system DejaVu fonts. No external assets,
network access, randomness, clock reads, or generated image metadata.
"""
from functools import lru_cache
from math import cos, sin, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
SCALE = 3
PAPER = "#f6f1e4"
INK = "#1a1a1a"
RED = "#b3382c"
NAVY = "#14213d"
BLUE = "#547a89"
PALE = "#dfE5df"
STONE = "#e5ddcc"
MUTED = "#646158"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
ROOT = Path(__file__).resolve().parent
image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
draw = ImageDraw.Draw(image)
TEXT_BOXES = []


@lru_cache(maxsize=None)
def font(size, family="sans"):
    names = {
        "sans": "DejaVuSans.ttf",
        "bold": "DejaVuSans-Bold.ttf",
        "serif": "DejaVuSerif-Bold.ttf",
        "book": "DejaVuSerif.ttf",
    }
    return ImageFont.truetype(str(FONT_DIR / names[family]), round(size * SCALE))


def rect(box, fill=None, outline=None, width=1):
    draw.rectangle(tuple(round(v * SCALE) for v in box), fill=fill,
                   outline=outline, width=round(width * SCALE))


def line(points, fill=INK, width=1):
    draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
              fill=fill, width=max(1, round(width * SCALE)), joint="curve")


def poly(points, fill, outline=None, width=1):
    scaled = [(round(x * SCALE), round(y * SCALE)) for x, y in points]
    draw.polygon(scaled, fill=fill)
    if outline:
        draw.line(scaled + [scaled[0]], fill=outline,
                  width=round(width * SCALE), joint="curve")


def ellipse(box, fill=None, outline=None, width=1):
    draw.ellipse(tuple(round(v * SCALE) for v in box), fill=fill,
                 outline=outline, width=round(width * SCALE))


def text_width(value, size, family="sans"):
    return draw.textlength(value, font=font(size, family)) / SCALE


def text(value, x, y, size, family="sans", color=INK, align="left", max_width=None):
    face = font(size, family)
    bounds = draw.textbbox((0, 0), value, font=face)
    w = (bounds[2] - bounds[0]) / SCALE
    h = (bounds[3] - bounds[1]) / SCALE
    if max_width is not None:
        assert w <= max_width + 0.5, (value, w, max_width)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    assert x >= 27 and x + w <= 997, (value, x, w)
    assert y >= 20 and y + h <= 1000, (value, y, h)
    draw.text((round(x * SCALE) - bounds[0], round(y * SCALE) - bounds[1]),
              value, font=face, fill=color)
    TEXT_BOXES.append((value, (x, y, x + w, y + h)))
    return h


def fitted(value, x, y, size, family, max_width, color=INK, align="left", minimum=10):
    while text_width(value, size, family) > max_width and size > minimum:
        size -= 0.25
    text(value, x, y, size, family, color, align, max_width)


def tracked(value, center, y, size, spacing, color=INK):
    widths = [text_width(ch, size, "bold") for ch in value]
    total = sum(widths) + spacing * (len(value) - 1)
    x = center - total / 2
    for ch, w in zip(value, widths):
        if ch != " ":
            text(ch, x, y, size, "bold", color)
        x += w + spacing


def star(cx, cy, radius, color=PAPER, points=5):
    vertices = []
    for i in range(points * 2):
        angle = -pi / 2 + i * pi / points
        r = radius if i % 2 == 0 else radius * 0.43
        vertices.append((cx + cos(angle) * r, cy + sin(angle) * r))
    poly(vertices, color)


def globe(cx, cy, r, color=INK, stroke=1):
    ellipse((cx-r, cy-r, cx+r, cy+r), outline=color, width=stroke)
    ellipse((cx-r*0.48, cy-r, cx+r*0.48, cy+r), outline=color, width=stroke)
    line([(cx-r, cy), (cx+r, cy)], color, stroke)
    line([(cx-r*0.85, cy-r*0.45), (cx+r*0.85, cy-r*0.45)], color, stroke)
    line([(cx-r*0.85, cy+r*0.45), (cx+r*0.85, cy+r*0.45)], color, stroke)


def bridge_art(x, y, w, h):
    rect((x, y, x+w, y+h), PALE)
    ellipse((x+235, y+19, x+265, y+49), PAPER)
    # A flat sea band keeps the broken structure visually legible.
    poly([(x,y+99),(x+35,y+83),(x+72,y+92),(x+113,y+88),
          (x+159,y+99),(x+w,y+90),(x+w,y+h),(x,y+h)], "#c9d4cf")
    rect((x, y+115, x+w, y+h), BLUE)
    # Surviving road sections and piers.
    for xx in [27, 75, 236, 280]:
        poly([(x+xx,y+98),(x+xx+12,y+98),(x+xx+9,y+138),
              (x+xx+3,y+138)], NAVY)
    poly([(x,y+91),(x+112,y+91),(x+121,y+99),(x+112,y+106),(x,y+106)], NAVY)
    poly([(x+218,y+91),(x+w,y+91),(x+w,y+106),(x+207,y+106)], NAVY)
    line([(x,y+88),(x+109,y+88)], PAPER, 2)
    line([(x+220,y+88),(x+w,y+88)], PAPER, 2)
    # Jagged ends make the open span read as a fresh structural break.
    poly([(x+80,y+91),(x+103,y+65),(x+132,y+48),(x+150,y+44),
          (x+151,y+52),(x+137,y+56),(x+130,y+61),(x+121,y+65),
          (x+114,y+75),(x+106,y+71),(x+101,y+91)], NAVY)
    poly([(x+186,y+49),(x+201,y+60),(x+207,y+65),(x+214,y+77),
          (x+222,y+83),(x+232,y+91),(x+218,y+91),(x+211,y+82),
          (x+204,y+78),(x+199,y+68),(x+190,y+62)], NAVY)
    for xx, yy, end in [(105,67,91),(126,54,91),(210,70,91)]:
        line([(x+xx,y+yy),(x+xx,y+end)], NAVY, 2)
    # A detached fractured section tumbles toward the water, trailing a crack.
    poly([(x+128,y+105),(x+190,y+132),(x+183,y+145),(x+121,y+117)], NAVY)
    line([(x+128,y+105),(x+140,y+111),(x+145,y+108),(x+157,y+119),
          (x+164,y+117),(x+177,y+128),(x+190,y+132)], PAPER, 2)
    poly([(x+158,y+68),(x+166,y+82),(x+151,y+77)], RED)
    poly([(x+193,y+106),(x+202,y+116),(x+188,y+120)], RED)
    # Splash arcs and impact rays sit on the surface of the flat sea band.
    line([(x+165,y+153),(x+177,y+147),(x+190,y+153)], PAPER, 2)
    line([(x+156,y+159),(x+172,y+156)], PAPER, 1.5)
    line([(x+184,y+158),(x+203,y+155)], PAPER, 1.5)
    line([(x+170,y+143),(x+166,y+136)], PAPER, 1)
    line([(x+185,y+143),(x+190,y+135)], PAPER, 1)
    line([(x+205,y+151),(x+212,y+146)], PAPER, 1)


def flame(x, y, s):
    # Overlapping triangular tongues and a darker triangular inner core.
    for points in [
        [(-19,2),(-12,-35),(0,2)],
        [(-12,3),(1,-49),(15,3)],
        [(2,3),(18,-29),(21,3)],
    ]:
        poly([(x+xx*s,y+yy*s) for xx,yy in points], RED)
    poly([(x-8*s,y+3*s),(x+2*s,y-26*s),(x+11*s,y+3*s)], "#762b28")


def ship(x, y, length, scale=1):
    # Clean, uninterrupted ship silhouettes: tapered hulls and simple bridges.
    poly([(x,y),(x+length,y),(x+length-14*scale,y+20*scale),
          (x+18*scale,y+20*scale)], PAPER)
    rect((x+12*scale,y-25*scale,x+37*scale,y), PAPER)
    line([(x+24*scale,y-25*scale),(x+24*scale,y-39*scale)], PAPER, 2)


def hormuz_art(x, y, w, h):
    rect((x,y,x+w,y+h), "#d9ded7")
    # Two opposed coastlines establish the narrow shipping channel.
    poly([(x,y),(x+116,y),(x+90,y+24),(x+103,y+43),(x+51,y+57),
          (x+37,y+86),(x,y+98)], STONE)
    poly([(x+w,y+29),(x+268,y+41),(x+252,y+66),(x+271,y+87),
          (x+w,y+98)], STONE)
    waterline = y+103
    poly([(x,waterline),(x+74,waterline),(x+144,waterline),
          (x+225,waterline),(x+w,waterline),(x+w,y+h),(x,y+h)], NAVY)
    ship(x+25,y+124,137,1)
    ship(x+167,y+124,112,0.78)
    flame(x+100,y+119,1)
    flame(x+227,y+119,0.84)
    for xx, yy, ll in [(13,154,67),(179,154,69),(68,168,74),(245,168,40)]:
        line([(x+xx,y+yy),(x+xx+ll,y+yy)], BLUE, 1.5)
    line([(x+88,y+153),(x+118,y+153)], RED, 3)
    line([(x+211,y+153),(x+240,y+153)], RED, 2)


def flag(x, y, country):
    w, h = 54, 34
    line([(x,y-4),(x,y+81)], INK, 1.6)
    ellipse((x-2.5,y-7,x+2.5,y-2), RED)
    rect((x+1,y,x+w,y+h), PAPER)
    if country == "US":
        for i in range(7):
            rect((x+1,y+i*h/7,x+w,y+i*h/7+h/14), RED)
        rect((x+1,y,x+24,y+19), NAVY)
        for row in range(3):
            for col in range(4):
                star(x+5+col*5,y+4+row*5,1.4,PAPER,points=5)
    elif country == "INDIA":
        rect((x+1,y,x+w,y+h/3), "#bf8854")
        rect((x+1,y+h*2/3,x+w,y+h), "#63735c")
        ellipse((x+23,y+12,x+33,y+22), outline=NAVY, width=1)
        for i in range(12):
            a = i*pi/6
            line([(x+28,y+17),(x+28+4*cos(a),y+17+4*sin(a))], NAVY, 0.45)
    elif country == "JAPAN":
        ellipse((x+19,y+9,x+36,y+26), RED)
    else:
        rect((x+1,y,x+w,y+h), NAVY)
        line([(x+2,y+1),(x+25,y+15)], PAPER, 3)
        line([(x+2,y+15),(x+25,y+1)], PAPER, 3)
        rect((x+1,y+5,x+26,y+10), PAPER)
        rect((x+11,y,x+16,y+17), PAPER)
        rect((x+1,y+6.5,x+26,y+8.5), RED)
        rect((x+12.5,y,x+14.5,y+17), RED)
        star(x+15,y+25,4,points=7)
        for xx, yy in [(39,9),(33,19),(46,18),(40,27)]:
            star(x+xx,y+yy,2.4,points=7)
    rect((x+1,y,x+w,y+h), outline=INK, width=0.6)


def manila_art(x, y, w, h):
    rect((x,y,x+w,y+h), STONE)
    # A concentric seal and four national flags on a shared stage.
    globe(x+w/2,y+51,32,"#c4bba8")
    for xx, name in zip([22,93,164,235],["US","INDIA","JAPAN","AUSTRALIA"]):
        flag(x+xx,y+42,name)
    rect((x+13,y+127,x+w-13,y+141), NAVY)
    rect((x+25,y+141,x+w-25,y+151), NAVY)
    line([(x+25,y+141),(x+w-25,y+141)], PAPER, 1)
    # A small mineral-crystal emblem under the negotiating stage.
    for xx, yy, ss in [(133,159,0.7),(153,154,1),(175,160,0.6)]:
        poly([(x+xx,y+yy+14*ss),(x+xx+6*ss,y+yy),
              (x+xx+16*ss,y+yy-4*ss),(x+xx+22*ss,y+yy+14*ss)], BLUE)
        line([(x+xx+6*ss,y+yy),(x+xx+11*ss,y+yy+14*ss)], PAPER, 0.8)


def icon(kind, x, y):
    """Consistent 34px editorial symbols on a shared baseline grid."""
    stroke = 1.7
    if kind == "outage":
        rect((x+3,y+4,x+31,y+24), outline=NAVY, width=stroke)
        line([(x+10,y+31),(x+24,y+31)], NAVY, stroke)
        line([(x+17,y+24),(x+17,y+31)], NAVY, stroke)
        poly([(x+19,y+7),(x+12,y+15),(x+17,y+15),(x+14,y+22),
              (x+23,y+13),(x+18,y+13)], RED)
    elif kind == "health":
        poly([(x+17,y+3),(x+29,y+8),(x+28,y+21),(x+17,y+31),
              (x+6,y+21),(x+5,y+8)], STONE, NAVY, stroke)
        rect((x+14.5,y+10,x+19.5,y+25), RED)
        rect((x+9.5,y+15,x+24.5,y+20), RED)
    elif kind == "climate":
        globe(x+17,y+17,13,NAVY,stroke)
        line([(x+7,y+27),(x+27,y+7)], RED, stroke)
    elif kind == "data":
        for yy in [4,14,24]:
            rect((x+4,y+yy,x+30,y+yy+7), outline=NAVY, width=stroke)
            ellipse((x+7,y+yy+2,x+10,y+yy+5), RED)
            line([(x+14,y+yy+3.5),(x+26,y+yy+3.5)], NAVY, stroke)
    elif kind == "hospital":
        rect((x+5,y+10,x+29,y+31), outline=NAVY, width=stroke)
        rect((x+13,y+4,x+21,y+17), RED)
        rect((x+10,y+7,x+24,y+14), RED)
        for xx in [9,21]:
            rect((x+xx,y+21,x+xx+4,y+26), NAVY)
        rect((x+15,y+26,x+19,y+31), NAVY)
    elif kind == "chip":
        rect((x+8,y+8,x+26,y+26), outline=NAVY, width=stroke)
        for pos in [11,17,23]:
            for ends in [[(pos,3),(pos,8)],[(pos,26),(pos,31)],
                         [(3,pos),(8,pos)],[(26,pos),(31,pos)]]:
                line([(x+a,y+b) for a,b in ends],NAVY,stroke)
        line([(x+12,y+22),(x+22,y+12)],RED,stroke)
    elif kind == "strike":
        line([(x+17,y+22),(x+17,y+31)],NAVY,stroke)
        poly([(x+4,y+7),(x+29,y+4),(x+31,y+21),(x+6,y+24)],RED)
        line([(x+9,y+12),(x+25,y+10)],PAPER,stroke)
        line([(x+10,y+18),(x+24,y+16)],PAPER,stroke)
    elif kind == "mongolia":
        line([(x+4,y+3),(x+4,y+31)],NAVY,stroke)
        rect((x+6,y+5,x+30,y+27),RED)
        rect((x+14,y+5,x+22,y+27),BLUE)
        ellipse((x+8,y+9,x+12,y+13),PAPER)
        rect((x+9,y+16,x+11,y+23),PAPER)


def italic(value, x, y, size, max_width):
    """Slant the installed DejaVu Serif regular; no extra font dependency."""
    face = font(size,"book")
    b = draw.textbbox((0,0),value,font=face)
    w,h = b[2]-b[0],b[3]-b[1]
    pad = round(5*SCALE)
    tile = Image.new("RGBA",(w+2*pad,h+2*pad),(0,0,0,0))
    ImageDraw.Draw(tile).text((pad-b[0],pad-b[1]),value,font=face,fill=INK)
    skew = 0.18
    extra = round(skew*tile.height)
    tile = tile.transform((tile.width+extra,tile.height),Image.Transform.AFFINE,
                          (1,skew,-extra,0,1,0),Image.Resampling.BICUBIC)
    assert (tile.width-2*pad)/SCALE <= max_width,(value,tile.width/SCALE,max_width)
    image.paste(tile,(round(x*SCALE)-pad,round(y*SCALE)-pad),tile)


def build():
    # Masthead: an oversized date, airy small caps, and traditional double rules.
    text("THE DAILY WORLD BRIEF",28,29,10,"bold",RED)
    globe(512,34,9,RED)
    text("INDEPENDENT WORLD EDITION",996,29,10,"bold",RED,"right")
    fitted("THE WORLD IN A DAY",512,52,49,"serif",968,align="center")
    line([(28,114),(419,114)],INK,1)
    tracked("TUESDAY",512,108,14,3.5,RED)
    line([(605,114),(996,114)],INK,1)
    fitted("17 NOVEMBER 2026",512,130,73,"serif",968,align="center",minimum=65)
    text("THE WORLD’S NEWS IN ONE PAGE · 17 STORIES · ONE DAY",512,204,
         11.5,"bold",align="center",max_width=968)
    line([(28,225),(996,225)],INK,2)
    line([(28,231),(996,231)],INK,0.8)

    panels = [
        (28,"01 / EUROPE", "UKRAINE · RUSSIA", bridge_art,
         ["Kerch Bridge", "road span falls"],
         "UKRAINE STRIKES THE CRIMEA LINK"),
        (356,"02 / MIDDLE EAST", "STRAIT OF HORMUZ", hormuz_art,
         ["US strikes Iran;", "ships burn"],
         "TWO TANKERS HIT IN THE STRAIT"),
        (684,"03 / ASIA–PACIFIC", "MANILA", manila_art,
         ["Trump in Manila:", "Quad reconvenes"],
         "LEADERS’ FIRST MEETING IN 2 YEARS"),
    ]
    for x,tag,place,art,headline,deck in panels:
        text(tag,x,247,10,"bold",RED)
        text(place,x+312,247,9,"bold",INK,"right")
        art(x+1,270,310,180)
        rect((x,269,x+312,451),outline=INK,width=2)
        for i, value in enumerate(headline):
            fitted(value,x,465+i*34,29,"serif",312,minimum=24)
        fitted(deck,x,539,10.3,"bold",312,color=MUTED)
    line([(28,568),(996,568)],INK,2)
    text("THE DAY IN EIGHT DISPATCHES",28,583,10.5,"bold",RED)
    text("POLITICS / HEALTH / CLIMATE / TECHNOLOGY",996,583,9,"bold",MUTED,"right")

    cards = [
        ("GLOBAL · TECHNOLOGY","outage",["Global tech", "outages"],"NSA, APPLE & BANKS HIT"),
        ("US · PUBLIC HEALTH","health",["US loses measles-", "free status"],"ELIMINATION STATUS REVOKED"),
        ("TÜRKIYE · CLIMATE","climate",["COP31: fossil", "fuel deadlock"],"ANTALYA NEGOTIATIONS"),
        ("US · ENVIRONMENT","data",["Data centers’", "carbon footprint"],"EMISSIONS ≈ DENMARK · STUDY"),
        ("GAZA · 12 NOV CONTEXT","hospital",["Hospital strike", "kills six"],"NASSER HOSPITAL · OFFICIALS"),
        ("RUSSIA · BASHKORTOSTAN","strike",["Refinery fire", "after drone night"],"1,441 DRONES · 17 NOVEMBER"),
        ("FRANCE · EUROPE","strike",["Public sector", "on strike"],"GRÈVE (FRANCE) · PAY DEMANDS"),
        ("NVIDIA · 17 NOVEMBER","chip",["Huang resigns", "amid China row"],"CHINA-CHIP SCANDAL"),
    ]
    for n,(region,kind,title,deck) in enumerate(cards):
        x = 28+(n%4)*(248)
        y = 610+(n//4)*134
        rect((x,y,x+224,y+118),outline=INK,width=1.5)
        text(region,x+16,y+16,8.2,"bold",RED,max_width=192)
        icon(kind,x+180,y+40)
        for i,value in enumerate(title):
            fitted(value,x+16,y+40+i*25,19,"serif",164,minimum=16)
        fitted(deck,x+16,y+96,8.2,"bold",192,color=MUTED,minimum=7.5)

    line([(28,886),(996,886)],INK,2)
    text("WORLD BRIEFS",40,902,11,"bold",RED)
    text("LATEST & CONTEXT · EARLIER EVENT DATES MARKED",984,903,8.5,"bold",MUTED,"right")
    briefs = [
        ("Kyiv: 2 Dnipro bridges hit · 50,000 without power", "Patterson named seventh 007"),
        ("Voyager 1 · CROSSES ONE LIGHT-DAY TOMORROW", "Jordan + Iraq block Telegram · MON 16 NOV"),
        ("US women win ice hockey worlds · MON 16 NOV", "Russia car bomb injures ex-PM aide · FRI 13 NOV"),
    ]
    for i,(left,right) in enumerate(briefs):
        yy = 927+i*21
        italic(left,40,yy,10.6,444)
        ellipse((505,yy+4,509,yy+8),RED)
        italic(right,533,yy,10.6,451)
    line([(28,992),(996,992)],INK,0.8)
    # Check all normal text boxes for unintended overlap, including small caps.
    for n,(a,ba) in enumerate(TEXT_BOXES):
        for b,bb in TEXT_BOXES[n+1:]:
            overlap_x = min(ba[2],bb[2])-max(ba[0],bb[0])
            overlap_y = min(ba[3],bb[3])-max(ba[1],bb[1])
            assert overlap_x <= 0.5 or overlap_y <= 0.5,("Text overlap",a,b)
    result = image.resize((SIZE,SIZE),Image.Resampling.LANCZOS)
    result.save(ROOT/"entry.png",format="PNG",optimize=True,compress_level=9)
    print("Rendered entry.png: 1024 × 1024 RGB; text bounds checked.")


if __name__ == "__main__":
    build()
