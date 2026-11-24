"""Tests for harness_setup.py's probes and doctor table.

Every probe is exercised against a *mocked* PATH and mocked subprocess calls,
so the suite asserts the same behaviour on any machine, including CI, which
has no TeX, no Bun and no agent runtime.

The cases worth reading are the ones that pin down defects the build actually
hit, because those are what a future refactor is most likely to undo:

* `test_bun_present_but_panicking_is_degraded`, Bun's stock build installs
  fine on a CPU without AVX2 and then panics on every call. A presence-only
  check reports green on a machine where all six portal CLIs are dead.
* `test_poppler_needs_pdfinfo_too`, Git for Windows ships pdftotext but not
  pdfinfo, so checking pdftotext alone reports poppler present when upstream's
  PDF verification cannot run.
* `test_tool_on_persistent_path_only_says_restart_shell`, a tool installed
  seconds ago is on the registry PATH but not in the running shell; reporting
  MISSING sends the user round in circles re-installing it.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import harness_setup as setup  # noqa: E402  (the path shim above must run first)


def fake_which(available: dict[str, str]):
    """shutil.which stand-in. `available` maps tool name -> fake path."""

    def _which(name, mode=None, path=None):
        # When called with an explicit `path=`, setup is probing the
        # persistent Windows PATH; only tools flagged persistent-only resolve.
        if path is not None:
            return available.get(f"persistent:{name}")
        return available.get(name)

    return _which


def fake_run(results: dict[str, tuple[int, str]], default=(0, "")):
    """setup.run stand-in, keyed on the first argument's basename."""

    def _run(args, timeout=180, cwd=None):
        return results.get(Path(args[0]).stem, default)

    return _run


class BunCheck(unittest.TestCase):
    def test_missing_bun_is_missing(self):
        with mock.patch.object(setup.shutil, "which", fake_which({})), \
             mock.patch.object(setup, "_persistent_path_dirs", return_value=[]):
            check = setup.check_bun()
        self.assertEqual(check.status, setup.MISSING)

    def test_working_bun_is_ok(self):
        with mock.patch.object(setup.shutil, "which",
                               fake_which({"bun": "/fake/bun"})), \
             mock.patch.object(setup, "run", fake_run({"bun": (0, "1.3.14\n")})):
            check = setup.check_bun()
        self.assertEqual(check.status, setup.OK)
        self.assertIn("1.3.14", check.detail)

    def test_bun_present_but_panicking_is_degraded(self):
        """A no-AVX2 CPU: bun exists, resolves, and dies on every call."""
        panic = (3, "Features: no_avx2\npanic: Illegal instruction at address 0x7FF\n")
        with mock.patch.object(setup.shutil, "which",
                               fake_which({"bun": "/fake/bun"})), \
             mock.patch.object(setup, "run", fake_run({"bun": panic})):
            check = setup.check_bun()
        self.assertEqual(check.status, setup.DEGRADED)
        self.assertIn("AVX2", check.detail)
        # The fix must name the baseline package, or the user cannot act on it.
        self.assertIn("Oven-sh.Bun.Baseline", check.fix)

    def test_bun_nonzero_exit_is_degraded_not_ok(self):
        with mock.patch.object(setup.shutil, "which",
                               fake_which({"bun": "/fake/bun"})), \
             mock.patch.object(setup, "run", fake_run({"bun": (1, "some error")})):
            check = setup.check_bun()
        self.assertEqual(check.status, setup.DEGRADED)


class PopplerCheck(unittest.TestCase):
    def test_both_binaries_present_is_ok(self):
        available = {"pdftotext": "/fake/pdftotext", "pdfinfo": "/fake/pdfinfo"}
        with mock.patch.object(setup.shutil, "which", fake_which(available)):
            check = setup.check_poppler()
        self.assertEqual(check.status, setup.OK)

    def test_poppler_needs_pdfinfo_too(self):
        """Git for Windows ships pdftotext only, that is not poppler."""
        with mock.patch.object(setup.shutil, "which",
                               fake_which({"pdftotext": "/git/pdftotext"})), \
             mock.patch.object(setup, "_persistent_path_dirs", return_value=[]):
            check = setup.check_poppler()
        self.assertEqual(check.status, setup.MISSING)
        self.assertIn("pdfinfo", check.detail)
        self.assertIn("Git for Windows", check.detail)

    def test_neither_binary_present_is_missing(self):
        with mock.patch.object(setup.shutil, "which", fake_which({})), \
             mock.patch.object(setup, "_persistent_path_dirs", return_value=[]):
            check = setup.check_poppler()
        self.assertEqual(check.status, setup.MISSING)


