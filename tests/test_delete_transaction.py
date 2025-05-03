"""
Delete flow:
1 add row
2 click trash icon in that row
3 confirm the row disappears
"""

from uuid import uuid4
from tests.conftest import login, creds


def add_txn(page, tag):
    page.click("button:has-text('Add Transaction')")
    page.fill("#date", "2025-04-29")
    page.select_option("#category", label="Gifts")
    page.fill("#amount", "333")
    page.select_option("select#payment_method", label="Cash")
    page.fill("#notes", tag)
    with page.expect_navigation(wait_until="networkidle"):
        page.click("#popup button[type='submit']")


def test_delete_transaction(page, creds):
    tag = f"Del-{uuid4().hex[:6]}"

    login(page, creds)
    page.goto("http://127.0.0.1:5000/transactions", wait_until="networkidle")
    add_txn(page, tag)

    # trash it
    row = page.locator(f"tbody tr:has-text('{tag}')")
    row.locator(".fa-trash-alt").click(force=True)
    page.wait_for_selector(f"tbody tr:has-text('{tag}')", state="detached")
    assert page.locator(f"tbody tr:has-text('{tag}')").count() == 0
