#!/usr/bin/env python
"""
Crawl every route of the Finance‑Tracker Flask app, capture all *form‑control*
selectors, and write them to selector_registry.json.

• Routes list comes from `app.app.url_map` (works because we import the Flask app)
• Uses Playwright in headless Chromium to render each page
• Captures only:  <input>, <textarea>, <select>, <button>
• Saves JSON structure:
    {
      "<route>": [
         {"css": "input#amount", "tag": "input", "type": "number"},
         ...
      ],
      ...
    }
Run locally:  python scripts/catalog_selectors.py
"""

#!/usr/bin/env python
"""
Generate selector_registry.json by visiting every GET route in the
Finance‑Tracker Flask app, capturing form‑control selectors.
"""

import json, pathlib, asyncio, sys
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]

# --- make the Folder-With-Flask‑app importable ---------------------------
#  app/        (submodule)
#    └── app.py   ← defines `app = Flask(__name__)`
sys.path.append(str(ROOT / "app"))        # adds …/finance-self-heal/app to PYTHONPATH
from app import app as FLASK_APP          # safe: we import the module app.py
# -------------------------------------------------------------------------

OUT  = ROOT / "selector_registry.json"
TAGS = {"input", "select", "textarea", "button", "a"}

async def crawl():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page    = await browser.new_page()
        catalog = {}

        for rule in FLASK_APP.url_map.iter_rules():
            # skip dynamic routes and Flask’s built‑in static helper
            if "<" in rule.rule or rule.endpoint == "static":
                continue
            # we only care that the route **allows** GET
            if "GET" in rule.methods:
                url = f"http://127.0.0.1:5000{rule.rule}"
                await page.goto(url)
                catalog[rule.rule] = parse(await page.content())

        await browser.close()

    OUT.write_text(json.dumps(catalog, indent=2))
    print(f"✔ wrote {OUT.name} with {sum(len(v) for v in catalog.values())} selectors")

def parse(html: str):
    soup = BeautifulSoup(html, "html.parser")
    nodes = []
    for tag in soup.find_all(TAGS):
        sel = selector(tag)
        if sel:
            nodes.append({"css": sel, "tag": tag.name, "type": tag.get("type", "")})
    return nodes

def selector(tag):
    if tag.get("id"):
        return f"{tag.name}#{tag['id']}"
    if tag.get("name"):
        return f'{tag.name}[name="{tag["name"]}"]'
    return ""

if __name__ == "__main__":
    asyncio.run(crawl())