class StalePathCheck(unittest.TestCase):
    def test_tool_on_persistent_path_only_says_restart_shell(self):
        available = {"persistent:pandoc": "/fake/pandoc"}
        with mock.patch.object(setup.shutil, "which", fake_which(available)), \
             mock.patch.object(setup, "_persistent_path_dirs", return_value=["/fake"]):
            check = setup.check_simple("pandoc", "pandoc", ["--version"],
                                       required=False)
        self.assertEqual(check.status, setup.STALE_PATH)
        self.assertIn("reopen", check.fix.lower())

    def test_find_tool_prefers_the_live_shell_path(self):
        available = {"bun": "/live/bun", "persistent:bun": "/registry/bun"}
        with mock.patch.object(setup.shutil, "which", fake_which(available)):
            path, stale = setup.find_tool("bun")
        self.assertEqual(path, "/live/bun")
        self.assertFalse(stale)


class TexCheck(unittest.TestCase):
    def test_missing_engines_are_reported_individually(self):
        with mock.patch.object(setup.shutil, "which", fake_which({})), \
             mock.patch.object(setup, "_persistent_path_dirs", return_value=[]):
            checks = setup.check_tex(quick=True)
        names = {c.name: c.status for c in checks}
        self.assertEqual(names["lualatex"], setup.MISSING)
        self.assertEqual(names["xelatex"], setup.MISSING)

    def test_quick_mode_marks_compiles_unverified_not_ok(self):
        """--quick must never claim a compile passed that never ran."""
        available = {"lualatex": "/fake/lualatex", "xelatex": "/fake/xelatex"}
        with mock.patch.object(setup.shutil, "which", fake_which(available)), \
             mock.patch.object(setup, "run", fake_run({}, default=(0, "TeX 1.0"))):
            checks = setup.check_tex(quick=True)
        compiles = [c for c in checks if c.name.endswith("compile")]
        self.assertEqual(len(compiles), 2)
        for check in compiles:
            self.assertEqual(check.status, setup.UNVERIFIED)

    def test_failed_compile_is_degraded_with_the_latex_error(self):
        log = "This is LuaTeX\n! LaTeX Error: File `moderncv.cls' not found.\n"
        with mock.patch.object(setup, "run", fake_run({}, default=(1, log))), \
             mock.patch.object(Path, "is_file", return_value=True):
            check = setup._test_compile("/fake/lualatex", "lualatex", Path("cv"),
                                        "main_example.tex", "CV template")
        self.assertEqual(check.status, setup.DEGRADED)
        self.assertIn("moderncv.cls", check.fix)


class PlanAndMode(unittest.TestCase):
    """Setup recommends lite below ChatGPT Pro / Claude Max and records the choice."""

    def pick(self, answer: str):
        with mock.patch("builtins.input", return_value=answer), \
             mock.patch("builtins.print"):
            return setup.ask_plan()

    def test_recommendation_follows_the_plan(self):
        self.assertEqual(("chatgpt-plus", "lite"), self.pick("1"))
        self.assertEqual(("chatgpt-pro", "standard"), self.pick("2"))
        self.assertEqual(("claude-pro", "lite"), self.pick("3"))
        self.assertEqual(("claude-max", "standard"), self.pick("4"))

    def test_no_answer_takes_the_cheapest_safe_choice(self):
        self.assertEqual(("other", "lite"), self.pick(""))
        self.assertEqual(("other", "lite"), self.pick("9"))

    def test_choice_is_recorded_once_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            setup.seed_preferences("claude-pro", "lite", root)
            text = (root / "preferences.yaml").read_text(encoding="utf-8")
            self.assertIn("mode: lite", text)
            self.assertIn("plan: claude-pro", text)
            setup.seed_preferences("claude-max", "standard", root)
            self.assertEqual(text, (root / "preferences.yaml").read_text(encoding="utf-8"))

    def test_standard_is_recorded_as_the_focused_usage_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            setup.seed_preferences("claude-max", "standard", Path(tmp))
            self.assertIn("mode: focused",
                          (Path(tmp) / "preferences.yaml").read_text(encoding="utf-8"))


