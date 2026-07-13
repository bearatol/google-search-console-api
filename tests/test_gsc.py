import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "gsc.py"
SPEC = importlib.util.spec_from_file_location("gsc", MODULE_PATH)
gsc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(gsc)


class GSCTest(unittest.TestCase):
    def test_default_dates_uses_ninety_day_inclusive_window(self):
        start, end = gsc.default_dates("2026-01-01", "2026-03-31")
        self.assertEqual((start, end), ("2026-01-01", "2026-03-31"))

    def test_default_dates_rejects_reverse_range(self):
        with self.assertRaises(gsc.GSCError):
            gsc.default_dates("2026-04-01", "2026-03-31")

    def test_parse_filters_preserves_colons_in_expression(self):
        result = gsc.parse_filters(["page:contains:https://toolkitch.ru/a"])
        self.assertEqual(result[0]["expression"], "https://toolkitch.ru/a")

    def test_parse_filters_rejects_invalid_value(self):
        with self.assertRaises(gsc.GSCError):
            gsc.parse_filters(["device:MOBILE"])

    @mock.patch.object(gsc, "fetch_sites")
    def test_resolve_site_prefers_domain_property(self, fetch_sites):
        fetch_sites.return_value = (
            {
                "siteEntry": [
                    {"siteUrl": "sc-domain:toolkitch.ru"},
                    {"siteUrl": "https://example.com/"},
                ]
            },
            Path("cache.json"),
        )
        self.assertEqual(gsc.resolve_site("toolkitch.ru"), "sc-domain:toolkitch.ru")

    @mock.patch.object(gsc, "fetch_sites")
    def test_resolve_site_accepts_property_url_without_trailing_slash(self, fetch_sites):
        fetch_sites.return_value = (
            {"siteEntry": [{"siteUrl": "https://toolkitch.ru/"}]},
            Path("cache.json"),
        )
        self.assertEqual(
            gsc.resolve_site("https://toolkitch.ru"), "https://toolkitch.ru/"
        )

    def test_write_performance_tsv(self):
        payload = {
            "rows": [
                {
                    "keys": ["seo запрос"],
                    "clicks": 3,
                    "impressions": 25,
                    "ctr": 0.12,
                    "position": 8.5,
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.tsv"
            count = gsc.write_performance_tsv(path, payload, ["query"])
            content = path.read_text(encoding="utf-8")
        self.assertEqual(count, 1)
        self.assertIn("query\tclicks\timpressions\tctr\tposition", content)
        self.assertIn("seo запрос\t3\t25\t0.120000\t8.500", content)

    @mock.patch.object(gsc, "request_json")
    @mock.patch.object(gsc, "save_secret_json")
    @mock.patch.object(gsc, "client_config")
    def test_refresh_token_is_preserved(self, client_config, save_secret_json, request_json):
        client_config.return_value = {"client_id": "id", "client_secret": "secret"}
        request_json.return_value = {"access_token": "new", "expires_in": 3600}
        token = gsc.refresh_access_token({"refresh_token": "refresh"})
        self.assertEqual(token["refresh_token"], "refresh")
        self.assertEqual(token["access_token"], "new")
        save_secret_json.assert_called_once()

    def test_performance_body(self):
        args = argparse.Namespace(
            date_from="2026-01-01",
            date_to="2026-01-31",
            dimensions="date,query",
            search_type="web",
            limit=100,
            start_row=0,
            data_state="final",
            aggregation="auto",
            filter=["device:equals:MOBILE"],
        )
        body = gsc.performance_body(args)
        self.assertEqual(body["dimensions"], ["date", "query"])
        self.assertEqual(
            body["dimensionFilterGroups"][0]["filters"][0]["expression"], "MOBILE"
        )


if __name__ == "__main__":
    unittest.main()
