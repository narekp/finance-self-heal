"""
Self-healing locator helper.

• fast-path: if orig selector already mapped in locator_cache.json ➜ return it
• slow-path: fuzzy-scan DOM, cache the mapping, log the heal
"""

import sys, json, pathlib, re
from typing import List, Tuple
from rich.console import Console          # show HEAL logs in CI and local
from playwright.sync_api import Page, Locator
from rapidfuzz import fuzz
from bs4 import BeautifulSoup

console = Console(file=sys.stdout)        # stream to stdout so GitHub Actions captures it
CACHE = pathlib.Path("locator_cache.json")

# Only consider form controls (keeps noise low)
ALLOWED_TAGS = ["input", "textarea", "select"]
DEFAULT_THRESHOLD = 60                    # 60 ≈ typo/abbrev tolerance

# ─── per-run store: (orig, new, score) ─────────────────────────────────────────
HEAL_EVENTS: List[Tuple[str, str, int]] = []


def fuzzy_find(page: Page, orig_css: str, thresh: int = DEFAULT_THRESHOLD) -> Locator:
    """
    Return a Playwright Locator that best matches *orig_css*.
    Healed mappings are cached; subsequent runs use the cache immediately.
    """
    # ① fast-path ────────────────────────────────────────────────────────────
    if CACHE.exists():
        cache = json.loads(CACHE.read_text())
        if orig_css in cache:
            return page.locator(cache[orig_css])

    # ② slow path: scan live DOM ────────────────────────────────────────────
    soup = BeautifulSoup(page.content(), "html.parser")
    orig_key = re.sub(r"\W+", "", orig_css)

    best_score, best_el = 0, None
    for el in soup.find_all(ALLOWED_TAGS):
        cand_text = el.get("id") or el.get("name") or el.get_text() or ""
        cand_key  = re.sub(r"\W+", "", cand_text)
        score     = fuzz.partial_ratio(orig_key, cand_key)
        if score > best_score:
            best_score, best_el = score, el

    if best_score >= thresh and best_el:
        selector = best_el.name
        if best_el.get("id"):
            selector += f"#{best_el['id']}"
        elif best_el.get("class"):
            selector += f".{best_el['class'][0]}"

        _update_cache(orig_css, selector)
        _log_once(orig_css, selector, int(best_score))
        return page.locator(selector)

    raise ValueError(
        f"No fuzzy match for selector '{orig_css}' (best score: {best_score})"
    )

# ───────────────────────── helpers ────────────────────────────────────────────
def _update_cache(orig: str, new: str) -> None:
    data = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    data[orig] = new
    CACHE.write_text(json.dumps(data, indent=2))


def _log_once(orig: str, new: str, score: int) -> None:
    """Log heal only the first time during this run."""
    key = (orig, new)
    if key not in {(o, n) for o, n, _ in HEAL_EVENTS}:
        HEAL_EVENTS.append((orig, new, score))
        console.log(f"[green]✅ Healed[/] '{orig}' → '{new}' ({score} %)")
