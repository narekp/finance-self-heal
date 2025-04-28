# tests/test_delete_transaction.py
"""
Delete flow:
1. add row (amount 333)
2. click trash icon in that row
3. confirm row is gone
"""
from uuid import uuid4
from tests.smart_locator import fuzzy_find
from tests.conftest import login, creds

def add_txn(page, tag):
    page.click("button:has-text('Add Transaction')")
    page.fill("#date", "2025-04-25")
    page.select_option("#category", label="Gifts")
    fuzzy_find(page, "input#amount").fill("333")
    page.select_option("#payment_method", label="Cash")
    page.fill("#notes", tag)
    page.click("#popup button[type='submit']")

def test_delete_transaction(page, creds):
    tag = f"Del-{uuid4().hex[:6]}"
    login(page, creds)
    page.goto("http://127.0.0.1:5000/transactions")
    add_txn(page, tag)

    # wait for row, then click its trash button
    row = page.locator(f"tbody tr:has-text('{tag}')")
    row.locator(".fa-trash-alt").click(force=True)
    page.wait_for_selector(f"tbody tr:has-text('{tag}')", state="detached")
    assert page.locator(f"tbody tr:has-text('{tag}')").count() == 0