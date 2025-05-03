"""
CSV download flow
─────────────────
1. Add a row with a unique tag
2. Click CSV button and wait for download
3. Assert:
   • header columns exactly as expected
   • tagged row present
"""

import csv, uuid, io
from tests.conftest import login, creds

EXPECTED_HEADER = [
    "Date",
    "Category",
    "Amount",
    "Payment Method",
    "Notes",
]


def add_txn(page, tag):
    page.click("button:has-text('Add Transaction')")
    page.fill("#date", "2025-04-27")
    page.select_option("#category", label="Food")
    page.fill("#amount", "444")
    page.select_option("select#payment_method", label="Cash")
    page.fill("#notes", tag)
    with page.expect_navigation(wait_until="networkidle"):
        page.click("#popup button[type='submit']")


def test_csv_download(page, creds, tmp_path):
    tag = f"CSV-{uuid.uuid4().hex[:6]}"

    # create row
    login(page, creds)
    page.goto("http://127.0.0.1:5000/transactions", wait_until="networkidle")
    add_txn(page, tag)
    page.wait_for_selector(f"tbody tr:has-text('{tag}')")

    # download
    with page.expect_download() as dl:
        page.locator(".fa-file-arrow-down").click()
    csv_path = dl.value.path()

    # parse & checks
    with io.open(csv_path, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    header, *rows = reader

    assert header == EXPECTED_HEADER, f"Header changed → {header}"
    assert any(tag in row for row in rows), "New transaction not in CSV"