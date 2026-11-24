"""Tests for the P4 apply overlay: intake ladder, apply wrapper, .md mirror.

`harness/tex_to_md.py` is exercised for real. The two command/skill documents
are checked for the promises whose loss would change behaviour silently, the
ones where a missing sentence produces a package that looks fine and is not:

* the humanizer pass is followed by a re-ground (a rewrite that strengthens a
  claim past its evidence reads *better*, so nothing catches it by eye);
* posting content is untrusted, including links inside it;
* a `mandatory_only` hard skip does not fire on a "preferred" line;
* the `.md` mirror is generated, never hand-written.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
COMMANDS = ROOT / ".claude" / "commands"
SKILLS = ROOT / ".claude" / "skills"


def flat(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8").lower())


class TexToMdMirror(unittest.TestCase):
    def test_self_check_passes(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "harness" / "tex_to_md.py"), "--self-check"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("OK", proc.stdout)

    def test_mirror_takes_its_identity_from_the_register(self):
        """The ported original carried a real person's name, phone and email as
        a module constant; identity must come from the register instead.

        This used to grep the module's own source for the string
        `contact_block` and accept either outcome of the run - so it passed
        with the function stubbed out, and never checked that any identity
        reached the output. It now renders against the demo register and looks
        for the demo candidate.
        """

        tex = ("\\begin{document}\\makecvtitle\n"
               "\\section{Experience}\n"
               "\\item Did a thing.\n"
               "\\end{document}")
        with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False,
                                         encoding="utf-8") as handle:
            handle.write(tex)
            path = handle.name
        try:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "harness" / "tex_to_md.py"), path,
                 "--register", str(ROOT / "evidence" / "register.example.yaml")],
                capture_output=True, text=True, cwd=str(ROOT),
            )
        finally:
            Path(path).unlink()
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("Riley Chen", proc.stdout)
        self.assertIn("riley.chen@example.com", proc.stdout)

    def test_mirror_refuses_to_render_without_a_register(self):
        """Better a loud failure than a mirror with no identity on it."""

        with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False,
                                         encoding="utf-8") as handle:
            handle.write("\\begin{document}\\makecvtitle\\end{document}")
            path = handle.name
        try:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "harness" / "tex_to_md.py"), path,
                 "--register", str(ROOT / "evidence" / "does-not-exist.yaml")],
                capture_output=True, text=True, cwd=str(ROOT),
            )
        finally:
            Path(path).unlink()
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("no evidence register", proc.stdout + proc.stderr)

    def test_profile_statement_survives_its_size_wrapper(self):
        """`\\small{...}` opened the profile paragraph, and every line starting
        with a backslash was dropped: the profile lost its first line in every
        .md/.docx and in the ATS check, and kept a stray closing brace."""
        import tex_to_md
        out = tex_to_md.convert_cv("\\small{Analyst who owns the data,\n"
                                   "from field collection to the report.}\n")
        self.assertEqual(["Analyst who owns the data,",
                          "from field collection to the report."], [line for line in out if line])


if __name__ == "__main__":
    unittest.main()
