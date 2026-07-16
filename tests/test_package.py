import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "google-search-console-api"
CYRILLIC = re.compile("[\u0400-\u04ff]")
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml"}
REQUIRED_FILES = {
    "README.md",
    "google-search-console-api/SKILL.md",
    "agents/openai.yaml",
    "google-search-console-api/.gitignore",
    "google-search-console-api/references/ANALYSIS.md",
    "google-search-console-api/references/SETUP.md",
    "google-search-console-api/scripts/gsc.py",
}
FORBIDDEN_TRACKED_FILES = {
    "google-search-console-api/config/client_secret.json",
    "google-search-console-api/config/token.json",
}


def tracked_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line for line in result.stdout.splitlines() if line}


def public_text_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        if any(part in {".git", "cache", "config"} for part in relative.parts):
            continue
        files.append(path)
    return files


class PackageTest(unittest.TestCase):
    def test_required_files_exist(self):
        missing = {path for path in REQUIRED_FILES if not (ROOT / path).is_file()}
        self.assertFalse(missing, f"Missing required files: {sorted(missing)}")

    def test_skill_frontmatter_and_body(self):
        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"))
        _, frontmatter, body = content.split("---", 2)
        self.assertRegex(frontmatter, r"(?m)^name: google-search-console-api$")
        self.assertRegex(frontmatter, r"(?m)^description: .+$")
        self.assertTrue(body.strip())

    def test_sensitive_runtime_files_are_not_tracked(self):
        tracked = tracked_files()
        self.assertTrue(FORBIDDEN_TRACKED_FILES.isdisjoint(tracked))
        self.assertFalse(
            any(path.startswith("google-search-console-api/cache/") for path in tracked)
        )

    def test_public_text_is_english(self):
        for path in public_text_files():
            relative_path = path.relative_to(ROOT)
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(
                CYRILLIC.search(content),
                f"Cyrillic text found in {relative_path}",
            )


if __name__ == "__main__":
    unittest.main()
