"""Offline checks for license preservation in standalone skill installations."""
from pathlib import Path
import shutil
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_installable_skill_has_license_notice(self):
        notice = (SKILL / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", notice)
        self.assertIn("Copyright (c) 2026 Mangesh Raut", notice)
        self.assertIn("The above copyright notice and this permission notice shall be included", notice)

    def test_repository_and_package_licenses_match(self):
        # The repository root is intentionally absent in a standalone install.
        root = SKILL.parent.parent
        if not (root / "README.md").is_file() or not (root / "LICENSE").is_file():
            self.skipTest("Standalone install has no repository root to compare")
        self.assertEqual((root / "LICENSE").read_bytes(), (SKILL / "LICENSE").read_bytes())

    def test_copying_only_skill_preserves_license(self):
        with tempfile.TemporaryDirectory() as folder:
            installed = Path(folder) / "oss-contribution-insights"
            shutil.copytree(SKILL, installed, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertEqual((installed / "LICENSE").read_bytes(), (SKILL / "LICENSE").read_bytes())


if __name__ == "__main__":
    unittest.main()
