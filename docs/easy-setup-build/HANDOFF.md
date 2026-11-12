# Handoff: easy set-up guide

**State (2026-11-11): finished and pushed to main.**

- The guide is `START-HERE-EASY-SETUP.md` at the repo root. The README links to it in a
  callout on its first screen. `CODEX-QUICKSTART.md` is now a pointer to it.
- Flow: install ChatGPT (Codex) or Claude, make a "Job Search" folder, open it, paste
  message 1 (download and install), click Allow, restart the program, new chat, paste
  message 2 (finish install, lite-mode onboarding), answer its questions.
- Images are in `docs/media/setup-*.webp`: the two public download pages and one drawing
  of the app.

## Not verified

- The two pasted messages have not been run end to end on a clean computer. What was
  checked: the repo downloads into an empty folder and the doctor runs there.
- Nothing was tried on a Mac.
- Button names inside the ChatGPT and Claude apps come from the vendors' docs on
  2026-11-11. Both apps change often.

## Next step, if wanted

Watch one real non-technical person follow the guide on their own computer, note where
they hesitate, and fix those lines. Replace the drawing with real in-app screenshots at
the same time.

## How to check

    python tools/harness_guards.py && python harness/privacy_sweep.py
    python -m unittest discover -s tests_harness -t .