class FirecrawlLocal(unittest.TestCase):
    """One local binary replaces Playwright and the Firecrawl cloud server."""

    def setUp(self):
        self.runtime = setup.Runtime(name="claude", exe="/fake/claude")

    def test_missing_binary_is_optional_and_runs_nothing(self):
        with mock.patch.object(setup, "find_tool", return_value=(None, "")), \
             mock.patch.object(setup, "mcp_listing", return_value=""), \
             mock.patch.object(setup, "run") as run:
            checks = setup.offer_mcp(self.runtime)
        run.assert_not_called()
        self.assertEqual(checks[0].status, setup.OPTIONAL)

    def test_registers_the_local_binary_and_refuses_private_addresses(self):
        captured: list[list[str]] = []

        def record(args, timeout=180, cwd=None):
            captured.append(args)
            return 0, ""

        with mock.patch.object(setup, "find_tool", return_value=("/opt/fc-local", "")), \
             mock.patch.object(setup, "confirm", return_value=True), \
             mock.patch.object(setup, "mcp_listing", side_effect=["", "firecrawl"]), \
             mock.patch.object(setup, "run", record), \
             mock.patch("builtins.print"):
            checks = setup.offer_mcp(self.runtime)
        self.assertEqual(["/fake/claude", "mcp", "add", "firecrawl", "--",
                          "/opt/fc-local", "mcp", "--public-only"], captured[0])
        self.assertEqual(checks[0].status, setup.OK)

    def test_add_without_a_listing_is_unverified_not_ok(self):
        with mock.patch.object(setup, "find_tool", return_value=("/opt/fc-local", "")), \
             mock.patch.object(setup, "confirm", return_value=True), \
             mock.patch.object(setup, "mcp_listing", side_effect=["", ""]), \
             mock.patch.object(setup, "run", return_value=(0, "")), \
             mock.patch("builtins.print"):
            checks = setup.offer_mcp(self.runtime)
        self.assertEqual(checks[0].status, setup.UNVERIFIED)

    def test_already_configured_is_not_re_added(self):
        with mock.patch.object(setup, "mcp_listing", return_value="firecrawl"), \
             mock.patch.object(setup, "run") as run, \
             mock.patch("builtins.print"):
            checks = setup.offer_mcp(self.runtime)
        run.assert_not_called()
        self.assertEqual(checks[0].status, setup.OK)

    def test_the_doctor_row_names_the_install_command(self):
        with mock.patch.object(setup, "find_tool", return_value=(None, "")):
            check = setup.check_firecrawl_local()
        self.assertEqual(check.status, setup.OPTIONAL)
        self.assertIn("cargo install", check.fix)

    def test_installed_binary_reports_its_version(self):
        with mock.patch.object(setup, "find_tool", return_value=("/opt/fc-local", "")), \
             mock.patch.object(setup, "run", return_value=(0, "firecrawl-local 0.4.1\n")):
            check = setup.check_firecrawl_local()
        self.assertEqual(check.status, setup.OK)
        self.assertIn("0.4.1", check.detail)


class PlatformHints(unittest.TestCase):
    """A fix line names a command that exists on the machine printing it."""

    def hint(self, os_name, platform):
        with mock.patch.object(setup.os, "name", os_name), \
             mock.patch.object(setup.sys, "platform", platform):
            return setup.platform_hint("winget x", "brew x", "apt x")

    def test_each_platform_gets_its_own_command(self):
        self.assertEqual(self.hint("nt", "win32"), "winget x")
        self.assertEqual(self.hint("posix", "darwin"), "brew x")
        self.assertEqual(self.hint("posix", "linux"), "apt x")

    def test_macos_advice_offers_no_windows_or_debian_command(self):
        with mock.patch.object(setup.os, "name", "posix"), \
             mock.patch.object(setup.sys, "platform", "darwin"), \
             mock.patch.object(setup, "find_tool", return_value=(None, "")):
            checks = [*setup.check_tex(), setup.check_poppler()]
        missing = [c for c in checks if c.status == setup.MISSING]
        self.assertTrue(missing, "TeX and poppler should both be reported missing")
        for check in missing:
            self.assertNotIn("winget", check.fix)
            self.assertNotIn("apt install", check.fix)
            self.assertIn("brew", check.fix)


