## Quick context

This repository extracts news from Finam, finds tickers mentioned in each article, then queries MOEX (ISS) for prices at the news time, +1 trading day and +7 days and writes results to `finam_news.csv`.

Key entry points:
- `main.py` — orchestration: loads URLs, calls parser and price lookup, writes CSV
- `gets_urls.py` — downloads Finam sitemap (uses `xmltodict`) and filters by `<lastmod>`
- `finam_parser.py` — uses Playwright (sync API) to render pages and extract tickers from `div[data-id='quote-info']`
- `moscow.py` — queries MOEX ISS endpoints to get intraday/close prices
- `schemas.py` — small dataclasses (`NewsUrl`, `NewsItem`) used across modules

## Concrete patterns and expectations for code edits

- Keep messages/logging simple: the project uses print statements and short emojis for progress (see `main.py`). Follow the same style for new scripts.
- Network calls are synchronous and blocking. Expect small `sleep()` delays (e.g., `time.sleep(2)` in `main.py`) to avoid rate limits.
- Timestamps: `finam_parser.parse_finam_news` extracts datetime from the URL using the pattern `YYYYMMDD-HHMM`. If you need to change parsing, update that regex there.
- Playwright usage: `finam_parser` uses `playwright.sync_api.sync_playwright()` and currently launches with `headless=False` (intended for local debugging). For CI or headless runs, set `chromium.launch(headless=True)` and call `playwright install` first.
- Sitemap logic: `gets_urls.get_news_urls` decodes BOMs and filters by `lastmod`. It currently selects items older than 9 days (`timedelta(days=9)`). Adjust the cutoff only if you intentionally change the window of interest.

## Important integration details

- Dependencies required at runtime (discoverable from imports): `playwright`, `requests`, `xmltodict`, `pandas` (used in `test.py`), `python>=3.9` for `list[...]` type hints.
- Playwright needs browser binaries installed: run `python -m pip install playwright` then `python -m playwright install` before running `finam_parser` locally or in CI.
- MOEX ISS endpoints are used directly (no API key). Expect occasional missing rows; `moscow.py` implements a simple `find_nearest_trade_day` to search forwards up to 5 days for a close price.

## Examples the assistant should use when proposing edits

- When extracting tickers: point at `finam_parser.py` — the code filters `a[href*='/quote/moex/']` and extracts the ticker by regex `/quote/moex/([a-z0-9]+)/`.
- When changing output format: `main.py` writes header `['text','ticker','price_news','price_1d','price_7d']` — preserve this order unless you update `README`/consumers.
- When changing sitemap filtering: edit `gets_urls.get_news_urls` and be explicit about timezone/`lastmod` format `%Y-%m-%d`.

## Recommended developer workflows (how to run things locally)

- Install dependencies (minimum):
  - `python -m pip install requests xmltodict playwright` 
  - `python -m playwright install` (downloads browser binaries)
- Run the main extraction locally: `python main.py`. Expect Playwright to open a Chromium window if `headless=False`.

## Testing and CI notes

- There are no formal tests yet. Prefer small unit tests that mock `requests` and the Playwright page API for `finam_parser`. For MOEX calls, mock the JSON responses from `iss.moex.com`.
- If adding CI, run Playwright with headless mode and avoid downloading browsers on every run by caching the Playwright installation.

## Safety / failure modes to call out to the user

- Network failures are common: `requests` calls may raise `requests.exceptions.RequestException`. The code currently relies on try/except around per-news processing in `main.py` — preserve that approach for resilience.
- Playwright timeouts / selector changes can silently break ticker extraction. If `quote-info` stops matching, examine `some.html` (the parser writes page content there for debugging).

## Files to inspect when diagnosing problems

- `main.py`, `finam_parser.py`, `gets_urls.py`, `moscow.py`, `schemas.py`, `some.html`, `finam_news.csv`

---

If you'd like, I can:
- add a short `requirements.txt` listing discovered dependencies,
- switch `finam_parser` to `headless=True` behind a `env` flag for CI, or
- add a tiny pytest-based test that mocks `requests` for `gets_urls.get_news_urls`.

Please tell me which of the above you'd like next or point out any missing details I should add. 
