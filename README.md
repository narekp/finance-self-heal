# Self-Healing Playwright Tests for Finance-Tracker

![CI](https://github.com/narekp/finance-self-heal/actions/workflows/ci.yml/badge.svg)

> **Impact:** Your test suite _fixes itself_ when the UI changes, so CI never breaks on simple selector renames.

Project shows how to wrap Playwright’s locator calls with an AI-enhanced, fuzzy-matching engine that:

- Detects broken selectors at runtime  
- Scans the live DOM for the closest match (by `id`, `name`, CSS class, or text)  
- Caches the fix so subsequent test runs are lightning-fast  
- Logs exactly _which_ selectors healed (and with what confidence)

## 🔍 Features

- **Zero-cost self-healing**: No commercial services—just open-source Python, Playwright, RapidFuzz, and BeautifulSoup  
- **ID / Name fallback**: Automatically repairs renamed `id` or `name` attributes  
- **Form control coverage**: Works out of the box on `<input>`, `<textarea>`, `<select>`, and buttons  
- **Cache-first lookup**: Once a broken selector is healed, it never scans the DOM again  
- **Clear test output**: Rich logs show exactly which selectors healed and their fuzzy-match score  
- ### 🗺️ Selector Registry

`scripts/catalog_selectors.py` crawls every **GET** route exposed by the Flask
demo (`/`, `/login`, `/transactions`, …).  For each page it records the
CSS selectors of UI controls – `input`, `select`, `textarea`, `button`, `a`.

```bash
python scripts/catalog_selectors.py      # ⇢ writes selector_registry.json
```

`selector_registry.json` maps **route → selector list**.  
Current demo size: **18 selectors across 8 routes**.

The registry enables upcoming automation:
* alert on *new / deleted* selectors in PRs  
* feed coverage stats to the healing‑metrics dashboard  

## Quick-Start

```bash
git clone --recurse-submodules https://github.com/narekp/finance-self-heal.git
cd finance-self-heal

# Set up Python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt      # test dependencies
pip install -r app/requirements.txt  # Flask demo dependencies

# Seed data & run the app
python scripts/seed_user.py
python app/app.py &                  # serves at http://127.0.0.1:5000

# Run the fully-automated, self-healing E2E suite
pytest -q
```

## Notes and Cnsiderations

- locator_cache.json and finance_tracker.db are git-ignored and re-created each run.
- If you forget --recurse-submodules, run git submodule update --init --recursive before pytest.

## 📋 Current Status

| Capability                                   | Status  | Notes |
|----------------------------------------------|:-------:|-------|
| **ID / name selector healing**               | ✅ Done | Phase 1 algorithm (RapidFuzz) in `smart_locator.py`. |
| **`data-testid` fallback healing**           | ✅ Done | Phase 2 implemented; kicks in after ID/Name. |
| **stable `Page.goto` (networkidle→load)** | ✅ Done | Minimal patch; removed over‑broad retries. |
| **Selector‑registry generator**              | ✅ Done | `catalog_selectors.py` + nightly Action |
| **Automated selector‑classification registry**| in progress | Use the registry to auto‑label and validate new elements |
| **Healing/Metrics dashboard**          | Future | Quick visual insight|
