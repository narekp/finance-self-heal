# 🤖 AI‑Assisted, Self‑Healing Playwright Suite  

[![CI](https://github.com/narekp/finance-self-heal/actions/workflows/ci.yml/badge.svg)](https://github.com/narekp/finance-self-heal/actions)

**What is this?** 
- end‑to‑end tests that **HEAL THEMSELVES** when selectors change.  
- Built with 100% open‑source tech, no flakiness on UI refactors.  
- Demonstrates my approach as a QA Engineer incorpoating AI:
  
  <span style="margin-left: 20px;"></span> -**Automation architecture**  
  <span style="margin-left: 20px;"></span> -**AI-backed heuristics** (RapidFuzz + DOM analysis)  
  <span style="margin-left: 20px;"></span> -**CI/CD** (GitHub Actions)  
  <span style="margin-left: 20px;"></span> -**Task decomposition** (see "Issues")


## 🚦 Why it matters

| Pain in traditional UI tests | This project’s answer |
|------------------------------|-----------------------|
| Minor `id` rename ⇒ whole CI red | Fuzzy heuristic heals the selector on‑the‑fly |
| Slow to debug flaky locators | One‑line Rich log shows **what healed** & **confidence %** |
| Manual upkeep of element maps | Crawler auto‑generates a *selector registry* on every PR |
| Vendor‑locked smart healing tools | Pure Python (Playwright + RapidFuzz + BeautifulSoup) |

---

## ✨ Current Capabilities

| Capability | Status | Where / Notes |
|------------|:------:|--------------|
| ID / name self‑healing | ✅ | `smart_locator.py` (phase‑1) |
| `data-testid` fallback | ✅ | automatic if IDs absent |
| Selector‑classification registry <br>*(`input.text`, `button.submit`, …)* | ✅ | `scripts/catalog_selectors.py` → `selector_registry.json` |
| Registry‑aware boost (+10 score) | ✅ | loaded at Pytest session‑start |
| CI auto‑update of registry | ✅ | Workflow step commits JSON diff |
| Rich, once‑per‑run heal log | ✅ | e.g. `✅ Healed '#amount' → '#amoumt' (83 %)` |
| Healing telemetry dashboard | 🔜 | (Story B in Issues) |

---

## 🧩 How it works — 3-layer design

       Playwright ▶ patched locator() ─┐
                                       │ ❶ Try original selector
                                       │ ❷ If fail → fuzzy search DOM
       + selector registry JSON ───────┘ ❸ Boost matches sharing same
                                              type class (input.text…)
                                           ⇢ write heal to cache + log


* **Crawler** visits every GET route, extracts form controls, classifies them, and writes a lightweight JSON registry.  
* **Smart Locator** wraps all `.fill() / .click()` calls. On failure it RapidFuzz‑matches IDs/names/test‑ids, boosted by registry class.  
* **Cache** means each selector heals only once per run → next test is instant.

---

## 🚀 Quick‑Start (local demo)

```bash
git clone --recurse-submodules https://github.com/narekp/finance-self-heal.git
cd finance-self-heal
python -m venv .venv && source .venv/bin/activate

# Framework deps
pip install -r requirements.txt
# Flask demo app deps
pip install -r app/requirements.txt

# seed demo user & run the app
python scripts/seed_user.py
python app/app.py &   # http://127.0.0.1:5000

pytest -q            # 5 green tests, watch self‑healing in action
```
> Tip: Both locator_cache.json and finance_tracker.db are git‑ignored and re‑created each run.

## 🗺️ Selector Registry (for curiosity)
python scripts/catalog_selectors.py   # regenerates selector_registry.json

18 selectors across 8 routes on the demo app
CI runs this automatically and pushes the diff when the UI changes.

## 🛣️ Road‑map / open stories
| Story | Goal |
|-------|------|
| **B — Healing telemetry dashboard** | Tiny Flask page that aggregates heal logs (selector, confidence, frequency) across CI runs |
| **C — Polish & tech‑debt** | Unit tests for scorer, optional OCR visual healing, staging/prod base‑URL parameter |

## 🤝 Let’s talk
> I built this repo to showcase AI‑augmented QA engineering - mixing heuristics, open‑source tools and clean CI/CD practice.
> Let's connect on [Linkedin](https://www.linkedin.com/in/narek-petrosyan/).
> PRs and ideas are welcome!
