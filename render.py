"""Render a deterministic, typeset 1024px world-news front page.

Requires Python 3, Pillow, and the system DejaVu fonts. No external assets,
network access, randomness, clock reads, or generated image metadata.
"""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from artwork import bridge, coordinate_hash, hormuz, manila

SIZE = 1024
SCALE = 3
PAPER = "#f5eedf"
INK = "#1b1b1f"
RED = "#b3382c"
NAVY = "#14213d"
BLUE = "#547a89"
STONE = "#e5ddcc"
MUTED = "#646158"
HAIRLINE = "#74695b"
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


def globe(cx, cy, r, color=INK, stroke=1):
    ellipse((cx-r, cy-r, cx+r, cy+r), outline=color, width=stroke)
    ellipse((cx-r*0.48, cy-r, cx+r*0.48, cy+r), outline=color, width=stroke)
    line([(cx-r, cy), (cx+r, cy)], color, stroke)
    line([(cx-r*0.85, cy-r*0.45), (cx+r*0.85, cy-r*0.45)], color, stroke)
    line([(cx-r*0.85, cy+r*0.45), (cx+r*0.85, cy+r*0.45)], color, stroke)


def paper_grain():
    """Fixed-coordinate hash fibers, with no mutable RNG or clock dependency."""
    for row in range(0, SIZE, 4):
        for col in range(0, SIZE, 4):
            code = coordinate_hash(col, row)
            if code & 3 == 0:
                continue
            x = col + ((code >> 2) & 7) / 3
            y = row + ((code >> 5) & 7) / 3
            color = ("#e9ddc8", "#eee2ce", "#fcf5e8", "#f9f3e6")[(code >> 8) & 3]
            line([(x, y), (x + .65, y + .33)], color, .45)


def double_rule(x1, x2, y, color=INK):
    line([(x1, y), (x2, y)], color, .65)
    line([(x1, y + 3), (x2, y + 3)], color, .65)


def display(value, y, width, height, tracking=0, color=INK, family="serif"):
    """Shape all-cap masthead type to a precise width using the installed serif."""
    face = font(100, family)
    kern = round(tracking * SCALE)
    advance = sum(face.getlength(ch) for ch in value) + kern * (len(value) - 1)
    mask = Image.new("L", (round(advance) + 12, 115 * SCALE))
    pen = ImageDraw.Draw(mask)
    cursor = 6
    for ch in value:
        pen.text((round(cursor), 0), ch, font=face, fill=255)
        cursor += face.getlength(ch) + kern
    mask = mask.crop(mask.getbbox()).resize((width * SCALE, height * SCALE), Image.Resampling.LANCZOS)
    x = (SIZE - width) / 2
    image.paste(color, (round(x * SCALE), round(y * SCALE)), mask)
    TEXT_BOXES.append((value, (x, y, x + width, y + height)))


def masthead(story_count):
    line([(28, 28), (996, 28)], INK, 2)
    line([(28, 33), (996, 33)], INK, .65)
    display("THE DAILY WORLD BRIEF", 44, 710, 63, tracking=-1.7)
    for left, right in [(28, 130), (894, 996)]:
        cx = (left + right) / 2
        double_rule(left, right, 72)
        ellipse((cx - 12, 62, cx + 12, 86), PAPER)
        globe(cx, 74, 8.4, RED, .7)
    text("EST. 2026", 79, 91, 9, "bold", RED, "center")
    text("INDEPENDENT WORLD EDITION", 930, 91, 7.1, "bold", RED, "center")
    double_rule(28, 996, 116)
    for x in (257, 767):
        line([(x, 124), (x, 137)], INK, .7)
    for x, value in [(142, "VOL. I · No. 347"), (512, "TUESDAY, 17 NOVEMBER 2026"),
                     (882, "WORLD EDITION · ONE PAGE")]:
        text(value, x, 126, 10, "book", align="center")
    line([(28, 142), (996, 142)], INK, .65)
    display("TUESDAY 17 NOVEMBER 2026", 155, 941, 56, tracking=-1.3, family="book")
    text("THE WORLD IN A DAY", 28, 225, 10.5, "serif", RED)
    text(f"THE WORLD’S NEWS IN ONE PAGE · {story_count} STORIES · 6 CONTINENTS · ONE DAY",
         996, 225, 10, "bold", align="right")
    line([(28, 246), (996, 246)], INK, 2)
    line([(28, 250), (996, 250)], INK, .65)


def chip(label, x, y, color):
    w = text_width(label, 8.4, "bold") + 15
    draw.rounded_rectangle(tuple(round(v * SCALE) for v in (x, y, x+w, y+14)),
                           radius=7*SCALE, fill=color)
    text(label, x + 7.5, y + 3.5, 8.4, "bold", PAPER)


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


