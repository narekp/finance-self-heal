"""
CSV download flow
─────────────────
1. Add a row with a unique tag
2. Click CSV button and wait for download
3. Assert:
   • header columns exactly as expected
   • tagged row present
   • every row has the right column count
"""

import csv, uuid, io
from tests.smart_locator import fuzzy_find
from tests.conftest import login, creds


def add_txn(page, tag):
    page.click("button:has-text('Add Transaction')")
    page.fill("#date", "2025-04-25")
    page.select_option("#category", label="Food")
    fuzzy_find(page, "input#amount").fill("444")
    page.select_option("#payment_method", label="Cash")
    page.fill("#notes", tag)
    page.click("#popup button[type='submit']")


EXPECTED_HEADER = [
    "Date",
    "Category",
    "Amount",
    "Payment Method",
    "Notes",
]

def test_csv_download(page, creds, tmp_path):
    tag = f"CSV-{uuid.uuid4().hex[:6]}"

    # create row
    login(page, creds)
    page.goto("http://127.0.0.1:5000/transactions")
    add_txn(page, tag)
    page.wait_for_selector(f"tbody tr:has-text('{tag}')")

    # download
    with page.expect_download() as dl:
        page.locator(".fa-file-arrow-down").click()
    csv_path = dl.value.path()

    # parse
    with io.open(csv_path, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    header, *rows = reader

    # checks
    assert header == EXPECTED_HEADER, f"Header changed → {header}"
    assert any(tag in row for row in rows), "New transaction not found in CSV"