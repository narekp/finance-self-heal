"""
Home‑page totals sanity:

1 record baseline card values
2 add UPI 100 & Cash 200
3 delete the Cash one
4 expect UPI +100, Cash unchanged, Total +100
"""

from uuid import uuid4
from decimal import Decimal
from tests.conftest import login, creds


def get_totals(page):
    def _value(label):
        return Decimal(
            page.locator(f"h5:has-text('{label}')")
            .locator("xpath=..")      # parent card
            .locator("h6")
            .inner_text()
            .lstrip("₹")
        )

    return _value("Total UPI Transactions"), _value("Total Cash Transactions"), _value("Total Amount")


def add_txn(page, tag, amt, pay_method):
    page.click("button:has-text('Add Transaction')")
    page.fill("#date", "2025-05-01")
    page.select_option("#category", label="Food")
    page.fill("#amount", str(amt))
    page.select_option("select#payment_method", label=pay_method)
    page.fill("#notes", tag)
    with page.expect_navigation(wait_until="networkidle"):
        page.click("#popup button[type='submit']")


def test_home_totals(page, creds):
    login(page, creds)

    # baseline
    page.goto("http://127.0.0.1:5000/", wait_until="networkidle")
    upi0, cash0, total0 = get_totals(page)

    # add two rows
    page.goto("http://127.0.0.1:5000/transactions")
    tag_upi  = f"HUPI-{uuid4().hex[:4]}"
    tag_cash = f"HCASH-{uuid4().hex[:4]}"
    add_txn(page, tag_upi, 100, "UPI")
    add_txn(page, tag_cash, 200, "Cash")

    # delete Cash row
    row_cash = page.locator(f"tbody tr:has-text('{tag_cash}')")
    row_cash.locator(".fa-trash-alt").click(force=True)
    page.wait_for_selector(f"tbody tr:has-text('{tag_cash}')", state="detached")

    # re‑check cards
    page.goto("http://127.0.0.1:5000/")
    upi1, cash1, total1 = get_totals(page)

    assert upi1 == upi0 + 100
    assert cash1 == cash0
    assert total1 == total0 + 100