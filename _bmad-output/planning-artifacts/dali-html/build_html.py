# -*- coding: utf-8 -*-
"""压缩原型截图并内嵌进单文件作品集 HTML。"""
import os, base64, io
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(ROOT, "_preview", "portfolio")
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "大理文旅作品集-作品集.html")
TEMPLATE = os.path.join(ROOT, "portfolio_html_template.html")

PHONES = {
    "PH_SPLASH": "splash.png",
    "PH_HOME": "home.png",
    "PH_SPOTS": "spots.png",
    "PH_SPOT_ERHAI": "spot-erhai.png",
    "PH_SPOT_XIZHOU": "spot-xizhou.png",
    "PH_EXHIBIT": "exhibit.png",
    "PH_CULTURE": "culture.png",
    "PH_CULTURE_DYE": "culture-dye.png",
    "PH_CULTURE_ADDED": "culture-added.png",
    "PH_FAVLIST": "fav-list.png",
    "PH_SEARCH": "search.png",
    "PH_TRIP_ADDED": "trip-added.png",
    "PH_TRIP_SHEET": "trip-sheet.png",
    "PH_TRIP_PLAN": "trip-plan.png",
    "PH_MINE": "mine.png",
    "PH_EMPTY": "empty.png",
    "PH_LOADING": "loading.png",
    "PH_FAIL": "fail.png",
}

HERO_BG = ("HERO_BG", os.path.join(ASSETS, "hero-erhai-aerial.jpg"), 1600)
PHONE_BG = ("PHONE_BG", os.path.join(ASSETS, "spot-erhai.jpg"), 800)
EXTRA_BG = ("EXTRA_BG", os.path.join(ASSETS, "culture-town.jpg"), 800)


def compress(path, max_w, quality=82):
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        h = int(im.height * max_w / im.width)
        im = im.resize((max_w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def main():
    tok = {}
    print("压缩手机屏 ...")
    for key, fn in PHONES.items():
        tok[key] = compress(os.path.join(SHOTS, fn), 560)
    print("压缩背景图 ...")
    tok[HERO_BG[0]] = compress(HERO_BG[1], HERO_BG[2])
    tok[PHONE_BG[0]] = compress(PHONE_BG[1], PHONE_BG[2])
    tok[EXTRA_BG[0]] = compress(EXTRA_BG[1], EXTRA_BG[2])

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    for k, v in tok.items():
        html = html.replace("{{" + k + "}}", v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(OUT) / 1024 / 1024
    print(f"写出 {OUT}  {size:.2f} MB  缺失占位:", html.count("{{"), "处")


if __name__ == "__main__":
    main()
