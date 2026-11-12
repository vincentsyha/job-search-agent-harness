# Build plan: easy set-up guide for non-technical people

**Goal.** A set-up guide a non-technical person can follow alone, obvious on the repo's
front page, with the AI program doing as much of the work as possible.

## Deepened brief

1. A professional would add: a "what you will see" picture, a "stuck" section with one
   message to paste, plain cost and safety notes, and no branch in the steps that needs a
   technical judgement (always restart, always start a new chat).
2. Primary sources: `harness_setup.py`, `.claude/commands/setup-harness.md`, the old
   `CODEX-QUICKSTART.md`, and the vendors' current install pages and docs (checked
   2026-11-11: Codex now lives inside the ChatGPT desktop app).
3. Methods: no Spec Kit (docs only). Playwright for screenshots.
4. Proof: see acceptance checks.

## Acceptance checks

- [x] A1. Guide is at the repo root with an unmistakable name and is linked in the first
      screen of the README.
- [x] A2. The first message's real path works: the repo downloads into an empty folder
      and `python harness_setup.py --doctor --quick` runs there.
- [x] A3. Every link and image in the guide resolves.
- [x] A4. Screenshots hold no personal information (clean browser, viewed one by one).
- [x] A5. A fresh-context reviewer reading as a non-technical person finds no blocking
      confusion; confirmed findings fixed.
- [x] A6. Repo guards, privacy sweep and harness tests pass.

## Steps

- [x] Research current install flow for ChatGPT (Codex) and Claude
- [x] Screenshots and drawing in `docs/media/`
- [x] Write `START-HERE-EASY-SETUP.md`
- [x] README callout; `CODEX-QUICKSTART.md` becomes a pointer
- [x] Review, checks, commit, push

## Later (not built)

- Real screenshots from inside the ChatGPT and Claude apps (needs the owner's screen;
  the drawing stands in for now).
- A short screen recording of the whole flow.
- Trying the guide on a clean computer with a real non-technical reader.
