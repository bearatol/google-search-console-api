# Google Search Console API Skill

An autonomous AI-agent skill for retrieving Google Search Console data, diagnosing organic search performance, and turning the findings into concrete website improvements.

[![skills.sh](https://skills.sh/b/bearatol/google-search-console-api)](https://skills.sh/bearatol/google-search-console-api)

## Ask for an outcome

After installation, the user does not need to name the skill, operate a CLI, or understand the Search Console API. They can make a normal request such as:

```text
Show me my site's Google search statistics and explain what I should improve.
```

```text
Find out why my organic traffic dropped and fix what you can in the website.
```

```text
Find pages that are close to the first page of Google and turn them into growth opportunities.
```

The agent invokes the skill automatically and operates its internal tools itself.

## What the agent does

1. Checks whether Search Console access is ready.
2. Leads the one-time Google Cloud and OAuth setup when needed.
3. Discovers the relevant Search Console property and matches it to the current website.
4. Retrieves current and previous-period data by query, page, date, and device.
5. Identifies losses, low-CTR opportunities, near-page-one rankings, index issues, and competing pages.
6. Connects the findings to specific website pages and source files.
7. Recommends improvements or, when the user asks for implementation, follows the website project's approval rules and makes the approved changes.
8. Reports evidence, actions taken, validation results, and remaining opportunities.

The agent does not ask the user to run Python commands. It asks for help only when Google requires the account owner to sign in or approve consent, when multiple properties remain genuinely ambiguous, or when the website project requires approval before file changes.

## Installation

```bash
npx skills add bearatol/google-search-console-api
```

Skills installed from the public GitHub repository can be discovered automatically by [skills.sh](https://skills.sh/).

## Capabilities

- Agent-led Google Cloud and OAuth 2.0 setup for a Desktop app.
- Search Console property discovery.
- Clicks, impressions, CTR, and average-position analysis.
- Query, page, date, device, and combined-dimension reports.
- Period-over-period diagnostics.
- URL Inspection for priority pages.
- Sitemap listing and guarded submission.
- Local caching without third-party Python dependencies.
- Evidence-backed SEO recommendations and implementation handoff.

## Authorization boundary

Google requires the account owner to complete sign-in and approve the OAuth consent screen. The agent handles the surrounding setup, opens the relevant pages when browser control is available, and pauses only for the required confirmation.

Credentials and tokens remain local, are excluded from Git, and are never printed in responses.

## Internal agent tooling

The bundled dependency-free CLI is an implementation detail used by the agent. It supports setup, authorization, property discovery, performance reports, sitemaps, and URL Inspection:

```bash
python3 scripts/gsc.py --help
```

See [references/SETUP.md](references/SETUP.md) for authorization handling and [references/ANALYSIS.md](references/ANALYSIS.md) for the analysis and improvement methodology.

Python 3.10 or newer is required.

## Safety

- Read-only Search Console access is requested by default.
- `config/client_secret.json`, `config/token.json`, and `cache/` are excluded from Git.
- Credentials and tokens are stored with `0600` permissions.
- Sitemap submission requires write access and an explicit confirmation flag.
- URL Inspection checks index status; it cannot request indexing for ordinary pages.
- Website files are changed only when the user requested implementation and the active project rules allow it.

## Development

```bash
python3 -B -m unittest discover -s tests -v
```

GitHub Actions runs the test suite on supported Python versions.

## Releasing

The repository is the source of truth for skills.sh. Skills are installed directly from the default GitHub branch; skills.sh does not provide a separate version-upload endpoint.

Create a semantic version tag to publish a GitHub Release:

```bash
git switch main
git pull --ff-only
git tag v1.0.0
git push origin v1.0.0
```

The release workflow validates the tag, confirms that its commit is on `main`, runs the complete reusable CI workflow, verifies installation through Skills CLI, and creates a GitHub Release with generated notes. If any check fails, no release is created.

Users install or update the current skill through the GitHub source:

```bash
npx skills add bearatol/google-search-console-api
npx skills update google-search-console-api -y
```

If a release is faulty, keep its tag immutable, fix `main`, and publish a new patch release. Mark the faulty release as superseded in its notes when useful. Do not move, delete, or reuse a published version tag.

## License

[MIT](LICENSE)
