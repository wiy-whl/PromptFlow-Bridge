# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image, ImageFilter, ImageChops

ROOT = Path(r"d:\AI\chajian\Promptbridge")
SRC = ROOT / "resume" / "大理"
OUT = ROOT / "_bmad-output" / "planning-artifacts" / "dali-html" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

SPOTS = SRC / "a8683bc91dad050e1f1e3ce146a60011.jpg"
CULTURE = SRC / "17dc3c39ad60a8605b61d36e9c35912c.jpg"
YUN = SRC / "73e63019012f90a3520695f3b44e3e53.jpg"
YUN2 = SRC / "d4b10d377086ead774d420c3367a0c9b.jpg"
BOARD = SRC / "fa5867e431860a3d1afdcd7da2ef0c9b.jpg"


def load(path):
    return Image.open(path).convert("RGB")


def box_frac(im, l, t, r, b):
    w, h = im.size
    return im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def box_px(im, l, t, r, b):
    return im.crop((l, t, r, b))


def trim_bg(im, tol=26, pad=2):
    """Trim near-uniform page background around a photo card."""
    w, h = im.size
    px = im.load()
    samples = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
    bg = tuple(sum(c[i] for c in samples) // 4 for i in range(3))

    def is_bg(x, y):
        p = px[x, y]
        return abs(p[0] - bg[0]) < tol and abs(p[1] - bg[1]) < tol and abs(p[2] - bg[2]) < tol

    top = 0
    while top < h - 8 and all(is_bg(x, top) for x in range(0, w, 6)):
        top += 1
    bottom = h - 1
    while bottom > 8 and all(is_bg(x, bottom) for x in range(0, w, 6)):
        bottom -= 1
    left = 0
    while left < w - 8 and all(is_bg(left, y) for y in range(0, h, 6)):
        left += 1
    right = w - 1
    while right > 8 and all(is_bg(right, y) for y in range(0, h, 6)):
        right -= 1

    left = max(0, left + pad)
    top = max(0, top + pad)
    right = min(w, right - pad)
    bottom = min(h, bottom - pad)
    if right - left < 40 or bottom - top < 40:
        return im
    return im.crop((left, top, right, bottom))


def is_page_col(im, x):
    h = im.size[1]
    px = im.load()
    samples = [px[x, y] for y in range(int(h * 0.22), int(h * 0.78), max(1, h // 36))]
    if len(samples) < 4:
        return False
    avg = tuple(sum(c[i] for c in samples) / len(samples) for i in range(3))
    spread = max(max(c[i] for c in samples) - min(c[i] for c in samples) for i in range(3))
    bright = sum(avg) / 3
    sat = max(avg) - min(avg)
    light = spread < 42 and bright > 158 and sat < 55
    dark = spread < 28 and bright < 80 and sat < 42
    return light or dark


def is_page_row(im, y):
    w = im.size[0]
    px = im.load()
    samples = [px[x, y] for x in range(int(w * 0.22), int(w * 0.78), max(1, w // 36))]
    if len(samples) < 4:
        return False
    avg = tuple(sum(c[i] for c in samples) / len(samples) for i in range(3))
    spread = max(max(c[i] for c in samples) - min(c[i] for c in samples) for i in range(3))
    bright = sum(avg) / 3
    sat = max(avg) - min(avg)
    light = spread < 42 and bright > 158 and sat < 55
    dark = spread < 28 and bright < 80 and sat < 42
    return light or dark


def trim_page(im, min_keep=0.55):
    w, h = im.size
    left, right, top, bottom = 0, w - 1, 0, h - 1
    while left < w * (1 - min_keep) and is_page_col(im, left):
        left += 1
    while right > w * min_keep and is_page_col(im, right):
        right -= 1
    while top < h * (1 - min_keep) and is_page_row(im, top):
        top += 1
    while bottom > h * min_keep and is_page_row(im, bottom):
        bottom -= 1
    if right - left < 40 or bottom - top < 40:
        return im
    return im.crop((left, top, right + 1, bottom + 1))


def save(im, name, max_w=1100, inset=None):
    im = trim_page(im)
    if inset:
        w, h = im.size
        im = im.crop((int(w * inset[0]), int(h * inset[1]), int(w * inset[2]), int(h * inset[3])))
    if im.width > max_w:
        nh = max(1, int(im.height * max_w / im.width))
        im = im.resize((max_w, nh), Image.Resampling.LANCZOS)
    dest = OUT / name
    im.save(dest, "JPEG", quality=90, optimize=True)
    print(f"{name:28} {im.size}")


spots = load(SPOTS)
culture = load(CULTURE)
yun = load(YUN)
yun2 = load(YUN2)
board = load(BOARD)

# 景点一览：航拍水面（避开大标题，只要栈桥）
save(box_frac(spots, 0.00, 0.118, 1.00, 0.162), "hero-erhai.jpg")
save(trim_bg(box_px(spots, 300, 1430, 970, 1760)), "spot-cangshan.jpg")
save(trim_bg(box_px(spots, 1020, 1760, 1640, 2080)), "spot-erhai.jpg", inset=(0, 0.04, 0.88, 1))
save(trim_bg(box_px(spots, 1080, 2520, 1660, 2840)), "spot-pagoda.jpg", inset=(0, 0, 0.90, 0.94))
save(trim_bg(box_px(spots, 260, 3680, 620, 4080)), "spot-shuanglang.jpg")
save(trim_bg(box_px(spots, 760, 3680, 1120, 4080)), "spot-xizhou.jpg")
save(trim_bg(box_px(spots, 1290, 3680, 1650, 4080)), "spot-bridge.jpg")
save(trim_bg(box_px(spots, 150, 4620, 540, 4940)), "spot-alley.jpg")
save(trim_bg(box_px(spots, 560, 4620, 950, 4940)), "spot-courtyard.jpg")
save(trim_bg(box_px(spots, 150, 4960, 540, 5280)), "craft-batik-round.jpg")
save(trim_bg(box_px(spots, 560, 4960, 950, 5280)), "craft-food.jpg")

# 文化：只要照片卡，躲开书法和说明
save(box_frac(culture, 0.72, 0.078, 0.99, 0.138), "hero-tiedye.jpg")
save(trim_bg(box_px(culture, 1040, 1500, 1660, 2140)), "culture-temple.jpg", inset=(0, 0, 0.93, 1))
save(trim_bg(box_px(culture, 250, 2515, 910, 2735)), "culture-town.jpg", inset=(0.08, 0.03, 1, 1))
save(trim_bg(box_px(culture, 220, 2920, 960, 3200)), "culture-room.jpg")
save(trim_bg(box_px(culture, 250, 3680, 610, 4040)), "craft-dye.jpg")
save(trim_bg(box_px(culture, 790, 3660, 1140, 3888)), "craft-tea.jpg")
save(trim_bg(box_px(culture, 1310, 3680, 1660, 4040)), "craft-fire.jpg", inset=(0, 0, 0.78, 1))
save(trim_bg(box_px(culture, 1055, 4730, 1310, 5020)), "craft-cloth.jpg")
save(trim_bg(box_px(culture, 1400, 4735, 1680, 5070)), "craft-shelf.jpg", inset=(0, 0, 0.76, 1))
save(trim_bg(box_px(culture, 1055, 5140, 1320, 5430)), "craft-set.jpg")
save(trim_bg(box_px(culture, 1400, 5130, 1680, 5435)), "craft-box.jpg")

# 云上：孤舟
save(trim_bg(box_frac(yun, 0.10, 0.518, 0.90, 0.642)), "hero-boat.jpg")
save(box_frac(yun, 0.42, 0.188, 0.92, 0.298), "hero-roof.jpg")

# 竖版长页拍立得
save(trim_bg(box_px(yun2, 30, 1100, 760, 1580)), "hero-wave.jpg")
save(trim_bg(box_px(yun2, 0, 1880, 793, 2360)), "spot-sky.jpg")
save(trim_bg(box_px(yun2, 40, 3080, 280, 3480)), "stamp-pagoda.jpg")
save(trim_bg(box_px(yun2, 300, 3080, 540, 3480)), "stamp-lake.jpg")
save(trim_bg(box_px(yun2, 560, 3080, 790, 3480)), "stamp-boat.jpg")
save(trim_bg(box_px(yun2, 400, 4000, 760, 4580)), "spot-gucheng.jpg")
save(trim_bg(box_px(yun2, 30, 4720, 400, 5340)), "spot-grass.jpg")
save(trim_bg(box_px(yun2, 340, 5620, 760, 6220)), "spot-shuanglang2.jpg")

# 展板大手机洱海
save(trim_bg(box_px(board, 850, 1320, 1210, 1640)), "phone-erhai.jpg")

print("done", len(list(OUT.glob("*.jpg"))), "jpgs")
