"""Layered, deterministic Pillow artwork; coordinates use a 310 × 180 grid."""
from math import cos, sin, pi
from PIL import Image, ImageDraw

NAVY = "#14213d"
RED = "#b3382c"
CREAM = "#f5eedf"


class Plate:
    def __init__(self, scale):
        self.scale = scale
        self.image = Image.new("RGB", (310 * scale, 180 * scale), NAVY)
        self.draw = ImageDraw.Draw(self.image)

    def box(self, coords, fill, outline=None, width=1):
        self.draw.rectangle(tuple(round(v * self.scale) for v in coords),
                            fill, outline, max(1, round(width * self.scale)))

    def ellipse(self, coords, fill=None, outline=None, width=1):
        self.draw.ellipse(tuple(round(v * self.scale) for v in coords),
                          fill, outline, max(1, round(width * self.scale)))

    def line(self, coords, fill, width=1):
        self.draw.line([(round(x * self.scale), round(y * self.scale)) for x, y in coords],
                       fill, max(1, round(width * self.scale)), joint="curve")

    def poly(self, coords, fill):
        self.draw.polygon([(round(x * self.scale), round(y * self.scale)) for x, y in coords], fill)

    def arc(self, coords, start, end, fill, width=1):
        self.draw.arc(tuple(round(v * self.scale) for v in coords), start, end,
                      fill, max(1, round(width * self.scale)))

    def star(self, x, y, radius, color=CREAM, points=5):
        self.poly([(x + cos(-pi / 2 + i * pi / points) * radius * (1 if i % 2 == 0 else .43),
                    y + sin(-pi / 2 + i * pi / points) * radius * (1 if i % 2 == 0 else .43))
                   for i in range(points * 2)], color)


def coordinate_hash(x, y):
    """Integer coordinate mixing; independent of process hash seeds and clocks."""
    value = ((x * 374761393) ^ (y * 668265263) ^ 20261117) & 0xffffffff
    value = ((value ^ (value >> 13)) * 1274126177) & 0xffffffff
    return value ^ (value >> 16)


def sea(p, top, palette):
    for row, color in enumerate(palette):
        y = top + row * (180 - top) / len(palette)
        p.box((0, y, 310, top + (row + 1) * (180 - top) / len(palette)), color)
    for row in range(7):
        yy = top + 8 + row * 9
        for col in range(5):
            xx = (col * 73 + row * 23) % 306
            length = 9 + coordinate_hash(col, row) % 24
            p.line([(xx, yy), (min(xx + length, 308), yy)], "#779497", .55)


