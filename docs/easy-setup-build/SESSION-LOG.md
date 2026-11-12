# Session log

- 2026-11-11 Branch `docs/easy-setup` from main 2a881aa. Resume cron b8177f8c (hourly :17).
- 2026-11-11 Decision: skip Spec Kit; this is documentation only.
- 2026-11-11 Decision: new guide is `START-HERE-EASY-SETUP.md` at the root, so it stands out in the file list. Undo: rename and fix the two links in README and the pointer file.
- 2026-11-11 Decision: `CODEX-QUICKSTART.md` kept as a five-line pointer, so links already sent to friends still work. The duplicated prompt in the README is replaced by a link. Undo: `git revert`.
- 2026-11-11 Decision: two chats, not three. Chat 1 downloads and installs; the reader always restarts the program; chat 2 re-checks, installs anything still missing, then onboards. One fewer step than the owner's sketch, same safety. Undo: split message 2 in the guide.
- 2026-11-11 Decision: the reader makes the folder and opens it before anything is downloaded (as the old quickstart did), so every chat is already in the right place.
- 2026-11-11 Finding: the Codex app is now part of the ChatGPT desktop app (chatgpt.com/download; choose Codex from the ChatGPT menu). Guide follows the vendor docs' wording; labels may drift, so the guide tells readers to ask the program when a button is missing.
- 2026-11-11 Finding: OpenAI's pricing page lists Codex on every ChatGPT plan including Free; Claude's Code tab needs a paid plan.
- 2026-11-11 Decision: screenshots are the two public download pages (clean Playwright browser, cropped) plus one drawing of the app. No capture of the owner's own apps: it would show personal sessions. Images are .webp because .gitignore ignores png and jpg.
- 2026-11-11 Verified: fresh clone of the public repo into an empty "Job Search" folder, then `python harness_setup.py --doctor --quick` there: all required prerequisites in place. Guards, privacy sweep and skill lint OK; 461 harness tests pass. All links and images in the three files resolve.
- 2026-11-11 Fresh-context review (non-technical reader, plus accuracy against the repo): 9 must-fix findings, all confirmed and fixed. Both pasted messages now use `--yes --quick` (the doctor installs nothing; the full run's test compiles can outlast an agent's shell limit), tolerate RESTART SHELL and a missing "Agent runtime" row (desktop app only), and handle a non-empty folder and a Mac. Message 2 asks for lite mode with no optional extras, so the reader never meets the plan question, an API key or a terminal. Step 8 and the safety note reworded to match what onboarding and uninstalling really do.
- 2026-11-11 Decision: lite mode for everyone on this guide (5 to 10 minute setup, far less usage). Undo: drop "in lite mode" from message 2. Trade-off accepted: with `--quick` the document templates are not test-compiled until the first application.
- 2026-11-11 Not verified: the two messages were not run end to end on a clean computer, and the guide was not tried on a Mac. In-app button names come from vendor docs dated 2026-11-11.
