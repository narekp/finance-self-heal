# Self-Healing Playwright Tests for Finance-Tracker

![CI](https://github.com/narekp/finance-self-heal/actions/workflows/ci.yml/badge.svg)

> **Impact:** Automatically repairs **100 %** of selector renames and keeps CI green.

A demo repo that *heals itself* when the underlying HTML changes.  
It wraps Playwright’s `locator()` with a fuzzy-matching helper that retargets missing elements at runtime and caches the fix.

## Quick-Start

```bash
git clone https://github.com/narekp/finance-self-heal.git
cd finance-self-heal
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt                  # test deps
pip install -r app/requirements.txt              # Flask deps
python scripts/seed_user.py                      # create demo user
python app/app.py &                              # serve on :5000
pytest -q                                        # watch all tests pass