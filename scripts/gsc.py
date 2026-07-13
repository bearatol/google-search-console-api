#!/usr/bin/env python3
"""Dependency-free Google Search Console API CLI."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import http.server
import json
import os
import secrets
import socketserver
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import date, timedelta
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = SKILL_DIR / "config"
CACHE_DIR = SKILL_DIR / "cache"
CLIENT_FILE = CONFIG_DIR / "client_secret.json"
TOKEN_FILE = CONFIG_DIR / "token.json"
WEBMASTERS_API = "https://www.googleapis.com/webmasters/v3"
INSPECTION_API = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
API_LIBRARY_URL = (
    "https://console.cloud.google.com/apis/library/searchconsole.googleapis.com"
)
AUTH_OVERVIEW_URL = "https://console.cloud.google.com/auth/overview"
OAUTH_CLIENTS_URL = "https://console.cloud.google.com/auth/clients"
SCOPES = {
    "readonly": "https://www.googleapis.com/auth/webmasters.readonly",
    "write": "https://www.googleapis.com/auth/webmasters",
}
MAX_DISPLAY_ROWS = 30


class GSCError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as stream:
            value = json.load(stream)
    except FileNotFoundError as exc:
        raise GSCError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GSCError(f"Invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GSCError(f"Expected a JSON object: {path}")
    return value


def save_secret_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    os.chmod(temporary, 0o600)
    temporary.replace(path)
    os.chmod(path, 0o600)


def validate_client_payload(payload: dict[str, Any]) -> dict[str, Any]:
    config = payload.get("installed")
    if not isinstance(config, dict):
        raise GSCError(
            "OAuth JSON has no 'installed' section. "
            "Create an OAuth Client ID of type Desktop app."
        )
    if not config.get("client_id") or not config.get("client_secret"):
        raise GSCError("OAuth JSON has no client_id or client_secret")
    return config


def client_config() -> dict[str, Any]:
    return validate_client_payload(load_json(CLIENT_FILE))


def install_client_file(source: Path) -> None:
    payload = load_json(source.expanduser())
    validate_client_payload(payload)
    save_secret_json(CLIENT_FILE, payload)
    print(f"OAuth client credentials imported securely: {CLIENT_FILE}")
    print("The original downloaded file was not deleted.")


def command_setup(args: argparse.Namespace) -> None:
    if args.client_file:
        install_client_file(args.client_file)

    if not CLIENT_FILE.exists():
        print("OAuth client credentials: missing")
        print("\nNext steps:")
        print(f"1. Enable Google Search Console API: {API_LIBRARY_URL}")
        print(f"2. Configure Google Auth Platform: {AUTH_OVERVIEW_URL}")
        print(f"3. Create a Desktop app OAuth client: {OAUTH_CLIENTS_URL}")
        print("4. Download its JSON file.")
        print(
            "5. Run: python3 scripts/gsc.py setup "
            "--client-file /path/to/file.json --authorize"
        )
        return

    client_config()
    print(f"OAuth client credentials: ready ({CLIENT_FILE})")
    if args.authorize:
        oauth_authorize(args.scope, args.no_browser, args.timeout)
        return

    if TOKEN_FILE.exists():
        token = load_json(TOKEN_FILE)
        print(f"OAuth token: {'ready' if token.get('refresh_token') else 'incomplete'}")
    else:
        print("OAuth token: missing")
    print("Next step: python3 scripts/gsc.py auth")


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
    retries: int = 2,
) -> dict[str, Any]:
    request_headers = {"Accept": "application/json", **(headers or {})}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        request_headers["Content-Type"] = "application/json; charset=utf-8"
    elif form_body is not None:
        data = urllib.parse.urlencode(form_body).encode("utf-8")
        request_headers["Content-Type"] = "application/x-www-form-urlencoded"

    for attempt in range(retries + 1):
        request = urllib.request.Request(
            url, data=data, headers=request_headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in {429, 500, 502, 503, 504} and attempt < retries:
                retry_after = exc.headers.get("Retry-After")
                wait = min(int(retry_after), 10) if retry_after and retry_after.isdigit() else 2 ** attempt
                time.sleep(wait)
                continue
            try:
                message = json.loads(body).get("error", {}).get("message", body)
            except json.JSONDecodeError:
                message = body
            raise GSCError(f"Google API HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise GSCError(f"Network error: {exc.reason}") from exc
    raise GSCError("Google API did not respond after retries")


def token_is_fresh(token: dict[str, Any]) -> bool:
    return bool(token.get("access_token")) and float(token.get("expires_at", 0)) > time.time() + 60


def refresh_access_token(token: dict[str, Any]) -> dict[str, Any]:
    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise GSCError("No refresh_token. Run authorization again")
    client = client_config()
    response = request_json(
        TOKEN_ENDPOINT,
        method="POST",
        form_body={
            "client_id": str(client["client_id"]),
            "client_secret": str(client["client_secret"]),
            "refresh_token": str(refresh_token),
            "grant_type": "refresh_token",
        },
    )
    token.update(response)
    token["refresh_token"] = refresh_token
    token["expires_at"] = time.time() + int(response.get("expires_in", 3600))
    save_secret_json(TOKEN_FILE, token)
    return token


def access_token() -> str:
    token = load_json(TOKEN_FILE)
    if not token_is_fresh(token):
        token = refresh_access_token(token)
    value = token.get("access_token")
    if not value:
        raise GSCError("token.json has no access_token")
    return str(value)


def api_request(
    url: str, *, method: str = "GET", body: dict[str, Any] | None = None
) -> dict[str, Any]:
    return request_json(
        url,
        method=method,
        headers={"Authorization": f"Bearer {access_token()}"},
        json_body=body,
    )


class OAuthCallback(http.server.BaseHTTPRequestHandler):
    result: dict[str, str] = {}
    expected_state = ""
    event = threading.Event()

    def do_GET(self) -> None:  # noqa: N802
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        state = query.get("state", [""])[0]
        if state != self.expected_state:
            type(self).result = {"error": "state_mismatch"}
            status = 400
            message = "OAuth state mismatch. Return to the terminal."
        elif query.get("error"):
            type(self).result = {"error": query["error"][0]}
            status = 400
            message = "Authorization was denied. Return to the terminal."
        else:
            type(self).result = {"code": query.get("code", [""])[0]}
            status = 200
            message = "Authorization is complete. You can close this tab."
        payload = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        self.event.set()

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def oauth_authorize(scope_name: str, no_browser: bool, timeout: int) -> None:
    client = client_config()
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)

    OAuthCallback.result = {}
    OAuthCallback.expected_state = state
    OAuthCallback.event = threading.Event()
    with socketserver.TCPServer(("127.0.0.1", 0), OAuthCallback) as server:
        port = server.server_address[1]
        redirect_uri = f"http://127.0.0.1:{port}/oauth2callback"
        params = {
            "client_id": str(client["client_id"]),
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": SCOPES[scope_name],
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        auth_url = AUTH_ENDPOINT + "?" + urllib.parse.urlencode(params)
        print("Open this URL in a browser:\n")
        print(auth_url)
        print(f"\nWaiting up to {timeout} seconds for the callback...")
        if not no_browser:
            webbrowser.open(auth_url)
        server.timeout = 1
        deadline = time.time() + timeout
        while not OAuthCallback.event.is_set() and time.time() < deadline:
            server.handle_request()

    if not OAuthCallback.event.is_set():
        raise GSCError("OAuth callback timed out")
    if OAuthCallback.result.get("error"):
        raise GSCError(f"OAuth error: {OAuthCallback.result['error']}")
    code = OAuthCallback.result.get("code")
    if not code:
        raise GSCError("Google did not return an authorization code")

    token = request_json(
        TOKEN_ENDPOINT,
        method="POST",
        form_body={
            "code": code,
            "client_id": str(client["client_id"]),
            "client_secret": str(client["client_secret"]),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": verifier,
        },
    )
    token["expires_at"] = time.time() + int(token.get("expires_in", 3600))
    token["scope_mode"] = scope_name
    save_secret_json(TOKEN_FILE, token)
    print(f"OAuth configured. Scope: {scope_name}. Token: {TOKEN_FILE}")


def cache_path(kind: str, key: Any, suffix: str = "json") -> Path:
    digest = hashlib.sha256(
        json.dumps(key, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    return CACHE_DIR / kind / f"{digest}.{suffix}"


def cached_json(path: Path, ttl_hours: int) -> dict[str, Any] | None:
    if not path.exists() or not path.stat().st_size:
        return None
    if time.time() - path.stat().st_mtime > ttl_hours * 3600:
        return None
    return load_json(path)


def save_cache(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def fetch_sites(no_cache: bool = False) -> tuple[dict[str, Any], Path]:
    path = cache_path("sites", "all")
    payload = None if no_cache else cached_json(path, 24)
    if payload is None:
        payload = api_request(f"{WEBMASTERS_API}/sites")
        save_cache(path, payload)
    return payload, path


def site_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries = payload.get("siteEntry", [])
    return entries if isinstance(entries, list) else []


def resolve_site(value: str, no_cache: bool = False) -> str:
    payload, _ = fetch_sites(no_cache)
    sites = [str(item.get("siteUrl", "")) for item in site_entries(payload)]
    if value in sites:
        return value
    normalized = value.lower().removeprefix("sc-domain:").strip().rstrip("/")
    parsed_value = urllib.parse.urlparse(
        normalized if "://" in normalized else "//" + normalized
    )
    domain = parsed_value.hostname or normalized
    exact_domain = f"sc-domain:{domain}"
    if exact_domain in sites:
        return exact_domain
    matches = []
    for site in sites:
        parsed = urllib.parse.urlparse(site if "://" in site else "//" + site)
        host = (parsed.hostname or "").lower()
        if host == domain or host.removeprefix("www.") == domain.removeprefix("www."):
            matches.append(site)
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise GSCError(f"No property found for '{value}'. List available properties")
    raise GSCError(f"Multiple properties found for '{value}': {', '.join(matches)}")


def default_dates(date_from: str | None, date_to: str | None) -> tuple[str, str]:
    end = date.fromisoformat(date_to) if date_to else date.today() - timedelta(days=3)
    start = date.fromisoformat(date_from) if date_from else end - timedelta(days=89)
    if start > end:
        raise GSCError("date-from cannot be later than date-to")
    return start.isoformat(), end.isoformat()


def parse_filters(values: list[str]) -> list[dict[str, Any]]:
    filters = []
    for value in values:
        parts = value.split(":", 2)
        if len(parts) != 3 or not all(parts):
            raise GSCError(
                f"Invalid filter '{value}'. Format: dimension:operator:expression"
            )
        filters.append(
            {"dimension": parts[0], "operator": parts[1], "expression": parts[2]}
        )
    return filters


def performance_body(args: argparse.Namespace) -> dict[str, Any]:
    start, end = default_dates(args.date_from, args.date_to)
    dimensions = [item.strip() for item in args.dimensions.split(",") if item.strip()]
    body: dict[str, Any] = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "type": args.search_type,
        "rowLimit": args.limit,
        "startRow": args.start_row,
        "dataState": args.data_state,
        "aggregationType": args.aggregation,
    }
    filters = parse_filters(args.filter)
    if filters:
        body["dimensionFilterGroups"] = [{"groupType": "and", "filters": filters}]
    return body


def query_performance(site: str, body: dict[str, Any]) -> dict[str, Any]:
    encoded = urllib.parse.quote(site, safe="")
    return api_request(
        f"{WEBMASTERS_API}/sites/{encoded}/searchAnalytics/query",
        method="POST",
        body=body,
    )


def write_performance_tsv(
    path: Path, payload: dict[str, Any], dimensions: list[str]
) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow([*dimensions, "clicks", "impressions", "ctr", "position"])
        for row in rows:
            keys = row.get("keys", [])
            writer.writerow(
                [
                    *keys,
                    row.get("clicks", 0),
                    row.get("impressions", 0),
                    f"{float(row.get('ctr', 0)):.6f}",
                    f"{float(row.get('position', 0)):.3f}",
                ]
            )
    return len(rows)


def print_file_head(path: Path, limit: int = MAX_DISPLAY_ROWS) -> None:
    with path.open(encoding="utf-8") as stream:
        for index, line in enumerate(stream):
            if index >= limit:
                break
            print(line.rstrip("\n"))
    with path.open(encoding="utf-8") as stream:
        total = sum(1 for _ in stream)
    if total > limit:
        print(f"... {total - limit} more rows")
    print(f"Full data: {path}")


def command_sites(args: argparse.Namespace) -> None:
    payload, path = fetch_sites(args.no_cache)
    print("site_url\tpermission")
    for item in site_entries(payload)[:MAX_DISPLAY_ROWS]:
        print(f"{item.get('siteUrl', '')}\t{item.get('permissionLevel', '')}")
    print(f"Full data: {path}")


def command_performance(args: argparse.Namespace) -> None:
    site = resolve_site(args.site, args.no_cache)
    body = performance_body(args)
    json_path = cache_path("performance", {"site": site, "body": body})
    payload = None if args.no_cache else cached_json(json_path, 24)
    if payload is None:
        payload = query_performance(site, body)
        save_cache(json_path, payload)
    dimensions = body["dimensions"]
    tsv_path = json_path.with_suffix(".tsv")
    rows = write_performance_tsv(tsv_path, payload, dimensions)
    print(f"Property: {site}")
    print(f"Period: {body['startDate']} to {body['endDate']}; rows: {rows}")
    print_file_head(tsv_path)


def list_sitemaps(site: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(site, safe="")
    return api_request(f"{WEBMASTERS_API}/sites/{encoded}/sitemaps")


def command_sitemaps(args: argparse.Namespace) -> None:
    site = resolve_site(args.site, args.no_cache)
    if args.action == "submit":
        if not args.sitemap_url or not args.confirm:
            raise GSCError("submit requires --sitemap-url and --confirm")
        encoded_site = urllib.parse.quote(site, safe="")
        encoded_feed = urllib.parse.quote(args.sitemap_url, safe="")
        api_request(
            f"{WEBMASTERS_API}/sites/{encoded_site}/sitemaps/{encoded_feed}",
            method="PUT",
        )
        print(f"Sitemap submitted: {args.sitemap_url}")
        return
    path = cache_path("sitemaps", site)
    payload = None if args.no_cache else cached_json(path, 24)
    if payload is None:
        payload = list_sitemaps(site)
        save_cache(path, payload)
    print("path\ttype\tlast_submitted\tis_pending\terrors\twarnings")
    for item in payload.get("sitemap", [])[:MAX_DISPLAY_ROWS]:
        print(
            "\t".join(
                str(item.get(key, ""))
                for key in (
                    "path",
                    "type",
                    "lastSubmitted",
                    "isPending",
                    "errors",
                    "warnings",
                )
            )
        )
    print(f"Full data: {path}")


def command_inspect(args: argparse.Namespace) -> None:
    site = resolve_site(args.site, args.no_cache)
    body = {
        "inspectionUrl": args.url,
        "siteUrl": site,
        "languageCode": args.language,
    }
    path = cache_path("inspection", body)
    payload = None if args.no_cache else cached_json(path, 24)
    if payload is None:
        payload = api_request(INSPECTION_API, method="POST", body=body)
        save_cache(path, payload)
    result = payload.get("inspectionResult", {})
    index = result.get("indexStatusResult", {})
    print(f"URL: {args.url}")
    print(f"Verdict: {index.get('verdict', '-')}")
    print(f"Coverage: {index.get('coverageState', '-')}")
    print(f"Robots: {index.get('robotsTxtState', '-')}")
    print(f"Indexing: {index.get('indexingState', '-')}")
    print(f"Google canonical: {index.get('googleCanonical', '-')}")
    print(f"User canonical: {index.get('userCanonical', '-')}")
    print(f"Last crawl: {index.get('lastCrawlTime', '-')}")
    print(f"Full data: {path}")


def command_summary(args: argparse.Namespace) -> None:
    site = resolve_site(args.site, args.no_cache)
    start, end = default_dates(args.date_from, args.date_to)
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": [],
        "type": "web",
        "rowLimit": 1,
        "dataState": "final",
        "aggregationType": "byProperty",
    }
    key = {"site": site, "body": body}
    path = cache_path("summary", key)
    payload = None if args.no_cache else cached_json(path, 24)
    if payload is None:
        performance = query_performance(site, body)
        sitemaps = list_sitemaps(site)
        payload = {"site": site, "performance": performance, "sitemaps": sitemaps}
        save_cache(path, payload)
    row = (payload.get("performance", {}).get("rows") or [{}])[0]
    sitemap_rows = payload.get("sitemaps", {}).get("sitemap", [])
    print(f"=== Google Search Console: {site} ===")
    print(f"Period: {start} to {end}")
    print(f"Clicks: {row.get('clicks', 0)}")
    print(f"Impressions: {row.get('impressions', 0)}")
    print(f"CTR: {float(row.get('ctr', 0)) * 100:.2f}%")
    print(f"Average position: {float(row.get('position', 0)):.2f}")
    print(f"Sitemaps: {len(sitemap_rows)}")
    print(f"Sitemap errors: {sum(int(item.get('errors', 0)) for item in sitemap_rows)}")
    print(f"Full data: {path}")


def command_token_info(_args: argparse.Namespace) -> None:
    token = load_json(TOKEN_FILE)
    expires_at = float(token.get("expires_at", 0))
    print(f"Token file: {TOKEN_FILE}")
    print(f"Scope mode: {token.get('scope_mode', 'unknown')}")
    print(f"Has refresh token: {bool(token.get('refresh_token'))}")
    print(f"Expires at Unix: {int(expires_at)}")
    print(f"Fresh: {token_is_fresh(token)}")


def add_site_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--site", required=True, help="Property URL, sc-domain, or domain")
    parser.add_argument("--no-cache", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    setup = commands.add_parser("setup", help="Guide and verify OAuth setup")
    setup.add_argument("--client-file", type=Path)
    setup.add_argument("--authorize", action="store_true")
    setup.add_argument("--scope", choices=SCOPES, default="readonly")
    setup.add_argument("--no-browser", action="store_true")
    setup.add_argument("--timeout", type=int, default=180)
    setup.set_defaults(handler=command_setup)

    auth = commands.add_parser("auth", help="Configure OAuth")
    auth.add_argument("--scope", choices=SCOPES, default="readonly")
    auth.add_argument("--no-browser", action="store_true")
    auth.add_argument("--timeout", type=int, default=180)
    auth.set_defaults(handler=lambda args: oauth_authorize(args.scope, args.no_browser, args.timeout))

    token_info = commands.add_parser("token-info", help="Show token status")
    token_info.set_defaults(handler=command_token_info)

    sites = commands.add_parser("sites", help="List Search Console properties")
    sites.add_argument("--no-cache", action="store_true")
    sites.set_defaults(handler=command_sites)

    summary = commands.add_parser("summary", help="Show an SEO performance summary")
    add_site_argument(summary)
    summary.add_argument("--date-from")
    summary.add_argument("--date-to")
    summary.set_defaults(handler=command_summary)

    performance = commands.add_parser("performance", help="Search Analytics")
    add_site_argument(performance)
    performance.add_argument("--date-from")
    performance.add_argument("--date-to")
    performance.add_argument("--dimensions", default="query")
    performance.add_argument(
        "--search-type",
        choices=("web", "image", "video", "news", "discover", "googleNews"),
        default="web",
    )
    performance.add_argument("--limit", type=int, choices=range(1, 25001), default=1000)
    performance.add_argument("--start-row", type=int, default=0)
    performance.add_argument("--filter", action="append", default=[])
    performance.add_argument("--data-state", choices=("final", "all"), default="final")
    performance.add_argument(
        "--aggregation", choices=("auto", "byPage", "byProperty"), default="auto"
    )
    performance.set_defaults(handler=command_performance)

    sitemaps = commands.add_parser("sitemaps", help="Sitemap")
    add_site_argument(sitemaps)
    sitemaps.add_argument("--action", choices=("list", "submit"), default="list")
    sitemaps.add_argument("--sitemap-url")
    sitemaps.add_argument("--confirm", action="store_true")
    sitemaps.set_defaults(handler=command_sitemaps)

    inspect = commands.add_parser("inspect", help="URL Inspection")
    add_site_argument(inspect)
    inspect.add_argument("--url", required=True)
    inspect.add_argument("--language", default="ru-RU")
    inspect.set_defaults(handler=command_inspect)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        args.handler(args)
        return 0
    except (GSCError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Operation cancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
