---
name: google-search-console-api
description: >-
  Autonomously retrieve and analyze Google Search Console data, diagnose
  organic search performance, and turn findings into website improvements.
  Use for natural-language requests in any language about a site's Google
  statistics, search traffic, clicks, impressions, CTR, rankings, indexing,
  traffic drops, SEO opportunities, or improving a website using real Google
  data. Also use for Search Console API setup, OAuth, properties, sitemaps, and
  URL Inspection. The user does not need to mention Search Console, GSC, an
  API, this skill, or any command explicitly.
---

# Google Search Console API

Treat the user's message as an outcome request. Operate `scripts/gsc.py` and all other internal tools yourself. Never ask the user to run a command, invoke the skill, inspect a file, calculate dates, or choose a report that the agent can handle.

Resolve bundled paths relative to this `SKILL.md` and run the CLI from the skill directory. Keep the website workspace as the source of project context and implementation files; do not assume it contains this skill's `scripts/` directory.

Do not mention the internal CLI unless the user asks for technical details or a narrowly scoped diagnostic requires it.

## Autonomous workflow

1. Inspect the current workspace for the website domain and relevant project instructions.
2. Run the setup check yourself:
   ```bash
   python3 scripts/gsc.py setup
   ```
3. If authorization is incomplete, follow [references/SETUP.md](references/SETUP.md). Take every permitted action yourself and pause only for Google sign-in, consent, an unknown business choice, or required access to a file outside the project boundary.
4. List Search Console properties yourself.
5. Match the property to the current website domain. Prefer an exact domain property, then an exact URL-prefix property. Ask the user only if multiple plausible properties remain after inspecting the workspace and request.
6. Follow [references/ANALYSIS.md](references/ANALYSIS.md) to select dates, retrieve reports, compare periods, diagnose causes, and prioritize opportunities.
7. Return the requested outcome, not a transcript of commands.

## When the user asks to improve the site

Use Search Console evidence to identify specific pages and changes. Then inspect the website source in the active workspace.

- Obey the website repository's instructions and approval gates.
- If the project requires a plan before edits, gather data first, present an evidence-backed plan, and wait for approval.
- After approval, make the approved changes yourself, run appropriate validation, and report what changed.
- If the website source is unavailable, provide a prioritized implementation brief with exact URLs, evidence, proposed changes, and success metrics.
- Do not interpret a broad request to improve the site as permission to submit a sitemap, change Search Console settings, or perform unrelated edits.

## Internal command reference

Run these commands yourself as needed:

```bash
# Setup and authorization
python3 scripts/gsc.py setup [--client-file PATH] [--authorize]
python3 scripts/gsc.py auth [--scope readonly|write] [--no-browser]
python3 scripts/gsc.py token-info

# Property discovery and overview
python3 scripts/gsc.py sites [--no-cache]
python3 scripts/gsc.py summary --site example.com [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD]

# Search Analytics
python3 scripts/gsc.py performance --site example.com --dimensions query
python3 scripts/gsc.py performance --site example.com --dimensions page
python3 scripts/gsc.py performance --site example.com --dimensions date,query --limit 1000
python3 scripts/gsc.py performance --site example.com --dimensions query,page --limit 25000
python3 scripts/gsc.py performance --site example.com --filter device:equals:MOBILE

# Sitemaps and index status
python3 scripts/gsc.py sitemaps --site example.com --action list
python3 scripts/gsc.py sitemaps --site example.com --action submit \
  --sitemap-url https://example.com/sitemap.xml --confirm
python3 scripts/gsc.py inspect --site example.com --url https://example.com/page
```

## Safety rules

- Use read-only scope by default.
- Do not add or remove Search Console properties.
- Do not delete sitemaps.
- Submit a sitemap only on explicit request, with write scope and `--confirm`.
- Do not promise indexing submission for ordinary pages. Search Console API provides URL Inspection, not Request Indexing.
- Never display credentials, authorization URLs containing sensitive parameters, access tokens, refresh tokens, or the contents of `config/client_secret.json` and `config/token.json`.
- Do not delete downloaded credentials without explicit permission.

## Reporting rules

- State exact comparison periods.
- Separate API facts, interpretations, recommendations, and implemented changes.
- Tie every major recommendation to a query, page, metric, or inspection result.
- Use relative site evidence instead of invented universal CTR or ranking benchmarks.
- Treat average position as an aggregate metric, not an exact rank for a specific user.
- Account for Google data finalization delay.
- End with the highest-impact next action, or with validation results when implementation is complete.