class ProjectEnvironment(unittest.TestCase):
    """uv owns the environment; the check reads the .venv it creates."""

    def test_missing_uv_is_required_and_names_an_installer(self):
        with mock.patch.object(setup, "find_tool", return_value=(None, "")):
            check = setup.check_uv()
        self.assertEqual(check.status, setup.MISSING)
        self.assertTrue(check.required)
        self.assertTrue({"winget", "brew", "uv/install.sh"} & {w for w in
                        ("winget", "brew", "uv/install.sh") if w in check.fix})

    def test_install_runs_uv_sync_in_the_repo(self):
        seen: list[list[str]] = []

        def record(args, timeout=180, cwd=None):
            seen.append(args)
            return 0, ""

        with mock.patch.object(setup, "find_tool", return_value=("/opt/uv", "")), \
             mock.patch.object(setup, "run", record), \
             mock.patch.object(setup, "check_python_deps",
                               return_value=setup.Check("Python packages", setup.OK)), \
             mock.patch("builtins.print"):
            check = setup.install_python_deps()
        self.assertEqual(["/opt/uv", "sync"], seen[0])
        self.assertEqual(setup.OK, check.status)

    def test_install_without_uv_says_so_instead_of_running_pip(self):
        with mock.patch.object(setup, "find_tool", return_value=(None, "")), \
             mock.patch.object(setup, "run") as run:
            check = setup.install_python_deps()
        run.assert_not_called()
        self.assertEqual(check.status, setup.MISSING)


