# ──────────────────────────────────────────────────────────────
# tests/conftest.py
# ──────────────────────────────────────────────────────────────

import sys, rich
from tests.smart_locator import HEAL_EVENTS, fuzzy_find
import os, pytest, functools, re
from dotenv import load_dotenv, find_dotenv
from playwright.sync_api import Page, TimeoutError as PWTimeout

load_dotenv(find_dotenv())

# ---------- original fixtures --------------------------------
@pytest.fixture(scope="session")
def creds():
    return {"u": os.getenv("FT_USER"), "p": os.getenv("FT_PASS")}

def login(page, creds):
    page.goto("http://127.0.0.1:5000/login", wait_until="networkidle")
    page.fill("#username", creds["u"])
    page.fill("#password", creds["p"])
    page.click("button[type='submit']")

# ---------- global smart-locator patch -----------------------
HEAL_TAGS = {"input", "textarea", "select", "button"}

def pytest_sessionstart(session):                 # runs once
    _patch_page_locator(Page)
    _patch_page_actions(Page)

def _patch_page_locator(PageCls):
    original = PageCls.locator

    def patched(self, selector: str, *a, **kw):
        """
        Wrap locator() so fill/select_option go through heal logic on timeout.
        """
        loc = original(self, selector, *a, **kw)
        return _SmartLocator(loc, self, selector)

    PageCls.locator = patched

def _patch_page_actions(PageCls):
    """
    Only route page.fill and page.select_option through locator().
    Leave page.click as original to avoid strict-mode issues.
    """
    # --- fill ---
    def fill(self, selector: str, *a, **kw):
        return self.locator(selector).fill(*a, **kw)
    PageCls.fill = fill

    # --- select_option ---
    def select_option(self, selector: str, *a, **kw):
        return self.locator(selector).select_option(*a, **kw)
    PageCls.select_option = select_option

class _SmartLocator:
    """
    Wraps a Playwright Locator to auto-heal on timeout for:
    fill, select_option, is_visible (click left intact).
    """
    def __init__(self, raw, page: Page, orig_css: str):
        self._raw  = raw
        self._page = page
        self._orig = orig_css

    def __getattr__(self, name):
        fn = getattr(self._raw, name)
        if name in {"fill", "select_option", "is_visible"}:
            return functools.partial(self._call_with_heal, fn, name)
        return fn

    def _call_with_heal(self, fn, action_name, *a, **kw):
        try:
            return fn(*a, **{**kw, "timeout": 2_000})
        except PWTimeout:
            if self._should_heal():
                healed = fuzzy_find(self._page, self._orig)
                return getattr(healed, action_name)(*a, **kw)
            raise

    def _should_heal(self) -> bool:
        """
        Heal when the selector contains an ID (#…), a name=…, or begins
        with one of HEAL_TAGS (input, textarea, select, button).
        """
        if "#" in self._orig or "name=" in self._orig:
            return True
        m = re.match(r"(\w+)", self._orig)
        return bool(m and m.group(1).lower() in HEAL_TAGS)

def pytest_sessionfinish(session, exitstatus):
    """Print one-line summary after all tests."""
    console = rich.console.Console(file=sys.stdout)
    if not HEAL_EVENTS:
        console.print("[green bold]🟢 0 selectors healed (cache up-to-date)")
    else:
        console.print(f"[yellow bold]🟡 {len(HEAL_EVENTS)} selectors healed this run:")
        for orig, new, score in HEAL_EVENTS:
            console.print(f"   {orig:<25} → {new:<25} ({score} %)")