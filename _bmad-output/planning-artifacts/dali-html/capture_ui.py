# -*- coding: utf-8 -*-
from pathlib import Path
import subprocess
from PIL import Image, ImageStat

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = Path(__file__).resolve().parent / "_preview" / "ui"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://127.0.0.1:8765/?shot=1&v=4#"

SCREENS = [
    "splash",
    "home",
    "search",
    "spots",
    "spot-erhai",
    "spot-xizhou",
    "spot-shuanglang",
    "spot-cangshan",
    "spot-pagoda",
    "spot-bridge",
    "culture",
    "culture-dye",
    "culture-wamao",
    "culture-house",
    "culture-tea",
    "culture-tower",
    "culture-fire",
    "exhibit",
    "mine",
    "empty",
    "history",
    "about",
    "loading",
    "fail",
]


def capture(name):
    dest = OUT / f"{name}.png"
    url = BASE + name
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--window-size=375,812",
            "--virtual-time-budget=4000",
            f"--screenshot={dest}",
            url,
        ],
        check=True,
        capture_output=True,
    )
    return dest


def region_var(im, box):
    crop = im.crop(box)
    return sum(ImageStat.Stat(crop).var)


def main():
    for name in SCREENS:
        dest = capture(name)
        im = Image.open(dest)
        print(f"{name:20} {im.size} {dest.stat().st_size:7d}")

    splash = Image.open(OUT / "splash.png")
    skip = region_var(splash, (250, 36, 375, 92))
    cta = region_var(splash, (32, 720, 343, 790))
    print(f"splash skip-var={skip:.1f} cta-var={cta:.1f}")

    erhai = Image.open(OUT / "spot-erhai.png")
    right = region_var(erhai, (300, 430, 367, 560))
    print(f"erhai cells-right-var={right:.1f}")

    mine = Image.open(OUT / "mine.png")
    mine_right = region_var(mine, (300, 210, 367, 300))
    print(f"mine cells-right-var={mine_right:.1f}")


if __name__ == "__main__":
    main()
