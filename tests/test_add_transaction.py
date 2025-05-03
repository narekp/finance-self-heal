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

    # --- go to transactions ---
    page.goto("http://127.0.0.1:5000/transactions", wait_until="networkidle")

    # --- open the popup and fill form ---
    page.click("button:has-text('Add Transaction')")
    page.fill("#date", "2025-04-25")
    page.select_option("#category", label="Food")
    page.fill("#amount", "123")
    page.select_option("select#payment_method", label="Cash")
    page.fill("#notes", f"AutoTest-{tag}")

    # --- click “Add” and wait for the redirect to /transactions ---
    with page.expect_navigation(wait_until="networkidle"):
        page.click("#popup button[type='submit']")

    # --- now assert the new row is visible ---
    assert page.locator(f"text=AutoTest-{tag}").first.is_visible(timeout=5_000)