# ──────────────────────────────────────────────────────────────
# tests/conftest.py
# ──────────────────────────────────────────────────────────────
import os, pytest, functools, re
from dotenv import load_dotenv, find_dotenv
from playwright.sync_api import Page, TimeoutError as PWTimeout
from tests.smart_locator import fuzzy_find

load_dotenv(find_dotenv())

# ---------- original fixtures --------------------------------
@pytest.fixture(scope="session")
def creds():
    return {"u": os.getenv("FT_USER"), "p": os.getenv("FT_PASS")}

def login(page, creds):
    page.goto("http://127.0.0.1:5000/login")
    page.fill("#username", creds["u"])
    page.fill("#password", creds["p"])
    page.click("button[type='submit']")

# ---------- global smart-locator patch -----------------------
HEAL_TAGS = {"input", "textarea", "select", "button"}

def pytest_sessionstart(session):                 # runs once
    _patch_page_locator(Page)

def _patch_page_locator(PageCls):
    original = PageCls.locator
    def patched(self, selector: str, *a, **kw):
        loc = original(self, selector, *a, **kw)
        return _SmartLocator(loc, self, selector)
    PageCls.locator = patched

class _SmartLocator:
    def __init__(self, raw, page: Page, orig_css: str):
        self._raw, self._page, self._orig = raw, page, orig_css
    def __getattr__(self, name):
        fn = getattr(self._raw, name)
        if name in {"fill", "click", "select_option", "is_visible"}:
            return functools.partial(self._call_with_heal, fn, name)
        return fn
    # heal wrapper
    def _call_with_heal(self, fn, action_name, *a, **kw):
        try:
            return fn(*a, **kw, timeout=2_000)
        except PWTimeout:
            if self._should_heal():
                healed = fuzzy_find(self._page, self._orig)
                return getattr(healed, action_name)(*a, **kw)
            raise
    def _should_heal(self) -> bool:
        m = re.match(r"(\w+)", self._orig)
        return m and m.group(1).lower() in HEAL_TAGS
