# -*- coding: utf-8 -*-
"""驱动大理原型，截取作品集所需的关键屏幕（375x812 @2x）。
注意：原型只在启动时读取一次 hash，因此每次换屏都强制全新加载。"""
import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_preview" / "portfolio"
OUT.mkdir(parents=True, exist_ok=True)
PORT = 8892

STATIC = [
    "splash", "home", "search", "spots", "spot-erhai", "spot-xizhou",
    "culture", "culture-dye", "exhibit", "mine", "empty", "loading", "fail",
]


def main():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        base = f"http://127.0.0.1:{PORT}/?shot=1#"

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 375, "height": 812}, device_scale_factor=2)

            def shot(name):
                page.screenshot(path=str(OUT / f"{name}.png"), type="png")
                print("shot:", name)

            def js_click(sel):
                page.eval_on_selector(sel, "el => el.click()")
                page.wait_for_timeout(280)

            def nav(name):
                """强制全新加载（应用只读一次 hash）。"""
                page.goto("about:blank")
                page.goto(base + name)
                page.wait_for_timeout(1000)

            # ---- 静态屏 ----
            for s in STATIC:
                nav(s)
                shot(s)

            # ---- 行程规划流程（同一会话内连续交互）----
            nav("spots")
            for sid in ["spot-erhai", "spot-xizhou", "spot-shuanglang", "spot-cangshan"]:
                js_click(f'[data-add="{sid}"]')
            shot("trip-added")
            js_click("#trip-fab")
            page.wait_for_timeout(700)
            page.evaluate("""() => {
                const sl = document.getElementById('trip-days');
                sl.value = '2';
                sl.dispatchEvent(new Event('input', {bubbles:true}));
            }""")
            page.wait_for_timeout(400)
            shot("trip-sheet")
            js_click("#trip-plan")
            page.wait_for_timeout(900)
            shot("trip-plan")

            # ---- 文化加入体验 ----
            nav("culture")
            js_click('[data-cult-add="culture-dye"]')
            js_click('[data-cult-add="culture-tea"]')
            page.wait_for_timeout(400)
            shot("culture-added")

            # ---- 想去列表（有数据）：同会话内加收藏后经页内按钮跳转 ----
            nav("spots")
            js_click('[data-fav="洱海"]')
            js_click('[data-fav="喜洲古镇"]')
            js_click("#open-fav-list")
            page.wait_for_timeout(900)
            shot("fav-list")

            browser.close()
        httpd.shutdown()
    print("done ->", OUT)


if __name__ == "__main__":
    main()
