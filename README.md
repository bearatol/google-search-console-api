# Google Search Console API Skill

An AI-agent skill for setting up Google Search Console API access and analyzing real search performance data.

## AI-first usage

Install the skill, then ask your AI agent:

```text
Use $google-search-console-api to set up Search Console access and analyze my website.
```

The agent will:

1. Check whether Google OAuth credentials and a token are already configured.
2. Open the relevant Google Cloud pages when browser control is available, or give one precise instruction at a time.
3. Validate and securely import the downloaded Desktop app credentials file.
4. Start the OAuth flow in the system browser.
5. Verify access, list available Search Console properties, and continue with the requested analysis.

Google requires the account owner to complete sign-in, choose or create the Cloud project, and approve the consent screen. The agent handles the surrounding setup and clearly pauses only for these required user actions.

## Installation

```bash
npx skills add bearatol/google-search-console-api
```

Skills installed from the public GitHub repository can be discovered automatically by [skills.sh](https://skills.sh/).

## What it can do

- Guide Google Cloud and OAuth 2.0 setup for a Desktop app.
- List accessible Search Console properties.
- Summarize clicks, impressions, CTR, and average position.
- Report by query, page, date, device, and other dimensions.
- Inspect a URL's Google index status.
- List sitemaps and submit one after explicit confirmation.
- Cache results locally without third-party Python dependencies.

## Agent-led setup command

Check the current setup:

```bash
python3 scripts/gsc.py setup
```

After downloading the Desktop app OAuth JSON, the agent can securely import it and immediately start authorization:

```bash
python3 scripts/gsc.py setup \
  --client-file /path/to/downloaded-client.json \
  --authorize
```

The imported credentials and token are stored with `0600` permissions. The original downloaded file is not deleted automatically.

See [references/SETUP.md](references/SETUP.md) for the complete agent playbook and manual fallback.

## Examples

```bash
python3 scripts/gsc.py sites
python3 scripts/gsc.py summary --site example.com
python3 scripts/gsc.py performance --site example.com --dimensions query
python3 scripts/gsc.py performance --site example.com --dimensions page
python3 scripts/gsc.py inspect --site example.com --url https://example.com/page
```

Show all commands:

```bash
python3 scripts/gsc.py --help
```

Python 3.10 or newer is required. The CLI uses only the Python standard library.

## Safety

- Read-only Search Console access is requested by default.
- `config/client_secret.json`, `config/token.json`, and `cache/` are excluded from Git.
- Credentials and tokens are never printed to the terminal.
- Sitemap submission requires write access and an explicit `--confirm` flag.
- URL Inspection checks index status; it cannot request indexing for ordinary pages.

## Development

Run the tests:

```bash
python3 -B -m unittest discover -s tests -v
```

GitHub Actions runs the test suite on supported Python versions.

## License

[MIT](LICENSE)
