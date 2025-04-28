import os, pytest
from dotenv import load_dotenv, find_dotenv
from tests.smart_locator import fuzzy_find
load_dotenv(find_dotenv())

@pytest.fixture(scope="session")
def creds():
    return {"u": os.getenv("FT_USER"), "p": os.getenv("FT_PASS")}

def login(page, creds):
    page.goto("http://127.0.0.1:5000/login")
    page.fill("#username", creds["u"])
    page.fill("#password", creds["p"])
    page.click("button[type='submit']")