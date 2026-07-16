# Agent Playbook: Google Search Console OAuth Setup

Use this playbook when `python3 scripts/gsc.py setup` reports missing or invalid credentials.

## Operating rules

- Take the setup as far as available tools and permissions allow.
- If browser control is available, open the relevant Google Cloud page and guide the user in context.
- Ask for one user action at a time. Do not send the user away with a long generic checklist.
- Never ask for a Google password, verification code, access token, refresh token, client ID, or client secret in chat.
- Never display the contents of an OAuth credentials or token file.
- The user must personally sign in to Google and approve the OAuth consent screen.
- Ask for permission before reading or copying a downloaded file outside the current project boundary.

## 1. Check readiness

Run:

```bash
python3 scripts/gsc.py setup
```

If both credentials and a token are ready, continue with `sites`. Otherwise follow the reported next action.

## 2. Create Google Cloud credentials

Open these pages as needed:

- Search Console API Library: https://console.cloud.google.com/apis/library/searchconsole.googleapis.com
- Google Auth Platform overview: https://console.cloud.google.com/auth/overview
- OAuth clients: https://console.cloud.google.com/auth/clients

Guide the user through the current Google Cloud interface:

1. Select an existing project or create one.
2. Enable **Google Search Console API**.
3. Configure Google Auth Platform if prompted:
   - provide the required app information;
   - choose the appropriate audience;
   - add the user's Google account as a test user when the app is in testing mode;
   - add only the minimum Search Console scope needed.
4. Open **Clients** and create an OAuth client.
5. Choose application type **Desktop app**.
6. Download the generated JSON file.

Google Cloud labels can change. Inspect the visible interface and adapt, while preserving the required outcome: an enabled Search Console API and an OAuth client of type Desktop app.

## 3. Import credentials safely

Ask the user for the downloaded file path or attached file. Do not ask them to paste its contents.

Then run:

```bash
python3 scripts/gsc.py setup --client-file /path/to/downloaded-client.json
```

The command validates the JSON structure and stores it as `config/client_secret.json` with `0600` permissions. It does not delete the original download. Offer to help remove the original only after successful import and only with explicit permission.

## 4. Authorize access

For normal reporting, request read-only access:

```bash
python3 scripts/gsc.py auth
```

The command starts a temporary callback server on `127.0.0.1`, opens Google's authorization page in the system browser, and stores the resulting token locally.

The user must personally:

1. choose the Google account that has Search Console access;
2. review the requested scope;
3. approve or reject access.

If the browser cannot be opened automatically, run:

```bash
python3 scripts/gsc.py auth --no-browser
```

Open the printed URL in a browser on the same computer. Do not use the deprecated manual copy-and-paste OAuth flow.

Request write access only when the user explicitly asks to submit a sitemap:

```bash
python3 scripts/gsc.py auth --scope write
```

## 5. Verify access

Run:

```bash
python3 scripts/gsc.py token-info
python3 scripts/gsc.py sites
```

If the expected property is missing, ask which Google account owns it and verify that the account has Search Console permission.

## Troubleshooting

- **`redirect_uri_mismatch`**: recreate the OAuth client as a **Desktop app**. Do not use a Web application client.
- **Access blocked or denied**: verify the OAuth audience and add the account as a test user when the app is in testing mode.
- **API disabled / HTTP 403**: enable Google Search Console API in the selected Cloud project.
- **No refresh token**: authorize again and approve consent; revoke the previous grant first if Google does not issue a new refresh token.
- **Callback timeout**: rerun authorization and complete the browser consent before the timeout expires.

## API references

- Search Console API: https://developers.google.com/webmaster-tools
- Search Console authorization: https://developers.google.com/webmaster-tools/v1/how-tos/authorizing
- OAuth for Desktop apps: https://developers.google.com/identity/protocols/oauth2/native-app
- Search Analytics: https://developers.google.com/webmaster-tools/v1/searchanalytics/query
- URL Inspection: https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect

Search Console API can inspect ordinary pages but cannot request their indexing. Google Indexing API is limited to supported content types such as job postings and livestream events.