def bridge(scale):
    p = Plate(scale)
    p.box((0, 0, 310, 53), "#17263c")
    p.box((0, 53, 310, 87), "#233a4e")
    p.box((0, 87, 310, 115), "#385263")
    for i in range(42):
        xx = 8 + coordinate_hash(i, 11) % 294
        yy = 7 + coordinate_hash(i, 17) % 60
        p.ellipse((xx, yy, xx + .8, yy + .8), "#c9c4ac")
    p.ellipse((260, 16, 278, 34), "#ece4c6")
    p.ellipse((256, 13, 272, 30), "#17263c")
    # Distant Crimean coast and a tiny lit shoreline, behind the bridge.
    p.poly([(0, 105), (29, 92), (52, 99), (85, 93), (105, 103),
            (222, 106), (253, 94), (276, 97), (310, 88), (310, 125), (0, 125)], "#243a47")
    for i in range(22):
        xx = 4 + i * 14
        p.box((xx, 107, xx + 1, 108), "#b8996d")
    sea(p, 119, ["#547884", "#426774", "#355863", "#294a58"])
    # Six complete arch bays. The fourth alone has an open, fractured arch.
    for bay in range(6):
        left = -8 + bay * 54
        right = left + 54
        p.poly([(left, 111), (left + 7, 111), (left + 6, 143),
                (left + 2, 147), (left - 1, 145)], "#111e2b")
        if bay == 3:
            p.line([(left, 107), (left + 7, 91), (left + 15, 83),
                    (left + 20, 80)], "#101d2b", 4.5)
            p.line([(right - 14, 83), (right - 7, 92), (right, 107)], "#101d2b", 4.5)
            p.line([(left + 18, 82), (left + 22, 79), (left + 23, 83)], CREAM, .7)
            continue
        arch = [(left + i * 54 / 32, 109 - 32 * sin(i * pi / 32)) for i in range(33)]
        p.line(arch, "#111e2b", 4)
        p.line([(a, b - 1.8) for a, b in arch], "#769092", .6)
        for i in range(1, 7):
            xx = left + i * 54 / 7
            yy = 109 - 32 * sin(i * pi / 7)
            p.line([(xx, yy + 2), (xx, 109)], "#111e2b", .9)
    for left, right in [(0, 166), (208, 310)]:
        p.box((left, 108, right, 115), "#101d2b")
        p.line([(left, 107), (right, 107)], "#d8c9a3", 1.2)
        for xx in range(left + 4, right, 8):
            p.line([(xx, 104), (xx, 108)], "#b5b39d", .6)
    # A fallen road section leans into the sea below the only broken bay.
    p.poly([(169, 112), (202, 145), (198, 152), (164, 119)], "#101d2b")
    p.line([(168, 112), (201, 145)], "#c4c2a7", 1.2)
    for i in range(5):
        xx, yy = 174 + i * 5, 120 + i * 5
        p.line([(xx, yy), (xx + 3, yy - 3)], "#9ca69e", .6)
    for xx, yy in [(174, 99), (180, 88), (186, 75), (190, 63)]:
        p.ellipse((xx - 5, yy - 6, xx + 5, yy + 6), "#5c6666")
    for xx, yy, r in [(197, 153, 10), (200, 155, 18), (202, 158, 28)]:
        p.arc((xx - r, yy - 4, xx + r, yy + 5), 185, 350, "#c4d3c7", 1)
    for xx, yy in [(186, 147), (200, 144), (211, 150)]:
        p.line([(xx, yy), (xx + 2, yy - 5)], "#dce0cf", .8)
    # Patrol vessel and its wake occupy a separate foreground layer.
    p.line([(35, 165), (74, 165)], "#91aaa5", 1)
    p.poly([(55, 156), (91, 156), (84, 163), (61, 163)], "#14212d")
    p.box((65, 149, 79, 156), "#172b3b")
    p.box((67, 150, 76, 152), "#b5c6bc")
    p.line([(72, 149), (72, 141), (80, 147)], "#162a39", .8)
    p.box((72, 141, 77, 144), RED)
    return p.image


def fire(p, x, y, scale=1):
    for dx, height, width in [(-14, 32, 15), (-3, 45, 18), (10, 30, 14), (20, 20, 10)]:
        p.poly([(x + (dx - width / 2) * scale, y),
                (x + (dx + 1) * scale, y - height * scale),
                (x + (dx + width / 2) * scale, y)], "#b3382c")
    for dx, height in [(-10, 23), (2, 35), (14, 23)]:
        p.poly([(x + (dx - 5) * scale, y), (x + (dx + 2) * scale, y - height * scale),
                (x + (dx + 7) * scale, y)], "#e48242")
    p.poly([(x - 4 * scale, y), (x + 4 * scale, y - 24 * scale),
            (x + 11 * scale, y)], "#f7cf75")


def tanker(p, x, y, length, scale):
    p.poly([(x, y), (x + length, y), (x + length - 10 * scale, y + 13 * scale),
            (x + 12 * scale, y + 13 * scale)], "#d2c4a7")
    p.line([(x + 11 * scale, y + 10 * scale), (x + length - 9 * scale, y + 10 * scale)], RED, 2)
    p.box((x + 10 * scale, y - 18 * scale, x + 27 * scale, y), "#ddcfb3")
    p.box((x + 11 * scale, y - 15 * scale, x + 24 * scale, y - 12 * scale), "#263e51")
    p.box((x + 17 * scale, y - 25 * scale, x + 23 * scale, y - 18 * scale), "#1a293c")
    p.line([(x + 19 * scale, y - 25 * scale), (x + 19 * scale, y - 32 * scale)], CREAM, .7)
    for i in range(5):
        xx = x + (38 + i * 12) * scale
        p.box((xx, y - 5 * scale, xx + 8 * scale, y - 1 * scale), "#8d9a91")
    p.line([(x + 29 * scale, y - 7 * scale), (x + length - 6 * scale, y - 7 * scale)], "#c1b89f", .7)


