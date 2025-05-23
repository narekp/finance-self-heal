"""
Self-healing locator helper.
• fast-path: if orig selector already mapped in locator_cache.json ➜ return it
• slow-path: fuzzy-scan DOM, cache the mapping, log the heal
"""

import sys, json, re
from pathlib import Path
from typing import List, Tuple
from rich.console import Console          # show HEAL logs in CI and local
from playwright.sync_api import Page, Locator
from rapidfuzz import fuzz, process
from bs4 import BeautifulSoup

# ---Adding a small helper to detect “id” vs “name”-----------------

def _extract_attr(orig_css: str):
    """
    If orig_css contains an #id or a name="…", return ("id", value) or ("name", value).
    Otherwise (None, None).
    """
    m = re.search(r"#([\w\-]+)", orig_css)
    if m:
        return "id", m.group(1)
    m = re.search(r"name=['\"]([\w\-]+)['\"]", orig_css)
    if m:
        return "name", m.group(1)
    return None, None
# ____________________________________________________________

console = Console(file=sys.stdout)        # stream to stdout so GitHub Actions captures it
CACHE = Path("locator_cache.json")

# Only consider form controls (keeps noise low)
ALLOWED_TAGS = ["input", "textarea", "select"]
DEFAULT_THRESHOLD = 60                    # 60 ≈ typo/abbrev tolerance

# ─── per-run store: (orig, new, score) ─────────────────────────────────────────
HEAL_EVENTS: List[Tuple[str, str, int]] = []

# ───registry + classifier helpers ──────────────────────────
REGISTRY = json.loads(Path("selector_registry.json").read_text()) # <- loads once

#---Score‑boost using class, if registry says broken selector is input.number, 
#----prefer candidates with the same type/tag even if their raw fuzzy score is a lower---
def _registry_class(sel: str) -> str | None:
    """Return the stored class (input.text, button.submit, …) for a selector."""
    for _, items in REGISTRY.items():
        for it in items:
            if it["selector"] == sel:
                return it["class"]
    return None

def _bs4_class(el) -> str:
    """Same classifier logic we used in the crawler."""
    if el.name == "input":
        t = el.get("type", "text").lower()
        return f"input.{t}"
    if el.name == "button":
        return "button.submit" if el.get("type", "").lower() == "submit" else "button"
    return el.name
# ─────────────────────────────────────────────────────────────────

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

    # ―――――― Phase 1: ID/Name–only healing ――――――
    attr, target = _extract_attr(orig_css)
    if attr:
        candidates = [tag[attr] for tag in soup.find_all(attrs={attr: True})]
        if candidates:
            healed_value, score, _ = process.extractOne(target, candidates, score_cutoff=thresh) or (None, 0, None)
            if healed_value:
                new_sel = f"#{healed_value}" if attr == "id" else f"[name=\"{healed_value}\"]"
                _update_cache(orig_css, new_sel)
                _log_once(orig_css, new_sel, int(score))
                return page.locator(new_sel)

    # ―――――― Phase 2: data-testid Fallback Healing ――――――
    # If your app uses data-testid="<value>" on elements, heal to the closest one.
    testids = [tag["data-testid"] for tag in soup.find_all(attrs={"data-testid": True})]
    if testids:
        # Compare against the cleaned orig_css key
        orig_key = re.sub(r"\W+", "", orig_css)
        match = process.extractOne(orig_key, testids, score_cutoff=thresh)
        if match:
            healed_value, score = match[0], int(match[1])
            new_sel = f"[data-testid=\"{healed_value}\"]"
            _update_cache(orig_css, new_sel)
            _log_once(orig_css, new_sel, score)
            return page.locator(new_sel)

    # ―――――― Phase 1b: Original fuzzy-text/CLASS fallback ――――――
    orig_key = re.sub(r"\W+", "", orig_css)
    best_score, best_el = 0, None
    for el in soup.find_all(ALLOWED_TAGS):
        cand_text = el.get("id") or el.get("name") or el.get_text() or ""
        cand_key  = re.sub(r"\W+", "", cand_text)
        score     = fuzz.partial_ratio(orig_key, cand_key)

        # ── registry‑aware boost ───────────────────────────────
        wanted_cls = _registry_class(orig_css)      # from the helper you added
        if wanted_cls and _bs4_class(el) == wanted_cls:
            score += 10     # bump ~10 pts when tag+type match
        # ───────────────────────────────────────────────────

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