"""Tests for the two privacy guards, and for the continuity layer's contracts.

The guards are deliberately two separate tools with different failure modes,
and these tests pin that split:

* `tools/harness_guards.py` is structural, ignore rules present, nothing
  personal tracked. It cannot see a phone number pasted into a README.
* `harness/privacy_sweep.py` is content, it scans what files actually say. It
  cannot see a deleted gitignore rule.

Merging them would lose one of those, which is why `test_the_two_guards_check_
different_things` exists.

The sweep's allow-list is the part most likely to be loosened under pressure, so
several tests assert it still catches the things it is for.
"""

from __future__ import annotations

import importlib
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

privacy_sweep = importlib.import_module("privacy_sweep")


def flat(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8").lower())


class GuardsPassOnThisRepo(unittest.TestCase):
    def test_harness_guards_pass(self):
        proc = subprocess.run([sys.executable, str(ROOT / "tools" / "harness_guards.py")],
                              capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_privacy_sweep_reports_no_blocking_hits(self):
        proc = subprocess.run([sys.executable, str(ROOT / "harness" / "privacy_sweep.py")],
                              capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("no personal data found", proc.stdout)

    def test_upstream_security_guards_still_pass(self):
        """The harness must never have weakened upstream's own guard."""
        proc = subprocess.run([sys.executable, str(ROOT / "tools" / "security_guards.py")],
                              capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)


class SweepStillCatchesRealData(unittest.TestCase):
    """The allow-list must not have become an everything-list."""

    def scan_text(self, text: str) -> list:
        """Run the production matcher over one blob of text.

        This used to re-implement the loop, which meant it could stay green
        after `scan()` stopped passing the label to `is_allowed`. Calling
        `find_hits`, the same function `scan()` uses, removes that gap.
        """
        return [(n, label, value) for n, label, value, _ in privacy_sweep.find_hits(text)]

    def test_a_placeholder_on_the_line_does_not_excuse_a_real_email(self):
        """REGRESSION: one `your-` anywhere on a line excused every match on it.

        The line-level placeholder check ran above the contact-label split, so
        a template-looking line carrying one real address shipped clean, the
        exact hole the split was written to close.
        """
        hits = self.scan_text(
            "your-config example: jane.doe@realcompany.co.uk")
        self.assertTrue(any(label == "email" for _, label, _ in hits), hits)

    def test_a_placeholder_inside_the_match_is_still_excused(self):
        self.assertEqual([], self.scan_text("email: your.email@example.com"))

    def test_catches_a_real_email(self):
        hits = self.scan_text("Contact me at jane.doe@realcompany.co.uk about the role.")
        self.assertTrue(any(label == "email" for _, label, _ in hits))

    def test_catches_a_real_phone_number(self):
        hits = self.scan_text("Call 604-555-9182 for details.")
        self.assertTrue(any(label == "phone" for _, label, _ in hits))

    def test_catches_a_canadian_postal_code(self):
        hits = self.scan_text("Mail it to R3C 4T2 before Friday.")
        self.assertTrue(any("postal" in label for _, label, _ in hits))

    def test_catches_an_api_key(self):
        hits = self.scan_text("token: ghp_abcdefghijklmnopqrstuvwxyz0123456789")
        self.assertTrue(any("key" in label or "token" in label for _, label, _ in hits))

    def test_catches_a_real_linkedin_profile(self):
        hits = self.scan_text("Profile: linkedin.com/in/jane-doe-8891")
        self.assertTrue(any("linkedin" in label for _, label, _ in hits))

    def test_allows_the_demo_candidate(self):
        hits = self.scan_text(
            "Riley Chen, riley.chen@example.com, +1 555-0142"
        )
        self.assertEqual([], hits)

    def test_allows_placeholder_tokens(self):
        hits = self.scan_text(
            "Email: [YOUR_EMAIL] · linkedin.com/in/your-profile · @@CONTACT@@"
        )
        self.assertEqual([], hits)

    def test_github_urls_are_advisory_not_blocking(self):
        """Attribution links must not fail the build.

        The first version of the sweep blocked on these and produced 71 hits,
        essentially all of them required licence attribution in upstream's own
        CONTRIBUTING.md and CHANGELOG.md. A gate that has to be waived every run
        is not a gate.
        """
        labels = {label for label, _ in privacy_sweep.BLOCKING_PATTERNS}
        self.assertNotIn("github url", labels)
        advisory = {label for label, _ in privacy_sweep.ADVISORY_PATTERNS}
        self.assertIn("github url", advisory)

    def test_strict_mode_promotes_advisory_to_blocking(self):
        """The category is kept, not deleted, the owner can still demand it."""
        blocking, advisory = privacy_sweep.scan(strict=True)
        self.assertEqual([], advisory)


class TelemetryMirror(unittest.TestCase):
    def test_extracts_the_documented_fields(self):
        module = importlib.import_module("telemetry_statusline")
        record = module.extract({
            "context_window": {"used_percentage": 81.5},
            "rate_limits": {"five_hour": {"used_percentage": 40},
                            "seven_day": {"used_percentage": 12}},
            "model": {"display_name": "Opus"},
        })
        self.assertEqual(81.5, record["context_pct"])
        self.assertEqual(40, record["five_hour_pct"])
        self.assertEqual(12, record["seven_day_pct"])
        self.assertTrue(record["caveats"])

    def test_missing_fields_become_null_not_guesses(self):
        module = importlib.import_module("telemetry_statusline")
        record = module.extract({})
        self.assertIsNone(record["context_pct"])
        self.assertIsNone(record["five_hour_pct"])

    def test_caveats_travel_with_the_numbers(self):
        """A percentage without its caveats invites planning around a lie."""
        module = importlib.import_module("telemetry_statusline")
        joined = " ".join(module.CAVEATS).lower()
        self.assertIn("input tokens only", joined)
        self.assertIn("compact", joined)

    def test_render_never_invents_a_value(self):
        module = importlib.import_module("telemetry_statusline")
        self.assertEqual("harness", module.render(module.extract({})))


if __name__ == "__main__":
    unittest.main()
