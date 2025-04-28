# tests/test_home_chart_toggle.py
"""
Chart legend toggle (pixel hash):

• click inside canvas legend area to hide dataset
• hash must differ
• click again to show dataset
• hash must differ again (from hidden)
"""

import hashlib, base64
from tests.conftest import login, creds

CANVAS = "#dailySpendingChart"

def canvas_hash(page):
    data_url = page.evaluate(
        "() => document.querySelector('#dailySpendingChart').toDataURL('image/png')"
    )
    png = base64.b64decode(data_url.split(",")[1])
    return hashlib.sha1(png).hexdigest()

def click_legend(page):
    box = page.locator(CANVAS).bounding_box()
    page.locator(CANVAS).click(position={"x": box["width"]/2, "y": 20})

def test_chart_legend_toggle_hash(page, creds):
    login(page, creds)
    page.goto("http://127.0.0.1:5000/")
    page.wait_for_selector(CANVAS)

    h_visible = canvas_hash(page)

    click_legend(page)               # hide
    page.wait_for_timeout(300)
    h_hidden = canvas_hash(page)
    assert h_hidden != h_visible, "canvas unchanged after hide"

    click_legend(page)               # show
    page.wait_for_timeout(300)
    h_shown = canvas_hash(page)
    assert h_shown != h_hidden, "canvas unchanged after show"