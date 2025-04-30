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
- **Extensible**: Next steps include `data-testid` support, timeout-aware waits, and optional visual diffs  

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

| Capability                             	| Status     |
|-------------------------------------------|:----------:|
| ID & Name attribute healing            	| ✅ Done     |
| `data-testid` fallback healing         	| ✅ Done     |
| Dynamic loading & auto-waits           	| 🔜 Pending  |
| Automated locator classification       	| 🔜 Future   |
| HTML/CSS visual regression (screenshots) | 🔜 Future |