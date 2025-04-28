"""
Home-page totals sanity

• Capture starting amounts
• Add one UPI and one Cash transaction (known values)
• Delete the Cash one
• Verify the three summary cards update correctly
"""

from uuid import uuid4
from decimal import Decimal
from tests.smart_locator import fuzzy_find
from tests.conftest import login, creds


def get_totals(page):
    upi  = Decimal(page.locator("h5:has-text('Total UPI Transactions')")
                         .locator("xpath=..")      # parent card
                         .locator("h6").inner_text().lstrip("₹"))
    cash = Decimal(page.locator("h5:has-text('Total Cash Transactions')")
                         .locator("xpath=..")
                         .locator("h6").inner_text().lstrip("₹"))
    total = Decimal(page.locator("h5:has-text('Total Amount')")
                           .locator("xpath=..")
                           .locator("h6").inner_text().lstrip("₹"))
    return upi, cash, total


def add_txn(page, tag, amt, pay_method):
    page.click("button:has-text('Add Transaction')")
    page.fill("#date", "2025-05-01")
    page.select_option("#category", label="Food")
    fuzzy_find(page, "input#amount").fill(str(amt))
    page.select_option("#payment_method", label=pay_method)
    page.fill("#notes", tag)
    page.click("#popup button[type='submit']")


def test_home_totals(page, creds):
    login(page, creds)

    # baseline
    page.goto("http://127.0.0.1:5000/")
    upi0, cash0, total0 = get_totals(page)

    # add UPI 100, add Cash 200
    tag_upi  = f"HUPI-{uuid4().hex[:4]}"
    tag_cash = f"HCASH-{uuid4().hex[:4]}"
    page.goto("http://127.0.0.1:5000/transactions")
    add_txn(page, tag_upi, 100, "UPI")
    add_txn(page, tag_cash, 200, "Cash")

    # delete the Cash row (leave the UPI one)
    row_cash = page.locator(f"tbody tr:has-text('{tag_cash}')")
    row_cash.locator(".fa-trash-alt").click(force=True)
    page.wait_for_selector(f"tbody tr:has-text('{tag_cash}')", state="detached")

    # back to Home and re-capture totals
    page.goto("http://127.0.0.1:5000/")
    upi1, cash1, total1 = get_totals(page)

    # expectations: UPI +100, Cash unchanged, Total +100
    assert upi1  == upi0  + 100
    assert cash1 == cash0
    assert total1 == total0 + 100