class PortalInstallScope(unittest.TestCase):
    """A disabled portal's CLI is not prepared, and setup says which it skipped."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name, enabled in (("alpha-search", "true"), ("beta-search", "false")):
            cli = self.root / ".agents" / "skills" / name / "cli"
            cli.mkdir(parents=True)
            (cli.parent / "SKILL.md").write_text(
                f"---\nname: {name}\nenabled: {enabled}\n---\n", encoding="utf-8")

    def test_enabled_only_filters_the_toggle(self):
        with mock.patch.object(setup, "ROOT", self.root):
            self.assertEqual(["alpha-search"],
                             [p.parent.name for p in setup.portal_cli_dirs(enabled_only=True)])
            self.assertEqual(["alpha-search", "beta-search"],
                             [p.parent.name for p in setup.portal_cli_dirs()])

    def test_only_the_enabled_portal_gets_a_bun_install(self):
        served: list[str] = []

        def record(args, timeout=180, cwd=None):
            served.append(Path(cwd).parent.name)
            return 0, ""

        with mock.patch.object(setup, "ROOT", self.root), \
             mock.patch.object(setup, "find_tool", return_value=("/fake/bun", "")), \
             mock.patch.object(setup, "run", record), \
             mock.patch("builtins.print"):
            checks = setup.install_portal_deps()
        self.assertEqual(["alpha-search"], served)
        self.assertEqual(checks[0].status, setup.OK)
        self.assertIn("1 CLIs", checks[0].detail)


class DoctorTable(unittest.TestCase):
    def test_exit_code_counts_only_required_failures(self):
        checks = [
            setup.Check("Python", setup.OK, "3.14.3"),
            setup.Check("Bun", setup.DEGRADED, "crashes"),
            setup.Check("lualatex", setup.MISSING, "not on PATH"),
            setup.Check("pandoc", setup.MISSING, "not on PATH", required=False),
            setup.Check("firecrawl MCP", setup.OPTIONAL, "declined", required=False),
        ]
        with mock.patch("builtins.print"):
            failures = setup.print_doctor(checks)
        self.assertEqual(failures, 2)


    def test_unverified_is_not_counted_as_pass_or_fail(self):
        """UNVERIFIED must stay visible rather than silently becoming OK."""
        checks = [setup.Check("lualatex compile", setup.UNVERIFIED,
                              "skipped (--quick)", required=False)]
        with mock.patch("builtins.print"):
            self.assertEqual(setup.print_doctor(checks), 0)
        self.assertNotEqual(checks[0].status, setup.OK)


class ConfirmBehaviour(unittest.TestCase):
    def tearDown(self):
        setup.AUTO_YES = False
        setup.DOCTOR_ONLY = False

    def test_doctor_mode_never_installs(self):
        setup.DOCTOR_ONLY = True
        self.assertFalse(setup.confirm("Install something?", default=True))

    def test_yes_mode_takes_the_default(self):
        setup.AUTO_YES = True
        with mock.patch("builtins.print"):
            self.assertTrue(setup.confirm("Recommended thing?", default=True))
            self.assertFalse(setup.confirm("Opt-in thing?", default=False))

    def test_piped_stdin_falls_back_to_default(self):
        with mock.patch("builtins.input", side_effect=EOFError), \
             mock.patch("builtins.print"):
            self.assertFalse(setup.confirm("Install the optional server?", default=False))


class PortalInstallRetry(unittest.TestCase):
    """A clean clone fails `bun install` once and succeeds on the second run.

    `@types/bun` pulls in the `bun` npm package, whose postinstall downloads a
    platform binary; on Windows it exits 1 with "Failed to find package
    @oven/bun-windows-x64-baseline". Measured on a clean clone of 2a4772b: 4 of
    7 CLIs failed, setup exited 1 telling the user the harness would not work,
    and a plain re-run fixed all 7 without any other change.
    """

    POSTINSTALL_FAILURE = (1, 'error: postinstall script from "bun" exited with 1')

    def _install(self, outcomes):
        """Run install_portal_deps against two fake CLI dirs. `outcomes` is the
        sequence of (code, output) pairs returned per `bun install` call."""
        calls: list[Path] = []

        def _run(args, timeout=180, cwd=None):
            calls.append(cwd)
            return outcomes[min(len(calls) - 1, len(outcomes) - 1)]

        dirs = [Path("/fake/a/cli"), Path("/fake/b/cli")]
        with mock.patch.object(setup.shutil, "which",
                               fake_which({"bun": "/fake/bun"})), \
             mock.patch.object(setup, "portal_cli_dirs", return_value=dirs), \
             mock.patch.object(setup, "run", _run), \
             mock.patch("builtins.print"):
            return setup.install_portal_deps(), calls

    def test_first_attempt_failure_is_retried_and_clears(self):
        checks, calls = self._install([self.POSTINSTALL_FAILURE, (0, "ok")])
        self.assertEqual(checks[0].status, setup.OK)
        # Two attempts on the first directory, one on the second.
        self.assertEqual(len(calls), 3)

    def test_a_failure_that_survives_the_retry_is_still_reported(self):
        checks, calls = self._install([self.POSTINSTALL_FAILURE])
        self.assertEqual(checks[0].status, setup.DEGRADED)
        self.assertIn("2 of 2 failed", checks[0].detail)
        self.assertEqual(len(calls), 4)  # never more than one retry each


class SeededPermissions(unittest.TestCase):
    def test_the_ats_text_extraction_is_pre_approved(self):
        """`pdftotext -layout` is a mandatory step of the Verification
        Checklist, so leaving it out costs one dialog on every application."""
        self.assertIn("Bash(pdftotext:*)", setup.HARNESS_PERMISSIONS)


class CodexNetworkCheck(unittest.TestCase):
    """Codex's workspace-write sandbox has no network unless the user enables
    it, and a board CLI that cannot connect looks like a quiet board."""

    def check(self, config: str | None):
        with tempfile.TemporaryDirectory() as home:
            if config is not None:
                (Path(home) / "config.toml").write_text(config, encoding="utf-8")
            return setup.check_codex_network(Path(home))

    def test_no_config_means_the_default_which_is_off(self):
        check = self.check(None)
        self.assertEqual(check.status, setup.OPTIONAL)
        self.assertIn("network_access = true", check.fix)
        self.assertFalse(check.required)

    def test_network_enabled_for_workspace_write_is_ok(self):
        check = self.check('[sandbox_workspace_write]\nnetwork_access = true\n')
        self.assertEqual(check.status, setup.OK)

    def test_full_access_sandbox_is_ok(self):
        self.assertEqual(self.check('sandbox_mode = "danger-full-access"\n').status, setup.OK)

    def test_profiles_are_not_guessed_at(self):
        self.assertEqual(self.check('profile = "work"\n').status, setup.UNVERIFIED)

    def test_unreadable_config_is_unverified_not_ok(self):
        self.assertEqual(self.check("this is = = not toml").status, setup.UNVERIFIED)


if __name__ == "__main__":
    unittest.main()
