---
name: google-search-console-api
description: >-
  Set up and use Google Search Console API with agent-led Google Cloud OAuth
  guidance, secure credential import, property discovery, Search Analytics,
  clicks, impressions, CTR, average position, sitemaps, and URL Inspection.
  Use when the user mentions Google Search Console API, GSC API, Google search
  queries or pages, index status, real Google SEO data, or needs help creating
  and authorizing Search Console OAuth credentials.
---

# Google Search Console API

Use `scripts/gsc.py` to set up access and work with Search Console. Use only the Python standard library. Keep OAuth files local to the skill and never expose credentials or tokens.

## Agent-led setup

Own the setup process. Do not begin by sending the user a generic Google Cloud checklist.

1. Read [references/SETUP.md](references/SETUP.md).
2. Run:
   ```bash
   python3 scripts/gsc.py setup
   ```
3. If credentials are missing, use available browser tools to open the exact Google Cloud page and guide the user through the visible interface. If browser control is unavailable, give one precise action at a time.
4. Pause only for actions Google requires the account owner to perform: sign-in, project choice when business context is unknown, consent configuration decisions, and OAuth approval.
5. Ask for the downloaded JSON file path or attachment. Never ask the user to paste its contents.
6. If the file is outside the allowed project boundary, request permission before accessing it.
7. Import and authorize:
   ```bash
   python3 scripts/gsc.py setup --client-file /path/to/client.json --authorize
   ```
8. Verify access:
   ```bash
   python3 scripts/gsc.py token-info
   python3 scripts/gsc.py sites
   ```

Default to `webmasters.readonly`. Request write scope only when the user explicitly asks to submit a sitemap.

## Required analysis order

1. List properties:
   ```bash
   python3 scripts/gsc.py sites
   ```
2. If the target is ambiguous, ask the user to choose a property.
3. Get the overview:
   ```bash
   python3 scripts/gsc.py summary --site example.com
   ```
4. Run only the detailed reports needed for the request.

## Commands

```bash
# Setup, OAuth, and token status
python3 scripts/gsc.py setup [--client-file PATH] [--authorize]
python3 scripts/gsc.py auth [--scope readonly|write] [--no-browser]
python3 scripts/gsc.py token-info

# Search Console properties
python3 scripts/gsc.py sites [--no-cache]

# Last 90 completed days by default
python3 scripts/gsc.py summary --site example.com [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD]

# Search Analytics
python3 scripts/gsc.py performance --site example.com --dimensions query
python3 scripts/gsc.py performance --site example.com --dimensions page
python3 scripts/gsc.py performance --site example.com --dimensions date,query --limit 1000
python3 scripts/gsc.py performance --site example.com --filter device:equals:MOBILE

# Sitemaps
python3 scripts/gsc.py sitemaps --site example.com --action list
python3 scripts/gsc.py sitemaps --site example.com --action submit \
  --sitemap-url https://example.com/sitemap.xml --confirm

# Google index status
python3 scripts/gsc.py inspect --site example.com --url https://example.com/page
```

## Safety rules

- Use read-only scope by default.
- Do not add or remove Search Console properties.
- Do not delete sitemaps.
- Submit a sitemap only on explicit request, with write scope and `--confirm`.
- Do not promise indexing submission for ordinary pages. Search Console API provides URL Inspection, not Request Indexing.
- Do not read or display `config/client_secret.json` or `config/token.json` except for narrowly scoped diagnostics. Never show their contents.
- Do not delete the original downloaded credentials file without explicit permission.

## Cache and reporting

- Store cache files under `cache/`.
- Cache `sites` for 24 hours and reports by request parameters.
- Use `--no-cache` when the user needs fresh data.
- Display at most 30 rows in the terminal; keep complete TSV or JSON results in the cache.
- State exact dates when comparing periods and account for Google data finalization delay.
- Separate API facts, interpretations, and recommendations.
- Do not treat average position as an exact ranking for a specific user.

Use the related `google-search-console` skill for deeper SEO analysis methodology when it is available.