def hormuz(scale):
    p = Plate(scale)
    p.box((0, 0, 310, 43), "#18263a")
    p.box((0, 43, 310, 76), "#24394c")
    p.box((0, 76, 310, 105), "#3d5361")
    p.ellipse((260, 14, 278, 32), "#e3d9b9")
    for i in range(15):
        xx, yy = 8 + coordinate_hash(i, 2) % 240, 7 + coordinate_hash(i, 3) % 42
        p.ellipse((xx, yy, xx + .65, yy + .65), "#9ca9aa")
    p.poly([(0, 89), (16, 78), (36, 81), (53, 75), (74, 87), (94, 92),
            (310, 99), (310, 111), (0, 111)], "#263c4b")
    sea(p, 103, ["#294b5b", "#23424f", "#1b3545", "#142b3d"])
    # A convoy on the horizon establishes distance and scale.
    for xx, yy, ll in [(175, 98, 30), (217, 95, 23), (250, 98, 23)]:
        p.poly([(xx, yy), (xx + ll, yy), (xx + ll - 4, yy + 3), (xx + 3, yy + 3)], "#a3afa6")
        p.box((xx + 5, yy - 4, xx + 10, yy), "#a3afa6")
        p.line([(xx + 8, yy - 6), (xx + 8, yy)], "#a3afa6", .6)
    # Smoke drifts to the right in overlapping, progressively lighter lobes.
    for x, y, s in [(97, 90, 1), (230, 114, .85)]:
        for i in range(7):
            xx, yy, r = x + i * 5, y - 32 - i * 6, 7 + i * 1.1
            p.ellipse((xx - r, yy - r, xx + r, yy + r),
                      ["#242c36", "#303a44", "#3d4750", "#49545a"][min(i // 2, 3)])
    tanker(p, 16, 111, 134, 1)
    tanker(p, 161, 126, 127, .9)
    fire(p, 98, 108, .95)
    fire(p, 230, 123, .93)
    for xx, yy in [(79, 132), (86, 137), (218, 148), (227, 153)]:
        p.line([(xx, yy), (xx + 24, yy)], "#bf633d", 1.2)
    # Quiet radar arcs surround the destroyer in the near sea.
    for r in [19, 29, 39]:
        p.arc((72 - r, 158 - r / 2, 72 + r, 158 + r / 2), 185, 352, "#668b8f", .65)
    p.line([(29, 168), (115, 168)], "#9aaba5", .8)
    p.poly([(37, 155), (108, 155), (99, 163), (49, 163)], "#aeb9ae")
    p.poly([(57, 155), (61, 146), (80, 146), (87, 155)], "#bac2b6")
    p.box((64, 143, 75, 146), "#d7d8be")
    p.line([(70, 144), (70, 131), (77, 139)], "#c7cdbd", .8)
    p.line([(64, 136), (77, 136)], "#c7cdbd", .8)
    p.ellipse((68, 130, 72, 134), outline="#d1cdb4", width=.6)
    p.line([(93, 155), (93, 151), (99, 151)], "#aeb9ae", 1)
    return p.image


def flag(p, x, y, country):
    width, height = 53, 33
    p.line([(x + 1, y - 5), (x + 1, 146)], "#293144", 1.1)
    p.ellipse((x - .7, y - 7, x + 2.7, y - 3.6), "#b9985d")
    p.box((x + 3, y + 1.5, x + width + 1, y + height + 1.5), "#6f665a")
    p.box((x + 2, y, x + width, y + height), "#f7f0df")
    if country == "US":
        for i in range(7):
            p.box((x + 2, y + i * height / 6.5, x + width, y + (i * 2 + 1) * height / 13), RED)
        p.box((x + 2, y, x + 24, y + 18), NAVY)
        for row in range(5):
            for col in range(5 if row % 2 == 0 else 4):
                p.star(x + 4.5 + col * 4 + (2 if row % 2 else 0), y + 2.5 + row * 3.2, .85)
    elif country == "INDIA":
        p.box((x + 2, y, x + width, y + 11), "#d99354")
        p.box((x + 2, y + 22, x + width, y + height), "#4b7052")
        cx, cy = x + 27.5, y + 16.5
        p.ellipse((cx - 4.6, cy - 4.6, cx + 4.6, cy + 4.6), outline=NAVY, width=.65)
        for i in range(24):
            a = i * pi / 12
            p.line([(cx, cy), (cx + 4.2 * cos(a), cy + 4.2 * sin(a))], NAVY, .3)
    elif country == "JAPAN":
        p.ellipse((x + 19, y + 8, x + 36, y + 25), RED)
    else:
        p.box((x + 2, y, x + width, y + height), NAVY)
        p.line([(x + 3, y + 1), (x + 25, y + 15)], CREAM, 2.6)
        p.line([(x + 3, y + 15), (x + 25, y + 1)], CREAM, 2.6)
        p.line([(x + 3, y + 1), (x + 25, y + 15)], RED, .8)
        p.line([(x + 3, y + 15), (x + 25, y + 1)], RED, .8)
        p.box((x + 2, y + 5, x + 26, y + 10), CREAM)
        p.box((x + 11, y, x + 16, y + 16), CREAM)
        p.box((x + 2, y + 6.5, x + 26, y + 8.5), RED)
        p.box((x + 12.5, y, x + 14.5, y + 16), RED)
        p.star(x + 14, y + 25, 3.4, points=7)
        for xx, yy in [(39, 7), (33, 18), (47, 17), (40, 27)]:
            p.star(x + xx, y + yy, 2.2, points=7)
        p.star(x + 44, y + 22, 1)
    # A translucent-looking fold, expressed with flat vector lines.
    p.line([(x + 48, y + 1), (x + 48, y + 32)], "#a79c87", .4)


def manila(scale):
    p = Plate(scale)
    p.box((0, 0, 310, 40), "#d6b197")
    p.box((0, 40, 310, 74), "#e6c4a1")
    p.box((0, 74, 310, 111), "#ecd4ae")
    p.box((0, 111, 310, 180), "#d9c7a6")
    p.ellipse((124, 24, 187, 87), "#f3e1b8")
    # Manila's layered high-rise silhouette: stepped towers and roof spires.
    for xx, ww, top in [(0, 19, 79), (21, 17, 62), (41, 26, 80), (71, 16, 51),
                        (90, 18, 76), (113, 17, 63), (136, 23, 77), (165, 20, 54),
                        (191, 18, 73), (215, 27, 57), (249, 17, 72), (272, 16, 49), (293, 17, 77)]:
        p.box((xx, top, xx + ww, 130), "#b3a58e")
        p.box((xx + 3, top - 4, xx + ww - 3, top + 1), "#b3a58e")
        p.line([(xx + ww / 2, top - 10), (xx + ww / 2, top - 4)], "#b3a58e", .7)
        for yy in range(top + 7, 123, 9):
            p.line([(xx + 4, yy), (xx + ww - 4, yy)], "#cdbda0", .6)
    p.poly([(0, 119), (15, 108), (33, 114), (52, 103), (73, 113), (94, 111),
            (119, 117), (149, 111), (177, 117), (198, 107), (220, 113), (249, 104),
            (273, 111), (291, 103), (310, 114), (310, 141), (0, 141)], "#8c9384")
    # Garlands hang high enough to leave clear space around the four flags.
    garland = [(i * 310 / 40, 10 + 11 * sin(i * pi / 40)) for i in range(41)]
    p.line(garland, "#605f56", .7)
    for i in range(18):
        xx = 8 + i * 17
        yy = 10 + 11 * sin(xx * pi / 310)
        p.poly([(xx - 4, yy), (xx + 4, yy), (xx, yy + 8)], [RED, NAVY, "#ede2c2"][i % 3])
    # Raised stage and long conference desk, in front of the skyline.
    p.box((12, 142, 298, 157), "#23384a")
    p.box((22, 157, 288, 166), NAVY)
    p.box((34, 166, 276, 173), "#283c4b")
    p.line([(12, 142), (298, 142)], "#f2d9a7", 1.2)
    p.line([(22, 157), (288, 157)], "#788784", .7)
    for xx, country in zip([20, 92, 164, 236], ["US", "INDIA", "JAPAN", "AUSTRALIA"]):
        flag(p, xx, 55, country)
    p.box((31, 131, 279, 136), "#8d644a")
    p.box((33, 136, 277, 145), "#b9895f")
    p.line([(34, 136), (276, 136)], "#e8c89b", .8)
    for xx in [56, 128, 200, 272]:
        p.box((xx - 9, 117, xx + 8, 130), "#3e4b4c")
        p.ellipse((xx - 8, 112, xx + 7, 123), "#3e4b4c")
        p.box((xx - 8, 133, xx + 7, 135), CREAM)
        p.line([(xx - 11, 130), (xx - 13, 124), (xx - 10, 123)], NAVY, .6)
    for i in range(24):
        xx = 41 + i * 10
        p.ellipse((xx - 2, 148, xx + 2, 151), "#8f9c77")
        if i % 3 == 0:
            p.ellipse((xx, 148, xx + 2, 150), "#dbba85")
    return p.image
