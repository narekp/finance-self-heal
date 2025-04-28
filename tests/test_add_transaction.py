import os
from uuid import uuid4
from dotenv import load_dotenv, find_dotenv
# Load .env from project root so FT_USER and FT_PASS become available in os.environ to pull
load_dotenv(find_dotenv())
from tests.smart_locator import fuzzy_find

def test_add_transaction(page):
    tag = uuid4().hex[:8]          # unique marker for this run

    # --- login ---
    page.goto("http://127.0.0.1:5000/login", wait_until="networkidle")
    page.fill("#username", os.environ["FT_USER"])
    page.fill("#password", os.environ["FT_PASS"])
    page.click("button[type='submit']")

    # --- navigate ---
    page.goto("http://127.0.0.1:5000/transactions", wait_until="networkidle")

    # --- add transaction ---
    page.click("button:has-text('Add Transaction')")
    page.fill("#date", "2025-04-25")
    page.select_option("#category", label="Food")
    fuzzy_find(page, "input#amount").fill("123")
    page.locator("select#payment_method").select_option(label="Cash")
    page.fill("#notes", f"AutoTest-{tag}")
    page.click("#popup button[type='submit']")

    # --- assert new row exists anywhere in table ---
    assert page.locator(f"text=AutoTest-{tag}").first.is_visible(timeout=5000)