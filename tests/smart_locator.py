from playwright.sync_api import Locator, Page
from rapidfuzz import fuzz
from bs4 import BeautifulSoup
import json, pathlib, re

CACHE = pathlib.Path("locator_cache.json")

# Only consider input, textarea, and select elements for fuzzy matching
ALLOWED_TAGS = ["input", "textarea", "select"]

# Lower threshold to 60 to handle small id changes like 'amt' vs 'amount'
DEFAULT_THRESHOLD = 60

def fuzzy_find(page: Page, orig_css: str, thresh: int = DEFAULT_THRESHOLD) -> Locator:
    """
    Fuzzy-locates a form element by id/name/content, caching fixes for future runs.

    :param page: Playwright Page instance
    :param orig_css: Original CSS selector string
    :param thresh: Minimum fuzz ratio to accept a candidate
    :return: Playwright Locator for the best-matching element
    """
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    # Clean up the original selector text for comparison
    orig_key = re.sub(r"\W+", "", orig_css)

    best_score, best_el = 0, None
    for el in soup.find_all(ALLOWED_TAGS):
        # Build candidate key from id, name, or element text
        cand_text = el.get("id") or el.get("name") or el.get_text() or ""
        cand_key = re.sub(r"\W+", "", cand_text)
        score = fuzz.partial_ratio(orig_key, cand_key)
        if score > best_score:
            best_score, best_el = score, el

    if best_score >= thresh and best_el:
        selector = best_el.name
        if best_el.get("id"):
            selector += f"#{best_el['id']}"
        elif best_el.get("class"):
            selector += f".{best_el['class'][0]}"
        _update_cache(orig_css, selector)
        return page.locator(selector)

    # If no candidate passes threshold, list best match to help debug
    raise ValueError(f"No fuzzy match for selector '{orig_css}' (best score: {best_score})")

def _update_cache(orig: str, new: str):
    data = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    data[orig] = new
    CACHE.write_text(json.dumps(data, indent=2))