def small_icon(kind, x, y, size=20):
    """Scale ink-only icon tiles and place a one-pixel, dark warm shadow."""
    global image, draw
    page, page_draw = image, draw
    tile = Image.new("RGBA", (36*SCALE, 36*SCALE))
    try:
        image, draw = tile, ImageDraw.Draw(tile)
        icon(kind, 1, 1)
        # Fine structural details share the symbols' 1.7-unit stroke grid.
        if kind == "outage":
            for xx in (8, 13, 18):
                line([(xx, 8), (xx+2, 8)], BLUE, 1.7)
            line([(7, 27), (12, 27)], BLUE, 1.7)
        elif kind == "health":
            line([(8, 9), (8, 18), (12, 24)], BLUE, 1.7)
        elif kind == "climate":
            line([(30, 26), (30, 33)], RED, 1.7)
            ellipse((28, 30, 32, 34), RED)
        elif kind == "hospital":
            line([(3, 33), (32, 33)], NAVY, 1.7)
            rect((8, 15, 11, 18), BLUE)
            rect((24, 15, 27, 18), BLUE)
        elif kind == "chip":
            rect((12, 12, 22, 22), outline=BLUE, width=1.7)
        elif kind == "strike":
            line([(12, 32), (24, 32)], NAVY, 1.7)
            ellipse((25, 26, 28, 29), NAVY)
    finally:
        image, draw = page, page_draw
    tile = tile.resize((round(size*SCALE), round(size*SCALE)), Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", tile.size, "#c4b79f")
    image.paste(shadow, (round((x+1)*SCALE), round((y+1)*SCALE)), tile.getchannel("A"))
    image.paste(tile, (round(x*SCALE), round(y*SCALE)), tile)


def artwork(plate, x, y, w, h):
    tile = plate(SCALE)
    if tile.size != (round(w*SCALE), round(h*SCALE)):
        tile = tile.resize((round(w*SCALE), round(h*SCALE)), Image.Resampling.LANCZOS)
    image.paste(tile, (round(x*SCALE), round(y*SCALE)))


def bridge_art(x, y, w, h):
    artwork(bridge, x, y, w, h)


def hormuz_art(x, y, w, h):
    artwork(hormuz, x, y, w, h)


def manila_art(x, y, w, h):
    artwork(manila, x, y, w, h)


def build():
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
    cards = [
        ("GLOBAL · TECHNOLOGY","outage",["Global tech", "outages"],"NSA, APPLE & BANKS HIT"),
        ("US · PUBLIC HEALTH","health",["US loses measles-", "free status"],"ELIMINATION STATUS REVOKED"),
        ("TÜRKIYE · CLIMATE","climate",["COP31: fossil", "fuel deadlock"],"ANTALYA NEGOTIATIONS"),
        ("US · ENVIRONMENT","data",["Data centers’", "carbon footprint"],"EMISSIONS ≈ DENMARK · STUDY"),
        ("GAZA · 12 NOV CONTEXT","hospital",["Hospital strike", "kills six"],"NASSER HOSPITAL · OFFICIALS"),
        ("WORLD · 17 NOVEMBER","health",["Cervical cancer", "elimination day"],"GLOBAL HEALTH OBSERVANCE"),
        ("FRANCE · EUROPE","strike",["Public sector", "on strike"],"GRÈVE (FRANCE) · PAY DEMANDS"),
        ("NVIDIA · 17 NOVEMBER","chip",["Huang resigns", "amid China row"],"CHINA-CHIP SCANDAL"),
    ]
    more = [
        ("KYIV · EUROPE", "strike", "Dnipro bridges hit", "50,000 without power"),
        ("SHENZHEN · ASIA", "climate", "Trump–Xi–Putin", "Trilateral planned Thu 19 Nov"),
        ("MANILA · ASIA", "strike", "Trump visit arrests", "Protests in the Philippines"),
        ("ISRAEL · MIDDLE EAST", "strike", "Kahana wins vote", "Coalition backs 66–52"),
        ("GAZA · MIDDLE EAST", "hospital", "WHO: unblock aid", "Fourth winter in Gaza"),
        ("GERMANY · EUROPE", "health", "More aid for Gaza", "Germany calls for access"),
        ("RUSSIA · EUROPE", "strike", "Refinery fire", "Bashkortostan · drone night"),
        ("CO₂ · WORLD", "data", "Data-center exports", "Russia, Saudi Arabia, Australia"),
        ("MARKETS · AMERICAS", "chip", "US stocks slide", "Tech outages extend decline"),
        ("AIR TRAVEL · US", "outage", "United cancels", "Flights disrupted by outage"),
        ("MONGOLIA · ASIA", "mongolia", "President resigns", "Political upheaval"),
        ("CHOLERA · AFRICA", "health", "WHO races outbreaks", "Cholera response in Africa"),
    ]
    briefs = [
        "Voyager 1: one light-day · WED 18 NOV",
        "Jordan + Iraq block Telegram · MON 16 NOV",
        "Russia car bomb injures ex-PM aide · FRI 13 NOV",
        "US women win ice hockey worlds · MON 16 NOV",
        "Robert Pattinson named seventh 007",
        "Brooklyn building collapse: death toll reaches 8",
        "DC gym shooting: suspect charged",
        "Tiger Woods returning after suspension",
        "Waymo pulls cars after California ban",
        "Iran claims hack of US MQ-170 drone",
        "Trump warns Iran over dirty bomb in DC",
        "ASEAN / APEC closes in Shenzhen",
        "Bangladesh: tear gas at wage protest · 500 factories shut",
        "Bahrain: Iran's third strike wave on US 5th Fleet host",
        "DRC: WHO panel on Bundibugyo outbreak · 11,000 cases",
        "Germany urges unblocked Gaza aid",
        "Kerch district: 2 killed in overnight drone attack",
        "3rd US carrier joins Gulf blockade · MON 16 NOV",
    ]
    story_count = len(panels) + len(cards) + len(more) + len(briefs)
    assert story_count == 41

    paper_grain()
    masthead(story_count)

    for x in (348, 676):
        line([(x, 261), (x, 531)], HAIRLINE, .5)
    for x,tag,place,art,headline,deck in panels:
        text(tag,x,262,10,"bold",RED)
        text(place,x+312,262,9,"bold",INK,"right")
        art(x+1,281,310,166)
        rect((x,280,x+312,448),outline=INK,width=.8)
        for i, value in enumerate(headline):
            fitted(value,x,458+i*29,27,"serif",312,minimum=24)
        fitted(deck,x,520,10.3,"bold",312,color=MUTED)

    line([(28,542),(996,542)],INK,2)
    text("THE DAY IN EIGHT DISPATCHES",28,553,10.5,"bold",RED)
    text("POLITICS / HEALTH / CLIMATE / TECHNOLOGY",996,554,9,"bold",MUTED,"right")
    for x in (270, 512, 754):
        line([(x,578),(x,754)],HAIRLINE,.5)
    for n,(region,kind,title,deck) in enumerate(cards):
        x = 28+(n%4)*242
        y = 579+(n//4)*91
        xx = x + (0 if n%4 == 0 else 10)
        line([(xx,y+82),(x+232,y+82)],HAIRLINE,.5)
        chip(region,xx,y,NAVY if n%4 != 0 else RED)
        small_icon(kind,xx+190,y+25,30)
        for i,value in enumerate(title):
            fitted(value,xx,y+24+i*21,18,"serif",180,minimum=16)
        fitted(deck,xx,y+68,8.2,"bold",222,color=MUTED,minimum=8)

    line([(28,765),(996,765)],INK,1.5)
    text("THE WORLD IN TWELVE MORE",28,777,10.5,"bold",RED)
    text("A WIDER LENS / SIX CONTINENTS",996,778,9,"bold",MUTED,"right")
    gap = 12
    card_width = (968-5*gap)/6
    for col in range(1,6):
        x = 28+col*(card_width+gap)-gap/2
        line([(x,797),(x,890)],HAIRLINE,.5)
    for n,(region,kind,headline,detail) in enumerate(more):
        x = 28+(n%6)*(card_width+gap)
        y = 798+(n//6)*49
        small_icon(kind,x,y,17)
        text(region,x+22,y+3,7.5,"bold",RED,max_width=card_width-22)
        fitted(headline,x,y+21,10.5,"serif",card_width,minimum=10)
        fitted(detail,x,y+34,8,"sans",card_width,minimum=8)
        if n<6:
            line([(x,y+45),(x+card_width,y+45)],HAIRLINE,.5)

    line([(28,900),(996,900)],INK,1.5)
    text("WORLD BRIEFS · EIGHTEEN IN FOCUS",28,911,10.5,"bold",RED)
    text("EARLIER & UPCOMING EVENT DATES MARKED",996,912,8.5,"bold",MUTED,"right")
    for x in (348.5, 674.5):
        line([(x,931),(x,996)],HAIRLINE,.5)
    for n,value in enumerate(briefs):
        x = 28+(n%3)*326
        y = 932+(n//3)*11.2
        poly([(x,y+3.3),(x+1.8,y+1.5),(x+3.6,y+3.3),(x+1.8,y+5.1)],RED)
        text(value,x+9,y,9.2,"book",max_width=307)
    line([(28,1000),(996,1000)],INK,.8)
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
